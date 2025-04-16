// client/src/components/Navbar.js
import React from 'react';
import { Link } from 'react-router-dom';
import './Navbar.css';

function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">
          SportViz <span className="icon">📊</span>
        </Link>
        <ul className="nav-menu">
          <li className="nav-item">
            <Link to="/" className="nav-links">
              Dashboard
            </Link>
          </li>
          <li className="nav-item">
            <Link to="/" className="nav-links">
              NBA
            </Link>
          </li>
          <li className="nav-item">
            <Link to="/" className="nav-links">
              NFL
            </Link>
          </li>
          <li className="nav-item">
            <Link to="/" className="nav-links">
              MLB
            </Link>
          </li>
        </ul>
      </div>
    </nav>
  );
}

export default Navbar;
