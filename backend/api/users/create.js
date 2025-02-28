//backend/api/users/create.js
const express = require("express");
const router = express.Router();
const { createUser } = require("../../controllers/userController");
const authenticateToken = require("../../middleware/auth");

// ✅ Create User Route
router.post("/", authenticateToken, createUser);

module.exports = router;