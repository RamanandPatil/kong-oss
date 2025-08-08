#!/usr/bin/env bash
set -euo pipefail
CLUSTER=${CLUSTER:-kong-hybrid}
cat <<EOF | kind create cluster --name "$CLUSTER" --config=-
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
  - role: control-plane
  - role: worker
  - role: worker
EOF
kubectl create namespace kong || true
echo "Kind cluster '${CLUSTER}' created and namespace 'kong' ensured."
