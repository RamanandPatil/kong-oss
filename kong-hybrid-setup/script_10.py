# Create example configurations
service_route_example = """# service-and-route.yaml - Example Kong Service and Route Configuration
# This creates a basic service and route for testing

apiVersion: v1
kind: Namespace
metadata:
  name: example
---
# Sample backend service
apiVersion: apps/v1
kind: Deployment
metadata:
  name: httpbin
  namespace: example
  labels:
    app: httpbin
spec:
  replicas: 2
  selector:
    matchLabels:
      app: httpbin
  template:
    metadata:
      labels:
        app: httpbin
    spec:
      containers:
      - name: httpbin
        image: kennethreitz/httpbin:latest
        ports:
        - containerPort: 80
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 200m
            memory: 256Mi
---
apiVersion: v1
kind: Service
metadata:
  name: httpbin
  namespace: example
  labels:
    app: httpbin
spec:
  selector:
    app: httpbin
  ports:
  - port: 80
    targetPort: 80
    protocol: TCP
  type: ClusterIP
---
# Kong Service configuration
apiVersion: configuration.konghq.com/v1
kind: KongService
metadata:
  name: httpbin-service
  namespace: kong
  annotations:
    kubernetes.io/ingress.class: kong
spec:
  protocol: http
  host: httpbin.example.svc.cluster.local
  port: 80
  path: /
  connect_timeout: 60000
  write_timeout: 60000
  read_timeout: 60000
  retries: 5
---
# Kong Route configuration
apiVersion: configuration.konghq.com/v1
kind: KongRoute
metadata:
  name: httpbin-route
  namespace: kong
  annotations:
    kubernetes.io/ingress.class: kong
spec:
  service_name: httpbin-service
  protocols:
  - http
  - https
  methods:
  - GET
  - POST
  - PUT
  - DELETE
  paths:
  - /httpbin
  strip_path: true
  preserve_host: false
  regex_priority: 0
---
# Alternative: Using standard Kubernetes Ingress
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: httpbin-ingress
  namespace: example
  annotations:
    kubernetes.io/ingress.class: kong
    konghq.com/strip-path: "true"
    konghq.com/preserve-host: "false"
spec:
  rules:
  - host: api.local  # Change to your domain
    http:
      paths:
      - path: /httpbin
        pathType: Prefix
        backend:
          service:
            name: httpbin
            port:
              number: 80
"""

plugin_examples = """# plugin-examples.yaml - Kong Plugin Configurations
# This file contains examples of various Kong plugin configurations

---
# Rate Limiting Plugin
apiVersion: configuration.konghq.com/v1
kind: KongPlugin
metadata:
  name: rate-limiting-example
  namespace: kong
  annotations:
    kubernetes.io/ingress.class: kong
plugin: rate-limiting
config:
  minute: 100
  hour: 1000
  policy: local
  hide_client_headers: false
---
# CORS Plugin  
apiVersion: configuration.konghq.com/v1
kind: KongPlugin
metadata:
  name: cors-example
  namespace: kong
  annotations:
    kubernetes.io/ingress.class: kong
plugin: cors
config:
  origins:
  - http://localhost:3000
  - https://example.com
  methods:
  - GET
  - POST
  - PUT
  - DELETE
  - OPTIONS
  headers:
  - Accept
  - Accept-Version
  - Content-Length
  - Content-MD5
  - Content-Type
  - Date
  - X-Auth-Token
  - Authorization
  exposed_headers:
  - X-Auth-Token
  credentials: true
  max_age: 3600
  preflight_continue: false
---
# Key Authentication Plugin
apiVersion: configuration.konghq.com/v1
kind: KongPlugin
metadata:
  name: key-auth-example
  namespace: kong
  annotations:
    kubernetes.io/ingress.class: kong
plugin: key-auth
config:
  key_names:
  - apikey
  - x-api-key
  key_in_body: false
  key_in_header: true
  key_in_query: true
  hide_credentials: true
  anonymous: ""
  run_on_preflight: true
---
# Prometheus Plugin
apiVersion: configuration.konghq.com/v1
kind: KongPlugin
metadata:
  name: prometheus-example
  namespace: kong
  annotations:
    kubernetes.io/ingress.class: kong
plugin: prometheus
config:
  per_consumer: true
  status_code_metrics: true
  latency_metrics: true
  bandwidth_metrics: true
  upstream_health_metrics: true
---
# Request Transformer Plugin
apiVersion: configuration.konghq.com/v1
kind: KongPlugin
metadata:
  name: request-transformer-example
  namespace: kong
  annotations:
    kubernetes.io/ingress.class: kong
plugin: request-transformer
config:
  remove:
    headers:
    - x-toremove
    querystring:
    - param-to-remove
  rename:
    headers:
    - old-name:new-name
  replace:
    headers:
    - "x-forwarded-for:$(X-Real-IP)"
  add:
    headers:
    - "x-new-header:value"
    - "x-another-header:$(X-Consumer-ID)"
    querystring:
    - "new-param:value"
  append:
    headers:
    - "x-forwarded-host:$(host)"
---
# Response Transformer Plugin
apiVersion: configuration.konghq.com/v1
kind: KongPlugin
metadata:
  name: response-transformer-example
  namespace: kong
  annotations:
    kubernetes.io/ingress.class: kong
plugin: response-transformer
config:
  remove:
    headers:
    - x-toremove
    json:
    - key-to-remove
  rename:
    headers:
    - old-name:new-name
  replace:
    headers:
    - "x-forwarded-for:$(X-Real-IP)"
  add:
    headers:
    - "x-new-header:value"
    - "x-processed-by:kong-gateway"
    json:
    - "new-field:value"
  append:
    headers:
    - "x-server:kong"
---
# Custom API Version Plugin
apiVersion: configuration.konghq.com/v1
kind: KongPlugin
metadata:
  name: api-version-example
  namespace: kong
  annotations:
    kubernetes.io/ingress.class: kong
plugin: api-version
config:
  version: "2.1.0"
  add_server_header: true
  add_timestamp: true
  modify_body: false
  log_version: true
  enable_logging: false
  custom_header_name: "X-API-Version"
  header_prefix: "v"
---
# Proxy Caching Plugin
apiVersion: configuration.konghq.com/v1
kind: KongPlugin
metadata:
  name: proxy-cache-example
  namespace: kong
  annotations:
    kubernetes.io/ingress.class: kong
plugin: proxy-cache
config:
  response_code: 
  - 200
  - 301
  - 404
  request_method:
  - GET
  - HEAD
  content_type:
  - text/plain
  - application/json
  cache_ttl: 300
  strategy: memory
  cache_control: false
  storage_ttl: 3600
---
# IP Restriction Plugin
apiVersion: configuration.konghq.com/v1
kind: KongPlugin
metadata:
  name: ip-restriction-example
  namespace: kong
  annotations:
    kubernetes.io/ingress.class: kong
plugin: ip-restriction
config:
  allow:
  - 10.0.0.0/8
  - 192.168.0.0/16
  - 172.16.0.0/12
  deny:
  - 192.168.1.100
  status: 403
  message: "Access denied"
---
# Consumer for Key Authentication
apiVersion: configuration.konghq.com/v1
kind: KongConsumer
metadata:
  name: example-consumer
  namespace: kong
  annotations:
    kubernetes.io/ingress.class: kong
username: example-user
custom_id: "12345"
---
# Consumer Credentials Secret for Key Auth
apiVersion: v1
kind: Secret
metadata:
  name: example-consumer-key-auth
  namespace: kong
  labels:
    konghq.com/credential: key-auth
stringData:
  kongCredType: key-auth
  key: my-secret-key-123
---
# Apply plugins to service using annotations
# Add this annotation to your service:
# konghq.com/plugins: rate-limiting-example,cors-example,prometheus-example

# Apply plugins to ingress using annotations  
# Add this annotation to your ingress:
# konghq.com/plugins: key-auth-example,api-version-example
"""

# Write example files
with open("kong-hybrid-setup/examples/service-and-route.yaml", "w") as f:
    f.write(service_route_example)

with open("kong-hybrid-setup/examples/plugin-examples.yaml", "w") as f:
    f.write(plugin_examples)

print("Example configuration files created:")
print("- service-and-route.yaml: Example service and route setup") 
print("- plugin-examples.yaml: Various Kong plugin configurations")