# Create PostgreSQL values for the database
postgres_values = """# postgres-values.yaml - PostgreSQL Configuration for Kong
# This deploys PostgreSQL as the backend database for Kong Control Plane

# Global configuration
global:
  postgresql:
    auth:
      postgresPassword: "admin-password"
      username: "kong"
      password: "kong-password" 
      database: "kong"

# Image configuration
image:
  registry: docker.io
  repository: bitnami/postgresql
  tag: "15.4.0"
  pullPolicy: IfNotPresent

# Architecture
architecture: standalone  # Use 'replication' for HA setup

# Authentication
auth:
  enablePostgresUser: true
  postgresPassword: "admin-password"
  username: "kong"
  password: "kong-password"
  database: "kong"
  
# Primary database configuration
primary:
  # Number of replicas  
  replicaCount: 1
  
  # Service configuration
  service:
    type: ClusterIP
    ports:
      postgresql: 5432
  
  # Persistence configuration
  persistence:
    enabled: true
    storageClass: ""  # Use default storage class
    size: 20Gi
    accessModes:
      - ReadWriteOnce
    # existingClaim: ""  # Use existing PVC if available
  
  # Resource configuration
  resources:
    limits:
      cpu: 1000m
      memory: 1Gi
    requests:
      cpu: 250m
      memory: 256Mi
  
  # Pod affinity (optional)
  affinity: {}
  
  # Node selector (optional)  
  nodeSelector: {}
  
  # Tolerations (optional)
  tolerations: []
  
  # PostgreSQL configuration
  configuration: |
    # PostgreSQL configuration for Kong
    max_connections = 200
    shared_buffers = 256MB
    effective_cache_size = 512MB
    maintenance_work_mem = 64MB
    checkpoint_completion_target = 0.9
    wal_buffers = 16MB
    default_statistics_target = 100
    random_page_cost = 1.1
    effective_io_concurrency = 200
    work_mem = 4MB
    min_wal_size = 1GB
    max_wal_size = 4GB
    max_worker_processes = 8
    max_parallel_workers_per_gather = 4
    max_parallel_workers = 8
    max_parallel_maintenance_workers = 4
    
    # Connection and authentication
    listen_addresses = '*'
    port = 5432
    
    # Logging configuration
    logging_collector = on
    log_directory = 'log'
    log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
    log_statement = 'none'
    log_min_duration_statement = 1000
    
  # PostgreSQL extended configuration  
  extendedConfiguration: |
    # Additional configuration
    shared_preload_libraries = 'pg_stat_statements'
    
  # Init scripts (create Kong database if needed)
  initScripts:
    kong-init.sql: |
      -- Create Kong database and user if not exists
      CREATE DATABASE IF NOT EXISTS kong;
      GRANT ALL PRIVILEGES ON DATABASE kong TO kong;
      
      -- Create additional schemas if needed
      \\c kong;
      CREATE SCHEMA IF NOT EXISTS kong;
      GRANT ALL ON SCHEMA kong TO kong;

# Read replicas (for HA setup)
readReplicas:
  # Number of read replicas
  replicaCount: 0  # Set to 1+ for HA
  
  # Service configuration
  service:
    type: ClusterIP
    ports:
      postgresql: 5432
  
  # Resource configuration
  resources:
    limits:
      cpu: 1000m
      memory: 1Gi
    requests:
      cpu: 250m
      memory: 256Mi

# Metrics and monitoring
metrics:
  enabled: true
  
  # Prometheus PostgreSQL exporter
  prometheusRule:
    enabled: true
    namespace: ""
    labels: {}
    rules: []
  
  # Service monitor for Prometheus
  serviceMonitor:
    enabled: true
    namespace: ""
    labels: {}
    interval: 30s
    scrapeTimeout: 30s

# Backup configuration (optional)
backup:
  enabled: false
  # cronjob:
  #   schedule: "0 2 * * *"
  #   historyLimit: 3
  #   restartPolicy: OnFailure
  
# Security context
securityContext:
  enabled: true
  fsGroup: 1001
  runAsUser: 1001
  runAsGroup: 1001

containerSecurityContext:
  enabled: true
  runAsUser: 1001
  runAsGroup: 1001
  runAsNonRoot: true
  readOnlyRootFilesystem: false

# Pod disruption budget
pdb:
  create: true
  minAvailable: ""
  maxUnavailable: 1

# Network policy (optional)
networkPolicy:
  enabled: false
  # allowExternal: true
  # explicitNamespacesSelector: {}

# Volume permissions (for non-root deployments)
volumePermissions:
  enabled: false
  
# LDAP configuration (if needed)
ldap:
  enabled: false

# TLS configuration (optional)
tls:
  enabled: false
  # certificatesSecret: ""
  # certFilename: ""
  # certKeyFilename: ""
  # certCAFilename: ""

# Audit logging (optional)
audit:
  logConnections: false
  logDisconnections: false
  pgAuditLog: ""
  pgAuditLogCatalog: "off"
  clientMinMessages: error
  logLinePrefix: ""
  logTimezone: ""

# Common labels
commonLabels:
  app.kubernetes.io/name: postgresql
  app.kubernetes.io/component: database
  app.kubernetes.io/part-of: kong
"""

with open("kong-hybrid-setup/database/postgres-values.yaml", "w") as f:
    f.write(postgres_values)

print("PostgreSQL Helm values created!")