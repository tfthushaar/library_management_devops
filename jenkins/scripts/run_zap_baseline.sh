#!/usr/bin/env bash
set -euo pipefail

TARGET_URL="${1:-}"

if [[ -z "${TARGET_URL}" ]]; then
  echo "Usage: $0 <target-url>"
  exit 1
fi

if ! command -v zap-baseline.py >/dev/null 2>&1; then
  if command -v docker >/dev/null 2>&1; then
    echo "zap-baseline.py not found in PATH. Falling back to the official ZAP Docker image."
    docker run --rm -v "$(pwd):/zap/wrk/:rw" -t ghcr.io/zaproxy/zaproxy:stable \
      zap-baseline.py -t "${TARGET_URL}" -r zap-report.html -m 3
    exit 0
  fi

  echo "OWASP ZAP baseline command not found."
  echo "Install ZAP baseline tooling on the Jenkins agent or install Docker so the official ZAP image can be used."
  exit 1
fi

zap-baseline.py -t "${TARGET_URL}" -r zap-report.html -m 3
