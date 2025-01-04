import React from 'react';
import { Link } from 'react-router-dom';
import '../styles/navbar.css';

const Navbar = () => (
  <nav className="navbar">
    <div className="navbar-container">
      <Link to="/" className="navbar-brand">NBA Analytics 2010s</Link>
      <div className="navbar-links">
        <Link to="/cluster-analysis" className="navbar-link">Team Clusters</Link>
        <Link to="/seasonal-distribution" className="navbar-link">Season Analysis</Link>
        <Link to="/conference-comparison" className="navbar-link">Conference Stats</Link>
      </div>
    </div>
  </nav>
);

export default Navbar;