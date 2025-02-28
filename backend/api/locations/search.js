// backend/api/locations/search.js
const express = require("express");
const router = express.Router();
const Location = require("../../models/Location"); // Assuming you have a Location model
const authenticateToken = require("../../middleware/auth");

router.get("/search", authenticateToken, async (req, res) => {
  const { query, clientId } = req.query;
  try {
    const locations = await Location.find({
      clientId,
      $or: [
        { addressLine1: { $regex: query, $options: "i" } },
        { city: { $regex: query, $options: "i" } },
      ],
    }).limit(10);
    res.json({ locations });
  } catch (err) {
    console.error("Error fetching locations:", err);
    res.status(500).json({ error: "Failed to fetch locations" });
  }
});

module.exports = router;