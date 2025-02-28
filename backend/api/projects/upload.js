// backend/api/projects/upload.js
const express = require("express");
const router = express.Router();
const multer = require("multer");
const path = require("path");
const { uploadPDF } = require("../../controllers/projectController");
const authenticateToken = require("../../middleware/auth");
const fs = require("fs");

// ✅ Multer configuration for file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
      console.log("📥 Received request body:", req.body);
      console.log("📥 Received headers:", req.headers);

      const uuid = req.headers["uuid"] || req.query.uuid || req.body.uuid;
      const plan_id = req.headers["plan_id"];

      console.log("🔍 Extracted UUID:", uuid); 
      console.log("🔍 Extracted Plan ID:", plan_id);

    if (!uuid || !plan_id) {
      return cb(new Error("Missing UUID or Plan ID in request"), null);
    }

    const uploadPath = path.join(__dirname, `../../../data/user/${uuid}/projects/${plan_id}/uploads`);

    console.log("📂 Final upload path:", uploadPath);

    // ✅ Ensure the directory exists
    if (!fs.existsSync(uploadPath)) {
      fs.mkdirSync(uploadPath, { recursive: true });
    }

    cb(null, uploadPath);
  },
  filename: (req, file, cb) => {
    cb(null, file.originalname);
  },
});

const upload = multer({ storage });

// ✅ Route: Upload PDF for a project
router.post("/", authenticateToken, upload.single("pdf"), (req, res, next) => {
  console.log("📥 /api/projects/upload called with body:", req.body); // ✅ Correct log placement
  uploadPDF(req, res, next); // ✅ Call the controller function
});

module.exports = router;