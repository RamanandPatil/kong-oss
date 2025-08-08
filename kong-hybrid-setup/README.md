# Kong OSS Hybrid Mode Deployment on Kubernetes

This repository provides a complete, production-ready setup for Kong OSS Gateway in hybrid mode using Kubernetes and Helm charts.

## Architecture Overview

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   Control Plane     │    │    Data Plane 1     │    │    Data Plane 2     │
│  (Configuration)    │◄──►│     (Traffic)       │    │     (Traffic)       │
│                     │    │                     │    │                     │
│ - Admin API         │    │ - Proxy Service     │    │ - Proxy Service     │
│ - Kong Manager      │    │ - Plugin Execution  │    │ - Plugin Execution  │
│ - Database          │    │ - Load Balancing    │    │ - Load Balancing    │
│ - Configuration     │    │                     │    │                     │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
```

## Features

- ✅ **Production-Ready**: Complete hybrid mode setup with SSL/TLS
- ✅ **Custom Plugins**: Support for bundled and custom plugins
- ✅ **High Availability**: Multiple data plane instances
- ✅ **Monitoring**: Prometheus metrics and observability
- ✅ **Security**: mTLS communication between CP and DP
- ✅ **Database**: PostgreSQL with persistence
- ✅ **Local Development**: Ready-to-run on local Kubernetes

## Quick Start

1. **Prerequisites**
   ```bash
   # Required tools
   kubectl
   helm
   minikube/kind/k3s (for local development)
   ```

2. **Setup Cluster**
   ```bash
   # For local development with minikube
   minikube start --cpus=4 --memory=8192 --disk-size=20g

   # Or with kind
   kind create cluster --name kong-hybrid
   ```

3. **Deploy Kong Hybrid**
   ```bash
   # Clone and navigate
   cd kong-hybrid-setup

   # Run the setup script
   ./scripts/setup.sh
   ```

4. **Access Services**
   ```bash
   # Kong Proxy (Data Plane)
   kubectl port-forward -n kong svc/kong-dp-kong-proxy 8000:80

   # Kong Admin API (Control Plane)  
   kubectl port-forward -n kong svc/kong-cp-kong-admin 8001:8001

   # Kong Manager GUI
   kubectl port-forward -n kong svc/kong-cp-kong-manager 8002:8002
   ```

## Directory Structure

```
kong-hybrid-setup/
├── README.md                          # This file
├── certificates/                      # SSL/TLS certificates
│   └── generate-certs.sh             # Certificate generation script
├── control-plane/                    # Control Plane configuration
│   └── values-cp.yaml                # CP Helm values
├── data-plane/                       # Data Plane configuration  
│   └── values-dp.yaml                # DP Helm values
├── custom-plugins/                   # Custom plugin development
│   └── api-version/                  # Sample custom plugin
├── database/                         # Database setup
│   └── postgres-values.yaml         # PostgreSQL configuration
├── scripts/                          # Automation scripts
│   ├── setup.sh                      # Complete setup script
│   ├── deploy-cp.sh                  # Deploy Control Plane
│   ├── deploy-dp.sh                  # Deploy Data Plane
│   └── cleanup.sh                    # Cleanup script
├── monitoring/                       # Monitoring setup
│   └── prometheus-values.yaml       # Prometheus configuration
└── examples/                         # Usage examples
    ├── service-and-route.yaml       # Basic service/route
    └── plugin-examples.yaml        # Plugin configurations
```

## Components

### 1. Control Plane (CP)
- **Kong Admin API**: Configuration management
- **Kong Manager**: Web GUI for administration
- **Database**: PostgreSQL for storing configurations
- **Certificates**: Manages mTLS for CP/DP communication

### 2. Data Plane (DP)
- **Kong Proxy**: Handles actual traffic
- **Plugin Execution**: Runs bundled and custom plugins
- **Load Balancing**: Distributes traffic to upstreams
- **Health Checks**: Monitors upstream services

### 3. Custom Plugins
- **Bundled Plugins**: All Kong OSS plugins available
- **Custom Plugins**: Your own Lua/Go/Python/JS plugins
- **Plugin Development**: Templates and examples

## Configuration

### Bundled Plugins Available
- Authentication: `key-auth`, `oauth2`, `jwt`, `ldap-auth`
- Security: `cors`, `ip-restriction`, `rate-limiting` 
- Traffic Control: `proxy-cache`, `request-transformer`
- Analytics: `prometheus`, `datadog`, `statsd`
- And many more...

### Custom Plugin Support
This setup supports custom plugins in multiple languages:
- **Lua**: Native Kong plugin development
- **Go**: Using Kong Go PDK
- **Python**: Using Kong Python PDK  
- **JavaScript**: Using Kong JS PDK

## Networking

### Ports Configuration
- **8000**: Kong Proxy (HTTP)
- **8443**: Kong Proxy (HTTPS) 
- **8001**: Kong Admin API
- **8444**: Kong Admin API (HTTPS)
- **8002**: Kong Manager
- **8005**: Control Plane Cluster (CP/DP Communication)
- **8006**: Control Plane Telemetry

### Service Mesh Integration
Kong can be integrated with service meshes:
- **Istio**: Using Kong as ingress gateway
- **Linkerd**: Traffic management integration
- **Consul Connect**: Service discovery integration

## Production Considerations

### High Availability
- Multiple Control Plane replicas
- Multiple Data Plane replicas across zones
- Database clustering with read replicas

### Security  
- mTLS between CP and DP
- RBAC for Admin API access
- Network policies for pod communication
- Secrets management with Kubernetes secrets

### Monitoring
- Prometheus metrics collection
- Grafana dashboards
- Alerting rules for critical events
- Distributed tracing with Jaeger/Zipkin

### Scaling
- Horizontal Pod Autoscaler (HPA) for data planes
- Vertical Pod Autoscaler (VPA) for resource optimization
- Cluster autoscaling for node management

## Troubleshooting

### Common Issues

1. **CP/DP Connection Issues**
   ```bash
   # Check cluster connectivity
   kubectl logs -n kong deployment/kong-cp-kong
   kubectl logs -n kong deployment/kong-dp-kong
   ```

2. **Plugin Loading Issues**
   ```bash
   # Check plugin configuration
   kubectl exec -n kong deployment/kong-cp-kong -- kong config
   ```

3. **Database Connection Issues**
   ```bash
   # Check database connectivity
   kubectl exec -n kong deployment/kong-cp-kong -- kong migrations status
   ```

### Debug Commands
```bash
# Check Kong configuration
kubectl exec -n kong deployment/kong-cp-kong -- kong config

# Check plugin status  
curl -s http://localhost:8001/plugins

# Check cluster status
curl -s http://localhost:8001/clustering/status

# Check data plane nodes
curl -s http://localhost:8001/clustering/data-planes
```

## Development Workflow

### Custom Plugin Development
1. Create plugin structure in `custom-plugins/`
2. Develop plugin logic (handler.lua, schema.lua)
3. Test with Kong development tools (Pongo)
4. Build custom Kong image with plugin
5. Deploy and test in local cluster

### Configuration Management
1. Update Helm values files
2. Apply changes using Helm upgrade
3. Verify deployment status
4. Test functionality

## Support

### Kong Community
- [Kong Nation](https://discuss.konghq.com/)
- [GitHub Issues](https://github.com/Kong/kong/issues)
- [Documentation](https://docs.konghq.com/)

### This Repository  
For issues with this setup, please create an issue in this repository.

## License

This project is licensed under the Apache 2.0 License - see the LICENSE file for details.
