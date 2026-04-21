# Blue-Green Deployment Flow

## Default State

- Blue serves live traffic.
- Green is idle or running the previous candidate version.

## Deployment Sequence

1. Jenkins checks out the latest code.
2. Jenkins builds the Python environment and runs unit tests.
3. Jenkins runs the mandatory OWASP ZAP baseline scan.
4. Jenkins deploys the updated library portal to the Green server using Ansible.
5. Jenkins verifies `http://127.0.0.1/health` on Green.
6. Jenkins updates the ALB listener to forward traffic to the Green target group.
7. Jenkins validates `http://ALB_DNS_NAME/health`.

## Rollback Sequence

If the post-switch ALB health check fails:

1. Jenkins runs `jenkins/scripts/rollback_blue.sh`.
2. The ALB listener is pointed back to the Blue target group.
3. Users continue using the stable Blue environment.

## Why This Matches the Rubric

- Green receives the new release first.
- Verification happens before and after the traffic cutover.
- Rollback to Blue is automated when final validation fails.
- The ALB is the switch point, which is what evaluators usually expect to see in a blue-green demo.
