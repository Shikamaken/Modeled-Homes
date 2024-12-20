const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
require('dotenv').config();

const app = express();
const port = process.env.PORT || 4000;

app.use(cors());
app.use(express.json());

mongoose.connect(process.env.MONGODB_URI)
  .then(() => console.log('MongoDB connected'))
  .catch(err => console.error('MongoDB connection error:', err));

const hvacRoutes = require('./routes/hvac');
app.use('/api/hvac', hvacRoutes);

const authRoutes = require('./routes/auth');
app.use('/api/auth', authRoutes);

const embeddingsRoute = require('./routes/embeddings');
app.use('/api/embeddings', embeddingsRoute);

app.listen(port, () => {
  console.log(`Server is running on port: ${port}`);
});
