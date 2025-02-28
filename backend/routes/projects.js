// backend/routes/projects.js
const express = require("express");
const router = express.Router();
const fs = require("fs");
const path = require("path");
const { createProject, getProjectById } = require("../controllers/projectController");

const createRoutes = require("../api/projects/create");
const uploadRoutes = require("../api/projects/upload");

const DATA_DIR = "C:/Users/shika/modeled-homes-hvac/data/user/";

// ✅ Function to get the correct projects directory for each user
const getUserProjectDir = (uuid) => path.join(DATA_DIR, uuid, "projects/");

// Ensure the user project directory exists before creating a project
router.use("/create", (req, res, next) => {
  const { uuid } = req.body; // Ensure `uuid` is passed

  if (!uuid) {
    return res.status(400).json({ error: "Missing UUID" });
  }

  const userProjectsDir = getUserProjectDir(uuid);

  if (!fs.existsSync(userProjectsDir)) {
    fs.mkdirSync(userProjectsDir, { recursive: true });
    console.log(`📂 Created projects directory for user: ${userProjectsDir}`);
  }

  next();
});

// ✅ Fetch all projects for a specific user
router.get("/:uuid/projects", (req, res) => {
  console.log("➡️ Incoming Request: GET /api/projects/pdf");
  console.log("🔍 Received UUID:", req.params.uuid);
  console.log("📂 Received plan ID:", req.params.planId);
  console.log("🔍 Received filename from request:", req.params.filename);

  const { uuid } = req.params;
  const userProjectsDir = getUserProjectDir(uuid);

  try {
    if (!fs.existsSync(userProjectsDir)) {
      return res.status(404).json({ error: "No projects found for this user." });
    }

    const projectDirs = fs.readdirSync(userProjectsDir);
    const projects = projectDirs
      .map((dir) => {
        const metadataPath = path.join(userProjectsDir, dir, "metadata.json");
        if (fs.existsSync(metadataPath)) {
          return JSON.parse(fs.readFileSync(metadataPath, "utf-8"));
        }
        return null;
      })
      .filter(Boolean);

    res.json(projects.length ? projects : []);
  } catch (error) {
    console.error("Error fetching projects:", error);
    res.status(500).json({ error: "Failed to fetch projects." });
  }
});

// ✅ Fetch all uploaded PDFs for a project
router.get("/:uuid/projects/:planId/pdfs", (req, res) => {
  const { uuid, planId } = req.params;
  const projectDir = path.join(getUserProjectDir(uuid), planId, "uploads"); // ✅ Now correctly pointing to the user's projects

  try {
    if (!fs.existsSync(projectDir)) {
      return res.status(404).json({ error: "Project not found." });
    }

    const files = fs.readdirSync(projectDir).filter(file => file.endsWith(".pdf"));
    res.json(files);  // ✅ Return an array of PDF filenames
  } catch (error) {
    console.error("Error fetching PDFs:", error);
    res.status(500).json({ error: "Failed to fetch PDFs." });
  }
});

// ✅ Serve PDFs correctly through Express
router.get("/pdf/:uuid/:planId/:filename", (req, res) => {
  const { uuid } = req.params;
  const planId = decodeURIComponent(req.params.planId);
  const filename = decodeURIComponent(req.params.filename);
  console.log("📂 Decoded plan ID:", planId);
  console.log("🔍 Decoded filename:", filename);  
  
  const uploadsDir = path.join(getUserProjectDir(uuid), planId, "uploads");

  if (!fs.existsSync(uploadsDir)) {
    console.error(`❌ Uploads directory does not exist: ${uploadsDir}`);
    return res.status(404).json({ error: "Uploads directory not found." });
  }

  const files = fs.readdirSync(uploadsDir);
  console.log("📂 Files found in uploads directory:", files);
  console.log("🔍 Requested filename:", filename);

  const actualFilename = files.find(f => decodeURIComponent(f) === decodeURIComponent(filename));

  if (!actualFilename) {
    console.error(`❌ ERROR: Requested file "${filename}" not found in uploads.`);
    console.error(`📄 Available files:`, files);
    return res.status(404).json({ error: "PDF file not found." });
  }

  const pdfPath = path.join(uploadsDir, actualFilename);
  console.log(`✅ Serving PDF from: ${pdfPath}`);

  if (!fs.existsSync(pdfPath)) {
    console.error(`❌ File does not exist at expected path: ${pdfPath}`);
    return res.status(404).json({ error: "PDF file not found at expected location." });
  }

  if (req.aborted) {
    console.error("❌ Request aborted by client before sending the file.");
    return;
  }

  res.setHeader("Content-Disposition", `inline; filename="${actualFilename}"`);
  res.setHeader("Content-Type", "application/pdf");

  setTimeout(() => {
    const fileStream = fs.createReadStream(pdfPath);

    fileStream.on("open", () => {
      console.log(`📄 PDF stream opened: ${pdfPath}`);
    });

    fileStream.on("data", (chunk) => {
      console.log(`📄 Sending chunk of ${chunk.length} bytes...`);
    });

    fileStream.on("end", () => {
      console.log(`✅ Finished sending PDF: ${pdfPath}`);
    });

    fileStream.on("error", (err) => {
      console.error("❌ ERROR: Stream failed while serving PDF:", err);
      if (!res.headersSent) {
        res.status(500).send("Error loading PDF");
      }
    });

    fileStream.pipe(res);
  }, 1000);

  res.on("close", () => {
    console.log("📄 PDF stream closed successfully.");
  });
});

// ✅ Include project creation and upload routes
router.use("/create", createRoutes);
router.use("/upload", uploadRoutes);

module.exports = router;