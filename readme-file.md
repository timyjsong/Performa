# Sports Data Visualization App

A web application for scraping, visualizing, and tracking sports player statistics with interactive charts and performance metrics.

![Sports Visualization App](https://via.placeholder.com/1200x600)

## Features

- Scrape historical player data from sports websites
- Visualize performance metrics with interactive charts
- Track player statistics over time
- Compare player performances with visually appealing graphs
- Robinhood-style percentage indicators and performance charts

## Project Structure

- **client/**: React frontend application
- **server/**: Node.js backend API

## Getting Started

### Prerequisites

- Node.js (v14 or higher)
- npm (v6 or higher)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/timyjsong/Performa.git
   cd performa
   ```

2. **Set up the backend**
   ```bash
   # Navigate to the server directory
   cd server
   
   # Install dependencies
   npm install
   
   # Start the server
   npm run dev
   ```

3. **Set up the frontend**
   ```bash
   # Open a new terminal window
   # Navigate to the client directory
   cd client
   
   # Install dependencies
   npm install
   
   # Start the development server
   npm start
   ```

4. **Open your browser** and navigate to `http://localhost:3000`

### Using the Application

1. Visit the dashboard at `http://localhost:3000`
2. Click the "Scrape NBA Data" button to load sample player data
3. View player cards showing performance metrics
4. Click "View Details" to see detailed statistics with interactive charts

## Development Info

- Backend API runs on port 5000
- Frontend development server runs on port 3000
- The frontend proxy is configured to redirect API requests to the backend

## Future Enhancements

1. **Data Sources**
   - Implement real web scrapers for different sports leagues
   - Add connection to official sports APIs
   - Support for multiple data sources

2. **Visualization Features**
   - Add more chart types (bar charts, radar charts, etc.)
   - Implement head-to-head player comparisons
   - Create team performance dashboards

3. **User Features**
   - User authentication and profiles
   - Saved favorite players and custom dashboards
   - Notification system for player performance milestones

4. **Infrastructure**
   - Database implementation (MongoDB/PostgreSQL)
   - Caching layer for API responses
   - Scheduled scraping jobs

## Folder Structure

```
performa/
├── client/                     # Frontend React application
│   ├── public/                 # Static files
│   ├── src/
│   │   ├── components/         # UI components
│   │   ├── services/           # API services
│   │   ├── App.js              # Main app component
│   │   └── index.js            # Entry point
│   └── package.json            # Frontend dependencies
│
├── server/                     # Backend Node.js application
│   ├── controllers/            # API controllers
│   ├── data/                   # Local data storage
│   ├── routes/                 # API routes
│   ├── scrapers/               # Data scrapers
│   ├── server.js               # Main server file
│   └── package.json            # Backend dependencies
│
└── README.md                   # Project documentation
```

## License

MIT
