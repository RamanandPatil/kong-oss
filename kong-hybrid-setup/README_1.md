# Kong API Version Plugin

A custom Kong plugin that adds API version information to HTTP responses.

## Features

- ✅ Add API version headers to responses
- ✅ Modify JSON response bodies with version metadata  
- ✅ Configurable header names and prefixes
- ✅ Request logging with version information
- ✅ Timestamp tracking

## Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `version` | string | `"1.0.0"` | API version string |
| `add_server_header` | boolean | `true` | Add X-Server header |
| `add_timestamp` | boolean | `false` | Add X-Response-Time header |
| `modify_body` | boolean | `false` | Add metadata to JSON bodies |
| `log_version` | boolean | `true` | Log version for each request |
| `enable_logging` | boolean | `false` | Enable detailed logging |
| `custom_header_name` | string | `"X-API-Version"` | Custom version header name |
| `header_prefix` | string | `"v"` | Prefix for version headers |

## Usage

### Enable via Admin API
```bash
curl -X POST http://kong-admin:8001/plugins \
  --data "name=api-version" \
  --data "config.version=2.1.0" \
  --data "config.add_timestamp=true"
```

### Enable via Kubernetes
```yaml
apiVersion: configuration.konghq.com/v1
kind: KongPlugin
metadata:
  name: api-version-plugin
plugin: api-version
config:
  version: "2.1.0"
  add_server_header: true
  add_timestamp: true
  modify_body: false
```

## Development

### Testing with Pongo
```bash
# Install pongo
git clone https://github.com/Kong/kong-pongo.git
export PATH=$PATH:$(pwd)/kong-pongo

# Run tests
pongo run
```

### Building Rock
```bash
# Build the rock
pongo pack

# Install locally
luarocks install kong-plugin-api-version-0.1.0-1.rock
```

## Installation

### Method 1: ConfigMap (Recommended for Development)
```bash
# Create ConfigMap from plugin files
kubectl create configmap kong-plugin-api-version \
  --from-file=handler.lua=kong/plugins/api-version/handler.lua \
  --from-file=schema.lua=kong/plugins/api-version/schema.lua \
  -n kong
```

### Method 2: Custom Image
```dockerfile
FROM kong/kong-gateway:3.11
COPY kong/plugins/api-version /opt/kong/plugins/api-version
USER kong
```

## License

Apache 2.0
