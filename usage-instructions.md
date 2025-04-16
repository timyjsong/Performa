# NBA Data Scraper for Performa

This guide explains how to use the NBA data scraper that collects player statistics from Covers.com for your Performa visualization app.

## Installation and Setup

1. Make sure you have Python 3.9+ installed.

2. Navigate to the scraper directory:
   ```bash
   cd Performa/performa/server/scraper
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Checking Robots.txt Compliance

Before running the scraper, it's a good practice to check the robots.txt file of the target website to ensure your scraping is allowed:

```bash
python check_robots.py https://www.covers.com/sport/basketball/nba/players
```

This will show you the robots.txt rules and whether the URL is allowed to be scraped.

## Running the Scraper

### Option 1: Direct Execution

To run the scraper directly:

```bash
python run.py
```

This will:
1. Check the robots.txt file for permissions
2. Fetch all NBA teams
3. Fetch players for each team
4. Fetch statistics for each player
5. Save all data to JSON files in the `../data` directory

### Option 2: Run via API Server

The scraper can also be run through the FastAPI server:

1. Start the API server:
   ```bash
   uvicorn api:app --reload --port 5000
   ```

2. To trigger a scrape, make a POST request to the `/scrape` endpoint:
   ```bash
   curl -X POST http://localhost:5000/scrape
   ```

3. You can check the status of the scraper:
   ```bash
   curl http://localhost:5000/status
   ```

## Accessing the Data

After running the scraper, the following data files will be available:

- `../data/teams.json` - List of all NBA teams
- `../data/players.json` - Index of all players
- `../data/visualization_data.json` - Formatted data ready for visualization
- `../data/{team_id}.json` - Detailed data for each team and its players

You can access this data through the API server at:

- `/teams` - List all teams
- `/players` - List all players
- `/players/{player_id}` - Get details for a specific player
- `/visualization` - Get formatted data for visualization

## Advanced Features

### Rate Limiting

The scraper includes a sophisticated rate limiting system that:

1. Respects the crawl delay specified in robots.txt
2. Keeps track of requests per domain to prevent overwhelming the server
3. Automatically throttles requests when necessary

### Caching

The scraper caches:

1. Robots.txt rules to avoid repeated lookups
2. HTTP responses to minimize requests

## Integrating with the Frontend

To use this data in your React frontend, update your API service to point to the new Python backend:

```javascript
// client/src/services/api.js
import axios from 'axios';

const API_URL = 'http://localhost:5000';

export const getPlayers = async () => {
  const response = await axios.get(`${API_URL}/players`);
  return response.data;
};

export const getPlayer = async (id) => {
  const response = await axios.get(`${API_URL}/players/${id}`);
  return response.data;
};

export const getVisualizationData = async () => {
  const response = await axios.get(`${API_URL}/visualization`);
  return response.data;
};

export const triggerScrape = async () => {
  const response = await axios.post(`${API_URL}/scrape`);
  return response.data;
};
```

## Troubleshooting

- If you encounter any errors, check the `scraper.log` file for detailed information.
- If the scraper is being blocked, try reducing the request rate or using a VPN.
- Make sure your system has proper internet access and DNS resolution.

## Ethical Considerations

Remember that web scraping should be done responsibly:

1. Always respect robots.txt rules
2. Add reasonable delays between requests
3. Identify your scraper with a proper user agent
4. Only scrape publicly available data
5. Use the data in accordance with the website's terms of service
