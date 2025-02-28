// backend/api/clients/index.js
const express = require("express");
const router = express.Router();
const { searchClients, createClient } = require("../../controllers/clientController");
const authenticateToken = require("../../middleware/auth");

// 🔎 Search clients
router.get("/search", authenticateToken, searchClients);

// ➕ Create new client
router.post("/", authenticateToken, createClient);

module.exports = router;