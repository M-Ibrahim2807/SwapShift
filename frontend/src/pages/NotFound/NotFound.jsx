import React from 'react';
import { useNavigate } from 'react-router-dom';
import './NotFound.css';

export default function NotFound() {
  const navigate = useNavigate();

  return (
    <div className="not-found-page">
      <div className="not-found-content">
        <h1 className="not-found-title">404</h1>
        <h2>Page Not Found</h2>
        <p>The page you are looking for does not exist.</p>
        <button onClick={() => navigate('/')} className="not-found-button">
          Go Home
        </button>
      </div>
    </div>
  );
}
