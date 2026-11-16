# Student Quickstart

1. Clone repository and open terminal in `dat250-secureapp`.
2. Generate a local development certificate: `sh scripts/generate-dev-cert.sh`.
3. Run `docker compose up --build`.
4. Open `https://localhost:18443` and accept the self-signed certificate warning for this local lab.
5. Use provided test users to explore functionality.
6. Use external course tools where required by assignments.

## Access from Kali or another VM

- Same machine: open `https://localhost:18443`
- App on host + Kali VM: open `https://<HOST-IP>:18443`
- App in target VM + Kali in separate VM: open `https://<TARGET-VM-IP>:18443`
- App inside Kali: open `https://localhost:18443`

The generated certificate is valid for `localhost` and `127.0.0.1` only. Accessing it by a VM/host IP will produce a name-mismatch warning; use a certificate with that IP in its subject alternative names if validating the server identity is part of the exercise.

For detailed VM networking steps, read:
- `docs/KALI_VM_NETWORKING.md`
- `docs/NETWORKING_TROUBLESHOOTING.md`

## Login with test users

1. Open `https://localhost:18443`.
2. Click **Login** in the top menu.
3. Sign in with one of these accounts:

- `admin@dat250.local` / `Admin123`
- `teacher@dat250.local` / `Teacher123`
- `ta@dat250.local` / `TA123`
- `alice@student.uis.no` / `Alice123`
- `bob@student.uis.no` / `Bob123`
- `charlie@student.uis.no` / `Charlie123`

## Database GUI access (phpPgAdmin)

- URL: `http://localhost:8081`
- Available only if enabled in your lab setup.
- Server/Host: `db`
- Port: `5432`
- Database: `dat250`
- Username: `dat250`
- Password: `dat250`
