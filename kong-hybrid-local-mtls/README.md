# Kong OSS Hybrid Mode — Local Kubernetes with internal PKI (mTLS)

This repo provides a production-like local setup for **Kong OSS** where Control Plane (CP) and Data Plane (DP) communicate over **mTLS** using an internal CA chain (Root CA -> Intermediate CA -> signed CP/DP certs).

> Important: Kong OSS doesn't natively manage CP↔DP identities like Enterprise. This configuration uses Kong's shared mTLS settings to enforce mutual TLS between nodes — suitable for production-like testing.

## Quick overview

Steps:
1. Install prerequisites (macOS / Ubuntu)
2. Create Kind cluster
3. Build Kong image with custom plugin
4. Generate internal CA & signed certs (CP, DP)
5. Create Kubernetes secrets from certs
6. Deploy CP and DP using Helm with cert mounts
7. Push declarative config (decK)
8. Test

## Prerequisites

Install tools (macOS):
```bash
brew install kind kubectl helm deck openssl jq
brew install --cask docker
open /Applications/Docker.app
```

Install tools (Ubuntu):
```bash
sudo apt update
sudo apt install -y curl jq openssl docker.io
curl -Lo ./kind https://kind.sigs.k8s.io/dl/latest/kind-linux-amd64
chmod +x ./kind && sudo mv ./kind /usr/local/bin/
curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
sudo snap install kubectl --classic
# decK: follow https://docs.konghq.com/deck/latest/installation/
```

## How to run (full run)
From project root:
```bash
chmod +x scripts/*.sh
make create-cluster
make build
make generate-certs
make create-secrets
make deploy-cp
make deploy-dp
# allow port-forwarding:
kubectl -n kong port-forward svc/kong-kong-proxy 8000:80 &
kubectl -n kong port-forward svc/kong-kong-admin 8001:8001 &
# push config
deck sync --kong-addr http://localhost:8001 --config deck/kong-config.yaml
# test
curl -i http://localhost:8000/example
```

## Tear down
```bash
make cleanup
```

## Notes
- This uses a simulated PKI: Root CA -> Intermediate -> CP/DP certs. Treat CA keys like sensitive assets.
- For real production, use your organization’s PKI (Vault PKI, internal CA, or ACME + internal CA).
- This setup is **OSS-only** (no Kong Enterprise). It mirrors mTLS behavior as close as possible.
