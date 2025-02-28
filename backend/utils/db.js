// backend/utils/db.js
const path = require('path');
require('dotenv').config({ path: path.resolve(__dirname, '../../.env') });  // ✅ Absolute path to avoid issues
const mongoose = require('mongoose');

const connectDB = async () => {
  try {
    const mongoUri = process.env.MONGODB_URI;
    if (!mongoUri) {
      console.error('❌ Error: MONGODB_URI is not set in the environment variables.');
      process.exit(1);
    }

    const conn = await mongoose.connect(mongoUri);

    console.log(`✅ Connected to MongoDB at ${conn.connection.host}, Database: ${conn.connection.name}`);
  } catch (err) {
    console.error('❌ MongoDB connection error:', err.message);
    process.exit(1);
  }
};

module.exports = connectDB;