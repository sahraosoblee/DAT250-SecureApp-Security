import time
from contextlib import closing
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from psycopg2.extras import RealDictCursor

from app.auth import (
    clear_session,
    create_session,
    get_user_from_session,
    hash_password,
    verify_password,
)
from app.database import get_conn, run_query
from app.email_service import send_reset_email

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

COOLDOWN_SECONDS = (30, 60, 120, 240, 480, 900)
FIRST_COOLDOWN_ATTEMPT = 5
FAILURE_WINDOW = timedelta(minutes=30)

COMMON_PASSWORDS = {
    "123456789012345",
    "1234567890123456",
    "abcdefghijklmnop",
    "passwordpassword",
    "passwordpasswordpassword",
    "qwertyuiopasdfgh",
    "correct horse battery staple",
}


def password_error(password: str) -> str | None:
    if len(password) < 15:
        return "Use at least 15 characters. A passphrase is fine."
    if len(password) > 128:
        return "Use no more than 128 characters."

    candidate = password.strip().casefold()
    if not candidate or len(set(candidate)) == 1 or candidate in COMMON_PASSWORDS:
        return "Choose a less predictable password."

    return None


def login_failed(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "error": (
                "Invalid email or password. "
                "If you have tried several times, wait before trying again."
            ),
        },
        status_code=401,
    )


@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    user = get_user_from_session(request)
    return templates.TemplateResponse(
        "index.html", {"request": request, "user": user}
    )


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(
        "login.html", {"request": request, "error": None}
    )


@router.post("/login", response_class=HTMLResponse)
def login(request: Request, email: str = Form(...), password: str = Form(...)):
    with closing(get_conn()) as conn:
        with conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Lock the account row so simultaneous attempts update it in order.
            cur.execute(
                """
                SELECT id, password_hash, failed_login_attempts,
                       last_failed_login_at, login_locked_until
                FROM users
                WHERE email = %s
                FOR UPDATE
                """,
                (email,),
            )
            user = cur.fetchone()
            if user is None:
                return login_failed(request)

            now = datetime.now(timezone.utc)
            locked_until = user["login_locked_until"]
            if locked_until is not None and now < locked_until:
                return login_failed(request)

            if not verify_password(password, user["password_hash"]):
                failures = user["failed_login_attempts"]
                last_failure = user["last_failed_login_at"]

                if last_failure is None or now - last_failure >= FAILURE_WINDOW:
                    failures = 0

                failures = min(
                    failures + 1,
                    FIRST_COOLDOWN_ATTEMPT + len(COOLDOWN_SECONDS) - 1,
                )

                locked_until = None
                if failures >= FIRST_COOLDOWN_ATTEMPT:
                    delay = COOLDOWN_SECONDS[failures - FIRST_COOLDOWN_ATTEMPT]
                    locked_until = now + timedelta(seconds=delay)

                cur.execute(
                    """
                    UPDATE users
                    SET failed_login_attempts = %s,
                        last_failed_login_at = %s,
                        login_locked_until = %s
                    WHERE id = %s
                    """,
                    (failures, now, locked_until, user["id"]),
                )
                return login_failed(request)

            cur.execute(
                """
                UPDATE users
                SET failed_login_attempts = 0,
                    last_failed_login_at = NULL,
                    login_locked_until = NULL
                WHERE id = %s
                """,
                (user["id"],),
            )

    token = create_session(user["id"])
    resp = RedirectResponse("/dashboard", status_code=302)
    resp.set_cookie("session_token", token, secure=True, httponly=True, samesite="lax")
    return resp


@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse(
        "register.html", {"request": request, "error": None}
    )


@router.post("/register", response_class=HTMLResponse)
def register(
    request: Request,
    email: str = Form(...),
    full_name: str = Form(...),
    password: str = Form(...),
):
    error = password_error(password)
    if error:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": error},
            status_code=400,
        )

    existing = run_query(
        "SELECT id FROM users WHERE email=%s", (email,), fetchone=True
    )
    if existing:
        return templates.TemplateResponse(
            "register.html", {"request": request, "error": "Email already exists."}
        )

    run_query(
        """
        INSERT INTO users (email, full_name, password_hash, role)
        VALUES (%s, %s, %s, 'student')
        """,
        (email, full_name, hash_password(password)),
        commit=True,
    )
    return RedirectResponse("/login", status_code=302)


@router.get("/logout")
def logout(request: Request):
    token = request.cookies.get("session_token")
    if token:
        clear_session(token)
    resp = RedirectResponse("/", status_code=302)
    resp.delete_cookie("session_token", secure=True, httponly=True, samesite="lax")
    return resp


@router.get("/reset-password", response_class=HTMLResponse)
def reset_password_page(request: Request):
    return templates.TemplateResponse(
        "reset_password.html",
        {"request": request, "mode": "request", "message": None},
    )


@router.post("/reset-password", response_class=HTMLResponse)
def reset_password_request(request: Request, email: str = Form(...)):
    user = run_query("SELECT * FROM users WHERE email=%s", (email,), fetchone=True)
    if not user:
        return templates.TemplateResponse(
            "reset_password.html",
            {
                "request": request,
                "mode": "request",
                "message": "No user found with that email.",
            },
        )

    token = str(int(time.time()))[-6:]
    run_query(
        "INSERT INTO password_reset_tokens (user_id, token) VALUES (%s, %s)",
        (user["id"], token),
        commit=True,
    )
    send_reset_email(email, token)
    return templates.TemplateResponse(
        "reset_password.html",
        {
            "request": request,
            "mode": "request",
            "message": f"Reset email sent to {email}.",
        },
    )


@router.get("/reset-password/{token}", response_class=HTMLResponse)
def reset_password_token_page(request: Request, token: str):
    return templates.TemplateResponse(
        "reset_password.html",
        {"request": request, "mode": "set", "token": token, "message": None},
    )


@router.post("/reset-password/{token}", response_class=HTMLResponse)
def reset_password_token(
    request: Request, token: str, new_password: str = Form(...)
):
    token_row = run_query(
        """
        SELECT * FROM password_reset_tokens
        WHERE token = %s
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (token,),
        fetchone=True,
    )
    if not token_row:
        return templates.TemplateResponse(
            "reset_password.html",
            {
                "request": request,
                "mode": "set",
                "token": token,
                "message": "Invalid token",
            },
        )

    error = password_error(new_password)
    if error:
        return templates.TemplateResponse(
            "reset_password.html",
            {"request": request, "mode": "set", "token": token, "message": error},
            status_code=400,
        )

    run_query(
        "UPDATE users SET password_hash=%s WHERE id=%s",
        (hash_password(new_password), token_row["user_id"]),
        commit=True,
    )
    return RedirectResponse("/login", status_code=302)
