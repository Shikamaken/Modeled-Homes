// backend/routes/clients.js
const express = require("express");
const router = express.Router();
const { createClient, searchClients } = require("../controllers/clientController");
const authenticateToken = require("../middleware/auth");

// ✅ Create a new client
router.post("/create", authenticateToken, createClient);

// ✅ Search for clients
router.get("/search", async (req, res) => {
  try {
    const query = req.query.query ?? ""; // Default to empty string
    const clients = await Client.find({ name: new RegExp(query, "i") });
    res.json(clients); // ✅ Always send a response
  } catch (err) {
    console.error("Client search failed:", err);
    res.status(500).json({ error: "Server error during client search." });
  }
});

module.exports = router;