// backend/routes/locations.js
const express = require("express");
const router = express.Router();
const { createLocation, searchLocations } = require("../controllers/locationController");
const authenticateToken = require("../middleware/auth");

// ✅ Create a new location
router.post("/create", authenticateToken, createLocation);

// ✅ Search for locations
router.get("/search", authenticateToken, searchLocations);

module.exports = router;