// client/src/components/PlayerCard.js
import React from 'react';
import { Link } from 'react-router-dom';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import './PlayerCard.css';

function PlayerCard({ player }) {
  // Get the most recent point value
  const latestPointsData = player.stats.points[player.stats.points.length - 1];
  const previousPointsData = player.stats.points[player.stats.points.length - 2];

  // Calculate percentage change
  const percentChange = previousPointsData ?
    ((latestPointsData.value - previousPointsData.value) / previousPointsData.value * 100).toFixed(1) : 0;

  // Determine if it's positive or negative change
  const isPositive = percentChange >= 0;

  return (
    <div className="player-card">
      <div className="player-header">
        <h2>{player.name}</h2>
        <div className="player-meta">
          <span className="team">{player.team}</span>
          <span className="position">{player.position}</span>
        </div>
      </div>

      <div className="stat-highlight">
        <div className="stat-value">{latestPointsData.value}</div>
        <div className={`percent-change ${isPositive ? 'positive' : 'negative'}`}>
          {isPositive ? '↑' : '↓'} {Math.abs(percentChange)}%
        </div>
        <div className="stat-label">Points</div>
      </div>

      <div className="chart-container">
        <ResponsiveContainer width="100%" height={100}>
          <LineChart data={player.stats.points}>
            <Line
              type="monotone"
              dataKey="value"
              stroke="#8884d8"
              strokeWidth={2}
              dot={false}
              isAnimationActive={false}
            />
            <XAxis dataKey="date" hide={true} />
            <YAxis hide={true} domain={['dataMin - 5', 'dataMax + 5']} />
            <Tooltip />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <Link to={`/player/${player.id}`} className="view-details">
        View Details
      </Link>
    </div>
  );
}

export default PlayerCard;
