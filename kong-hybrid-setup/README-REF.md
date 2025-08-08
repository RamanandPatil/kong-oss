# Kong OSS Hybrid Mode Deployment - Complete Setup Guide

I've created a comprehensive, production-ready Kong OSS hybrid mode deployment setup for Kubernetes using Helm charts. This setup includes everything you need for local development and production deployment.

## What You Get

### 🏗️ **Complete Hybrid Architecture**
- **Control Plane (CP)**: Manages configuration, Admin API, Kong Manager, database connectivity
- **Data Plane (DP)**: Handles traffic proxying, plugin execution, load balancing  
- **mTLS Communication**: Secure certificate-based communication between CP and DP
- **PostgreSQL Database**: Persistent storage with high availability options

### 🔌 **Bundled + Custom Plugin Support**
- **All Kong OSS Plugins**: Rate limiting, CORS, authentication, transformations, caching, monitoring
- **Custom Plugin Framework**: Complete API Version plugin example with Lua implementation
- **Multi-Language Support**: Lua, Go, Python, JavaScript plugin development
- **Easy Integration**: ConfigMap and custom image deployment methods

### 📊 **Production Features**
- **High Availability**: Multi-replica deployments with pod anti-affinity
- **Auto-Scaling**: HPA configuration for data planes based on CPU/memory
- **Monitoring**: Prometheus metrics collection with Grafana dashboard
- **Security**: RBAC, security contexts, network policies ready
- **Certificate Management**: Automated SSL/TLS certificate generation

## 📁 Project Structure

The complete setup includes:

```
kong-hybrid-setup/
├── README.md & DEPLOYMENT_GUIDE.md     # Complete documentation
├── certificates/generate-certs.sh      # SSL certificate generation
├── control-plane/values-cp.yaml        # CP Helm configuration
├── data-plane/values-dp.yaml          # DP Helm configuration  
├── database/postgres-values.yaml       # PostgreSQL setup
├── custom-plugins/api-version/         # Sample custom plugin
├── scripts/setup.sh                   # One-command deployment
├── monitoring/prometheus-values.yaml   # Monitoring setup
└── examples/                          # Service & plugin examples
```

## 🚀 Quick Start

1. **Prerequisites**: Kubernetes cluster, Helm 3.0+, kubectl

2. **Deploy Everything**:
   ```bash
   ./scripts/setup.sh
   ```

3. **Access Services**:
   ```bash
   # Kong Proxy (Data Plane)
   kubectl port-forward -n kong svc/kong-dp-kong-proxy 8000:80
   
   # Admin API (Control Plane)
   kubectl port-forward -n kong svc/kong-cp-kong-admin 8001:8001
   
   # Kong Manager GUI
   kubectl port-forward -n kong svc/kong-cp-kong-manager 8002:8002
   ```

## 🛠️ Key Features

### **Hybrid Mode Benefits**[1][2][3]
- **Database Independence**: Data planes don't need database connections
- **Deployment Flexibility**: Deploy DPs in different clusters/regions
- **High Availability**: CP failure doesn't affect DP traffic handling
- **Reduced Database Load**: Only CPs connect to database
- **Enhanced Security**: Compromised DP can't affect other nodes

### **Custom Plugin Development**[4][5][6]
The setup includes a complete API Version plugin example that demonstrates:
- Plugin handler phases (access, header_filter, body_filter, log)
- Configuration schema with validation
- Request/response transformation
- Logging and metrics integration

### **Production Readiness**
- **Resource Management**: Proper CPU/memory limits and requests
- **Scaling**: Horizontal Pod Autoscaler with custom metrics
- **Security**: Pod security contexts, RBAC configuration
- **Monitoring**: Prometheus scraping with alert rules
- **Persistence**: PostgreSQL with persistent volumes

## 📋 What's Included

### **Kong Components**
- ✅ Control Plane with Admin API and Kong Manager
- ✅ Multiple Data Plane replicas with auto-scaling
- ✅ PostgreSQL database with persistence
- ✅ mTLS certificates for secure CP/DP communication

### **Custom Plugins**
- ✅ API Version plugin (complete Lua implementation)
- ✅ Plugin development templates and examples
- ✅ ConfigMap and custom image deployment methods
- ✅ LuaRocks packaging configuration

### **Monitoring & Operations**
- ✅ Prometheus metrics collection
- ✅ Grafana dashboard for Kong metrics
- ✅ Health checks and liveness probes  
- ✅ Automated deployment and cleanup scripts

### **Examples & Documentation**
- ✅ Service and route configurations
- ✅ Plugin configuration examples (rate limiting, CORS, auth)
- ✅ Consumer management examples
- ✅ Comprehensive deployment guide

## 🌟 Advanced Features

### **Multi-Language Plugin Support**[5][7]
- **Lua**: Native Kong plugin development (included example)
- **Go**: External process with Kong Go PDK
- **Python**: Kong Python PDK integration  
- **JavaScript**: Kong JS PDK support

### **Kubernetes Integration**
- **CRDs**: KongService, KongRoute, KongPlugin, KongConsumer
- **Ingress Controller**: Standard Kubernetes ingress support
- **Service Discovery**: Automatic upstream service registration
- **ConfigMaps/Secrets**: Secure configuration management

### **Enterprise-Grade Features**
- **Load Balancing**: Multiple algorithms (round-robin, least-connections, etc.)
- **Health Checks**: Active and passive upstream health monitoring
- **Caching**: Proxy caching with memory and Redis backends
- **Rate Limiting**: Multiple strategies (local, cluster, Redis)
- **Authentication**: Multiple methods (key-auth, OAuth2, JWT, LDAP)

This setup provides everything needed to run Kong OSS in hybrid mode locally for development and scale it to production environments. The included automation scripts make deployment simple while the comprehensive configuration supports advanced enterprise use cases.

The project is immediately ready to run - simply execute the setup script and you'll have a fully functional Kong hybrid deployment with custom plugin support!

## References:
[1] https://blog.jwconsult.in/kong-gateway-in-hybrid-mode-using-helm
[2] https://docs.jp.konghq.com/gateway/latest/production/deployment-topologies/hybrid-mode/
[3] https://docs.jp.konghq.com/gateway/latest/production/deployment-topologies/hybrid-mode/setup/
[4] https://dev.to/zelar/kong-plugin-development-local-development-and-installation-on-your-laptopvm-dbp
[5] https://developer.konghq.com/custom-plugins/
[6] https://dev.to/zelar/installing-custom-plugins-in-kong-api-gateway-on-kubernetes-helm-deployment-in-hybrid-mode-3552
[7] https://docs.konghq.com/gateway/latest/plugin-development/pluginserver/go/
[8] https://konghq.com/blog/engineering/separating-data-control-planes
[9] https://developer.konghq.com/gateway/deployment-topologies/
[10] https://github.com/Kong/kong-data-plane-spec
[11] https://blog.zelarsoft.com/kong-hybrid-mode-deployment-gke-and-on-prem-2b83a5152b6
[12] https://blog.zelarsoft.com/deploy-kong-gateway-in-hybrid-mode-using-helm-chart-with-self-signed-certificates-on-aks-78fcfff4813c
[13] https://stackoverflow.com/questions/71191596/kongs-control-plane-data-plane-mapping
[14] https://developer.konghq.com/operator/dataplanes/get-started/hybrid/install/
[15] https://konghq.com/blog/learning-center/control-plane-vs-data-plane
[16] https://dev.to/zelar/kong-hybrid-mode-deployment-gke-and-on-prem-j32
[17] https://www.youtube.com/watch?v=fi-3T6AS5tY
[18] https://konghq.com/blog/product-releases/incremental-config-sync-tech-preview
[19] https://developer.konghq.com/gateway-manager/data-plane-reference/
[20] https://discuss.konghq.com/t/pros-cons-of-kong-in-hybrid-mode/6968
[21] https://developer.konghq.com/gateway/cp-dp-communication/
[22] https://developer.konghq.com/gateway/hybrid-mode/
[23] https://developer.konghq.com/gateway-manager/control-plane-groups/
[24] https://github.com/Kong/kong/discussions/9167
[25] https://github.com/Kong/charts
[26] https://discuss.konghq.com/t/where-is-the-default-values-yml-for-the-helm-chart-install-of-kong/12769
[27] https://www.cloudthat.com/resources/blog/kong-gateway-on-openshift-cluster-using-helm
[28] https://developer.konghq.com/gateway/install/kubernetes/konnect/
[29] https://gerrit.o-ran-sc.org/r/gitweb?p=ric-plt%2Fric-dep.git%3Bhb%3Drefs%2Fchanges%2F24%2F3824%2F3%3Bf%3Dhelm%2Finfrastructure%2Fsubcharts%2Fkong%2Fvalues.yaml
[30] https://www.youtube.com/watch?v=xbFXvNUtfFQ
[31] https://git.app.uib.no/caleno/helm-charts/-/blob/052c2882e92f180b4bf41ac5da05e0527e5d6fe4/stable/kong/values.yaml
[32] https://www.youtube.com/watch?v=lYm912ANi_E
[33] https://artifacthub.io/packages/helm/kong/kong
[34] https://artifacthub.io/packages/helm/kong/kong/2.4.0
[35] https://developer.konghq.com/kubernetes-ingress-controller/install/
[36] https://developer.konghq.com/mesh/production-usage-values/
[37] https://artifacthub.io/packages/helm/kong/ingress
[38] https://developer.konghq.com/kubernetes-ingress-controller/faq/upgrading-gateway/
[39] https://bitnami.com/stack/kong/helm
[40] https://github.com/Kong/kong-plugin/blob/master/kong/plugins/myplugin/handler.lua
[41] https://www.nylas.com/blog/building-custom-plugins-for-kong-api-gateway-dev/
[42] https://konghq.com/blog/engineering/custom-lua-plugin-kong-gateway
[43] https://www.youtube.com/watch?v=RfgpqY6CVhw
[44] https://github.com/Kong/kong/discussions/9147
[45] https://github.com/Kong/kong-plugin
[46] https://developer.konghq.com/custom-plugins/reference/
[47] https://konghq.com/blog/engineering/lua-custom-plugin-best-practices
[48] https://developer.konghq.com/custom-plugins/handler.lua/
[49] https://discuss.konghq.com/t/custom-plugin-using-admin-api-in-hybrid-mode/8922
[50] https://github.com/Kong/kong/discussions/13755
[51] https://blog.zelarsoft.com/tagged/kong-plugin-development
[52] https://github.com/Intility/local-kong-guide
[53] https://konghq.com/blog/engineering/set-up-kong-gateway
[54] https://github.com/giantswarm/kong-app/blob/master/helm/kong-app/README.md
[55] https://dev.to/deepanshup04/the-ultimate-guide-to-installing-kong-gateway-on-docker-kubernetes-and-linux-4kbk
[56] https://developer.konghq.com/gateway/get-started/
[57] https://blog.searce.com/api-management-on-kubernetes-simplified-discover-kongs-db-less-ingress-controller-e2f32d6047ae
[58] https://shurutech.com/complete-guide-to-setting-up-kong-api-gateway/
[59] https://cloud.theodo.com/en/blog/kong-apigateway-kubernetes
[60] https://konghq.com/blog/engineering/kubernetes-ingress-api-gateway
[61] https://www.youtube.com/watch?v=McwNOyK1dQI
[62] https://konghq.com/resources/videos/docker-app-kubernetes-ingress-controller
[63] https://konghq.com/blog/engineering/kong-gateway-tutorial
[64] https://docs.konghq.com/mesh/latest/quickstart/kubernetes-demo/
[65] https://discuss.konghq.com/t/switch-to-kong-api-steps-to-make-it-production-ready/4905
[66] https://www.youtube.com/watch?v=6jEFc77IpaA
[67] https://developer.konghq.com/gateway/install/
[68] https://developer.konghq.com/mesh/kubernetes/
[69] https://developer.konghq.com/gateway/install/kubernetes/on-prem/
[70] https://support.konghq.com/support/s/article/How-to-enable-Data-Plane-Resilience-when-using-helm
[71] https://discuss.konghq.com/t/kong-hybrid-mode-for-kubernetes/9052
[72] https://developer.konghq.com/mesh/cp-config/
[73] https://artifacthub.io/packages/helm/kong/kong/2.6.2
[74] https://registry.terraform.io/modules/Kong/kong-gateway/kubernetes/latest/examples/hybrid?tab=inputs