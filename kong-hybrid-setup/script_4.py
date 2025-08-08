# Create Data Plane Helm values
dp_values = """# values-dp.yaml - Kong Data Plane Configuration
# This configures Kong Gateway as a Data Plane node in hybrid mode

# Image configuration  
image:
  repository: kong/kong-gateway
  tag: "3.11"
  pullPolicy: IfNotPresent
  # If using custom image with plugins, specify here:
  # repository: your-registry/kong-custom
  # tag: "3.11-with-plugins"

# Custom image pull secrets (if using private registry)
imagePullSecrets: []
# - name: your-registry-secret

# Deployment configuration
deployment:
  kong:
    enabled: true
  
  # Number of Data Plane replicas (scale as needed)
  replicaCount: 3
  
  # Update strategy
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 2
      maxUnavailable: 1

# Disable Kong Ingress Controller (can be enabled if needed)
ingressController:
  enabled: false

# Environment variables for Kong Data Plane
env:
  # Hybrid mode configuration
  role: data_plane
  database: "off"  # Data plane doesn't need database
  
  # Cluster certificates for mTLS
  cluster_cert: /etc/secrets/kong-cluster-cert/tls.crt
  cluster_cert_key: /etc/secrets/kong-cluster-cert/tls.key
  lua_ssl_trusted_certificate: /etc/secrets/kong-cluster-cert/tls.crt
  
  # Control Plane connection
  cluster_control_plane: "kong-cp-kong-cluster.kong.svc.cluster.local:8005"
  cluster_telemetry_endpoint: "kong-cp-kong-clustertelemetry.kong.svc.cluster.local:8006"
  
  # Proxy configuration
  proxy_listen: "0.0.0.0:8000, 0.0.0.0:8443 ssl"
  
  # Status API for health checks
  status_listen: "0.0.0.0:8100"
  
  # Plugin configuration (must match Control Plane)
  plugins: "bundled,api-version,custom-auth,request-logger"
  
  # Logging configuration
  log_level: notice
  proxy_access_log: /dev/stdout
  proxy_error_log: /dev/stderr
  
  # Performance tuning
  nginx_worker_processes: "auto" 
  nginx_worker_connections: "1024"
  
  # Memory cache settings
  mem_cache_size: "128m"
  
  # Upstream health checks
  upstream_keepalive_requests: "100"
  upstream_keepalive_timeout: "60s"

# Secret volumes for certificates and custom plugins
secretVolumes:
  - kong-cluster-cert
  - kong-proxy-cert
  # - kong-custom-plugins  # Uncomment if using custom plugins via ConfigMap

# Admin service (disabled for Data Plane)
admin:
  enabled: false

# Manager service (disabled for Data Plane)  
manager:
  enabled: false

# Cluster service (disabled for Data Plane)
cluster:
  enabled: false

# Cluster telemetry service (disabled for Data Plane)
clustertelemetry:
  enabled: false

# Portal service (disabled for OSS)
portal:
  enabled: false

# Portal API service (disabled for OSS)
portalapi:
  enabled: false

# Proxy service configuration
proxy:
  enabled: true
  type: LoadBalancer
  # Use ClusterIP for internal access, LoadBalancer for external
  # type: ClusterIP
  
  annotations: {}
  # For cloud providers, add LB annotations:
  # service.beta.kubernetes.io/aws-load-balancer-type: nlb
  # service.beta.kubernetes.io/azure-load-balancer-internal: "true"
  
  # HTTP proxy service
  http:
    enabled: true
    servicePort: 80
    containerPort: 8000
    # nodePort: 32000  # Set if using NodePort
    
  # HTTPS proxy service  
  tls:
    enabled: true
    servicePort: 443
    containerPort: 8443
    # nodePort: 32443  # Set if using NodePort
    overrideServiceTargetPort: 8443

  # Ingress for external access
  ingress:
    enabled: false
    # Enable if you want ingress for proxy
    # className: nginx
    # hostname: kong-proxy.local
    # annotations:
    #   nginx.ingress.kubernetes.io/ssl-redirect: "false"

# Status service for health checks and metrics
status:
  enabled: true
  http:
    enabled: true
    containerPort: 8100
    
# Resource limits and requests
resources:
  limits:
    cpu: 2000m
    memory: 2Gi
  requests:
    cpu: 500m
    memory: 512Mi

# Node affinity and pod anti-affinity for HA  
affinity:
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
    - weight: 100
      podAffinityTerm:
        labelSelector:
          matchExpressions:
          - key: app.kubernetes.io/name
            operator: In
            values:
            - kong
          - key: app.kubernetes.io/component
            operator: In
            values:
            - app
        topologyKey: kubernetes.io/hostname

# Health checks
readinessProbe:
  httpGet:
    path: "/status/ready"
    port: status
    scheme: HTTP
  initialDelaySeconds: 5
  timeoutSeconds: 5
  periodSeconds: 10
  successThreshold: 1
  failureThreshold: 3

livenessProbe:
  httpGet:
    path: "/status" 
    port: status
    scheme: HTTP
  initialDelaySeconds: 5
  timeoutSeconds: 5
  periodSeconds: 10
  successThreshold: 1
  failureThreshold: 3

# Pod Disruption Budget for HA
podDisruptionBudget:
  enabled: true
  maxUnavailable: 1

# Horizontal Pod Autoscaler
autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15

# Service Monitor for Prometheus
serviceMonitor:
  enabled: true
  labels: {}
  interval: 30s
  namespace: ""
  namespaceSelector: {}

# Annotations
podAnnotations:
  prometheus.io/scrape: "true"
  prometheus.io/port: "8100"
  prometheus.io/path: "/metrics"

# Security context
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  runAsGroup: 1000
  fsGroup: 1000

podSecurityContext:
  fsGroup: 1000
  runAsGroup: 1000
  runAsNonRoot: true
  runAsUser: 1000

# Additional volumes and volume mounts
extraVolumes: []
# - name: custom-plugin-volume
#   configMap:
#     name: kong-custom-plugins

extraVolumeMounts: []
# - name: custom-plugin-volume
#   mountPath: /opt/kong/plugins/custom
#   readOnly: true

# Migration jobs (disabled for Data Plane)
migrations:
  preUpgrade: false
  postUpgrade: false

# Enterprise features (disabled for OSS)
enterprise:
  enabled: false

# Custom plugins configuration  
plugins:
  configMaps: []
  # - pluginName: api-version
  #   name: kong-plugin-api-version
  secrets: []

# Topology Spread Constraints for better distribution
topologySpreadConstraints:
- maxSkew: 1
  topologyKey: kubernetes.io/hostname
  whenUnsatisfiable: DoNotSchedule
  labelSelector:
    matchLabels:
      app.kubernetes.io/name: kong
      app.kubernetes.io/component: app

# Pod priority class (optional)
# priorityClassName: high-priority

# Tolerations for specific node scheduling (optional)
tolerations: []
# - key: "dedicated"
#   operator: "Equal"
#   value: "kong"
#   effect: "NoSchedule"

# Node selector for specific node scheduling (optional)
nodeSelector: {}
# dedicated: kong

# Wait image (not needed for DP, but included for consistency)
waitImage:
  repository: busybox
  tag: latest
  pullPolicy: IfNotPresent

# Custom environment variables (for advanced configurations)
customEnv: {}
# KONG_UPSTREAM_KEEPALIVE_POOL_SIZE: "30"
# KONG_UPSTREAM_KEEPALIVE_MAX_REQUESTS: "100"

# Init containers (optional, for custom setup)
extraInitContainers: []
# - name: custom-init
#   image: busybox:latest
#   command: ['sh', '-c', 'echo "Custom initialization"']

# Sidecar containers (optional, for logging, monitoring)
extraContainers: []
# - name: log-shipper
#   image: fluent/fluent-bit:latest
#   # Configure log shipping
"""

with open("kong-hybrid-setup/data-plane/values-dp.yaml", "w") as f:
    f.write(dp_values)

print("Data Plane Helm values created!")