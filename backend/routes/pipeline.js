// backend/routes/pipeline.js
const express = require("express");
const router = express.Router();
const { startPipeline, checkPipelineStatus, markPipelineComplete } = require("../controllers/pipelineController");
const authenticateToken = require("../middleware/auth");

router.post("/start", authenticateToken, (req, res, next) => {
  console.log("📥 /api/pipeline/start called with body:", req.body); // ✅ Correct placement
  startPipeline(req, res, next); // Call the controller function
});

router.get("/status", checkPipelineStatus);

router.post("/complete", markPipelineComplete);

module.exports = router;