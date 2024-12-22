const express = require('express');
const cors = require('cors');
require('dotenv').config();
const connectDB = require('./utils/db'); // Import the MongoDB connection function

const app = express();
const port = process.env.PORT || 4000;

// Middleware setup
app.use(cors());
app.use(express.json());

// Connect to MongoDB
connectDB();

// Route setup
const hvacRoutes = require('./routes/hvac');
app.use('/api/hvac', hvacRoutes);

const authRoutes = require('./routes/auth');
app.use('/api/auth', authRoutes);

const embeddingsRoute = require('./routes/embeddings');
app.use('/api/embeddings', embeddingsRoute);

// Start the server
app.listen(port, () => {
  console.log(`Server is running on port: ${port}`);
});