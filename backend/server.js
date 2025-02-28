// backend/server.js
// 🌟 Imports
const express = require('express');
const cors = require('cors');
const mongoose = require("mongoose");
require('dotenv').config({ path: '../.env' });
const path = require('path');

// 🗂️ Route Imports
const pipelineRoutes = require("./routes/pipeline");
const projectRoutes = require("./routes/projects");
const authRoutes = require('./routes/auth');
const hvacRoutes = require('./routes/hvac');
const clientRoutes = require('./routes/clients');
const locationRoutes = require('./routes/locations');
const userRoutes = require('./routes/users');

// 🗂️ API Route Imports
const clientsApi = require("./api/clients");
const locationsApi = require("./api/locations");
const usersApi = require("./api/users");
const pipelineProgressApi = require("./api/pipeline/progress");

// 🗄️ MongoDB Connection
const connectDB = require('./utils/db');

// 🚀 Initialize Express
const app = express();
const port = process.env.PORT || 4000;

// 🛡️ Middleware
app.use(cors({ origin: "http://localhost:3000", credentials: true }));
app.use(express.json());
app.use((req, res, next) => {
  console.log(`➡️ Incoming Request: ${req.method} ${req.originalUrl}`);
  next();
});

// 🌐 API Routes
app.use("/api/auth", authRoutes);
app.use("/api/hvac", hvacRoutes);
app.use("/api/pipeline", pipelineRoutes);
app.use("/api/projects", projectRoutes);
app.use("/api/clients", clientsApi);
app.use("/api/locations", locationsApi);
app.use("/api/users", usersApi);
app.use("/api/pipeline/progress", pipelineProgressApi);

// 🗂️ Serve Uploads
app.use("/uploads", express.static(path.join(__dirname, '../data/user')));

// 🗂️ Serve React Frontend as a Fallback
app.use(express.static(path.join(__dirname, '../frontend/public')));

// 🗺️ Frontend Catch-All Route (Must Come Last)
app.get('*', (req, res) => {
  res.sendFile(path.resolve(__dirname, "../frontend/public/index.html"));
});

// 🛠️ Connect to Database & Start Server
// MongoDB connection for testing; AWS migration planned
connectDB();

app.listen(port, () => {
  console.log(`🚀 Server is running on port: ${port}`);
});