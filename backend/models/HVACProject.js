// backend/models/HVACProject.js
const mongoose = require('mongoose');

const HVACProjectSchema = new mongoose.Schema({
  name: { type: String, required: true },
  location: { type: String, required: true },
  createdAt: { type: Date, default: Date.now },
  updatedAt: { type: Date, default: Date.now },
  // Add other relevant fields
});

module.exports = mongoose.model('HVACProject', HVACProjectSchema);