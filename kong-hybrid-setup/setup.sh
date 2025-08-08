#!/bin/bash

# setup.sh - Complete Kong Hybrid Setup Script
set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Configuration
NAMESPACE="kong"
POSTGRES_NAMESPACE="postgres"

echo -e "${BLUE}🚀 Kong OSS Hybrid Mode Setup${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Function to print status
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to check prerequisites
check_prerequisites() {
    echo -e "${BLUE}🔍 Checking prerequisites...${NC}"

    # Check if kubectl is installed
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl is not installed. Please install kubectl first."
        exit 1
    fi

    # Check if helm is installed
    if ! command -v helm &> /dev/null; then
        print_error "helm is not installed. Please install helm first."
        exit 1
    fi

    # Check if cluster is accessible
    if ! kubectl cluster-info &> /dev/null; then
        print_error "Cannot connect to Kubernetes cluster. Please check your kubectl configuration."
        exit 1
    fi

    print_status "Prerequisites check passed"
}

# Function to setup Helm repositories
setup_helm_repos() {
    echo -e "${BLUE}📦 Setting up Helm repositories...${NC}"

    # Add Kong Helm repository
    helm repo add kong https://charts.konghq.com

    # Add Bitnami Helm repository for PostgreSQL
    helm repo add bitnami https://charts.bitnami.com/bitnami

    # Update repositories
    helm repo update

    print_status "Helm repositories configured"
}

# Function to create namespaces
create_namespaces() {
    echo -e "${BLUE}🏷️  Creating namespaces...${NC}"

    # Create Kong namespace
    kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

    # Create PostgreSQL namespace
    kubectl create namespace "$POSTGRES_NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

    print_status "Namespaces created"
}

# Function to generate certificates
generate_certificates() {
    echo -e "${BLUE}🔐 Generating certificates...${NC}"

    # Run certificate generation script
    bash "$PROJECT_ROOT/certificates/generate-certs.sh"

    # Create Kubernetes secrets from certificates
    kubectl create secret tls kong-cluster-cert \
        --cert="$PROJECT_ROOT/certificates/cluster.crt" \
        --key="$PROJECT_ROOT/certificates/cluster.key" \
        -n "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

    kubectl create secret tls kong-admin-cert \
        --cert="$PROJECT_ROOT/certificates/admin.crt" \
        --key="$PROJECT_ROOT/certificates/admin.key" \
        -n "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

    kubectl create secret tls kong-proxy-cert \
        --cert="$PROJECT_ROOT/certificates/proxy.crt" \
        --key="$PROJECT_ROOT/certificates/proxy.key" \
        -n "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

    print_status "Certificates generated and secrets created"
}

# Function to create custom plugin ConfigMap
create_custom_plugins() {
    echo -e "${BLUE}🔌 Creating custom plugin ConfigMaps...${NC}"

    # Create ConfigMap for API version plugin
    kubectl create configmap kong-plugin-api-version \
        --from-file=handler.lua="$PROJECT_ROOT/custom-plugins/api-version/kong/plugins/api-version/handler.lua" \
        --from-file=schema.lua="$PROJECT_ROOT/custom-plugins/api-version/kong/plugins/api-version/schema.lua" \
        -n "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

    print_status "Custom plugin ConfigMaps created"
}

# Function to deploy PostgreSQL
deploy_postgresql() {
    echo -e "${BLUE}🐘 Deploying PostgreSQL database...${NC}"

    # Deploy PostgreSQL using Helm
    helm upgrade --install postgres bitnami/postgresql \
        --namespace "$POSTGRES_NAMESPACE" \
        --values "$PROJECT_ROOT/database/postgres-values.yaml" \
        --wait \
        --timeout 10m

    # Wait for PostgreSQL to be ready
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=postgresql -n "$POSTGRES_NAMESPACE" --timeout=300s

    print_status "PostgreSQL deployed and ready"
}

# Function to deploy Kong Control Plane
deploy_control_plane() {
    echo -e "${BLUE}🎛️  Deploying Kong Control Plane...${NC}"

    # Deploy Kong Control Plane
    helm upgrade --install kong-cp kong/kong \
        --namespace "$NAMESPACE" \
        --values "$PROJECT_ROOT/control-plane/values-cp.yaml" \
        --wait \
        --timeout 10m

    # Wait for Control Plane to be ready
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=kong -n "$NAMESPACE" --timeout=300s

    print_status "Kong Control Plane deployed and ready"
}

# Function to run database migrations
run_migrations() {
    echo -e "${BLUE}🔄 Running database migrations...${NC}"

    # Run Kong migrations
    kubectl exec -n "$NAMESPACE" deployment/kong-cp-kong -- kong migrations bootstrap

    print_status "Database migrations completed"
}

# Function to deploy Kong Data Plane
deploy_data_plane() {
    echo -e "${BLUE}🌐 Deploying Kong Data Plane...${NC}"

    # Deploy Kong Data Plane
    helm upgrade --install kong-dp kong/kong \
        --namespace "$NAMESPACE" \
        --values "$PROJECT_ROOT/data-plane/values-dp.yaml" \
        --wait \
        --timeout 10m

    # Wait for Data Plane to be ready
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=kong,app.kubernetes.io/instance=kong-dp -n "$NAMESPACE" --timeout=300s

    print_status "Kong Data Plane deployed and ready"
}

# Function to verify deployment
verify_deployment() {
    echo -e "${BLUE}🔍 Verifying deployment...${NC}"

    # Check if all pods are running
    echo "Checking pod status..."
    kubectl get pods -n "$NAMESPACE"
    kubectl get pods -n "$POSTGRES_NAMESPACE"

    # Check services
    echo ""
    echo "Checking services..."
    kubectl get svc -n "$NAMESPACE"

    # Test Control Plane Admin API
    echo ""
    echo "Testing Control Plane connectivity..."
    if kubectl exec -n "$NAMESPACE" deployment/kong-cp-kong -- curl -s http://localhost:8001/status | grep -q "database"; then
        print_status "Control Plane Admin API is responding"
    else
        print_warning "Control Plane Admin API test failed"
    fi

    # Test Data Plane status
    echo "Testing Data Plane connectivity..."
    if kubectl exec -n "$NAMESPACE" deployment/kong-dp-kong -- curl -s http://localhost:8100/status | grep -q "ready"; then
        print_status "Data Plane status API is responding"
    else
        print_warning "Data Plane status API test failed"
    fi

    print_status "Deployment verification completed"
}

# Function to show access information
show_access_info() {
    echo ""
    echo -e "${BLUE}🎉 Kong Hybrid Setup Complete!${NC}"
    echo -e "${BLUE}===============================${NC}"
    echo ""
    echo "📋 Access Information:"
    echo ""
    echo "🎛️  Kong Admin API (Control Plane):"
    echo "   kubectl port-forward -n $NAMESPACE svc/kong-cp-kong-admin 8001:8001"
    echo "   Access: http://localhost:8001"
    echo ""
    echo "🖥️  Kong Manager GUI:"
    echo "   kubectl port-forward -n $NAMESPACE svc/kong-cp-kong-manager 8002:8002"
    echo "   Access: http://localhost:8002"
    echo ""
    echo "🌐 Kong Proxy (Data Plane):"
    echo "   kubectl port-forward -n $NAMESPACE svc/kong-dp-kong-proxy 8000:80"
    echo "   Access: http://localhost:8000"
    echo ""
    echo "📊 PostgreSQL Database:"
    echo "   kubectl port-forward -n $POSTGRES_NAMESPACE svc/postgres-postgresql 5432:5432"
    echo "   Connection: postgresql://kong:kong-password@localhost:5432/kong"
    echo ""
    echo "🔧 Useful Commands:"
    echo "   # Check cluster status:"
    echo "   curl http://localhost:8001/clustering/status"
    echo ""
    echo "   # Check data planes:"
    echo "   curl http://localhost:8001/clustering/data-planes"
    echo ""
    echo "   # Create a test service:"
    echo "   curl -X POST http://localhost:8001/services \\"
    echo "     --data 'name=httpbin' \\"
    echo "     --data 'url=http://httpbin.org'"
    echo ""
    echo "   # Create a test route:"  
    echo "   curl -X POST http://localhost:8001/services/httpbin/routes \\"
    echo "     --data 'paths[]=/httpbin'"
    echo ""
    echo "   # Test the proxy:"
    echo "   curl http://localhost:8000/httpbin/get"
}

# Main execution
main() {
    echo "Starting Kong OSS Hybrid Mode deployment..."
    echo "This will deploy Kong Control Plane, Data Plane, and PostgreSQL"
    echo ""

    # Ask for confirmation
    read -p "Do you want to continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Deployment cancelled."
        exit 0
    fi

    # Execute deployment steps
    check_prerequisites
    setup_helm_repos
    create_namespaces
    generate_certificates
    create_custom_plugins
    deploy_postgresql
    deploy_control_plane
    run_migrations
    deploy_data_plane
    verify_deployment
    show_access_info

    echo ""
    print_status "Kong Hybrid Mode setup completed successfully!"
}

# Error handling
trap 'print_error "An error occurred. Exiting."; exit 1' ERR

# Run main function
main "$@"
