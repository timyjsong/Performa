// server/routes/players.js
const express = require('express');
const router = express.Router();
const fs = require('fs');
const path = require('path');

const dataFile = path.join(__dirname, '../data/players.json');

// Initialize with empty data if file doesn't exist
if (!fs.existsSync(dataFile)) {
  fs.writeFileSync(dataFile, JSON.stringify({ players: [] }));
}

// Get all players
router.get('/', (req, res) => {
  try {
    const data = JSON.parse(fs.readFileSync(dataFile));
    res.json(data.players);
  } catch (error) {
    res.status(500).json({ message: 'Error reading player data', error: error.message });
  }
});

// Get a specific player by ID
router.get('/:id', (req, res) => {
  try {
    const data = JSON.parse(fs.readFileSync(dataFile));
    const player = data.players.find(p => p.id === parseInt(req.params.id));

    if (!player) {
      return res.status(404).json({ message: 'Player not found' });
    }

    res.json(player);
  } catch (error) {
    res.status(500).json({ message: 'Error reading player data', error: error.message });
  }
});

module.exports = router;
