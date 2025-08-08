#!/usr/bin/env bash
set -euo pipefail
helm repo add kong https://charts.konghq.com || true
helm repo update

helm upgrade --install kong-dp kong/kong   --namespace kong   -f ../helm-values/dp-values.yaml   --wait --timeout 5m
