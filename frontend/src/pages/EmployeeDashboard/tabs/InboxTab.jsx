import React, { useEffect, useState } from 'react';
import { decideSwap, getSwapInbox } from '../../../services/api';
import LoadingSpinner from '../../../components/LoadingSpinner/LoadingSpinner';

export default function InboxTab({ showToast, onSwapAccepted }) {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [decidingId, setDecidingId] = useState(null);
  const [pollInterval, setPollInterval] = useState(null);

  useEffect(() => {
    fetchInbox();
    // Set up auto-refresh every 5 seconds
    const interval = setInterval(fetchInbox, 5000);
    setPollInterval(interval);

    return () => {
      if (interval) clearInterval(interval);
    };
  }, []);

  const fetchInbox = async () => {
    try {
      const response = await getSwapInbox();
      setRequests(Array.isArray(response.data) ? response.data : []);
    } catch (err) {
      showToast('Failed to load inbox', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleDecide = async (requestId, decision) => {
    try {
      setDecidingId(requestId);
      await decideSwap(requestId, decision);
      showToast(decision === 'ACCEPT' ? 'Swap accepted!' : 'Swap declined', decision === 'ACCEPT' ? 'success' : 'error');
      setRequests((prev) => prev.filter((r) => r.id !== requestId));
      
      // Notify parent to refresh timetable if swap was accepted
      if (decision === 'ACCEPT' && onSwapAccepted) {
        onSwapAccepted();
      }
    } catch (err) {
      showToast(err.response?.data?.detail || 'Action failed', 'error');
    } finally {
      setDecidingId(null);
    }
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  if (requests.length === 0) {
    return (
      <div style={{ textAlign: 'center', color: 'var(--color-text-muted)', padding: '40px 20px' }}>
        No pending swap requests.
      </div>
    );
  }

  return (
    <div style={{ display: 'grid', gap: '16px' }}>
      {requests.map((req) => (
        <div
          key={req.id}
          style={{
            background: 'var(--color-white)',
            padding: '20px',
            borderRadius: 'var(--border-radius-md)',
            boxShadow: 'var(--shadow-sm)',
          }}
        >
          <h4 style={{ marginBottom: '12px' }}>Request #{req.id}</h4>
          <p style={{ fontSize: '14px', color: 'var(--color-text-muted)', marginBottom: '8px' }}>
            Type: {req.swap_type}
          </p>
          <p style={{ fontSize: '14px', color: 'var(--color-text-muted)', marginBottom: '8px' }}>
            Date Range: {req.start_date} to {req.end_date}
          </p>
          <p style={{ fontSize: '14px', color: 'var(--color-text-muted)', marginBottom: '16px' }}>
            From Employee ID: {req.requester_id}
          </p>
          <div style={{ display: 'flex', gap: '12px' }}>
            <button
              onClick={() => handleDecide(req.id, 'ACCEPT')}
              disabled={decidingId === req.id}
              style={{
                flex: 1,
                padding: '10px',
                background: 'var(--color-success)',
                color: 'white',
                border: 'none',
                borderRadius: 'var(--border-radius-sm)',
                fontWeight: 500,
                cursor: 'pointer',
                fontSize: '14px',
                transition: 'var(--transition)',
              }}
            >
              Accept
            </button>
            <button
              onClick={() => handleDecide(req.id, 'REJECT')}
              disabled={decidingId === req.id}
              style={{
                flex: 1,
                padding: '10px',
                background: 'var(--color-error)',
                color: 'white',
                border: 'none',
                borderRadius: 'var(--border-radius-sm)',
                fontWeight: 500,
                cursor: 'pointer',
                fontSize: '14px',
                transition: 'var(--transition)',
              }}
            >
              Decline
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}

  const handleDecide = async (requestId, decision) => {
    try {
      setDecidingId(requestId);
      await decideSwap(requestId, decision);
      showToast(decision === 'ACCEPT' ? 'Swap accepted!' : 'Swap declined', decision === 'ACCEPT' ? 'success' : 'error');
      setRequests((prev) => prev.filter((r) => r.id !== requestId));
    } catch (err) {
      showToast(err.response?.data?.detail || 'Action failed', 'error');
    } finally {
      setDecidingId(null);
    }
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  if (requests.length === 0) {
    return (
      <div style={{ textAlign: 'center', color: 'var(--color-text-muted)', padding: '40px 20px' }}>
        No pending swap requests.
      </div>
    );
  }

  return (
    <div style={{ display: 'grid', gap: '16px' }}>
      {requests.map((req) => (
        <div
          key={req.id}
          style={{
            background: 'var(--color-white)',
            padding: '20px',
            borderRadius: 'var(--border-radius-md)',
            boxShadow: 'var(--shadow-sm)',
          }}
        >
          <h4 style={{ marginBottom: '12px' }}>Request #{req.id}</h4>
          <p style={{ fontSize: '14px', color: 'var(--color-text-muted)', marginBottom: '8px' }}>
            Type: {req.swap_type}
          </p>
          <p style={{ fontSize: '14px', color: 'var(--color-text-muted)', marginBottom: '8px' }}>
            Date Range: {req.start_date} to {req.end_date}
          </p>
          <p style={{ fontSize: '14px', color: 'var(--color-text-muted)', marginBottom: '16px' }}>
            From Employee ID: {req.requester_id}
          </p>
          <div style={{ display: 'flex', gap: '12px' }}>
            <button
              onClick={() => handleDecide(req.id, 'ACCEPT')}
              disabled={decidingId === req.id}
              style={{
                flex: 1,
                padding: '10px',
                background: 'var(--color-success)',
                color: 'white',
                border: 'none',
                borderRadius: 'var(--border-radius-sm)',
                fontWeight: 500,
                cursor: 'pointer',
                fontSize: '14px',
                transition: 'var(--transition)',
              }}
            >
              Accept
            </button>
            <button
              onClick={() => handleDecide(req.id, 'REJECT')}
              disabled={decidingId === req.id}
              style={{
                flex: 1,
                padding: '10px',
                background: 'var(--color-error)',
                color: 'white',
                border: 'none',
                borderRadius: 'var(--border-radius-sm)',
                fontWeight: 500,
                cursor: 'pointer',
                fontSize: '14px',
                transition: 'var(--transition)',
              }}
            >
              Decline
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
