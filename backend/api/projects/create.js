// backend/api/projects/create.js
const express = require("express");
const router = express.Router();
const { createProject } = require("../../controllers/projectController");
const authenticateToken = require("../../middleware/auth");

// ✅ Route: POST /api/projects/create
router.post("/", authenticateToken, (req, res, next) => {
  console.log("📥 /api/projects/create called with body:", req.body);
  createProject(req, res, next);
});

module.exports = router;