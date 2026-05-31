require("dotenv").config();
const express = require("express");
const path = require("path");
const chatbotRouter = require("./routes/chatbot");

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());

// Serve frontend static files
app.use(express.static(path.join(__dirname, "static")));

// Chatbot routes
app.use("/api/chatbot", chatbotRouter);

// Fallback ke index.html untuk SPA
app.get("/{*path}", (req, res) => {
  res.sendFile(path.join(__dirname, "static", "index.html"));
});

app.listen(PORT, () => {
  console.log(`Express running on http://localhost:${PORT}`);
});
