// backend/api/projects/index.js
const express = require("express");
const router = express.Router();
const { createProject, uploadPDF } = require("../../controllers/projectController");
const authenticateToken = require("../../middleware/auth");
const multer = require("multer");

// 📂 Multer storage setup
const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, "uploads/"),
  filename: (req, file, cb) => cb(null, file.originalname),
});

const upload = multer({ storage });

// 📝 Create a new project
router.post("/", authenticateToken, createProject);

// 📤 Upload project PDF
router.post("/upload", authenticateToken, upload.single("pdf"), uploadPDF);

module.exports = router;