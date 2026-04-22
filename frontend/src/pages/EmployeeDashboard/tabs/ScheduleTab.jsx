import React, { useEffect, useState } from 'react';
import { getTimetable } from '../../../services/api';
import LoadingSpinner from '../../../components/LoadingSpinner/LoadingSpinner';
import { adjustTimeForPKST } from '../../../utils/timeUtils';

export default function ScheduleTab({ showToast }) {
  const [timetable, setTimetable] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTimetable();
  }, []);

  const fetchTimetable = async () => {
    try {
      setLoading(true);
      const response = await getTimetable();
      setTimetable(response.data);
    } catch (err) {
      showToast(err.response?.data?.detail || 'Failed to load schedule', 'error');
      setTimetable(null);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  if (!timetable || !Array.isArray(timetable.rows) || timetable.rows.length === 0) {
    return (
      <div style={{ textAlign: 'center', color: 'var(--color-text-muted)', padding: '40px 20px' }}>
        No schedule assigned yet.
      </div>
    );
  }

  return (
    <div>
      <div
        style={{
          background: 'var(--color-white)',
          padding: '16px',
          borderRadius: 'var(--border-radius-md)',
          marginBottom: '16px',
          boxShadow: 'var(--shadow-sm)',
        }}
      >
        <p style={{ margin: 0, color: 'var(--color-text)' }}>
          Employee: <strong>{timetable.employee_id}</strong>
        </p>
        <p style={{ margin: '6px 0 0', color: 'var(--color-text-muted)' }}>
          Week: {timetable.week_start} to {timetable.week_end}
        </p>
      </div>

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
              <th style={{ padding: '12px 16px', textAlign: 'left', fontWeight: 600, fontSize: '14px' }}>Date</th>
              <th style={{ padding: '12px 16px', textAlign: 'left', fontWeight: 600, fontSize: '14px' }}>Shift</th>
            </tr>
          </thead>
          <tbody>
            {timetable.rows.map((row, idx) => (
              <tr
                key={`${row.date}-${idx}`}
                style={{
                  borderBottom: '1px solid var(--color-border)',
                  background: idx % 2 === 0 ? 'var(--color-white)' : 'var(--color-bg)',
                }}
              >
                <td style={{ padding: '12px 16px', fontSize: '14px' }}>{row.date}</td>
                <td style={{ padding: '12px 16px', fontSize: '14px' }}>{adjustTimeForPKST(row.shift_name)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
