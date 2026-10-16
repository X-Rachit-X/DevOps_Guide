console.log(JSON.stringify({
  level: "info",
  event: "request_completed",
  method: req.method,
  path: req.path,
  statusCode: res.statusCode,
  durationMs,
  requestId
}));
