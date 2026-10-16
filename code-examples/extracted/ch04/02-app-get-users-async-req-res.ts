app.get("/users", async (req, res) => {
  const users = await db.user.findMany();

  res.json(users);
});
