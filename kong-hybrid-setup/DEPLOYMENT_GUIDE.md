# Kong OSS Hybrid Mode Deployment Guide

This guide provides step-by-step instructions for deploying Kong OSS Gateway in hybrid mode on Kubernetes using Helm charts.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites) 
3. [Quick Setup](#quick-setup)
4. [Manual Setup](#manual-setup)
5. [Custom Plugins](#custom-plugins)
6. [Configuration Management](#configuration-management)
7. [Monitoring & Observability](#monitoring--observability)
8. [Production Considerations](#production-considerations)
9. [Troubleshooting](#troubleshooting)

## Architecture Overview

Kong Hybrid Mode separates the control plane (CP) and data plane (DP):

- **Control Plane**: Manages configuration, hosts Admin API and Kong Manager
- **Data Plane**: Handles actual traffic, executes plugins, proxies requests

```
┌─────────────────────────────────────────────────────────────────┐
│                           Kong Hybrid Architecture              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    mTLS    ┌─────────────────┐             │
│  │ Control Plane   │◄──────────►│  Data Plane     │             │
│  │                 │            │                 │             │
│  │ • Admin API     │            │ • Proxy Service │             │
│  │ • Kong Manager  │            │ • Load Balancer │             │
│  │ • Configuration │            │ • Plugin Exec   │             │
│  │ • Database      │            │ • Health Checks │             │
│  └─────────────────┘            └─────────────────┘             │
│           │                              │                      │
│           │                              │                      │
│  ┌─────────────────┐            ┌─────────────────┐             │
│  │   PostgreSQL    │            │   Upstream      │             │
│  │   Database      │            │   Services      │             │
│  └─────────────────┘            └─────────────────┘             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Prerequisites

### System Requirements
- **Kubernetes**: 1.21+ 
- **Helm**: 3.0+
- **kubectl**: Latest version
- **Resources**: Minimum 4 CPU cores, 8GB RAM

### Local Development Options
Choose one of these for local development:

#### Option 1: Minikube
```bash
# Start minikube with adequate resources
minikube start --cpus=4 --memory=8192 --disk-size=20g
minikube addons enable ingress
```

#### Option 2: Kind
```bash
# Create kind cluster  
kind create cluster --name kong-hybrid --config - <<EOF
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  kubeadmConfigPatches:
  - |
    kind: InitConfiguration
    nodeRegistration:
      kubeletExtraArgs:
        node-labels: "ingress-ready=true"
  extraPortMappings:
  - containerPort: 80
    hostPort: 80
    protocol: TCP
  - containerPort: 443
    hostPort: 443
    protocol: TCP
- role: worker
- role: worker
EOF
```

#### Option 3: K3s (Lightweight)
```bash
# Install k3s
curl -sfL https://get.k3s.io | sh -
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
```

### Required Tools Installation

#### Install kubectl
```bash
# Linux
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/

# macOS
brew install kubectl

# Windows (using Chocolatey)
choco install kubernetes-cli
```

#### Install Helm
```bash
# Linux/macOS
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# macOS (using Homebrew)
brew install helm

# Windows (using Chocolatey) 
choco install kubernetes-helm
```

## Quick Setup

The fastest way to get Kong hybrid mode running:

```bash
# Clone this repository
git clone <repository-url>
cd kong-hybrid-setup

# Run the automated setup
./scripts/setup.sh
```

This will:
1. ✅ Check prerequisites
2. ✅ Setup Helm repositories  
3. ✅ Create namespaces
4. ✅ Generate certificates
5. ✅ Deploy PostgreSQL
6. ✅ Deploy Kong Control Plane
7. ✅ Run database migrations
8. ✅ Deploy Kong Data Plane
9. ✅ Verify deployment

## Manual Setup

For step-by-step control or production environments:

### Step 1: Setup Helm Repositories
```bash
# Add Kong and Bitnami Helm repositories
helm repo add kong https://charts.konghq.com
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
```

### Step 2: Create Namespaces  
```bash
# Create namespaces
kubectl create namespace kong
kubectl create namespace postgres
```

### Step 3: Generate Certificates
```bash
# Generate certificates for mTLS communication
./certificates/generate-certs.sh

# Create Kubernetes secrets
kubectl create secret tls kong-cluster-cert \
    --cert=certificates/cluster.crt \
    --key=certificates/cluster.key \
    -n kong

kubectl create secret tls kong-admin-cert \
    --cert=certificates/admin.crt \
    --key=certificates/admin.key \
    -n kong

kubectl create secret tls kong-proxy-cert \
    --cert=certificates/proxy.crt \
    --key=certificates/proxy.key \
    -n kong
```

### Step 4: Deploy PostgreSQL
```bash
# Deploy PostgreSQL database
helm install postgres bitnami/postgresql \
    --namespace postgres \
    --values database/postgres-values.yaml \
    --wait --timeout 10m
```

### Step 5: Deploy Control Plane
```bash  
# Deploy Kong Control Plane
helm install kong-cp kong/kong \
    --namespace kong \
    --values control-plane/values-cp.yaml \
    --wait --timeout 10m
```

### Step 6: Run Database Migrations
```bash
# Bootstrap the database
kubectl exec -n kong deployment/kong-cp-kong -- kong migrations bootstrap
```

### Step 7: Deploy Data Plane
```bash
# Deploy Kong Data Plane  
helm install kong-dp kong/kong \
    --namespace kong \
    --values data-plane/values-dp.yaml \
    --wait --timeout 10m
```

### Step 8: Verify Deployment
```bash
# Check pod status
kubectl get pods -n kong
kubectl get pods -n postgres

# Test Control Plane
kubectl port-forward -n kong svc/kong-cp-kong-admin 8001:8001 &
curl http://localhost:8001/clustering/status

# Test Data Plane
kubectl port-forward -n kong svc/kong-dp-kong-proxy 8000:80 &
curl http://localhost:8000/
```

## Custom Plugins

This setup includes support for custom plugins alongside bundled ones.

### Available Bundled Plugins
Kong OSS includes these bundled plugins:
- **Authentication**: `key-auth`, `oauth2`, `jwt`, `ldap-auth`, `basic-auth`
- **Security**: `cors`, `ip-restriction`, `bot-detection`
- **Traffic Control**: `rate-limiting`, `proxy-cache`, `request-size-limiting`
- **Transformations**: `request-transformer`, `response-transformer`
- **Analytics**: `prometheus`, `datadog`, `statsd`, `file-log`
- **Utilities**: `correlation-id`, `request-id`

### Custom Plugin Development

#### Example: API Version Plugin
The included API Version plugin demonstrates custom plugin development:

```bash
# Create ConfigMap for the plugin
kubectl create configmap kong-plugin-api-version \
    --from-file=handler.lua=custom-plugins/api-version/kong/plugins/api-version/handler.lua \
    --from-file=schema.lua=custom-plugins/api-version/kong/plugins/api-version/schema.lua \
    -n kong
```

#### Plugin Structure
```
custom-plugins/api-version/
├── kong/plugins/api-version/
│   ├── handler.lua      # Plugin logic and execution phases  
│   └── schema.lua       # Configuration schema
├── README.md           # Plugin documentation
└── *.rockspec         # LuaRocks package specification
```

#### Plugin Development Workflow
1. **Design**: Define plugin requirements and configuration schema
2. **Implement**: Write handler.lua with plugin logic
3. **Test**: Use Pongo for testing (recommended)
4. **Package**: Create ConfigMap or custom image
5. **Deploy**: Add to Kong configuration
6. **Verify**: Test plugin functionality

#### Adding Custom Plugins

**Method 1: ConfigMap (Development)**
```bash
# Create ConfigMap
kubectl create configmap kong-plugin-<name> \
    --from-file=handler.lua=path/to/handler.lua \
    --from-file=schema.lua=path/to/schema.lua \
    -n kong

# Update values to include plugin
# Add to env.plugins: "bundled,<plugin-name>"
```

**Method 2: Custom Image (Production)**
```dockerfile
FROM kong/kong-gateway:3.11
COPY custom-plugins/ /opt/kong/plugins/
USER kong
```

### Plugin Configuration Examples
See `examples/plugin-examples.yaml` for detailed plugin configurations.

## Configuration Management

### Service and Route Configuration

#### Using Kong CRDs
```yaml
apiVersion: configuration.konghq.com/v1
kind: KongService  
metadata:
  name: httpbin-service
  namespace: kong
spec:
  protocol: http
  host: httpbin.example.svc.cluster.local
  port: 80
```

#### Using Kubernetes Ingress
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: httpbin-ingress
  annotations:
    kubernetes.io/ingress.class: kong
    konghq.com/plugins: rate-limiting,cors
spec:
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: httpbin
            port:
              number: 80
```

### Plugin Configuration
```yaml
apiVersion: configuration.konghq.com/v1
kind: KongPlugin
metadata:
  name: rate-limiting
plugin: rate-limiting
config:
  minute: 100
  hour: 1000
  policy: local
```

### Consumer Management
```yaml  
apiVersion: configuration.konghq.com/v1
kind: KongConsumer
metadata:
  name: api-user
username: api-user
custom_id: "12345"
```

## Monitoring & Observability

### Prometheus Integration
Deploy Prometheus to collect Kong metrics:

```bash
# Deploy Prometheus
helm install prometheus prometheus-community/prometheus \
    --namespace monitoring --create-namespace \
    --values monitoring/prometheus-values.yaml
```

### Available Metrics
- `kong_http_requests_total`: Total HTTP requests
- `kong_latency_bucket`: Request latency histogram
- `kong_bandwidth_bytes`: Bandwidth usage
- `kong_database_connections`: Database connection pool
- `kong_memory_lua_shared_dict_bytes`: Memory usage

### Grafana Dashboard
Import the provided dashboard from `monitoring/kong-dashboard.json`.

### Logging
Configure structured logging:
```yaml
# In values files
env:
  log_level: notice
  proxy_access_log: /dev/stdout
  admin_access_log: /dev/stdout
```

## Production Considerations

### High Availability

#### Control Plane HA
```yaml
# In values-cp.yaml
deployment:
  replicaCount: 3

affinity:
  podAntiAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
    - labelSelector:
        matchLabels:
          app.kubernetes.io/name: kong
      topologyKey: kubernetes.io/hostname
```

#### Database HA
```yaml
# In postgres-values.yaml  
architecture: replication
readReplicas:
  replicaCount: 2
```

#### Data Plane Scaling
```yaml
# In values-dp.yaml
autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
```

### Security

#### Network Policies
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: kong-network-policy
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/name: kong
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: kong
    ports:
    - protocol: TCP
      port: 8000
```

#### RBAC
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: kong-admin
rules:
- apiGroups: ["configuration.konghq.com"]  
  resources: ["*"]
  verbs: ["*"]
```

### Performance Tuning

#### Resource Allocation
```yaml  
# Control Plane
resources:
  requests:
    cpu: 500m
    memory: 1Gi
  limits:
    cpu: 2000m
    memory: 2Gi

# Data Plane  
resources:
  requests:
    cpu: 1000m
    memory: 1Gi
  limits:
    cpu: 2000m
    memory: 2Gi
```

#### Kong Configuration
```yaml
env:
  nginx_worker_processes: "auto"
  nginx_worker_connections: "1024"
  upstream_keepalive_requests: "100"
  upstream_keepalive_timeout: "60s"
```

### Storage

#### Persistent Volumes
```yaml
# PostgreSQL storage
primary:
  persistence:
    enabled: true
    storageClass: "ssd"
    size: 100Gi
```

## Troubleshooting

### Common Issues

#### 1. CP/DP Connection Problems
**Symptoms**: Data planes can't connect to control plane
```bash
# Check logs
kubectl logs -n kong deployment/kong-cp-kong
kubectl logs -n kong deployment/kong-dp-kong

# Verify certificates
kubectl exec -n kong deployment/kong-dp-kong -- ls -la /etc/secrets/kong-cluster-cert/

# Test connectivity
kubectl exec -n kong deployment/kong-dp-kong -- \
  curl -k https://kong-cp-kong-cluster.kong.svc.cluster.local:8005
```

#### 2. Database Connection Issues  
**Symptoms**: Control plane can't connect to database
```bash
# Check database status
kubectl get pods -n postgres

# Test connection
kubectl exec -n kong deployment/kong-cp-kong -- \
  kong migrations status
```

#### 3. Plugin Loading Issues
**Symptoms**: Plugins not loading or working
```bash
# Check plugin configuration
kubectl exec -n kong deployment/kong-cp-kong -- kong config

# Verify custom plugins
kubectl get configmap kong-plugin-api-version -n kong -o yaml
```

### Debug Commands

#### Cluster Status
```bash
# Check cluster health
curl http://localhost:8001/clustering/status

# List data plane nodes
curl http://localhost:8001/clustering/data-planes
```

#### Configuration Inspection
```bash
# List services
curl http://localhost:8001/services

# List routes
curl http://localhost:8001/routes

# List plugins
curl http://localhost:8001/plugins
```

#### Performance Analysis
```bash
# Check memory usage
kubectl top pods -n kong

# Check resource utilization
kubectl describe pod <pod-name> -n kong
```

### Health Checks

#### Control Plane Health
```bash
curl http://localhost:8001/status
```

#### Data Plane Health  
```bash
curl http://localhost:8100/status
```

## Testing the Setup

### Basic Functionality Test
```bash
# 1. Create test service
curl -X POST http://localhost:8001/services \
  --data "name=httpbin" \  
  --data "url=http://httpbin.org"

# 2. Create test route
curl -X POST http://localhost:8001/services/httpbin/routes \
  --data "paths[]=/test"

# 3. Test proxy
curl http://localhost:8000/test/get
```

### Plugin Test
```bash
# Enable rate limiting
curl -X POST http://localhost:8001/services/httpbin/plugins \
  --data "name=rate-limiting" \
  --data "config.minute=5"

# Test rate limiting
for i in {1..10}; do
  curl http://localhost:8000/test/get
done
```

### Load Testing  
```bash
# Using Apache Bench
ab -n 1000 -c 10 http://localhost:8000/test/get

# Using curl in loop
for i in {1..100}; do
  curl -w "%{time_total}\n" -o /dev/null -s http://localhost:8000/test/get
done
```

## Updating Kong

### Update Control Plane
```bash
# Update Control Plane first
helm upgrade kong-cp kong/kong \
  --namespace kong \
  --values control-plane/values-cp.yaml

# Run migrations if needed
kubectl exec -n kong deployment/kong-cp-kong -- kong migrations up
```

### Update Data Plane
```bash
# Update Data Plane after CP
helm upgrade kong-dp kong/kong \
  --namespace kong \
  --values data-plane/values-dp.yaml
```

## Cleanup

### Remove Kong Deployment
```bash
# Run cleanup script
./scripts/cleanup.sh

# Or manual cleanup
helm uninstall kong-dp -n kong
helm uninstall kong-cp -n kong  
helm uninstall postgres -n postgres
kubectl delete namespace kong postgres
```

## Next Steps

1. **Configure DNS**: Set up proper DNS for external access
2. **SSL Certificates**: Use cert-manager for automatic SSL
3. **CI/CD Integration**: Automate deployments with GitOps
4. **Backup Strategy**: Implement database backup procedures  
5. **Monitoring Alerts**: Set up alerting for critical metrics
6. **Documentation**: Document your specific configuration

## Resources

- [Kong Documentation](https://docs.konghq.com/)
- [Kong Kubernetes Deployment](https://docs.konghq.com/kubernetes-ingress-controller/)
- [Kong Plugin Development](https://docs.konghq.com/gateway/latest/plugin-development/)
- [Kong Helm Charts](https://github.com/Kong/charts)
- [Kong Community Forum](https://discuss.konghq.com/)

---

This deployment guide provides everything needed for a production-ready Kong OSS hybrid mode setup on Kubernetes with custom plugin support.
