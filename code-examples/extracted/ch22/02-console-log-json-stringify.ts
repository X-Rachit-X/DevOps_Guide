console.log(JSON.stringify({
  level: "info",
  event: "server_started",
  port,
  timestamp: new Date().toISOString()
}));
