// backend/controllers/authController.js
const User = require('../models/User');
const jwt = require('jsonwebtoken');
const { v4: uuidv4 } = require('uuid');
const bcrypt = require("bcrypt");

// ✅ Helper function to generate JWT token
const generateToken = (user) => {
  return jwt.sign(
    { userId: user._id, uuid: user.uuid },  // Include UUID in token payload for convenience
    process.env.JWT_SECRET,
    { expiresIn: '1h' }
  );
};

// ✅ User Registration
exports.register = async (req, res) => {
  try {
    const { username, password, phone, email } = req.body;

    // Check if the user already exists
    const existingUser = await User.findOne({ username });
    if (existingUser) {
      return res.status(400).json({ error: "Username already taken" });
    }

    // Create a new user with UUID
    const newUser = new User({
      username,
      password,
      phone,
      email,
      uuid: uuidv4(),
    });

    await newUser.save();

    // Generate JWT token
    const token = generateToken(newUser);

    res.status(201).json({
      message: "User registered successfully",
      token,
      uuid: newUser.uuid,
    });
  } catch (error) {
    console.error("Registration error:", error);
    res.status(500).json({ error: "Failed to register user" });
  }
};

// ✅ User Login
exports.login = async (req, res) => {
  console.log("Login request received:", req.body); // ✅ Check payload

  try {
    const { username, password } = req.body;
    const user = await User.findOne({ username });

    if (!user) {
      console.warn("User not found.");
      return res.status(401).json({ error: "Invalid credentials" });
    }

    const isPasswordValid = await bcrypt.compare(password, user.password);
    if (!isPasswordValid) {
      console.warn("Incorrect password.");
      return res.status(401).json({ error: "Invalid credentials" });
    }

    const token = generateToken(user);
    console.log("User authenticated:", { token, uuid: user.uuid });
    res.json({ token, uuid: user.uuid });

  } catch (error) {
    console.error("Login server error:", error);
    res.status(500).json({ error: "Internal server error" });
  }
};