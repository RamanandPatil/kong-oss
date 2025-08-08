#!/usr/bin/env bash
set -euo pipefail
CERT_DIR=${CERT_DIR:-./certs}
NS=${NS:-kong}

if [ ! -d "${CERT_DIR}" ]; then
  echo "Error: ${CERT_DIR} does not exist. Run generate-mtls-certs.sh first."
  exit 1
fi

kubectl create namespace ${NS} || true

kubectl -n ${NS} delete secret kong-cp-pki || true
kubectl -n ${NS} create secret generic kong-cp-pki \
  --from-file=tls.crt=${CERT_DIR}/cp.crt \
  --from-file=tls.key=${CERT_DIR}/cp.key \
  --from-file=intermediate.crt=${CERT_DIR}/intermediate.crt \
  --from-file=root.crt=${CERT_DIR}/root.crt

kubectl -n ${NS} delete secret kong-dp-pki || true
kubectl -n ${NS} create secret generic kong-dp-pki \
  --from-file=tls.crt=${CERT_DIR}/dp.crt \
  --from-file=tls.key=${CERT_DIR}/dp.key \
  --from-file=intermediate.crt=${CERT_DIR}/intermediate.crt

kubectl -n ${NS} delete secret kong-ca || true
kubectl -n ${NS} create secret generic kong-ca \
  --from-file=intermediate.crt=${CERT_DIR}/intermediate.crt \
  --from-file=root.crt=${CERT_DIR}/root.crt

echo "Secrets created in namespace ${NS}: kong-cp-pki, kong-dp-pki, kong-ca"
