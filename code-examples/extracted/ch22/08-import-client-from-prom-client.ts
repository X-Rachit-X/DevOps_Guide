import client from "prom-client";

client.collectDefaultMetrics();

app.get("/metrics", async (_req, res) => {
  res.set("Content-Type", client.register.contentType);

  res.end(await client.register.metrics());
});
