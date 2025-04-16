// server/controllers/nbaScraper.js
const axios = require('axios');
const cheerio = require('cheerio');
const fs = require('fs');
const path = require('path');

const dataFile = path.join(__dirname, '../data/players.json');

// Simple NBA data scraper
const scrapeNBAData = async () => {
  try {
    // This is a very basic scraper that just creates dummy data
    // In a real implementation, you would scrape actual data from sports websites

    // Load existing data
    let data = { players: [] };
    if (fs.existsSync(dataFile)) {
      data = JSON.parse(fs.readFileSync(dataFile));
    }

    // Add some dummy NBA player data
    const dummyPlayers = [
      {
        id: 1,
        name: "LeBron James",
        team: "Los Angeles Lakers",
        sport: "NBA",
        position: "Forward",
        stats: {
          points: generateHistoricalData(25, 35),
          rebounds: generateHistoricalData(7, 10),
          assists: generateHistoricalData(7, 11)
        }
      },
      {
        id: 2,
        name: "Stephen Curry",
        team: "Golden State Warriors",
        sport: "NBA",
        position: "Guard",
        stats: {
          points: generateHistoricalData(20, 33),
          rebounds: generateHistoricalData(4, 7),
          assists: generateHistoricalData(5, 8)
        }
      }
    ];

    // Merge with existing data
    data.players = [...dummyPlayers, ...data.players.filter(p => p.sport !== "NBA")];

    // Save to file
    fs.writeFileSync(dataFile, JSON.stringify(data, null, 2));

    return dummyPlayers;
  } catch (error) {
    console.error("Error scraping NBA data:", error);
    throw error;
  }
};

// Helper function to generate random historical data
function generateHistoricalData(min, max) {
  const today = new Date();
  const data = [];

  // Generate data for the past 30 days
  for (let i = 30; i >= 0; i--) {
    const date = new Date();
    date.setDate(today.getDate() - i);

    data.push({
      date: date.toISOString().split('T')[0],
      value: parseFloat((Math.random() * (max - min) + min).toFixed(1))
    });
  }

  return data;
}

module.exports = {
  scrapeNBAData
};
