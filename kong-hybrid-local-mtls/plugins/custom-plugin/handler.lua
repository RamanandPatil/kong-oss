local CustomHandler = {
  PRIORITY = 1000,
  VERSION = "1.0",
}

function CustomHandler:access(conf)
  kong.log.info("custom-plugin: access phase")
  kong.response.set_header("x-custom-plugin", "ok")
end

return CustomHandler
