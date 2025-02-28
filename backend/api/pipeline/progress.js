// backend/api/pipeline/progress.js
const express = require("express");
const router = express.Router();
const PipelineProgress = require("../../models/PipelineProgress"); // Assuming you have a model tracking pipeline progress
const authenticateToken = require("../../middleware/auth");

router.get("/progress/:projectId", authenticateToken, async (req, res) => {
  const { projectId } = req.params;
  try {
    const progress = await PipelineProgress.findOne({ projectId });
    if (!progress) {
      return res.status(404).json({ error: "Progress not found" });
    }
    res.json({ progress: progress.percentage });
  } catch (err) {
    console.error("Error fetching pipeline progress:", err);
    res.status(500).json({ error: "Failed to fetch pipeline progress" });
  }
});

module.exports = router;