# OWASP ZAP Baseline Scan Integration

## Purpose

OWASP ZAP is the mandatory automated security scanner for this project.

It is used to identify:

- Missing security headers
- Information disclosure risks
- Insecure configurations
- Common low-risk web issues that still need documentation

## Jenkins Integration

The pipeline runs:

```bash
jenkins/scripts/run_zap_baseline.sh http://127.0.0.1:5001
```

This happens before deployment to Green so basic security issues are caught early.

## Manual Command Against the ALB

```bash
zap-baseline.py -t http://ALB_DNS_NAME -r zap-report.html -m 3
```

## Required Evidence

- Screenshot of the Jenkins security testing stage
- `zap-report.html` artifact
- Short table of findings and severity
- Notes showing what you fixed after the first scan
