require('dotenv').config();
const { MongoClient } = require('mongodb');

let client;
let db;

async function connectDB() {
  if (!client) {
    client = new MongoClient(process.env.MONGODB_URI, { // Updated here
      useNewUrlParser: true,
      useUnifiedTopology: true,
    });
    await client.connect();
    db = client.db('ModeledHomes');
  }
  return db;
}

module.exports = { connectDB };
