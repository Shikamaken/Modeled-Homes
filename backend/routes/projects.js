const express = require("express");
const router = express.Router();
const fs = require("fs");
const path = require("path");
const multer = require("multer");

const PROJECTS_DIR = "C:/Users/shika/modeled-homes-hvac/data/user/projects/";

// Ensure the project directory exists
if (!fs.existsSync(PROJECTS_DIR)) {
  fs.mkdirSync(PROJECTS_DIR, { recursive: true });
}

// ✅ **Route: Fetch All Projects**
router.get("/", (req, res) => {
  try {
    const projectDirs = fs.readdirSync(PROJECTS_DIR);
    const projects = projectDirs
      .map((dir) => {
        const metadataPath = path.join(PROJECTS_DIR, dir, "metadata.json");
        if (fs.existsSync(metadataPath)) {
          return JSON.parse(fs.readFileSync(metadataPath, "utf-8"));
        }
        return null;
      })
      .filter((project) => project !== null);

    res.json(projects.length ? projects : []);
  } catch (error) {
    console.error("Error fetching projects:", error);
    res.status(500).json({ error: "Failed to fetch projects." });
  }
});

// ✅ Middleware to Extract `projectId` BEFORE Uploading the File
const extractProjectId = (req, res, next) => {
  if (!req.body.projectId) {
    return res.status(400).json({ error: "Project ID is required." });
  }
  req.projectPath = path.join(PROJECTS_DIR, `project_${req.body.projectId}`);
  
  if (!fs.existsSync(req.projectPath)) {
    fs.mkdirSync(req.projectPath, { recursive: true });
  }
  
  next();
};

// ✅ Configure Multer Storage (Now Uses `req.projectPath`)
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    const projectDir = path.join(PROJECTS_DIR, `project_${req.params.projectId}`);
    fs.mkdirSync(projectDir, { recursive: true });
    cb(null, projectDir);
  },
  filename: (req, file, cb) => {
    cb(null, "input.pdf");
  },
});

const upload = multer({ storage });

// ✅ **Route: Upload PDF File for a Project**
router.post(
  "/upload/:projectId",
  upload.single("pdf"),
  (req, res) => {
    console.log("req.params.projectId:", req.params.projectId);
    // The file is saved to ".../project_123" for example
    return res.status(200).json({ message: "OK" });
  }
);

module.exports = router;