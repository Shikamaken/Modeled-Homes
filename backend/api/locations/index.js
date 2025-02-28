// backend/api/locations/index.js
const express = require("express");
const router = express.Router();
const { searchLocations, createLocation } = require("../../controllers/locationController");
const authenticateToken = require("../../middleware/auth");

// 🔎 Search locations
router.get("/search", authenticateToken, searchLocations);

// ➕ Create new location
router.post("/", authenticateToken, createLocation);

module.exports = router;