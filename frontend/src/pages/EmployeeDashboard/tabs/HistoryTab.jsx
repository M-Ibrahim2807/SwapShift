import React, { useEffect, useState } from 'react';
import { getSwapHistory } from '../../../services/api';
import LoadingSpinner from '../../../components/LoadingSpinner/LoadingSpinner';

const getStatusColor = (status) => {
  switch ((status || '').toUpperCase()) {
    case 'ACCEPTED':
      return { bg: 'var(--color-success-light)', text: '#166534' };
    case 'REJECTED':
      return { bg: 'var(--color-error-light)', text: '#991b1b' };
    case 'PENDING':
      return { bg: 'var(--color-warning-light)', text: '#b45309' };
    case 'EXPIRED':
      return { bg: '#e5e7eb', text: '#374151' };
    default:
      return { bg: 'var(--color-border)', text: 'var(--color-text-muted)' };
  }
};

export default function HistoryTab({ showToast }) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      setLoading(true);
      const response = await getSwapHistory();
      setHistory(Array.isArray(response.data) ? response.data : []);
    } catch (err) {
      showToast('Failed to load history', 'error');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  if (history.length === 0) {
    return (
      <div style={{ textAlign: 'center', color: 'var(--color-text-muted)', padding: '40px 20px' }}>
        No swap history found.
      </div>
    );
  }

  return (
    <div
      style={{
        background: 'var(--color-white)',
        borderRadius: 'var(--border-radius-md)',
        boxShadow: 'var(--shadow-sm)',
        overflow: 'auto',
      }}
    >
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr style={{ background: 'var(--color-bg)', borderBottom: '1px solid var(--color-border)' }}>
            <th style={{ padding: '12px 16px', textAlign: 'left', fontWeight: 600, fontSize: '14px' }}>Request</th>
            <th style={{ padding: '12px 16px', textAlign: 'left', fontWeight: 600, fontSize: '14px' }}>Type</th>
            <th style={{ padding: '12px 16px', textAlign: 'left', fontWeight: 600, fontSize: '14px' }}>Date Range</th>
            <th style={{ padding: '12px 16px', textAlign: 'left', fontWeight: 600, fontSize: '14px' }}>Status</th>
            <th style={{ padding: '12px 16px', textAlign: 'left', fontWeight: 600, fontSize: '14px' }}>Created</th>
          </tr>
        </thead>
        <tbody>
          {history.map((item, idx) => {
            const colors = getStatusColor(item.status);
            return (
              <tr
                key={item.id}
                style={{
                  borderBottom: '1px solid var(--color-border)',
                  background: idx % 2 === 0 ? 'var(--color-white)' : 'var(--color-bg)',
                }}
              >
                <td style={{ padding: '12px 16px', fontSize: '14px' }}>#{item.id}</td>
                <td style={{ padding: '12px 16px', fontSize: '14px' }}>{item.swap_type}</td>
                <td style={{ padding: '12px 16px', fontSize: '14px' }}>
                  {item.start_date} to {item.end_date}
                </td>
                <td style={{ padding: '12px 16px' }}>
                  <span
                    style={{
                      display: 'inline-block',
                      padding: '4px 12px',
                      borderRadius: '12px',
                      fontSize: '12px',
                      fontWeight: 600,
                      background: colors.bg,
                      color: colors.text,
                    }}
                  >
                    {item.status}
                  </span>
                </td>
                <td style={{ padding: '12px 16px', fontSize: '14px' }}>
                  {new Date(item.created_at).toLocaleString()}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
