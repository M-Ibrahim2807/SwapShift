import React, { useEffect, useState } from 'react';
import {
  cancelCoverback,
  createCoverback,
  getCoverbackAlerts,
  getMyCoverbackPosts,
} from '../../../services/api';

export default function CoverbacksTab({ showToast }) {
  const [mode, setMode] = useState('');
  const [targetDate, setTargetDate] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [alerts, setAlerts] = useState([]);
  const [myPosts, setMyPosts] = useState([]);
  const [loadingLists, setLoadingLists] = useState(true);
  const [cancellingId, setCancellingId] = useState(null);

  useEffect(() => {
    loadLists();
  }, []);

  const loadLists = async () => {
    try {
      setLoadingLists(true);
      const [alertsRes, mineRes] = await Promise.all([
        getCoverbackAlerts(),
        getMyCoverbackPosts(),
      ]);
      setAlerts(Array.isArray(alertsRes.data) ? alertsRes.data : []);
      setMyPosts(Array.isArray(mineRes.data) ? mineRes.data : []);
    } catch (err) {
      showToast(err.response?.data?.detail || 'Failed to load coverbacks', 'error');
    } finally {
      setLoadingLists(false);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!mode) {
      showToast('Please choose Find Coverback or Offer Coverback', 'warning');
      return;
    }
    if (!targetDate) {
      showToast('Please select a date', 'warning');
      return;
    }

    try {
      setSubmitting(true);
      await createCoverback({
        coverback_type: mode,
        target_date: targetDate,
      });
      showToast('Coverback post created successfully', 'success');
      setTargetDate('');
      await loadLists();
    } catch (err) {
      showToast(err.response?.data?.detail || 'Failed to create coverback post', 'error');
    } finally {
      setSubmitting(false);
    }
  };

  const handleCancel = async (postId) => {
    try {
      setCancellingId(postId);
      const response = await cancelCoverback(postId);
      showToast('Coverback post cancelled', 'success');
      const whatsappLink = response?.data?.whatsapp_link;
      if (whatsappLink) {
        const openNow = window.confirm('Open WhatsApp redirect link?');
        if (openNow) {
          window.open(whatsappLink, '_blank', 'noopener,noreferrer');
        }
      }
      await loadLists();
    } catch (err) {
      showToast(err.response?.data?.detail || 'Failed to cancel coverback post', 'error');
    } finally {
      setCancellingId(null);
    }
  };

  return (
    <div style={{ display: 'grid', gap: '16px' }}>
      <div
        style={{
          background: 'var(--color-white)',
          borderRadius: 'var(--border-radius-md)',
          boxShadow: 'var(--shadow-sm)',
          padding: '16px',
        }}
      >
        <h3 style={{ marginBottom: '12px' }}>Coverbacks</h3>
        <div style={{ display: 'flex', gap: '8px', marginBottom: '12px' }}>
          <button
            type="button"
            onClick={() => setMode('FIND')}
            style={{
              padding: '8px 12px',
              borderRadius: 'var(--border-radius-sm)',
              border: '1px solid var(--color-border)',
              background: mode === 'FIND' ? 'var(--color-primary)' : 'var(--color-white)',
              color: mode === 'FIND' ? 'var(--color-white)' : 'var(--color-text)',
              cursor: 'pointer',
              fontSize: '13px',
              fontWeight: 600,
            }}
          >
            Find Coverback
          </button>
          <button
            type="button"
            onClick={() => setMode('OFFER')}
            style={{
              padding: '8px 12px',
              borderRadius: 'var(--border-radius-sm)',
              border: '1px solid var(--color-border)',
              background: mode === 'OFFER' ? 'var(--color-primary)' : 'var(--color-white)',
              color: mode === 'OFFER' ? 'var(--color-white)' : 'var(--color-text)',
              cursor: 'pointer',
              fontSize: '13px',
              fontWeight: 600,
            }}
          >
            Offer Coverback
          </button>
        </div>

        <form onSubmit={handleCreate} style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          <input
            type="date"
            value={targetDate}
            onChange={(e) => setTargetDate(e.target.value)}
            min={new Date().toISOString().split('T')[0]}
            style={{
              padding: '8px 10px',
              border: '1px solid var(--color-border)',
              borderRadius: 'var(--border-radius-sm)',
              fontSize: '14px',
            }}
          />
          <button
            type="submit"
            disabled={submitting}
            style={{
              padding: '8px 12px',
              background: 'var(--color-primary)',
              color: 'white',
              border: 'none',
              borderRadius: 'var(--border-radius-sm)',
              cursor: 'pointer',
              fontSize: '13px',
              fontWeight: 600,
            }}
          >
            {submitting ? 'Posting...' : 'Post'}
          </button>
        </form>
      </div>

      <div
        style={{
          background: 'var(--color-white)',
          borderRadius: 'var(--border-radius-md)',
          boxShadow: 'var(--shadow-sm)',
          padding: '16px',
        }}
      >
        <h4 style={{ marginBottom: '10px' }}>Open Coverback Alerts</h4>
        {loadingLists ? (
          <p style={{ color: 'var(--color-text-muted)', fontSize: '14px' }}>Loading...</p>
        ) : alerts.length === 0 ? (
          <p style={{ color: 'var(--color-text-muted)', fontSize: '14px' }}>No open coverback alerts.</p>
        ) : (
          <div style={{ display: 'grid', gap: '10px' }}>
            {alerts.map((post) => (
              <div
                key={post.id}
                style={{
                  border: '1px solid var(--color-border)',
                  borderRadius: 'var(--border-radius-sm)',
                  padding: '10px',
                  fontSize: '14px',
                }}
              >
                <div><strong>{post.employee_id}</strong> ({post.name || 'N/A'})</div>
                <div>Type: {post.coverback_type}</div>
                <div>Date: {post.target_date}</div>
                <div>Shift: {post.employee_shift}</div>
                <div>Contact: {post.contact_number}</div>
                {post.whatsapp_link && (
                  <button
                    type="button"
                    onClick={() => window.open(post.whatsapp_link, '_blank', 'noopener,noreferrer')}
                    style={{
                      marginTop: '8px',
                      padding: '6px 10px',
                      border: 'none',
                      borderRadius: 'var(--border-radius-sm)',
                      background: '#128c7e',
                      color: 'white',
                      fontSize: '12px',
                      cursor: 'pointer',
                    }}
                  >
                    Open WhatsApp
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      <div
        style={{
          background: 'var(--color-white)',
          borderRadius: 'var(--border-radius-md)',
          boxShadow: 'var(--shadow-sm)',
          padding: '16px',
        }}
      >
        <h4 style={{ marginBottom: '10px' }}>My Coverback Posts</h4>
        {loadingLists ? (
          <p style={{ color: 'var(--color-text-muted)', fontSize: '14px' }}>Loading...</p>
        ) : myPosts.length === 0 ? (
          <p style={{ color: 'var(--color-text-muted)', fontSize: '14px' }}>No coverback posts yet.</p>
        ) : (
          <div style={{ display: 'grid', gap: '10px' }}>
            {myPosts.map((post) => (
              <div
                key={post.id}
                style={{
                  border: '1px solid var(--color-border)',
                  borderRadius: 'var(--border-radius-sm)',
                  padding: '10px',
                  fontSize: '14px',
                }}
              >
                <div>Type: {post.coverback_type}</div>
                <div>Date: {post.target_date}</div>
                <div>Status: {post.status}</div>
                {post.whatsapp_link && (
                  <button
                    type="button"
                    onClick={() => window.open(post.whatsapp_link, '_blank', 'noopener,noreferrer')}
                    style={{
                      marginTop: '8px',
                      marginRight: '8px',
                      padding: '6px 10px',
                      border: 'none',
                      borderRadius: 'var(--border-radius-sm)',
                      background: '#128c7e',
                      color: 'white',
                      fontSize: '12px',
                      cursor: 'pointer',
                    }}
                  >
                    Open WhatsApp
                  </button>
                )}
                {post.status === 'OPEN' && (
                  <button
                    type="button"
                    onClick={() => handleCancel(post.id)}
                    disabled={cancellingId === post.id}
                    style={{
                      marginTop: '8px',
                      padding: '6px 10px',
                      border: 'none',
                      borderRadius: 'var(--border-radius-sm)',
                      background: 'var(--color-error)',
                      color: 'white',
                      fontSize: '12px',
                      cursor: 'pointer',
                    }}
                  >
                    {cancellingId === post.id ? 'Cancelling...' : 'Cancel'}
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
