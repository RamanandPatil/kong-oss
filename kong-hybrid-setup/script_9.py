# Create monitoring configuration
prometheus_values = """# prometheus-values.yaml - Prometheus Configuration for Kong Monitoring
# This configures Prometheus to scrape metrics from Kong

# Server configuration
server:
  # Persistence  
  persistentVolume:
    enabled: true
    size: 10Gi
    storageClass: ""
  
  # Resource configuration
  resources:
    limits:
      cpu: 1000m
      memory: 2Gi
    requests:
      cpu: 250m
      memory: 512Mi
  
  # Data retention
  retention: "7d"
  
  # Global scrape configuration
  global:
    scrape_interval: 30s
    evaluation_interval: 30s
  
# Kong-specific scrape configurations
serverFiles:
  prometheus.yml:
    global:
      scrape_interval: 30s
      evaluation_interval: 30s
      
    rule_files:
      - "/etc/prometheus/rules/*.yml"
      
    scrape_configs:
      # Prometheus self-monitoring
      - job_name: 'prometheus'
        static_configs:
          - targets: ['localhost:9090']
          
      # Kong Control Plane metrics
      - job_name: 'kong-control-plane'
        static_configs:
          - targets: ['kong-cp-kong-admin.kong.svc.cluster.local:8100']
        metrics_path: '/metrics'
        scrape_interval: 30s
        
      # Kong Data Plane metrics  
      - job_name: 'kong-data-plane'
        kubernetes_sd_configs:
          - role: pod
            namespaces:
              names: ['kong']
        relabel_configs:
          - source_labels: [__meta_kubernetes_pod_label_app_kubernetes_io_name]
            action: keep
            regex: kong
          - source_labels: [__meta_kubernetes_pod_label_app_kubernetes_io_instance]
            action: keep
            regex: kong-dp
          - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
            action: keep
            regex: true
          - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
            action: replace
            target_label: __metrics_path__
            regex: (.+)
          - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
            action: replace
            regex: ([^:]+)(?::\\d+)?;(\\d+)
            replacement: $1:$2
            target_label: __address__
            
      # PostgreSQL metrics
      - job_name: 'postgresql'
        static_configs:
          - targets: ['postgres-postgresql.postgres.svc.cluster.local:9187']
        metrics_path: '/metrics'
        
      # Kubernetes cluster metrics
      - job_name: 'kubernetes-nodes'
        kubernetes_sd_configs:
          - role: node
        relabel_configs:
          - action: labelmap
            regex: __meta_kubernetes_node_label_(.+)
          - target_label: __address__
            replacement: kubernetes.default.svc:443
          - source_labels: [__meta_kubernetes_node_name]
            regex: (.+)
            target_label: __metrics_path__
            replacement: /api/v1/nodes/$1/proxy/metrics
            
# Alerting rules
ruleFiles:
  kong_rules.yml: |
    groups:
    - name: kong
      rules:
      # Kong service availability
      - alert: KongDown
        expr: up{job="kong-control-plane"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Kong Control Plane is down"
          description: "Kong Control Plane has been down for more than 1 minute"
          
      - alert: KongDataPlaneDown
        expr: up{job="kong-data-plane"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Kong Data Plane is down"
          description: "Kong Data Plane {{ $labels.instance }} has been down for more than 1 minute"
      
      # High latency alerts
      - alert: KongHighLatency
        expr: histogram_quantile(0.95, rate(kong_latency_bucket[5m])) > 1000
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Kong high latency detected"
          description: "Kong 95th percentile latency is above 1000ms"
          
      # High error rate
      - alert: KongHighErrorRate
        expr: rate(kong_http_status{code=~"5.."}[5m]) / rate(kong_http_status[5m]) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Kong high error rate"
          description: "Kong error rate is above 5%"
          
      # Database connection issues
      - alert: KongDatabaseDown
        expr: kong_database_reachable == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Kong cannot reach database"
          description: "Kong cannot reach the database for more than 1 minute"

# Node exporter for system metrics
nodeExporter:
  enabled: true
  resources:
    limits:
      cpu: 200m
      memory: 128Mi
    requests:
      cpu: 50m
      memory: 64Mi

# Push gateway (optional)
pushgateway:
  enabled: false

# Alert manager configuration
alertmanager:
  enabled: true
  
  # Persistence
  persistentVolume:
    enabled: true
    size: 2Gi
    
  # Configuration
  config:
    global:
      smtp_smarthost: 'localhost:587'
      smtp_from: 'alertmanager@company.com'
      
    route:
      group_by: ['alertname']
      group_wait: 30s
      group_interval: 5m
      repeat_interval: 12h
      receiver: 'web.hook'
      
    receivers:
      - name: 'web.hook'
        webhook_configs:
          - url: 'http://webhook.example.com/alerts'
            
# Service monitor for Kong
extraScrapeConfigs: |
  # Additional scrape configs can be added here
  
# Grafana integration (if using Grafana operator)
grafana:
  enabled: false  # Set to true if you want to deploy Grafana
  
# RBAC configuration
rbac:
  create: true
  
# Service account
serviceAccount:
  create: true
  name: prometheus
  
# Network policy (optional)
networkPolicy:
  enabled: false
"""

# Create monitoring values
with open("kong-hybrid-setup/monitoring/prometheus-values.yaml", "w") as f:
    f.write(prometheus_values)

# Create Grafana dashboard for Kong
grafana_dashboard = """{
  "dashboard": {
    "id": null,
    "title": "Kong Gateway Dashboard",
    "tags": ["kong", "api-gateway"],
    "style": "dark",
    "timezone": "browser",
    "refresh": "30s",
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "panels": [
      {
        "id": 1,
        "title": "Kong Requests per Second",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(kong_http_requests_total[5m])",
            "legendFormat": "{{service}} - {{method}}"
          }
        ],
        "yAxes": [
          {
            "label": "Requests/sec"
          }
        ],
        "gridPos": {
          "h": 8,
          "w": 12,
          "x": 0,
          "y": 0
        }
      },
      {
        "id": 2,
        "title": "Kong Response Status Codes",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(kong_http_status[5m])",
            "legendFormat": "{{code}}"
          }
        ],
        "gridPos": {
          "h": 8,
          "w": 12,
          "x": 12,
          "y": 0
        }
      },
      {
        "id": 3,
        "title": "Kong Latency Percentiles",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.50, rate(kong_latency_bucket[5m]))",
            "legendFormat": "50th percentile"
          },
          {
            "expr": "histogram_quantile(0.95, rate(kong_latency_bucket[5m]))",
            "legendFormat": "95th percentile"
          },
          {
            "expr": "histogram_quantile(0.99, rate(kong_latency_bucket[5m]))",
            "legendFormat": "99th percentile"
          }
        ],
        "yAxes": [
          {
            "label": "Latency (ms)"
          }
        ],
        "gridPos": {
          "h": 8,
          "w": 24,
          "x": 0,
          "y": 8
        }
      },
      {
        "id": 4,
        "title": "Kong Memory Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "kong_memory_lua_shared_dict_bytes",
            "legendFormat": "{{shared_dict}}"
          }
        ],
        "yAxes": [
          {
            "label": "Bytes"
          }
        ],
        "gridPos": {
          "h": 8,
          "w": 12,
          "x": 0,
          "y": 16
        }
      },
      {
        "id": 5,
        "title": "Kong Database Connections",
        "type": "graph",
        "targets": [
          {
            "expr": "kong_database_connections_available",
            "legendFormat": "Available"
          },
          {
            "expr": "kong_database_connections_used",
            "legendFormat": "Used"
          }
        ],
        "gridPos": {
          "h": 8,
          "w": 12,
          "x": 12,
          "y": 16
        }
      }
    ]
  }
}"""

with open("kong-hybrid-setup/monitoring/kong-dashboard.json", "w") as f:
    f.write(grafana_dashboard)

print("Monitoring configuration created:")
print("- prometheus-values.yaml: Prometheus setup with Kong scraping")
print("- kong-dashboard.json: Grafana dashboard for Kong metrics")