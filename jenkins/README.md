# Jenkins Notes

This project expects a Jenkins agent with the following tools installed:

- Git
- Python 3 with `venv`
- Ansible
- AWS CLI v2
- OWASP ZAP baseline tooling available as `zap-baseline.py` or Docker

Suggested Jenkins setup:

- Create a Pipeline job from SCM and point the Jenkinsfile path to `Jenkinsfile`.
- Pass the Terraform outputs into the Jenkins parameters:
  - `ALB_LISTENER_ARN`
  - `BLUE_TARGET_GROUP_ARN`
  - `GREEN_TARGET_GROUP_ARN`
  - `ALB_DNS_NAME`
- Ensure the Jenkins agent has SSH access to the blue and green EC2 instances.
- Store the private key on the agent and set `ANSIBLE_PRIVATE_KEY_FILE` to its path.
- Archive `zap-report.html` from the mandatory security testing stage as submission evidence.
