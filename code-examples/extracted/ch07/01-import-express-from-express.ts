import express from "express";

const app = express();

app.get("/", (_req, res) => {
  res.json({ message: "Hello Docker" });
});

app.listen(3000, "0.0.0.0", () => {
  console.log("Server running on port 3000");
});
