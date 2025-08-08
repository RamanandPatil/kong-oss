#!/bin/bash

# cleanup.sh - Clean up Kong deployment
set -euo pipefail

NAMESPACE="kong"
POSTGRES_NAMESPACE="postgres"

echo "🧹 Cleaning up Kong deployment..."

# Ask for confirmation
read -p "This will delete all Kong resources. Are you sure? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cleanup cancelled."
    exit 0
fi

# Delete Helm releases
echo "Deleting Helm releases..."
helm uninstall kong-dp -n "$NAMESPACE" 2>/dev/null || true
helm uninstall kong-cp -n "$NAMESPACE" 2>/dev/null || true
helm uninstall postgres -n "$POSTGRES_NAMESPACE" 2>/dev/null || true

# Delete secrets
echo "Deleting secrets..."
kubectl delete secret kong-cluster-cert -n "$NAMESPACE" 2>/dev/null || true
kubectl delete secret kong-admin-cert -n "$NAMESPACE" 2>/dev/null || true  
kubectl delete secret kong-proxy-cert -n "$NAMESPACE" 2>/dev/null || true

# Delete ConfigMaps
echo "Deleting ConfigMaps..."
kubectl delete configmap kong-plugin-api-version -n "$NAMESPACE" 2>/dev/null || true

# Delete PVCs (optional)
read -p "Delete persistent volumes (data will be lost)? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    kubectl delete pvc -l app.kubernetes.io/name=postgresql -n "$POSTGRES_NAMESPACE" 2>/dev/null || true
fi

# Delete namespaces (optional)
read -p "Delete namespaces? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    kubectl delete namespace "$NAMESPACE" 2>/dev/null || true
    kubectl delete namespace "$POSTGRES_NAMESPACE" 2>/dev/null || true
fi

echo "✅ Cleanup completed!"
