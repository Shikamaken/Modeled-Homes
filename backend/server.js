const express = require('express');
const cors = require('cors');
require('dotenv').config();
const connectDB = require('./utils/db'); // Import the MongoDB connection function

const app = express();
const port = process.env.PORT || 4000;

// Middleware setup
app.use(cors({ origin: "http://localhost:3000", credentials: true }));
app.use(express.json());

// Connect to MongoDB (suspended; migrating to AWS in the future)
// connectDB();

// Route setup
const projectRoutes = require("./routes/projects");
app.use("/api/projects", projectRoutes);

const hvacRoutes = require('./routes/hvac');
app.use('/api/hvac', hvacRoutes);

const authRoutes = require('./routes/auth');
app.use('/api/auth', authRoutes);

// const embeddingsRoute = require('./routes/embeddings');
// app.use('/api/embeddings', embeddingsRoute);

// Start the server
app.listen(port, () => {
  console.log(`Server is running on port: ${port}`);
});