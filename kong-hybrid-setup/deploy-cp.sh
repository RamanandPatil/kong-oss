#!/bin/bash

# deploy-cp.sh - Deploy Kong Control Plane only
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
NAMESPACE="kong"

echo "🎛️  Deploying Kong Control Plane..."

# Deploy Control Plane
helm upgrade --install kong-cp kong/kong \
    --namespace "$NAMESPACE" \
    --values "$PROJECT_ROOT/control-plane/values-cp.yaml" \
    --wait \
    --timeout 10m

echo "✅ Kong Control Plane deployment completed!"
