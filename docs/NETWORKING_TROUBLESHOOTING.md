# DAT250 SecureApp — Networking Troubleshooting

## Docker is not running

```bash
docker compose ps
```

If services are not listed as running, start Docker Desktop/Engine and run:

```bash
sh scripts/generate-dev-cert.sh
docker compose up --build
```

## Port already in use

Another local service may already use port 18181, 18443, or 8025.

```bash
docker compose down
docker compose ps
```

Then stop conflicting local services and restart the lab.

## Cannot reach app from Kali VM

Checklist:
- Is Docker Compose running?
- Is the target IP correct?
- Are the VMs on the same virtual network?
- Is the firewall blocking inbound connections?
- Is the app reachable from the host first?
- Was the development certificate generated before starting Compose?
- Try curl from the target machine:
  `curl -k -I https://localhost:18443`
- Try curl from Kali:
  `curl -k -I https://<TARGET-IP>:18443`

The self-signed certificate is valid only for `localhost` and `127.0.0.1`. Access by a host/VM IP causes a certificate name-mismatch warning unless the certificate is regenerated with that IP.

## VirtualBox/VMware/UTM/Parallels notes

- NAT can be difficult for inbound connections.
- Bridged networking often makes the VM visible on the same LAN.
- Host-only networking is good for isolated lab networks.
- Internal network works only between VMs configured with the same internal network name.

## Safety

Never scan public networks or UiS infrastructure.
