local CustomPluginHandler = {}

CustomPluginHandler.PRIORITY = 1000
CustomPluginHandler.VERSION = "0.1.0"

function CustomPluginHandler:access(conf)
  kong.service.request.set_header(conf.header_name, conf.header_value)
end

return CustomPluginHandler
