// backend/api/locations/create.js
const express = require("express");
const router = express.Router();
const { createLocation } = require("../../controllers/locationController");
const authenticateToken = require("../../middleware/auth");

// ✅ Create Location Route
router.post("/", authenticateToken, createLocation);

module.exports = router;