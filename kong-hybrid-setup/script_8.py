# Create additional deployment scripts
deploy_cp_script = """#!/bin/bash

# deploy-cp.sh - Deploy Kong Control Plane only
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
NAMESPACE="kong"

echo "🎛️  Deploying Kong Control Plane..."

# Deploy Control Plane
helm upgrade --install kong-cp kong/kong \\
    --namespace "$NAMESPACE" \\
    --values "$PROJECT_ROOT/control-plane/values-cp.yaml" \\
    --wait \\
    --timeout 10m

echo "✅ Kong Control Plane deployment completed!"
"""

deploy_dp_script = """#!/bin/bash

# deploy-dp.sh - Deploy Kong Data Plane only
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
NAMESPACE="kong"

echo "🌐 Deploying Kong Data Plane..."

# Deploy Data Plane
helm upgrade --install kong-dp kong/kong \\
    --namespace "$NAMESPACE" \\
    --values "$PROJECT_ROOT/data-plane/values-dp.yaml" \\
    --wait \\
    --timeout 10m

echo "✅ Kong Data Plane deployment completed!"
"""

cleanup_script = """#!/bin/bash

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
"""

# Write the scripts
scripts = [
    ("deploy-cp.sh", deploy_cp_script),
    ("deploy-dp.sh", deploy_dp_script), 
    ("cleanup.sh", cleanup_script)
]

for script_name, script_content in scripts:
    with open(f"kong-hybrid-setup/scripts/{script_name}", "w") as f:
        f.write(script_content)
    
    # Make executable
    os.chmod(f"kong-hybrid-setup/scripts/{script_name}", 
             stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)

print("Additional deployment scripts created:")
print("- deploy-cp.sh: Deploy Control Plane only")
print("- deploy-dp.sh: Deploy Data Plane only") 
print("- cleanup.sh: Clean up all resources")