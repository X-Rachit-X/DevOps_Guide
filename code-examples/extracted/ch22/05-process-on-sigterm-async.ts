process.on("SIGTERM", async () => {
  console.log("Shutting down");

  server.close();

  await databasePool.end();

  process.exit(0);
});
