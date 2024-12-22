const express = require('express');
const router = express.Router();
const { spawn } = require('child_process');
const path = require('path');
const { connectDB } = require('../utils/db');
const mongoose = require('mongoose'); // Added mongoose for database interaction

// Define the full path to your Python interpreter
const pythonPath = 'C:\\Users\\shika\\modeled-homes-hvac\\venv\\Scripts\\python.exe'; // Updated Python path

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
    // Spawn the Python process
    const python = spawn(pythonPath, [scriptPath, imgPath]);

    let dataChunks = [];
    let errorChunks = [];

    python.stdout.on('data', (data) => dataChunks.push(data));
    python.stderr.on('data', (data) => errorChunks.push(data));

    python.on('close', (code) => {
      if (code !== 0) {
        return reject(`Embedding script failed: ${Buffer.concat(errorChunks).toString()}`);
      }
      try {
        const embeddings = JSON.parse(Buffer.concat(dataChunks).toString());
        resolve(embeddings); // Return all embeddings (one per tile)
      } catch (parseError) {
        reject(`Could not parse embedding output: ${parseError}`);
      }
    });
  });
}

async function storeEmbeddingInDB(planId, pageNumber, embeddings) {
  const collection = mongoose.connection.db.collection('plan_embeddings');

  // Insert each tile embedding as a separate document
  const documents = embeddings.map((tile) => ({
    planId,
    pageNumber,
    tileIndex: tile.tileIndex, // Add tile metadata
    embedding: tile.embedding, // Embedding for this tile
    createdAt: new Date(),
  }));

  // Insert all documents in a batch
  await collection.insertMany(documents);
}

module.exports = router;