import React from 'react';
import { Link, useLocation } from 'react-router-dom';

function Footer() {
  const location = useLocation();

  // Don't render footer on login page (it has its own footer)
  if (location.pathname === '/login') {
    return null;
  }
  return (
    <footer>
      <div className="container">
        <div className="footer-links">
          <Link to="/">Dashboard</Link>
          <Link to="/calendar">Calendar</Link>
          <Link to="/management">HR Management</Link>
          <Link to="/about">About Us</Link>
          <Link to="/company">Company Profile</Link>
        </div>
        <p className="footer-text">&copy; 2025 Resumify. All rights reserved. | support@resumify.com</p>
      </div>
    </footer>
  );
}

export default Footer;