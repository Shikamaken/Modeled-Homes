// backend/controllers/locationController.js
const Location = require("../models/Location");

// ✅ Create a new location
exports.createLocation = async (req, res) => {
  try {
    console.log("📥 Received request body:", req.body);
    
    const { clientId, addressLine1, addressLine2, city, state, zip } = req.body;

    if (!clientId || !addressLine1 || !city || !state || !zip) {
      return res.status(400).json({ error: "All fields are required." });
    }

    const newLocation = new Location({
      client: clientId,
      addressLine1,
      addressLine2,
      city,
      state,
      zip,
    });
    await newLocation.save();

    res.status(201).json(newLocation);
  } catch (err) {
    console.error("Error creating location:", err);
    res.status(500).json({ error: "Failed to create location." });
  }
};

// ✅ Search for locations by client ID
exports.searchLocations = async (req, res) => {
  try {
    const { clientId, query } = req.query;
    console.log("🔍 Searching locations for client:", clientId, "Query:", query);

    if (!clientId) {
      console.warn("🚫 Missing clientId in request.");
      return res.status(400).json({ error: "Client ID is required." });
    }

    // ✅ Log all locations for debugging
    const allClientLocations = await Location.find({ client: clientId });
    console.log("📍 All locations for client:", allClientLocations);

    // Apply search filter
    const locations = await Location.find({
      client: clientId,
      $or: [
        { addressLine1: { $regex: query, $options: "i" } },
        { city: { $regex: query, $options: "i" } },
      ],
    }).limit(10);

    console.log("🔎 Filtered locations:", locations);
    res.json({ locations });
  } catch (err) {
    console.error("🔥 Error searching locations:", err);
    res.status(500).json({ error: "Failed to fetch locations." });
  }
};