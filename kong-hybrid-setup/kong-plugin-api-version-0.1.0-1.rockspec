package = "kong-plugin-api-version"
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
