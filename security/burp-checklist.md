# Burp Suite Community Checklist

## Goal

Use Burp Suite Community Edition for the mandatory manual security testing activity.

## Recommended Test Steps

1. Configure the browser to proxy traffic through Burp Suite.
2. Browse the library portal using the ALB DNS name.
3. Confirm requests for `/`, `/api/books`, `/api/summary`, `/api/loans`, and `/health` are visible.
4. Intercept a book creation request and modify one or more fields.
5. Try malformed input such as script tags, broken ISBNs, or unexpected characters.
6. Intercept a borrow request and tamper with `member_name`.
7. Observe whether the application rejects invalid input safely.

## Evidence to Capture

- Browser + Burp proxy enabled screenshot
- Intercepted request screenshot
- Modified request screenshot
- Response showing validation or safe rejection
