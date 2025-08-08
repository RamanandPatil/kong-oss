return {
  no_consumer = true, -- can be configured on a Service or Route
  fields = {
    header_name = { type = "string", default = "X-My-Plugin" },
    header_value = { type = "string", default = "Hello from Custom Plugin" }
  }
}
