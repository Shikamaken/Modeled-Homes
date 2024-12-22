require('dotenv').config();
const mongoose = require('mongoose');

const connectDB = async () => {
  try {
    // Ensure MONGODB_URI is set
    const mongoUri = process.env.MONGODB_URI;
    if (!mongoUri) {
      console.error('Error: MONGODB_URI is not set in the environment variables.');
      process.exit(1); // Exit if MONGODB_URI is not set
    }

    // Connect to MongoDB Atlas
    await mongoose.connect(mongoUri);
    console.log('MongoDB connected successfully');
  } catch (err) {
    console.error('MongoDB connection error:', err);
    process.exit(1); // Exit the process on connection failure
  }
};

module.exports = connectDB;