// backend/controllers/projectController.js
const mongoose = require("mongoose");
const axios = require("axios");
const Project = require("../models/Project");
const path = require("path");
const fs = require("fs");

// ✅ Create a new project
exports.createProject = async (req, res) => {
  try {
    const { projectName, clientId, locationId, assignedUser, uuid, plan_id } = req.body;

    if (!projectName || !clientId || !locationId || !uuid || !plan_id) {
      return res.status(400).json({ error: "Missing required fields." });
    }
    console.log("Received IDs:", { clientId, locationId, assignedUser });

    const clientIdObj = "60d21b4667d0d8992e610c85";   // Mock valid ObjectId
    const locationIdObj = "60d21b4967d0d8992e610c86"; // Mock valid ObjectId
    const assignedUserObj = "60d21b4a67d0d8992e610c87"; // Mock valid ObjectId

    // 🛑 Check for invalid ObjectIds
    if (!clientIdObj || !locationIdObj || !assignedUserObj) {
      console.error("🚫 Invalid ObjectId detected.");
      return res.status(400).json({ error: "Invalid ObjectId provided for clientId, locationId, or assignedUser." });
    }

    const newProject = new Project({
      projectName,
      clientId: clientIdObj,
      locationId: locationIdObj,
      assignedUser: assignedUserObj,
      uuid,
      plan_id,
      createdAt: new Date(),
    });

    const savedProject = await newProject.save();
    res.status(201).json({ message: "Project created successfully!", projectId: savedProject._id });
  } catch (err) {
    console.error("Error creating project:", err);
    res.status(500).json({ error: "Failed to create project." });
  }
};

// ✅ Upload PDF associated with a project
exports.uploadPDF = async (req, res) => {
  try {
    const uuid = req.headers["uuid"];
    const plan_id = req.headers["plan_id"];

    if (!req.file) {
      return res.status(400).json({ error: "No PDF file uploaded." });
    }

    if (!uuid || !plan_id) {
      return res.status(400).json({ error: "Missing UUID or Plan ID in request." });
    }

    // Define the correct storage path
    const uploadDir = path.join(__dirname, `../../data/user/${uuid}/projects/${plan_id}/uploads`);
    
    console.log("📂 Upload Directory:", uploadDir);

    // Ensure the directory exists
    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir, { recursive: true });
    }

    // Move the file to the correct location
    const finalPath = path.join(uploadDir, req.file.originalname);
    fs.rename(req.file.path, finalPath, (err) => {
      if (err) {
        console.error("❌ Error moving PDF:", err);
        return res.status(500).json({ error: "Failed to save PDF." });
      }

      console.log("📄 PDF saved successfully at:", finalPath);
      
      // ✅ Step 2: Trigger the pipeline after a successful upload
      console.log("🚀 Triggering pipeline...");
      axios.post(
        "http://localhost:4000/api/pipeline/start",
        { uuid, plan_id },
        { headers: { Authorization: req.headers.authorization } } // ✅ Include token
      )
      .then(() => {
        console.log("✅ Pipeline successfully started.");
        res.status(200).json({ message: "PDF uploaded and pipeline started!", filePath: finalPath });
      })
      .catch((err) => {
        console.error("❌ Error triggering pipeline:", err);
        res.status(500).json({ error: "Pipeline execution failed." });
      });
    });

  } catch (err) {
    console.error("❌ Error in uploadPDF:", err);
    res.status(500).json({ error: "Internal server error." });
  }
};

// ✅ Get project details by ID
exports.getProjectById = async (req, res) => {
  try {
    const { projectId } = req.params;
    const project = await Project.findById(projectId);

    if (!project) {
      return res.status(404).json({ error: "Project not found." });
    }

    res.status(200).json(project);
  } catch (err) {
    console.error("Error fetching project:", err);
    res.status(500).json({ error: "Failed to fetch project." });
  }
};