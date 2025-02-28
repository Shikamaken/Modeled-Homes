// backend/controllers/userController.js
const User = require("../models/User");

// ✅ Create a new user or team
exports.createUser = async (req, res) => {
  try {
    console.log("📥 Received user/team creation request:", req.body);
    const { name } = req.body;

    if (!name) {
      console.warn("🚫 Missing name field in request.");
      return res.status(400).json({ error: "Name is required." });
    }

    const newUser = new User({ name });
    await newUser.save();

    console.log("✅ User/Team created:", newUser);
    res.status(201).json(newUser);
  } catch (err) {
    console.error("Error creating user:", err);
    res.status(500).json({ error: "Failed to create user." });
  }
};

// ✅ Search for users or teams
exports.searchUsers = async (req, res) => {
  try {
    const { query } = req.query;

    console.log("🔍 Searching users with query:", query);

    // ✅ Log all users before filtering
    const allUsers = await User.find();
    console.log("📍 All users in DB:", allUsers);

    const users = await User.find({
      username: { $regex: query, $options: "i" },  // ✅ Case-insensitive search
    }).limit(10);

    console.log("🔎 Filtered users:", users);
    res.json({ users });
  } catch (err) {
    console.error("Error searching users:", err);
    res.status(500).json({ error: "Failed to search users." });
  }
};