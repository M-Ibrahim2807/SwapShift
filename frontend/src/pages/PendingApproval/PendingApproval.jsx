import React from 'react';
import { useNavigate } from 'react-router-dom';
import './PendingApproval.css';

export default function PendingApproval() {
  const navigate = useNavigate();

  return (
    <div className="pending-page">
      <div className="pending-content">
        <div className="pending-icon">⏱</div>
        <h1 className="pending-title">Registration Submitted!</h1>
        <p className="pending-text">
          Your account is pending admin approval. You will be able to login once approved.
        </p>
        <button
          className="pending-button"
          onClick={() => navigate('/')}
        >
          Back to Login
        </button>
      </div>
    </div>
  );
}
