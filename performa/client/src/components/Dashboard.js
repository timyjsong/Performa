// client/src/components/Dashboard.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import PlayerCard from './PlayerCard';
import './Dashboard.css';

function Dashboard() {
  const [players, setPlayers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPlayers = async () => {
      try {
        const response = await axios.get('/api/players');
        setPlayers(response.data);
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    fetchPlayers();
  }, []);

  const handleScrapeData = async () => {
    try {
      setLoading(true);
      await axios.post('/api/scrapers/nba');
      const response = await axios.get('/api/players');
      setPlayers(response.data);
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  return (
    <div className="dashboard">
      <h1>Sports Performance Dashboard</h1>
      <div className="actions">
        <button onClick={handleScrapeData}>Scrape NBA Data</button>
      </div>

      {players.length === 0 ? (
        <div className="no-data">
          <p>No player data available. Click the button above to scrape some sample data.</p>
        </div>
      ) : (
        <div className="player-grid">
          {players.map(player => (
            <PlayerCard key={player.id} player={player} />
          ))}
        </div>
      )}
    </div>
  );
}

export default Dashboard;
