app.get("/ready", async (_req, res) => {
  try {
    await pool.query("SELECT 1");

    res.status(200).json({
      status: "ready"
    });
  } catch {
    res.status(503).json({
      status: "not_ready"
    });
  }
});
