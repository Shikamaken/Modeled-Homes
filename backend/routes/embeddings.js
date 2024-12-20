const express = require('express');
const router = express.Router();
const { spawn } = require('child_process');
const path = require('path');
const { connectDB } = require('../utils/db');

// POST /api/embeddings/generate
// Body: { planId: "string", pageNumber: number, imagePath: "string" }
// imagePath should be relative to the project root or absolute.
router.post('/generate', async (req, res) => {
  const { planId, pageNumber, imagePath } = req.body;

  if (!planId || pageNumber == null || !imagePath) {
    return res.status(400).json({ error: "Missing required fields" });
  }

  // Full path to the image
  const fullImagePath = path.resolve(__dirname, '../../', imagePath);

  // Path to the python script
  const scriptPath = path.resolve(__dirname, '../scripts/clip_embedding.py');

  try {
    const embedding = await runEmbeddingScript(scriptPath, fullImagePath);
    await storeEmbeddingInDB(planId, pageNumber, embedding);
    res.json({ success: true, message: "Embedding generated and stored." });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Failed to generate embedding." });
  }
});

async function runEmbeddingScript(scriptPath, imgPath) {
  return new Promise((resolve, reject) => {
    const python = spawn('python3', [scriptPath, imgPath]);

    let dataChunks = [];
    let errorChunks = [];

    python.stdout.on('data', (data) => dataChunks.push(data));
    python.stderr.on('data', (data) => errorChunks.push(data));

    python.on('close', (code) => {
      if (code !== 0) {
        return reject(`Embedding script failed: ${Buffer.concat(errorChunks).toString()}`);
      }
      try {
        const embedding = JSON.parse(Buffer.concat(dataChunks).toString());
        resolve(embedding);
      } catch (parseError) {
        reject(`Could not parse embedding output: ${parseError}`);
      }
    });
  });
}

async function storeEmbeddingInDB(planId, pageNumber, embedding) {
  const db = await connectDB();
  const collection = db.collection('plan_embeddings');
  
  // Insert document with vector field
  await collection.insertOne({
    planId,
    pageNumber,
    embedding, // This should be stored as an array of floats
    createdAt: new Date()
  });
}

module.exports = router;