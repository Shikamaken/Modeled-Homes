// backend/controllers/pipelineController.js
const { spawn } = require("child_process");
const fs = require("fs");
const path = require("path");

exports.startPipeline = async (req, res) => {
  const { plan_id, uuid } = req.body;

  if (!plan_id || !uuid) {
    return res.status(400).json({ error: "Missing required fields." });
  }

  console.log("🔥 Starting pipeline with:", { plan_id, uuid });

  try {
    const scriptPath = path.join(__dirname, "../../scripts/pdf_model_conv.py");

    const pipelineProcess = spawn("python", [
      scriptPath,
      uuid,     // First argument should be uuid
      plan_id   // Second argument should be plan_id
    ]);

    pipelineProcess.stdout.on("data", (data) => {
      console.log(`[PIPELINE STDOUT]: ${data}`);
    });

    pipelineProcess.stderr.on("data", (data) => {
      const message = data.toString().trim().toLowerCase();

      // ✅ Define "bad" keywords that indicate real errors
      const errorKeywords = ["error", "failed", "exception", "warning", "traceback", "critical"];

      // ✅ If STDERR contains any "bad" keyword, treat it as an error
      if (errorKeywords.some(keyword => message.includes(keyword))) {
        console.error(`[PIPELINE STDERR]: ${message}`);  // ❌ Real errors stay in STDERR
      } else {
        console.log(`[PIPELINE STDOUT]: ${message}`);  // ✅ Normal messages go to STDOUT
      }
    });

    pipelineProcess.on("close", (code) => {
      if (code === 0) {
        console.log("✅ Pipeline completed successfully.");
        
        res.status(200).json({ 
          message: "Pipeline completed successfully", 
          plan_id, // Use plan_id since projectId isn’t available here
          status: "success" 
        });
      } else {
        console.error(`❌ Pipeline process exited with code ${code}`);
        res.status(500).json({ error: "Pipeline execution failed." });
      }
    });

  } catch (err) {
    console.error("❌ Pipeline error:", err);
    res.status(500).json({ error: "Internal server error." });
  }
};

let completedPipelines = {};

exports.markPipelineComplete = (req, res) => {
  const { uuid, plan_id } = req.body;

  if (!uuid || !plan_id) {
    console.error("❌ Invalid completion request - missing UUID or Plan ID.");
    return res.status(400).json({ error: "Missing UUID or Plan ID" });
  }

  const normalizedPlanId = decodeURIComponent(plan_id).trim();
  const pipelineKey = `${uuid}_${normalizedPlanId}`;
  
  completedPipelines[pipelineKey] = true;
  console.log(`✅ Marked pipeline as completed: ${pipelineKey}`);
  console.log(`📌 Updated pipeline states:`, completedPipelines);

  res.status(200).json({ message: "Pipeline marked as completed" });
};

exports.checkPipelineStatus = async (req, res) => {
  const { uuid, plan_id } = req.query;

  if (!uuid || !plan_id) {
    return res.status(400).json({ error: "Missing UUID or Plan ID" });
  }

  const normalizedPlanId = decodeURIComponent(plan_id).trim();
  const pipelineKey = `${uuid}_${normalizedPlanId}`;
  console.log(`🔎 Checking pipeline status for ${pipelineKey}`);
  console.log(`📌 Current pipeline states:`, completedPipelines);
  const pipelineCompleted = completedPipelines[pipelineKey] || false;

  if (completedPipelines[pipelineKey]) {
    console.log(`✅ Marking pipeline as completed: ${pipelineKey}`);
    res.status(200).json({ status: "success", message: "Pipeline completed successfully" });
  } else {
    console.log("⏳ Pipeline still processing...");
    res.status(200).json({ status: "pending", message: "Pipeline still processing" });
  }
};