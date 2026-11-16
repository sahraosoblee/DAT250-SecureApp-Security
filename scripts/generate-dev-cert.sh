#!/bin/sh
set -eu

cd "$(dirname "$0")/.."
mkdir -p certs
umask 077

if [ -e certs/cert.pem ] || [ -e certs/key.pem ]; then
    if [ -f certs/cert.pem ] && [ -f certs/key.pem ]; then
        echo "Using existing development certificate in certs/"
        exit 0
    fi
    echo "certs/ contains an incomplete certificate pair; remove that pair and rerun this script." >&2
    exit 1
fi

MSYS_NO_PATHCONV=1 openssl req -x509 -newkey rsa:2048 -sha256 -nodes -days 365 \
    -keyout certs/key.pem \
    -out certs/cert.pem \
    -subj "/CN=localhost" \
    -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"

chmod 600 certs/key.pem
echo "Created an untrusted, local development certificate in certs/"
