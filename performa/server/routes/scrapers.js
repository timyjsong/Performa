// server/routes/scrapers.js
const express = require('express');
const router = express.Router();
const nbaScraperController = require('../controllers/nbaScraper');

// Trigger NBA scraper
router.post('/nba', async (req, res) => {
  try {
    await nbaScraperController.scrapeNBAData();
    res.json({ message: 'NBA data scraping completed' });
  } catch (error) {
    res.status(500).json({ message: 'Error running scraper', error: error.message });
  }
});

// Get scraper status
router.get('/status', (req, res) => {
  res.json({
    nba: { status: 'idle', lastRun: null }
  });
});

module.exports = router;
