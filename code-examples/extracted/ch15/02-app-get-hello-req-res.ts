app.get("/hello", (req, res) => {
  res.json({ message: "Hello" });
});

app.listen(3000);
