import React from 'react';
import './Toast.css';

export default function Toast({ message, type = 'info', onClose }) {
  const getColor = () => {
    switch (type) {
      case 'success':
        return 'var(--color-success)';
      case 'error':
        return 'var(--color-error)';
      case 'warning':
        return 'var(--color-warning)';
      case 'info':
      default:
        return 'var(--color-info)';
    }
  };

  return (
    <div className={`toast toast-${type}`} style={{ borderLeftColor: getColor() }}>
      <span className="toast-message">{message}</span>
      <button className="toast-close" onClick={onClose} aria-label="Close">
        ×
      </button>
    </div>
  );
}
