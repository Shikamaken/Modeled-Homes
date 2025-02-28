// backend/routes/users.js
const express = require("express");
const router = express.Router();
const { createUser, searchUsers } = require("../controllers/userController");
const authenticateToken = require("../middleware/auth");

// ✅ Create a new user
router.post("/create", authenticateToken, createUser);

// ✅ Search for users/teams
router.get("/search", authenticateToken, searchUsers);

module.exports = router;