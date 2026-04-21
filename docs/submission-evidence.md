# Submission Evidence Checklist

Use this checklist when preparing your final project report or viva demo.

## Terraform Evidence

- Screenshot or terminal output of `terraform apply`
- EC2 instances named for blue and green
- Security Group rules for SSH and HTTP/HTTPS
- ALB with listener and both target groups
- IAM role and instance profile for CloudWatch
- CloudWatch dashboard and log group

## Ansible Evidence

- `setup_web.yml` execution output
- Apache installed and running
- App files present in `/var/www/html/library-portal`
- Gunicorn service enabled
- Apache restarted after deployment

## Jenkins Evidence

- Checkout stage screenshot
- Build stage screenshot
- Test stage screenshot
- Security Testing Stage screenshot
- Deploy to Green screenshot
- Verify Green screenshot
- Switch Traffic screenshot
- Rollback screenshot or explanation of successful post-switch validation

## Security Evidence

- `zap-report.html` artifact
- Screenshot of OWASP ZAP baseline results
- Burp Suite request interception screenshot
- Burp Suite modified request/response screenshot
- Wireshark packet capture screenshot
- Notes on vulnerabilities found and fixes applied

## Functional Evidence

- Browser screenshot of the Library Management Portal
- Add-book action screenshot
- Issue-book action screenshot
- Return-book action screenshot
- `/health` endpoint screenshot

## Observability Evidence

- CloudWatch log stream screenshot
- CloudWatch dashboard screenshot showing request count or CPU metrics
