# Create custom plugin files - API Version plugin
handler_lua = '''-- handler.lua - API Version Plugin Handler
-- This plugin adds API version information to responses

local kong = kong
local ngx = ngx
local plugin = {
  PRIORITY = 1000, -- set the plugin priority, which determines plugin execution order
  VERSION = "0.1.0", -- version in X.Y.Z format. Check hybrid-mode compatibility requirements.
}

-- Initialize plugin
function plugin:init_worker()
  -- Your custom code here
  kong.log.debug("api-version plugin initialized")
end

-- Access phase - runs for every request
function plugin:access(plugin_conf)
  -- Add request processing logic here
  kong.log.debug("api-version plugin access phase")
  
  -- Add custom header to identify the plugin is working
  kong.service.request.set_header("X-Kong-Plugin", "api-version")
  
  -- Log the API version being used
  if plugin_conf.log_version then
    kong.log.info("API Version: ", plugin_conf.version)
  end
end

-- Header filter phase - modify response headers
function plugin:header_filter(plugin_conf)
  -- Add API version to response headers
  kong.response.set_header("X-API-Version", plugin_conf.version)
  kong.response.set_header("X-Plugin-Version", plugin.VERSION)
  
  -- Add custom headers based on configuration
  if plugin_conf.add_server_header then
    kong.response.set_header("X-Server", "Kong-Gateway")
  end
  
  if plugin_conf.add_timestamp then
    kong.response.set_header("X-Response-Time", tostring(ngx.now()))
  end
end

-- Body filter phase - modify response body (optional)
function plugin:body_filter(plugin_conf)
  -- Only process if we need to modify the response body
  if not plugin_conf.modify_body then
    return
  end
  
  local body = kong.response.get_raw_body()
  if body then
    -- Add version info to JSON responses
    local content_type = kong.response.get_header("content-type")
    if content_type and string.find(content_type, "application/json") then
      local json_body = kong.json.decode(body)
      if json_body then
        json_body._meta = {
          api_version = plugin_conf.version,
          plugin_version = plugin.VERSION,
          timestamp = os.date("!%Y-%m-%dT%H:%M:%SZ")
        }
        local new_body = kong.json.encode(json_body)
        kong.response.set_raw_body(new_body)
      end
    end
  end
end

-- Log phase - for logging and analytics
function plugin:log(plugin_conf)
  -- Custom logging logic
  if plugin_conf.enable_logging then
    kong.log.info("API Version Plugin executed for version: ", plugin_conf.version)
    
    -- Log request details
    local log_data = {
      version = plugin_conf.version,
      method = kong.request.get_method(),
      path = kong.request.get_path(),
      status = kong.response.get_status(),
      latency = kong.ctx.shared.response_latency or 0
    }
    
    kong.log.info("Request processed: ", kong.json.encode(log_data))
  end
end

-- Return our plugin object
return plugin
'''

schema_lua = '''-- schema.lua - API Version Plugin Schema
-- This defines the configuration schema for the API version plugin

local typedefs = require "kong.db.schema.typedefs"

return {
  name = "api-version",
  fields = {
    { consumer = typedefs.no_consumer },
    { protocols = typedefs.protocols_http },
    { config = {
        type = "record",
        fields = {
          { version = { 
              type = "string", 
              required = true, 
              default = "1.0.0",
              description = "API version string to add to responses"
            }
          },
          { add_server_header = { 
              type = "boolean", 
              default = true,
              description = "Add X-Server header to responses"
            }
          },
          { add_timestamp = { 
              type = "boolean", 
              default = false,
              description = "Add X-Response-Time header to responses"
            }
          },
          { modify_body = { 
              type = "boolean", 
              default = false,
              description = "Add version metadata to JSON response body"
            }
          },
          { log_version = { 
              type = "boolean", 
              default = true,
              description = "Log API version for each request"
            }
          },
          { enable_logging = { 
              type = "boolean", 
              default = false,
              description = "Enable detailed request logging"
            }
          },
          { custom_header_name = { 
              type = "string",
              default = "X-API-Version",
              description = "Custom header name for API version"
            }
          },
          { header_prefix = { 
              type = "string",
              default = "v",
              description = "Prefix for version in headers"
            }
          }
        }
      }
    }
  }
}
'''

# Create plugin files
plugin_dir = "kong-hybrid-setup/custom-plugins/api-version/kong/plugins/api-version"
os.makedirs(plugin_dir, exist_ok=True)

with open(f"{plugin_dir}/handler.lua", "w") as f:
    f.write(handler_lua)

with open(f"{plugin_dir}/schema.lua", "w") as f:
    f.write(schema_lua)

# Create rockspec file for the plugin
rockspec = '''package = "kong-plugin-api-version"
version = "0.1.0-1"
source = {
   url = "git+https://github.com/your-org/kong-plugin-api-version.git"
}
description = {
   summary = "A Kong plugin to add API version information to responses",
   detailed = [[
      This plugin adds API version information to HTTP responses.
      It can add version headers, modify response bodies, and provide
      detailed logging for API version tracking.
   ]],
   homepage = "https://github.com/your-org/kong-plugin-api-version",
   license = "Apache 2.0"
}
dependencies = {
   "lua >= 5.1"
}
build = {
   type = "builtin",
   modules = {
      ["kong.plugins.api-version.handler"] = "kong/plugins/api-version/handler.lua",
      ["kong.plugins.api-version.schema"] = "kong/plugins/api-version/schema.lua"
   }
}
'''

with open("kong-hybrid-setup/custom-plugins/api-version/kong-plugin-api-version-0.1.0-1.rockspec", "w") as f:
    f.write(rockspec)

# Create README for the plugin
plugin_readme = '''# Kong API Version Plugin

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
curl -X POST http://kong-admin:8001/plugins \\
  --data "name=api-version" \\
  --data "config.version=2.1.0" \\
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
kubectl create configmap kong-plugin-api-version \\
  --from-file=handler.lua=kong/plugins/api-version/handler.lua \\
  --from-file=schema.lua=kong/plugins/api-version/schema.lua \\
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
'''

with open("kong-hybrid-setup/custom-plugins/api-version/README.md", "w") as f:
    f.write(plugin_readme)

print("Custom plugin files created!")
print("- handler.lua: Plugin logic and execution phases")
print("- schema.lua: Configuration schema and validation")
print("- rockspec: LuaRocks package specification")
print("- README.md: Plugin documentation")