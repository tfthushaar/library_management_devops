# Wireshark Checklist

## Goal

Use Wireshark to inspect traffic while operating the deployed library portal.

## Suggested Filters

- `http`
- `tcp.port == 80`
- `tcp.port == 443`
- `ip.addr == YOUR_CLIENT_IP`

## Recommended Observations

- Opening the portal homepage
- Fetching `/api/books`
- Issuing a book
- Returning a book
- Accessing `/health`

## What to Look For

- Whether traffic is HTTP or HTTPS
- Whether any sensitive values are visible in plain text
- Whether application responses look normal during portal activity

## Evidence to Capture

- Packet list screenshot
- Detailed packet view screenshot
- Short note describing whether sensitive data was exposed
