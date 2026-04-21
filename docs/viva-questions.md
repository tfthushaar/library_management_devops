# Viva Questions and Answers

## Why did you choose blue-green deployment?

Blue-green deployment reduces downtime and makes rollback easy because the stable version remains available while the new version is verified on Green.

## Why is OWASP ZAP compulsory in this project?

It provides automated baseline security scanning and helps identify missing headers, insecure configurations, and common low-risk vulnerabilities before traffic is switched.

## What is the role of Burp Suite here?

Burp Suite is used for manual testing. It lets us intercept requests, modify inputs, and observe how the application behaves under tampered conditions.

## What is the role of Wireshark here?

Wireshark helps verify whether traffic is encrypted properly and whether sensitive information appears in plain text over the network.

## Why use Terraform instead of manually creating AWS resources?

Terraform gives repeatable, version-controlled infrastructure provisioning and makes it easier to re-create the same ALB, EC2, IAM, and CloudWatch setup.

## Why use Ansible when Jenkins already exists?

Jenkins orchestrates the pipeline, while Ansible performs the server configuration and deployment tasks on EC2 instances.

## Why is the `/health` endpoint important?

It is used by both Jenkins and the ALB to confirm that the app is working before and after the traffic switch.

## What does CloudWatch contribute?

CloudWatch centralizes application logs and gives a dashboard for metrics such as request count, healthy hosts, and EC2 CPU usage.

## What would happen if Green failed after the switch?

The Jenkins rollback script would point the ALB listener back to Blue so users return to the last stable release.
