# DAT250 SecureApp — Kali/VM Networking Guide

## Purpose
This guide explains how to access your own DAT250 SecureApp lab from Kali Linux or another VM.

## Supported setups

1. App and Kali tools on the same machine
2. App on physical laptop, Kali in VM
3. App in target VM, Kali in separate VM
4. App inside Kali

## Important rule
Only test your own local lab environment.

## Mode A: Same machine

App URL:
`https://localhost:18443`

MailHog:
`http://localhost:8025`

## Mode B: App on physical laptop, Kali in VM

Steps:
1. Start app on host laptop:
   `sh scripts/generate-dev-cert.sh`
   `docker compose up --build`
2. Find host IP.

For macOS:
`ifconfig`

For Linux:
`ip -4 addr`

For Windows PowerShell:
`ipconfig`

3. From Kali:
   `ping <HOST-IP>`
   `curl -k -I https://<HOST-IP>:18443`

4. Open browser in Kali:
   `https://<HOST-IP>:18443`

The development certificate covers `localhost` and `127.0.0.1`, not the host IP. The browser will report a certificate name mismatch when using the IP; generate a certificate containing the lab host IP in its subject alternative names to verify the server identity.

Troubleshooting:
- If NAT does not work, try bridged adapter or host-only adapter.
- Check firewall settings.
- Check Docker Desktop is running.
- Check app is listening on `0.0.0.0:18181`.

## Mode C: App in target VM, Kali in another VM

Steps:
1. Put both VMs on same network:
   - Bridged Adapter, or
   - Host-only Adapter, or
   - Internal Network in VirtualBox/VMware/UTM/Parallels.
2. Start Docker app inside target VM:
   `sh scripts/generate-dev-cert.sh`
   `docker compose up --build`
3. Find target VM IP:
   `ip -4 addr`
4. From Kali:
   `ping <TARGET-VM-IP>`
   `curl -k -I https://<TARGET-VM-IP>:18443`
5. Open:
   `https://<TARGET-VM-IP>:18443`

## Mode D: App inside Kali

Start app in Kali:
`sh scripts/generate-dev-cert.sh`
`docker compose up --build`

Open:
`https://localhost:18443`

## Useful basic commands

- `curl -k -I https://<TARGET-IP>:18443`
- `nc -vz <TARGET-IP> 18181`
- `ip route`
- `ip -4 addr`
