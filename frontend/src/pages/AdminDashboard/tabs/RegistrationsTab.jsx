import React, { useState, useEffect } from 'react';
import { getPendingRegistrations, approveRegistration, rejectRegistration } from '../../../services/api';
import LoadingSpinner from '../../../components/LoadingSpinner/LoadingSpinner';

export default function RegistrationsTab({ showToast, onCountChange }) {
  const [registrations, setRegistrations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actingId, setActingId] = useState(null);

  useEffect(() => {
    fetchRegistrations();
  }, []);

  const fetchRegistrations = async () => {
    try {
      setLoading(true);
      const response = await getPendingRegistrations();
      const rows = Array.isArray(response.data) ? response.data : [];
      setRegistrations(rows);
      if (onCountChange) {
        onCountChange(rows.length);
      }
    } catch (err) {
      showToast('Failed to load registrations', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (employeeId) => {
    try {
      setActingId(employeeId);
      await approveRegistration(employeeId);
      showToast('Employee approved successfully!', 'success');
      setRegistrations((prev) => prev.filter((r) => r.employee_id !== employeeId));
      if (onCountChange) {
        onCountChange((prev) => Math.max(0, prev - 1));
      }
    } catch (err) {
      showToast(err.response?.data?.detail || 'Action failed', 'error');
    } finally {
      setActingId(null);
    }
  };

  const handleReject = async (employeeId) => {
    try {
      setActingId(employeeId);
      await rejectRegistration(employeeId);
      showToast('Employee rejected', 'error');
      setRegistrations((prev) => prev.filter((r) => r.employee_id !== employeeId));
      if (onCountChange) {
        onCountChange((prev) => Math.max(0, prev - 1));
      }
    } catch (err) {
      showToast(err.response?.data?.detail || 'Action failed', 'error');
    } finally {
      setActingId(null);
    }
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  if (registrations.length === 0) {
    return (
      <div style={{ textAlign: 'center', color: 'var(--color-text-muted)', padding: '40px 20px' }}>
        No pending registrations.
      </div>
    );
  }

  return (
    <div>
      <p style={{ marginBottom: '24px', color: 'var(--color-text-muted)', fontSize: '14px' }}>
        {registrations.length} pending registration{registrations.length !== 1 ? 's' : ''}
      </p>
      <div style={{ display: 'grid', gap: '16px' }}>
        {registrations.map((emp) => (
          <div
            key={emp.employee_id}
            style={{
              background: 'var(--color-white)',
              padding: '24px',
              borderRadius: 'var(--border-radius-md)',
              boxShadow: 'var(--shadow-sm)',
            }}
          >
            <h3 style={{ marginBottom: '16px' }}>{emp.employee_id}</h3>
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                gap: '16px',
                marginBottom: '20px',
                fontSize: '14px',
              }}
            >
              <div>
                <span style={{ color: 'var(--color-text-muted)', display: 'block', marginBottom: '4px' }}>
                  Contact Number
                </span>
                <span style={{ fontWeight: 500 }}>{emp.contact_number}</span>
              </div>
              <div>
                <span style={{ color: 'var(--color-text-muted)', display: 'block', marginBottom: '4px' }}>
                  Status
                </span>
                <span style={{ fontWeight: 500 }}>{emp.registration_status}</span>
              </div>
              <div>
                <span style={{ color: 'var(--color-text-muted)', display: 'block', marginBottom: '4px' }}>
                  Active
                </span>
                <span style={{ fontWeight: 500 }}>{emp.is_active ? 'Yes' : 'No'}</span>
              </div>
              <div>
                <span style={{ color: 'var(--color-text-muted)', display: 'block', marginBottom: '4px' }}>
                  Created At
                </span>
                <span style={{ fontWeight: 500 }}>{new Date(emp.created_at).toLocaleString()}</span>
              </div>
            </div>
            <div style={{ display: 'flex', gap: '12px' }}>
              <button
                onClick={() => handleApprove(emp.employee_id)}
                disabled={actingId === emp.employee_id}
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
                Approve
              </button>
              <button
                onClick={() => handleReject(emp.employee_id)}
                disabled={actingId === emp.employee_id}
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
                Reject
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
