// backend/models/Client.js
const mongoose = require('mongoose');

const ClientSchema = new mongoose.Schema({
  name: { type: String, required: true, unique: true },
  email: { type: String },
  phone: { type: String },
  createdAt: { type: Date, default: Date.now },
}, { collection: 'clients' });  // ✅ Explicitly define collection name

module.exports = mongoose.model('Client', ClientSchema);