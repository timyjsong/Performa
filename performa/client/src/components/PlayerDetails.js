// client/src/components/PlayerDetails.js
import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './PlayerDetails.css';

function PlayerDetails() {
  const { id } = useParams();
  const [player, setPlayer] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPlayerDetails = async () => {
      try {
        const response = await axios.get(`/api/players/${id}`);
        setPlayer(response.data);
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    fetchPlayerDetails();
  }, [id]);

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  if (!player) {
    return <div className="not-found">Player not found</div>;
  }

  return (
    <div className="player-details">
      <div className="back-link">
        <Link to="/">← Back to Dashboard</Link>
      </div>

      <div className="player-header">
        <h1>{player.name}</h1>
        <div className="player-info">
          <span className="team">{player.team}</span>
          <span className="position">{player.position}</span>
          <span className="sport">{player.sport}</span>
        </div>
      </div>

      <div className="stats-container">
        <div className="stat-card">
          <h3>Points</h3>
          <div className="chart">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={player.stats.points} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="value" name="Points" stroke="#8884d8" activeDot={{ r: 8 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="stat-card">
          <h3>Rebounds</h3>
          <div className="chart">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={player.stats.rebounds} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="value" name="Rebounds" stroke="#82ca9d" activeDot={{ r: 8 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="stat-card">
          <h3>Assists</h3>
          <div className="chart">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={player.stats.assists} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="value" name="Assists" stroke="#ffc658" activeDot={{ r: 8 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}

export default PlayerDetails;
