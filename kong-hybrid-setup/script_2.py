# Create certificate generation script
cert_script = """#!/bin/bash

# generate-certs.sh - Generate certificates for Kong hybrid mode
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CERT_DIR="${SCRIPT_DIR}"

echo "🔐 Generating Kong Hybrid Mode Certificates..."

# Create certificates directory if it doesn't exist
mkdir -p "${CERT_DIR}"

# Generate cluster certificate and key for mTLS communication between CP and DP
echo "📜 Generating cluster certificate and key..."
openssl req -new -x509 -nodes \\
    -newkey ec:<(openssl ecparam -name secp384r1) \\
    -keyout "${CERT_DIR}/cluster.key" \\
    -out "${CERT_DIR}/cluster.crt" \\
    -days 1095 \\
    -subj "/CN=kong_clustering"

echo "✅ Cluster certificate generated: ${CERT_DIR}/cluster.crt"
echo "✅ Cluster key generated: ${CERT_DIR}/cluster.key"

# Generate admin API certificate (optional, for HTTPS admin API)
echo "📜 Generating admin API certificate and key..."
openssl req -new -x509 -nodes \\
    -newkey rsa:2048 \\
    -keyout "${CERT_DIR}/admin.key" \\
    -out "${CERT_DIR}/admin.crt" \\
    -days 1095 \\
    -subj "/CN=kong-admin-api"

echo "✅ Admin API certificate generated: ${CERT_DIR}/admin.crt"
echo "✅ Admin API key generated: ${CERT_DIR}/admin.key"

# Generate proxy certificate (optional, for HTTPS proxy)
echo "📜 Generating proxy certificate and key..."
openssl req -new -x509 -nodes \\
    -newkey rsa:2048 \\
    -keyout "${CERT_DIR}/proxy.key" \\
    -out "${CERT_DIR}/proxy.crt" \\
    -days 1095 \\
    -subj "/CN=kong-proxy" \\
    -addext "subjectAltName=DNS:localhost,DNS:kong-proxy,IP:127.0.0.1"

echo "✅ Proxy certificate generated: ${CERT_DIR}/proxy.crt"
echo "✅ Proxy key generated: ${CERT_DIR}/proxy.key"

# Set proper permissions
chmod 600 "${CERT_DIR}"/*.key
chmod 644 "${CERT_DIR}"/*.crt

echo ""
echo "🎉 All certificates generated successfully!"
echo "📁 Certificates location: ${CERT_DIR}"
echo ""
echo "📋 Next steps:"
echo "1. Create Kubernetes secrets from these certificates"
echo "2. Configure Kong Control Plane and Data Plane with these certificates"
echo "3. Deploy Kong using Helm charts"
echo ""
echo "🔧 Create Kubernetes secrets:"
echo "kubectl create secret tls kong-cluster-cert --cert=${CERT_DIR}/cluster.crt --key=${CERT_DIR}/cluster.key -n kong"
echo "kubectl create secret tls kong-admin-cert --cert=${CERT_DIR}/admin.crt --key=${CERT_DIR}/admin.key -n kong"
echo "kubectl create secret tls kong-proxy-cert --cert=${CERT_DIR}/proxy.crt --key=${CERT_DIR}/proxy.key -n kong"
"""

with open("kong-hybrid-setup/certificates/generate-certs.sh", "w") as f:
    f.write(cert_script)

# Make it executable
import stat
os.chmod("kong-hybrid-setup/certificates/generate-certs.sh", 
         stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)

print("Certificate generation script created!")