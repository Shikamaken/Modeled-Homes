// backend/api/pipeline/index.js
const express = require("express");
const router = express.Router();
const { startPipeline, getPipelineProgress } = require("../../controllers/pipelineController");
const authenticateToken = require("../../middleware/auth");

// 🚀 Start the pipeline
router.post("/start", authenticateToken, startPipeline);

// 📊 Get pipeline progress
router.post("/progress", authenticateToken, getPipelineProgress);

module.exports = router;