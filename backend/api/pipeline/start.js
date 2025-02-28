// backend/api/pipeline/start.js
const express = require("express");
const { spawn } = require("child_process");
const router = express.Router();

const runningJobs = new Map(); // Track running pipeline jobs

// ✅ Start pipeline route
router.post("/start", (req, res) => {
  const { projectId, plan_id, uuid } = req.body;

  if (!projectId || !plan_id || !uuid) {
    return res.status(400).json({ error: "Missing required fields." });
  }

  if (runningJobs.has(projectId)) {
    return res.status(409).json({ error: "Pipeline already running for this project." });
  }

  const process = spawn("python", ["pdf_model_conv.py", projectId, plan_id, uuid]);
  runningJobs.set(projectId, { process, progress: 0 });

  process.stdout.on("data", (data) => {
    const message = data.toString();
    console.log(`Pipeline Output (${projectId}): ${message}`);

    if (message.includes("OCR Complete")) runningJobs.get(projectId).progress = 25;
    else if (message.includes("Line Detection Complete")) runningJobs.get(projectId).progress = 50;
    else if (message.includes("Scale Extraction Complete")) runningJobs.get(projectId).progress = 75;
    else if (message.includes("Pipeline Complete")) runningJobs.get(projectId).progress = 100;
  });

  process.stderr.on("data", (data) => {
    console.error(`Error (${projectId}): ${data}`);
  });

  process.on("close", () => {
    runningJobs.delete(projectId); // Clean up when done
  });

  res.status(202).json({ message: "Pipeline started", projectId });
});

// ✅ Progress polling route
router.get("/progress/:projectId", (req, res) => {
  const { projectId } = req.params;
  const job = runningJobs.get(projectId);

  if (!job) {
    return res.status(404).json({ error: "No running job found." });
  }

  res.json({ progress: job.progress });
});

module.exports = router;