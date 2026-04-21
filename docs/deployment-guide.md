# Deployment Guide

## 1. Provision Infrastructure with Terraform

Inside `terraform/`:

```bash
terraform init
terraform plan
terraform apply
```

Required resources created by the stack:

- Blue EC2 instance
- Green EC2 instance
- ALB
- Blue target group
- Green target group
- Security Groups
- IAM role and instance profile
- CloudWatch Log Group
- CloudWatch Dashboard

## 2. Update Ansible Inventory

Copy the public IP outputs into [ansible/inventory/inventory.ini](../ansible/inventory/inventory.ini).

Example:

```ini
[blue]
blue ansible_host=BLUE_PUBLIC_IP ansible_user=ec2-user app_slot=blue

[green]
green ansible_host=GREEN_PUBLIC_IP ansible_user=ec2-user app_slot=green
```

## 3. Configure Both EC2 Servers

Run:

```bash
ansible-playbook -i ansible/inventory/inventory.ini ansible/playbooks/setup_web.yml
```

This installs:

- Apache
- Python 3 and pip
- Gunicorn app service
- Amazon CloudWatch agent

## 4. Configure Jenkins

Create a Pipeline job from SCM and point it to this repository.

Provide these build parameters from Terraform outputs:

- `AWS_REGION`
- `ALB_LISTENER_ARN`
- `BLUE_TARGET_GROUP_ARN`
- `GREEN_TARGET_GROUP_ARN`
- `ALB_DNS_NAME`
- `ANSIBLE_PRIVATE_KEY_FILE`

## 5. Run the Pipeline

The pipeline will:

1. Checkout
2. Build
3. Test
4. Run OWASP ZAP baseline scan
5. Deploy to Green
6. Verify Green
7. Switch traffic
8. Roll back to Blue if final verification fails

## 6. Validate the Application

After a successful deployment:

- Open the ALB DNS name in a browser
- Add a new book
- Issue a book to a member
- Return a book
- Confirm `/health` returns JSON with status and summary data

## 7. Collect Security Evidence

- Export `zap-report.html`
- Capture Burp Suite interception and modified request screenshots
- Capture Wireshark traffic screenshots
- Capture CloudWatch dashboard and log stream screenshots
