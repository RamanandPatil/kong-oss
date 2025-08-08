#!/usr/bin/env bash
set -euo pipefail
OUT_DIR=${OUT_DIR:-./certs}
mkdir -p ${OUT_DIR}
cd ${OUT_DIR}

echo "Generating Root CA..."
openssl genpkey -algorithm RSA -out root.key -pkeyopt rsa_keygen_bits:4096
openssl req -x509 -new -nodes -key root.key -days 3650 -subj "/C=US/ST=CA/L=Local/O=ExampleRootCA/CN=Example Root CA" -out root.crt

echo "Generating Intermediate CA..."
openssl genpkey -algorithm RSA -out intermediate.key -pkeyopt rsa_keygen_bits:4096
openssl req -new -key intermediate.key -subj "/C=US/ST=CA/L=Local/O=ExampleIntermediateCA/CN=Example Intermediate CA" -out intermediate.csr

cat > intermediate_ext.cnf <<EOF
basicConstraints = CA:TRUE,pathlen:0
keyUsage = critical, cRLSign, digitalSignature, keyCertSign
subjectKeyIdentifier=hash
authorityKeyIdentifier=keyid,issuer
EOF

openssl x509 -req -in intermediate.csr -CA root.crt -CAkey root.key -CAcreateserial -out intermediate.crt -days 3650 -extfile intermediate_ext.cnf

echo "Generate CP certificate (server cert signed by Intermediate CA)..."
openssl genpkey -algorithm RSA -out cp.key -pkeyopt rsa_keygen_bits:2048
openssl req -new -key cp.key -subj "/C=US/ST=CA/L=Local/O=KongCP/CN=kong-cp.kong.svc" -out cp.csr

cat > cp_ext.cnf <<EOF
subjectAltName = DNS:kong-cp-kong-admin.kong.svc.cluster.local, DNS:localhost
keyUsage = critical, digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth, clientAuth
EOF

openssl x509 -req -in cp.csr -CA intermediate.crt -CAkey intermediate.key -CAcreateserial -out cp.crt -days 365 -extfile cp_ext.cnf

echo "Generate DP certificate (client cert signed by Intermediate CA)..."
openssl genpkey -algorithm RSA -out dp.key -pkeyopt rsa_keygen_bits:2048
openssl req -new -key dp.key -subj "/C=US/ST=CA/L=Local/O=KongDP/CN=kong-dp" -out dp.csr

cat > dp_ext.cnf <<EOF
subjectAltName = DNS:kong-dp.kong.svc.cluster.local, DNS:localhost
keyUsage = critical, digitalSignature, keyEncipherment
extendedKeyUsage = clientAuth, serverAuth
EOF

openssl x509 -req -in dp.csr -CA intermediate.crt -CAkey intermediate.key -CAcreateserial -out dp.crt -days 365 -extfile dp_ext.cnf

echo "Write out combined CA chain (intermediate + root)..."
cat intermediate.crt root.crt > ca-chain.crt
cp root.crt root_ca.crt

echo "Files generated in: $(pwd)"
ls -l cp.* dp.* intermediate.* root.*
echo "DONE"
