# Automated Secure Deployment of Library Management Web Portal

This project is a library-management adaptation of the reference DevSecOps repository at [tfthushaar/DEVOps-project](https://github.com/tfthushaar/DEVOps-project). It satisfies the mandatory project rubric you shared:

- Terraform for AWS infrastructure provisioning
- Ansible for EC2 configuration and application deployment
- Jenkins for CI/CD automation
- Blue-Green deployment using an Application Load Balancer
- CloudWatch logging and dashboarding
- Mandatory security testing with OWASP ZAP
- Manual security validation guidance for Burp Suite Community Edition and Wireshark

## What This Portal Does

The Flask application is a lightweight Library Management Web Portal that lets you:

- View catalog and circulation statistics
- Add books to the catalog
- Search by title, author, category, or ISBN
- Issue books to members
- Return books
- Expose a `/health` endpoint for ALB checks and Jenkins verification

## Mandatory DevOps Scope Covered

### Terraform

The Terraform stack provisions:

- 2 EC2 instances for `blue` and `green`
- Security Groups for SSH and HTTP/HTTPS
- Application Load Balancer with blue and green target groups
- IAM role and instance profile for CloudWatch logging
- CloudWatch Log Group
- CloudWatch Dashboard

### Ansible

The Ansible automation performs:

- Apache installation
- Python and Gunicorn installation
- CloudWatch agent installation
- Apache enable and start
- Deployment of app code into `/var/www/html/library-portal`
- Service restart after deployment

### Jenkins Pipeline

The `Jenkinsfile` implements the required stages:

1. Checkout
2. Build
3. Test
4. Security Testing Stage
5. Deploy to Green
6. Verify Green
7. Switch Traffic
8. Rollback to Blue if verification fails

### DevSecOps Security Layer

Mandatory tools included in the workflow:

- OWASP ZAP for automated baseline scanning
- Burp Suite Community Edition for manual request interception and tampering tests
- Wireshark for packet capture and transport inspection

## Project Structure

```text
.
├── app/
│   ├── requirements.txt
│   ├── tests/
│   ├── wsgi.py
│   └── library_portal/
├── ansible/
│   ├── inventory/
│   ├── playbooks/
│   └── roles/
├── docs/
├── jenkins/
│   └── scripts/
├── security/
├── terraform/
│   ├── modules/
│   └── *.tf
└── Jenkinsfile
```

## Quick Start

1. Copy [terraform/terraform.tfvars.example](./terraform/terraform.tfvars.example) to `terraform/terraform.tfvars` and fill in your AWS values.
2. Run `terraform init`, `terraform plan`, and `terraform apply` inside `terraform/`.
3. Put the Terraform public IP outputs into [ansible/inventory/inventory.ini](./ansible/inventory/inventory.ini).
4. Run `ansible-playbook -i ansible/inventory/inventory.ini ansible/playbooks/setup_web.yml`.
5. Configure a Jenkins Pipeline job from SCM and provide the ALB and target group outputs as build parameters.
6. Run the Jenkins pipeline to deploy to Green, verify `/health`, switch traffic, and roll back to Blue if needed.
7. Capture CloudWatch, OWASP ZAP, Burp Suite, and Wireshark evidence for submission.

## Local App Run

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r app/requirements.txt
cd app
python wsgi.py
```

Open `http://127.0.0.1:5000`.

## Local Test Run

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r app/requirements.txt
PYTHONPATH=app pytest -q app/tests
```

## Important Assumptions

- You already have an AWS account, a VPC, and two public subnets.
- You will provide an Amazon Linux 2 AMI and EC2 key pair name.
- HTTPS is optional unless you supply an ACM certificate ARN.
- Burp Suite and Wireshark steps are documented as guided manual activities because they are part of submission evidence rather than the Jenkins automation itself.

## Recommended Submission Evidence

- Terraform apply output showing EC2, ALB, Security Groups, IAM, and CloudWatch creation
- Ansible run showing Apache and app deployment
- Jenkins screenshots for all pipeline stages
- `zap-report.html`
- Burp Suite interception screenshots
- Wireshark packet capture screenshots
- CloudWatch dashboard screenshot
- Browser screenshot of the library portal before and after green deployment
