# Hardening Recommendations

- Keep `allowed_ssh_cidr` restricted to your IP instead of `0.0.0.0/0` for the final demo.
- Prefer HTTPS with an ACM certificate and ALB HTTPS listener.
- Store private keys and secrets outside the repository.
- Keep strict validation for book titles, author names, ISBN values, categories, and member names.
- Re-run OWASP ZAP after every major UI or endpoint change.
- Review Apache and Gunicorn logs in CloudWatch after each deployment.
- Remove or pause unused Jenkins jobs and stale EC2 instances after evaluation.
