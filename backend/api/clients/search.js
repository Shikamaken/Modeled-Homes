// backend/api/clients/search.js
const express = require("express");
const router = express.Router();
const Client = require("../../models/Client"); // Assuming you have a Client model
const authenticateToken = require("../../middleware/auth");

router.get("/search", authenticateToken, async (req, res) => {
  const { query } = req.query;
  try {
    const clients = await Client.find({
      name: { $regex: query, $options: "i" },
    }).limit(10);
    res.json({ clients });
  } catch (err) {
    console.error("Error fetching clients:", err);
    res.status(500).json({ error: "Failed to fetch clients" });
  }
});

module.exports = router;