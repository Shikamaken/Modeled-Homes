// backend/api/users/search.js
const express = require("express");
const router = express.Router();
const User = require("../../models/User");
const authenticateToken = require("../../middleware/auth");

router.get("/search", authenticateToken, async (req, res) => {
  const { query } = req.query;
  try {
    const users = await User.find({
      username: { $regex: query, $options: "i" },
    }).limit(10);
    res.json({ users });
  } catch (err) {
    console.error("Error fetching users:", err);
    res.status(500).json({ error: "Failed to fetch users" });
  }
});

module.exports = router;