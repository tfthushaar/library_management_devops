# Automated Secure Deployment of Library Management Web Portal

This repository contains a complete beginner-friendly DevSecOps project for a **Library Management Web Portal** deployed on AWS with:

- Terraform
- Ansible
- Jenkins
- Blue-Green Deployment
- CloudWatch
- OWASP ZAP
- Burp Suite Community Edition
- Wireshark

This guide is written for someone who is **starting from zero** and may not know AWS, Terraform, Ansible, Jenkins, or web security tools yet.

## 1. What You Are Building

By the end of this setup, you will have:

- 2 application EC2 instances:
  - `blue`
  - `green`
- 1 Application Load Balancer (ALB)
- Security Groups for SSH and web traffic
- IAM role for CloudWatch
- CloudWatch Log Group and Dashboard
- Ansible automation to install Apache, Gunicorn, Python, and deploy the app
- Jenkins pipeline for:
  - Checkout
  - Build
  - Test
  - Security Testing Stage
  - Deploy to Green
  - Verify Green
  - Switch Traffic
  - Rollback to Blue if verification fails
- OWASP ZAP automated baseline scan
- Burp Suite manual testing evidence
- Wireshark traffic inspection evidence

## 2. Beginner Architecture

Think of the project like this:

- Your laptop:
  - edit files
  - run small local tests
  - use AWS Console
- AWS EC2 instance 1:
  - Blue application server
- AWS EC2 instance 2:
  - Green application server
- Optional but recommended AWS EC2 instance 3:
  - Jenkins server

Recommended setup for beginners:

- Keep **Blue** and **Green** for the application only
- Run **Jenkins on a separate Ubuntu EC2 instance**

This keeps responsibilities clean:

- Terraform creates infrastructure
- Ansible configures servers
- Jenkins automates deployment
- CloudWatch monitors and stores logs
- ZAP, Burp, and Wireshark handle security evidence

## 3. Project Folder Overview

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

Important files:

- Terraform variables: [terraform/terraform.tfvars.example](./terraform/terraform.tfvars.example)
- Ansible inventory: [ansible/inventory/inventory.ini](./ansible/inventory/inventory.ini)
- Jenkins pipeline: [Jenkinsfile](./Jenkinsfile)
- CloudWatch Terraform: [terraform/modules/observability/main.tf](./terraform/modules/observability/main.tf)
- CloudWatch agent config: [ansible/roles/webserver/templates/cloudwatch-agent.json.j2](./ansible/roles/webserver/templates/cloudwatch-agent.json.j2)

## 4. Before You Touch AWS

Install these tools on your own machine first:

- Git
- Python 3.11 or newer
- AWS CLI
- Terraform
- A Linux environment for Ansible and Jenkins
  - Ubuntu EC2 instance is recommended
  - WSL Ubuntu or a Linux VM also works
- OWASP ZAP
- Burp Suite Community Edition
- Wireshark

Why Linux is recommended:

- Ansible works more smoothly on Linux
- Jenkinsfile uses Linux shell commands
- SSH key permissions are easier on Linux
- ZAP command-line usage is easier on Linux

## 5. Step 0: Verify the Application Locally

Before deploying anything to AWS, make sure the app works locally.

Open a terminal in this project and run:

### Windows PowerShell

```powershell
cd "C:\Users\thush\OneDrive\Desktop\library management system"
python -m venv .venv
.\.venv\Scripts\python -m pip install -r app\requirements.txt
$env:PYTHONPATH="app"
.\.venv\Scripts\python -m pytest -q app\tests
```

If the tests pass, the app is healthy enough to continue.

## 6. Step 1: Create and Secure an AWS Account

If you already have an AWS account, you can still follow this section to make sure it is set up safely.

### 6.1 Create an AWS account

1. Go to AWS and sign up.
2. Complete billing verification.
3. Sign in to the AWS Console.

### 6.2 Do not use the root account for daily work

After account creation:

1. Open the IAM service.
2. Create an IAM user for yourself.
3. Give it administrative access for this project.
4. Enable MFA if possible.
5. Sign out of the root account and use the IAM user.

### 6.3 Create AWS CLI credentials

You need an access key so Terraform and AWS CLI can work.

1. In IAM, open your IAM user.
2. Create an Access Key.
3. Keep the `Access Key ID` and `Secret Access Key`.

Then configure AWS CLI locally:

```bash
aws configure
```

Enter:

- Access key
- Secret key
- Default region, for example `ap-south-1`
- Output format, for example `json`

Verify AWS CLI:

```bash
aws sts get-caller-identity
```

If this works, your AWS CLI is correctly configured.

## 7. Step 2: Understand the AWS Network Pieces First

This is the part beginners usually find confusing, so here is the simplest explanation.

### 7.1 What is a VPC?

A **VPC** is your private network inside AWS.

Everything in this project lives inside one VPC:

- Blue EC2
- Green EC2
- ALB
- Security Groups
- Subnets

In Terraform you give its ID like:

```hcl
vpc_id = "vpc-xxxxxxxx"
```

### 7.2 What is a subnet?

A subnet is a smaller section inside the VPC.

For this project you need **two public subnets**, ideally in two different Availability Zones.

Why two?

- Blue instance goes into one subnet
- Green instance goes into another subnet
- The ALB also needs multiple subnets

In Terraform:

```hcl
public_subnet_ids = ["subnet-aaaa", "subnet-bbbb"]
```

### 7.3 What is a public subnet?

A public subnet is a subnet whose route table sends internet traffic to an Internet Gateway.

That makes it possible for:

- EC2 instances to get package updates
- Jenkins/Ansible to SSH into the servers
- the ALB to receive public traffic

### 7.4 What is an Internet Gateway?

An Internet Gateway is the VPC's link to the internet.

Without it:

- your ALB will not be public
- your EC2 instances may not reach the internet
- package installation can fail

### 7.5 What is a route table?

A route table tells a subnet where traffic should go.

For a public subnet, the important route is:

- Destination: `0.0.0.0/0`
- Target: Internet Gateway

### 7.6 What is an Availability Zone?

An Availability Zone is like a separate AWS data-center area in the same region.

Example in `ap-south-1`:

- `ap-south-1a`
- `ap-south-1b`

For this project, use subnets in two different zones if possible.

### 7.7 What is a key pair?

A key pair is used for SSH into EC2.

AWS stores the public key on the server.
You keep the private `.pem` file.

You will use that `.pem` file for:

- manual SSH
- Ansible
- Jenkins

### 7.8 What is a security group?

A security group is a virtual firewall.

This project needs rules for:

- SSH `22`
- HTTP `80`
- HTTPS `443`

### 7.9 What is `allowed_ssh_cidr`?

This controls who is allowed to SSH into Blue and Green.

Bad beginner shortcut:

```hcl
allowed_ssh_cidr = "0.0.0.0/0"
```

Better:

```hcl
allowed_ssh_cidr = "YOUR_PUBLIC_IP/32"
```

### 7.10 What is an ALB?

The ALB is the public entry point to your application.

Users access the ALB DNS name, not Blue or Green directly.

The ALB forwards traffic to:

- Blue target group
- or Green target group

### 7.11 What is a target group?

A target group is a backend list that the ALB can forward traffic to.

You have two:

- Blue target group
- Green target group

Blue-green deployment works by switching the ALB from Blue to Green.

### 7.12 What is IAM role in this project?

The EC2 instances need permission to send logs to CloudWatch.

Terraform creates an IAM role and attaches it to the EC2 instances.

### 7.13 What is CloudWatch here?

CloudWatch is used for:

- log storage
- monitoring metrics
- dashboard screenshots

This project sends Apache and Gunicorn logs to CloudWatch.

## 8. Step 3: Create or Find a Suitable VPC

If you already have a VPC with two public subnets, you can reuse it.

If not, the beginner-friendly option is:

1. Open the VPC service in AWS Console.
2. Choose **Create VPC**.
3. Use the guided option that creates:
   - 1 VPC
   - 2 public subnets
   - Internet Gateway
   - route tables

You need to write down:

- VPC ID
- Public Subnet 1 ID
- Public Subnet 2 ID

Make sure:

- both subnets belong to the same VPC
- both are in the same region as your project
- route table allows internet access

## 9. Step 4: Create an EC2 Key Pair

1. Open the EC2 service.
2. Open **Key Pairs**.
3. Click **Create key pair**.
4. Give it a name, for example `library-key`.
5. Choose `.pem`.
6. Download the file and keep it safe.

You will need:

- the key pair name in Terraform
- the `.pem` file for Ansible and Jenkins

## 10. Step 5: Find an Amazon Linux 2 AMI

Your Blue and Green instances need a base operating system image.

For this project, use **Amazon Linux 2**.

Open EC2 and find the current Amazon Linux 2 AMI ID for your chosen region.

Write down the AMI ID.

Important:

- AMI IDs are region-specific
- Use the AMI for the same region as your VPC and subnets

## 11. Step 6: Fill Terraform Variables

Copy [terraform/terraform.tfvars.example](./terraform/terraform.tfvars.example) to `terraform/terraform.tfvars`.

Edit it and replace the placeholders.

Example:

```hcl
aws_region        = "ap-south-1"
project_name      = "library-devsecops"
vpc_id            = "vpc-0abc123456789def0"
public_subnet_ids = ["subnet-01234aaaa", "subnet-05678bbbb"]
ami_id            = "ami-0123456789abcdef0"
instance_type     = "t2.micro"
key_pair_name     = "library-key"
allowed_ssh_cidr  = "YOUR_PUBLIC_IP/32"
active_target     = "blue"
certificate_arn   = ""

environment_tags = {
  Owner      = "YourName"
  Department = "MCA-Project"
}
```

What each field means:

- `aws_region`: your AWS region
- `project_name`: prefix for naming resources
- `vpc_id`: the VPC to deploy into
- `public_subnet_ids`: two public subnets
- `ami_id`: Amazon Linux 2 AMI ID
- `instance_type`: EC2 size
- `key_pair_name`: EC2 SSH key pair name
- `allowed_ssh_cidr`: who can SSH to EC2
- `active_target`: live environment at the start
- `certificate_arn`: ACM certificate if using HTTPS

## 12. Step 7: Run Terraform

From the project folder:

```bash
cd terraform
terraform init
terraform validate
terraform plan
terraform apply
```

Type `yes` when Terraform asks for confirmation.

Terraform will create:

- Blue EC2
- Green EC2
- ALB
- Blue target group
- Green target group
- Security Groups
- IAM role and instance profile
- CloudWatch Log Group
- CloudWatch Dashboard

When it finishes, write down these outputs:

- `alb_dns_name`
- `listener_arn`
- `blue_target_group_arn`
- `green_target_group_arn`
- `blue_instance_public_ip`
- `green_instance_public_ip`

## 13. Step 8: Create a Jenkins Server

Recommended approach:

- launch a **separate Ubuntu EC2 instance** for Jenkins

Why separate?

- Blue and Green stay clean as app servers
- Jenkins acts as deployment controller only
- easier to explain in a viva

### 13.1 Launch the Jenkins EC2

In AWS Console:

1. Open EC2.
2. Click **Launch instance**.
3. Name it something like `jenkins-server`.
4. Choose **Ubuntu Server LTS**.
5. Choose `t2.micro` or `t3.micro` for student demo use.
6. Select your key pair.
7. Place it in the same VPC.
8. Use a public subnet.

Security group for Jenkins should allow:

- SSH `22` from your own IP
- Jenkins UI `8080` from your own IP

### 13.2 SSH into Jenkins EC2

```bash
ssh -i your-key.pem ubuntu@JENKINS_PUBLIC_IP
```

## 14. Step 9: Install Jenkins and Its Dependencies

On the Jenkins Ubuntu server:

### 14.1 Install Java

```bash
sudo apt update
sudo apt install -y fontconfig openjdk-17-jre
java -version
```

### 14.2 Install Jenkins

```bash
curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key | sudo tee \
  /usr/share/keyrings/jenkins-keyring.asc > /dev/null

echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] \
  https://pkg.jenkins.io/debian-stable binary/ | sudo tee \
  /etc/apt/sources.list.d/jenkins.list > /dev/null

sudo apt update
sudo apt install -y jenkins
```

### 14.3 Start Jenkins

```bash
sudo systemctl enable jenkins
sudo systemctl start jenkins
sudo systemctl status jenkins
```

### 14.4 Open Jenkins in browser

Go to:

```text
http://JENKINS_PUBLIC_IP:8080
```

Get the unlock password:

```bash
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```

Paste it into the browser, then:

- install suggested plugins
- create admin user

### 14.5 Install tools Jenkins needs

```bash
sudo apt install -y git python3 python3-venv python3-pip ansible unzip
```

Install AWS CLI v2:

```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
aws --version
```

Optional but recommended for ZAP Docker fallback:

```bash
sudo apt install -y docker.io
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker jenkins
```

Restart Jenkins after adding docker group membership:

```bash
sudo systemctl restart jenkins
```

### 14.6 Give Jenkins AWS access

Simplest beginner method:

```bash
aws configure
```

Enter the IAM access key and secret key of a user that can manage the ALB.

### 14.7 Put your EC2 private key on the Jenkins server

```bash
sudo mkdir -p /var/lib/jenkins/.ssh
sudo cp your-key.pem /var/lib/jenkins/.ssh/library-bluegreen.pem
sudo chown jenkins:jenkins /var/lib/jenkins/.ssh/library-bluegreen.pem
sudo chmod 400 /var/lib/jenkins/.ssh/library-bluegreen.pem
```

This matches the default path in [Jenkinsfile](./Jenkinsfile).

## 15. Step 10: Put the Project in GitHub

If your code is not already on GitHub, create a GitHub repository and push the project there.

This repository already has a remote configured:

```text
origin = https://github.com/tfthushaar/library_management_devops.git
```

Jenkins is easiest to use when the repo is on GitHub.

## 16. Step 11: Update Ansible Inventory

Open [ansible/inventory/inventory.ini](./ansible/inventory/inventory.ini).

Replace the placeholders with Terraform outputs:

```ini
[blue]
blue ansible_host=BLUE_PUBLIC_IP ansible_user=ec2-user app_slot=blue

[green]
green ansible_host=GREEN_PUBLIC_IP ansible_user=ec2-user app_slot=green

[web:children]
blue
green
```

Use the public IPs from:

- `blue_instance_public_ip`
- `green_instance_public_ip`

## 17. Step 12: Test SSH to Blue and Green

From your Linux machine or Jenkins server:

```bash
ssh -i /path/to/your-key.pem ec2-user@BLUE_PUBLIC_IP
ssh -i /path/to/your-key.pem ec2-user@GREEN_PUBLIC_IP
```

If SSH fails, check:

- security group port 22
- correct IP
- correct `.pem`
- correct user `ec2-user`

## 18. Step 13: Run Ansible Setup

From the Linux/Jenkins machine:

```bash
ansible -i ansible/inventory/inventory.ini all -m ping --private-key /path/to/your-key.pem
ansible-playbook -i ansible/inventory/inventory.ini ansible/playbooks/setup_web.yml --private-key /path/to/your-key.pem
```

This installs and configures:

- Apache
- Python 3
- Gunicorn
- CloudWatch agent
- library-portal service

## 19. Step 14: Understand CloudWatch in This Project

CloudWatch does two jobs:

### 19.1 CloudWatch Logs

It stores log files from Blue and Green:

- Apache access log
- Apache error log
- Gunicorn log

These logs are pushed by the CloudWatch Agent.

### 19.2 CloudWatch Dashboard

Terraform creates a dashboard showing:

- EC2 CPU utilization
- ALB request count
- Healthy host count

This is important evidence for your observability section.

### 19.3 Where to check CloudWatch

After deployment:

1. Open CloudWatch in AWS Console
2. Open **Log groups**
3. Open the log group for this project
4. Confirm streams exist for Blue and Green
5. Open **Dashboards**
6. Confirm graphs are visible

## 20. Step 15: Create the Jenkins Pipeline Job

In Jenkins:

1. Click **New Item**
2. Name it `library-devsecops`
3. Choose **Pipeline**
4. Choose **Pipeline script from SCM**
5. Select **Git**
6. Enter your GitHub repository URL
7. Set branch, for example `main`
8. Set script path to:

```text
Jenkinsfile
```

Save the job.

## 21. Step 16: Run the Jenkins Pipeline

When you click **Build with Parameters**, enter:

- `AWS_REGION`
- `ALB_LISTENER_ARN`
- `BLUE_TARGET_GROUP_ARN`
- `GREEN_TARGET_GROUP_ARN`
- `ALB_DNS_NAME`
- `ANSIBLE_PRIVATE_KEY_FILE`

Example:

- `AWS_REGION = ap-south-1`
- `ANSIBLE_PRIVATE_KEY_FILE = /var/lib/jenkins/.ssh/library-bluegreen.pem`

The values for the ALB and target groups come from Terraform outputs.

### 21.1 What each Jenkins stage does

1. `Checkout`
   - pulls code from GitHub
2. `Build`
   - creates Python virtual environment
   - installs dependencies
3. `Test`
   - runs pytest
4. `Security Testing Stage`
   - runs OWASP ZAP baseline scan
5. `Deploy to Green`
   - uses Ansible to deploy the app to Green
6. `Verify Green`
   - checks `http://127.0.0.1/health` on Green
7. `Switch Traffic`
   - ALB moves from Blue to Green
8. `Rollback to Blue if verification fails`
   - if ALB health check fails, traffic returns to Blue

## 22. Step 17: Verify the Application

After a successful pipeline run:

1. Open the ALB DNS name in a browser
2. Test the portal

Try:

- add a book
- search catalog
- issue a book
- return a book
- open `/health`

Example:

```text
http://ALB_DNS_NAME/health
```

## 23. Step 18: Run OWASP ZAP

OWASP ZAP is compulsory.

The Jenkins pipeline already runs it automatically, but you should also understand it.

### 23.1 Automated scan in Jenkins

Jenkins runs:

```bash
jenkins/scripts/run_zap_baseline.sh http://127.0.0.1:5001
```

### 23.2 Manual ZAP scan against the ALB

```bash
zap-baseline.py -t http://ALB_DNS_NAME -r zap-report.html -m 3
```

Keep:

- `zap-report.html`
- screenshot of Jenkins Security Testing Stage
- screenshot of ZAP results

## 24. Step 19: Use Burp Suite Community Edition

Burp Suite is compulsory for manual testing.

### 24.1 What Burp is used for

Burp lets you:

- intercept requests
- modify form fields
- test how the app responds to tampered input

### 24.2 What to test

Open the app through Burp and inspect requests for:

- `/`
- `/api/books`
- `/api/summary`
- `/api/loans`
- `/health`

Try modifying:

- title
- author
- ISBN
- category
- member name

Take screenshots of:

- intercepted request
- modified request
- application response

## 25. Step 20: Use Wireshark

Wireshark is compulsory for traffic inspection.

### 25.1 What to do

Start Wireshark while you use the app in a browser.

Use filters like:

```text
http
tcp.port == 80
tcp.port == 443
```

### 25.2 What actions to perform

- open homepage
- search books
- add a book
- issue a book
- return a book
- open `/health`

### 25.3 What to observe

- whether traffic is plain HTTP or HTTPS
- whether sensitive values are visible
- whether requests and responses look normal

Take screenshots.

## 26. Step 21: What Evidence to Collect

For final submission, collect:

- Terraform apply output
- EC2 screenshot showing Blue and Green
- ALB screenshot
- Security Group screenshot
- IAM role screenshot
- CloudWatch dashboard screenshot
- CloudWatch log screenshot
- Ansible playbook output
- Jenkins pipeline screenshots for all stages
- `zap-report.html`
- Burp Suite screenshots
- Wireshark screenshots
- browser screenshots of the working app
- `/health` endpoint screenshot

Also use:

- [docs/submission-evidence.md](./docs/submission-evidence.md)

## 27. Step 22: Common Problems and Fixes

### Terraform fails

Check:

- VPC ID
- subnet IDs
- AMI ID
- key pair name
- region mismatch

### SSH fails

Check:

- port 22 allowed
- correct `.pem`
- correct username
- correct public IP

### Ansible fails

Check:

- inventory file
- SSH access
- private key path

### Jenkins cannot deploy

Check:

- Jenkins server has Ansible installed
- Jenkins server has AWS CLI configured
- Jenkins server can SSH into Blue and Green
- pipeline parameters match Terraform outputs

### CloudWatch logs do not appear

Check:

- EC2 IAM role is attached
- `amazon-cloudwatch-agent` service is running
- expected log files actually exist

### Green verification fails

SSH into Green and check:

```bash
sudo systemctl status library-portal
sudo systemctl status httpd
```

## 28. Step 23: Recommended Order of Work

If you want the cleanest beginner path, follow this exact order:

1. Run local tests
2. Prepare AWS account and CLI
3. Create or identify VPC and public subnets
4. Create key pair
5. Find AMI
6. Fill `terraform.tfvars`
7. Run Terraform
8. Launch separate Ubuntu Jenkins EC2
9. Install Jenkins and its tools
10. Update Ansible inventory
11. Test SSH to Blue and Green
12. Run Ansible setup
13. Create Jenkins pipeline job
14. Run Jenkins pipeline
15. Test the ALB URL
16. Check CloudWatch
17. Run OWASP ZAP, Burp, and Wireshark evidence steps

## 29. Local Test Commands

### Windows PowerShell

```powershell
cd "C:\Users\thush\OneDrive\Desktop\library management system"
python -m venv .venv
.\.venv\Scripts\python -m pip install -r app\requirements.txt
$env:PYTHONPATH="app"
.\.venv\Scripts\python -m pytest -q app\tests
```

## 30. Final Notes

- Terraform provisions the AWS infrastructure
- Ansible configures Blue and Green
- Jenkins automates deployment
- CloudWatch provides logs and monitoring
- OWASP ZAP is the mandatory automated security stage
- Burp Suite and Wireshark provide required manual testing evidence

If you are presenting this project, the easiest strong explanation is:

> Terraform creates the AWS infrastructure, Ansible configures both Blue and Green application servers, Jenkins automates build, test, security scanning, green deployment, verification, traffic switching, and rollback, while CloudWatch collects logs and shows health metrics. OWASP ZAP, Burp Suite, and Wireshark form the DevSecOps and web security evidence layer.
