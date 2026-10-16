-- Keep the complete original interface available as a floating desktop widget.
o.window({ title = "^Presto Widget$" }, {
  float = true,
  pin = true,
  size = { 880, 700 },
  move = { "(monitor_w-window_w-16)", 48 },
})
