#!/usr/bin/env bash
set -euo pipefail
kind delete cluster --name kong-hybrid || true
kubectl delete ns kong || true
rm -rf certs
echo "Cleaned up cluster, namespace, and cert files."
