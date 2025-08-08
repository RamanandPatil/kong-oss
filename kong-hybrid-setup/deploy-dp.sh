#!/bin/bash

# deploy-dp.sh - Deploy Kong Data Plane only
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
NAMESPACE="kong"

echo "🌐 Deploying Kong Data Plane..."

# Deploy Data Plane
helm upgrade --install kong-dp kong/kong \
    --namespace "$NAMESPACE" \
    --values "$PROJECT_ROOT/data-plane/values-dp.yaml" \
    --wait \
    --timeout 10m

echo "✅ Kong Data Plane deployment completed!"
