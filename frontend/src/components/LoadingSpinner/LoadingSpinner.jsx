import React from 'react';
import './LoadingSpinner.css';

export default function LoadingSpinner({ size = 'md', fullPage = false }) {
  return (
    <div className={`spinner-wrapper ${fullPage ? 'full-page' : ''}`}>
      <div className={`spinner spinner-${size}`} />
    </div>
  );
}
