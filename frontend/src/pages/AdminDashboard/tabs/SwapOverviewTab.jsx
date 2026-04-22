import React from 'react';

export default function SwapOverviewTab({ showToast }) {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '60px 20px',
        textAlign: 'center',
      }}
    >
      <div style={{ fontSize: '60px', marginBottom: '24px' }}>📊</div>
      <h2 style={{ marginBottom: '12px', color: 'var(--color-primary)' }}>Swap Overview</h2>
      <p style={{ color: 'var(--color-text-muted)', fontSize: '16px', maxWidth: '400px' }}>
        Full swap management panel coming soon. Monitor all swap requests, approvals, and employee activity here.
      </p>
    </div>
  );
}
