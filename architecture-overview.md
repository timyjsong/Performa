# Sports Data Visualization Web App

This architecture provides a complete skeleton of a sports data visualization application, with core functionality in place and ready for expansion.

## Project Structure
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

## Technologies Used

### Backend
- Node.js with Express for the API server
- Axios for HTTP requests in scrapers
- Cheerio for HTML parsing

### Frontend
- React for the UI components
- React Router for navigation
- Recharts for data visualization
- Axios for API communication

### Data Storage
- Simple JSON files (for the starter version)
- Will be replaced with MongoDB/PostgreSQL in future iterations

## Initial Features
- Dashboard with player cards showing performance metrics
- Line charts showing performance over time
- Simple data scraper that generates sample data
- Detail view of individual player statistics

## Setup Instructions
See the README.md file for detailed setup and installation instructions.
