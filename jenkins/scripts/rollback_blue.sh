#!/usr/bin/env bash
set -euo pipefail

: "${ALB_LISTENER_ARN:?ALB_LISTENER_ARN environment variable is required}"
: "${BLUE_TARGET_GROUP_ARN:?BLUE_TARGET_GROUP_ARN environment variable is required}"
: "${AWS_DEFAULT_REGION:?AWS_DEFAULT_REGION environment variable is required}"

aws elbv2 modify-listener \
  --region "${AWS_DEFAULT_REGION}" \
  --listener-arn "${ALB_LISTENER_ARN}" \
  --default-actions "Type=forward,TargetGroupArn=${BLUE_TARGET_GROUP_ARN}"

echo "Rollback completed. Traffic switched back to blue target group."

