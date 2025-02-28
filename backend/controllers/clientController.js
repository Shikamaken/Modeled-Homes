// backend/controllers/clientController.js
const Client = require("../models/Client");

// ✅ Create a new client
exports.createClient = async (req, res) => {
  console.log('📥 Received client creation request:', req.body);
  try {
    const { name } = req.body;

    if (!name) {
      console.error("🚫 Client name is required.");
      return res.status(400).json({ error: "Client name is required." });
    }

    const existingClient = await Client.findOne({ name });
    if (existingClient) {
      console.warn(`🚫 Client with name "${name}" already exists.`);
      return res.status(409).json({ error: "Client already exists." });
    }

    const newClient = new Client({ name });
    await newClient.save();
    const savedClient = await newClient.save()    

    console.log('✅ Client created successfully:', savedClient);
    res.status(201).json({ message: 'Client created successfully!', client: { name } });
  } catch (err) {
    console.error("Error creating client:", err);
    res.status(500).json({ error: "Failed to create client." });
  }
};

// ✅ Search for clients
exports.searchClients = async (req, res) => {
  try {
    const { query } = req.query;
    console.log("🔍 Searching clients with query:", query);

    const clients = await Client.find({
      name: { $regex: new RegExp(query, "i") },
    });

    console.log("🔎 Found clients:", clients);  // ✅ Confirm found clients

    if (clients.length === 0) {
      console.warn("⚠️ No clients found for query:", query);
    }

    res.json({ clients });  // ✅ Ensure response includes { clients: [...] }
  } catch (err) {
    console.error("❌ Error searching clients:", err);
    res.status(500).json({ error: "Failed to search clients." });
  }
};