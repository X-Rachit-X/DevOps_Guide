console.log(JSON.stringify({
  level: "info",
  event: "user_created",
  userId,
  timestamp: new Date().toISOString(),
}));
