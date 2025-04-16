// server/server.js
const express = require('express');
const cors = require('cors');
const morgan = require('morgan');
const fs = require('fs');
const path = require('path');

// Import routes
const playerRoutes = require('./routes/players');
const scraperRoutes = require('./routes/scrapers');

// Initialize express app
const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(morgan('dev'));

// Routes
app.use('/api/players', playerRoutes);
app.use('/api/scrapers', scraperRoutes);

// Create data directory if it doesn't exist
const dataDir = path.join(__dirname, 'data');
if (!fs.existsSync(dataDir)) {
  fs.mkdirSync(dataDir);
}

// Default route
app.get('/', (req, res) => {
  res.json({
    message: 'Welcome to the Sports Data Visualization API'
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
