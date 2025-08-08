#!/usr/bin/env bash
set -euo pipefail
helm repo add kong https://charts.konghq.com || true
helm repo update
kubectl create ns kong || true

helm upgrade --install kong-cp kong/kong   --namespace kong   -f ../helm-values/cp-values.yaml   --wait --timeout 5m
