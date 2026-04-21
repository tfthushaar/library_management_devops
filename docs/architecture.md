# Architecture Notes

The application is deployed as a classic blue-green AWS web stack.

## Runtime Components

- `blue` EC2 instance: currently stable release
- `green` EC2 instance: next candidate release
- Application Load Balancer: sends traffic to the active target group
- Apache: public-facing web server on each instance
- Gunicorn: runs the Flask app on `127.0.0.1:5000`
- CloudWatch agent: forwards Apache and Gunicorn logs

## Application Flow

1. A user opens the ALB DNS name.
2. The ALB forwards HTTP traffic to either the blue or green target group.
3. Apache proxies requests to Gunicorn on the same EC2 instance.
4. The Flask app serves the library portal and exposes `/health`.
5. Jenkins validates `/health` on Green before switching traffic.

## Infrastructure Responsibilities

- Terraform provisions the AWS resources and outputs the ALB DNS name plus target group ARNs.
- Ansible configures both EC2 instances identically.
- Jenkins performs safe deployment by promoting Green only after verification.
- CloudWatch provides central visibility for logs and traffic trends.

## Security Responsibilities

- App-level headers reduce common browser-side exposure.
- Input validation is applied to book, member, and search fields.
- OWASP ZAP is used as the compulsory automated security gate.
- Burp Suite and Wireshark provide the required manual verification evidence.
