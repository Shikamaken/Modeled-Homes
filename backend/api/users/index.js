// backend/api/users/index.js
const express = require("express");
const router = express.Router();
const { searchUsers, createUser } = require("../../controllers/userController");
const authenticateToken = require("../../middleware/auth");

// 🔎 Search users
router.get("/search", authenticateToken, searchUsers);

// ➕ Create new user
router.post("/", authenticateToken, createUser);

module.exports = router;