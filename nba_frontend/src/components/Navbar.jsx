import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import '../styles/navbar.css';

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const location = useLocation();

  const isActive = (path) => location.pathname === path ? 'active' : '';

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-brand">
          NBA Analytics 2010s
        </Link>

        <button 
          className="navbar-menu-button"
          onClick={() => setIsOpen(!isOpen)}
        >
          <svg viewBox="0 0 20 20" width="24" height="24">
            <path 
              fill="currentColor" 
              d={isOpen 
                ? "M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" 
                : "M3 5a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 5a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 5a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z"
              }
            />
          </svg>
        </button>

        <div className={`navbar-links ${isOpen ? 'open' : ''}`}>
          <Link 
            to="/cluster-analysis" 
            className={`navbar-link ${isActive('/cluster-analysis')}`}
            onClick={() => setIsOpen(false)}
          >
            Team Clusters
          </Link>
          <Link 
            to="/seasonal-distribution" 
            className={`navbar-link ${isActive('/seasonal-distribution')}`}
            onClick={() => setIsOpen(false)}
          >
            Season Analysis
          </Link>
          <Link 
            to="/conference-comparison" 
            className={`navbar-link ${isActive('/conference-comparison')}`}
            onClick={() => setIsOpen(false)}
          >
            Conference Stats
          </Link>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;