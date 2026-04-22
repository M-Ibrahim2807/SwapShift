import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Navbar.css';

export default function Navbar({ userName, role, onLogout }) {
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);

  const handleLogout = () => {
    setMenuOpen(false);
    onLogout();
  };

  return (
    <>
      <nav className="navbar">
        <div className="navbar-content">
          <div className="navbar-logo" onClick={() => navigate('/')}>
            SwapShift
          </div>

          <button
            className="navbar-hamburger"
            onClick={() => setMenuOpen(!menuOpen)}
            aria-label="Toggle menu"
          >
            <span />
            <span />
            <span />
          </button>

          <div className={`navbar-right ${menuOpen ? 'open' : ''}`}>
            <div className="navbar-user">
              <span className="navbar-username">{userName}</span>
              <span className={`navbar-role ${role === 'admin' ? 'admin' : 'employee'}`}>
                {role === 'admin' ? 'Admin' : 'Employee'}
              </span>
            </div>
            <button className="navbar-logout" onClick={handleLogout}>
              Logout
            </button>
          </div>
        </div>
      </nav>
      {menuOpen && (
        <div className="navbar-overlay" onClick={() => setMenuOpen(false)} />
      )}
    </>
  );
}
