// backend/api/clients/create.js
const express = require("express");
const router = express.Router();
const { createClient } = require("../../controllers/clientController");
const authenticateToken = require("../../middleware/auth");

// ✅ Create Client Route
router.post("/", authenticateToken, createClient);

module.exports = router;