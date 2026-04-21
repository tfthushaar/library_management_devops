#!/usr/bin/env bash
set -euo pipefail

: "${ALB_LISTENER_ARN:?ALB_LISTENER_ARN environment variable is required}"
: "${GREEN_TARGET_GROUP_ARN:?GREEN_TARGET_GROUP_ARN environment variable is required}"
: "${AWS_DEFAULT_REGION:?AWS_DEFAULT_REGION environment variable is required}"

aws elbv2 modify-listener \
  --region "${AWS_DEFAULT_REGION}" \
  --listener-arn "${ALB_LISTENER_ARN}" \
  --default-actions "Type=forward,TargetGroupArn=${GREEN_TARGET_GROUP_ARN}"

echo "Traffic switched to green target group."

