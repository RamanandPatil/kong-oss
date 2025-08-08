#!/usr/bin/env bash
set -euo pipefail
IMAGE_NAME=${IMAGE_NAME:-kong-custom:local}
docker build -t ${IMAGE_NAME} -f ../Dockerfile .
kind load docker-image ${IMAGE_NAME} --name kong-hybrid || true
echo "Built and loaded image ${IMAGE_NAME}"
