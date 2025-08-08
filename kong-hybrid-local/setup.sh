#!/bin/bash

# --- Configuration ---
KONG_NAMESPACE="kong"
CHART_VERSION="2.35.0"
KONG_IMAGE_VERSION="3.7"

# --- 1. Setup Namespace ---
echo ">>> Creating Kubernetes namespace: $KONG_NAMESPACE"
kubectl get ns $KONG_NAMESPACE > /dev/null 2>&1 || kubectl create namespace $KONG_NAMESPACE

# --- 2. Create Cluster Certificate Secret ---
echo ">>> Generating self-signed certificates for CP-DP communication..."
openssl req -new -x509 -nodes \
    -newkey ec:<(openssl ecparam -name secp384r1) \
    -keyout cluster.key \
    -out cluster.crt \
    -days 1095 \
    -subj "/CN=kong_clustering"

echo ">>> Creating Kubernetes secret for cluster certificates..."
kubectl create secret tls kong-cluster-cert \
    --cert=cluster.crt \
    --key=cluster.key \
    -n $KONG_NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Clean up local cert files
rm cluster.crt cluster.key

# --- 3. Create Custom Plugin ConfigMap ---
echo ">>> Creating ConfigMap for custom plugins..."
kubectl create configmap kong-custom-plugins \
    --from-file=custom-plugins/kong/plugins/my-custom-plugin/ \
    -n $KONG_NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# --- 4. Add Helm Repos ---
echo ">>> Adding Kong and Bitnami Helm repositories..."
helm repo add kong https://charts.konghq.com
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# --- 5. Deploy PostgreSQL Database ---
echo ">>> Deploying PostgreSQL for Kong CP..."
helm upgrade --install kong-postgresql bitnami/postgresql \
    --set auth.database=kong \
    --set auth.username=kong \
    --set auth.password=kong \
    -n $KONG_NAMESPACE

echo ">>> Waiting for PostgreSQL to be ready..."
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=postgresql -n $KONG_NAMESPACE --timeout=300s

# --- 6. Run Kong Migrations ---
echo ">>> Running Kong database migrations..."
helm upgrade --install kong-migrations kong/kong \
    --version $CHART_VERSION \
    --set-string image.tag=$KONG_IMAGE_VERSION \
    --set runMigrations=true \
    -f values/cp-values.yaml \
    -n $KONG_NAMESPACE \
    --wait

# Uninstall migration job after completion
helm uninstall kong-migrations -n $KONG_NAMESPACE

# --- 7. Deploy Kong Control Plane (CP) ---
echo ">>> Deploying Kong Control Plane..."
helm upgrade --install kong-cp kong/kong \
    --version $CHART_VERSION \
    --set-string image.tag=$KONG_IMAGE_VERSION \
    -f values/cp-values.yaml \
    -n $KONG_NAMESPACE

# --- 8. Deploy Kong Data Plane (DP) ---
echo ">>> Deploying Kong Data Plane..."
helm upgrade --install kong-dp kong/kong \
    --version $CHART_VERSION \
    --set-string image.tag=$KONG_IMAGE_VERSION \
    -f values/dp-values.yaml \
    -n $KONG_NAMESPACE

echo -e "\n✅ Deployment complete! Wait for all pods to be in the 'Running' state."
echo "Use 'kubectl get all -n $KONG_NAMESPACE' to check status."

