import React, { useEffect, useMemo, useState } from 'react';
import { deleteEmployee, getAllEmployees } from '../../../services/api';
import LoadingSpinner from '../../../components/LoadingSpinner/LoadingSpinner';

export default function EmployeesTab({ showToast }) {
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState('');
  const [deletingId, setDeletingId] = useState(null);

  useEffect(() => {
    fetchEmployees();
  }, []);

  const fetchEmployees = async () => {
    try {
      setLoading(true);
      const response = await getAllEmployees();
      setEmployees(Array.isArray(response.data) ? response.data : []);
    } catch (err) {
      showToast(err.response?.data?.detail || 'Failed to load employees', 'error');
    } finally {
      setLoading(false);
    }
  };

  const filteredEmployees = useMemo(() => {
    const keyword = query.trim().toLowerCase();
    if (!keyword) {
      return employees;
    }
    return employees.filter((emp) => {
      const idMatch = (emp.employee_id || '').toLowerCase().includes(keyword);
      const nameMatch = (emp.name || '').toLowerCase().includes(keyword);
      return idMatch || nameMatch;
    });
  }, [employees, query]);

  const handleDelete = async (employeeId) => {
    const confirmed = window.confirm(`Are you sure you want to deregister ${employeeId}?`);
    if (!confirmed) {
      return;
    }

    try {
      setDeletingId(employeeId);
      const response = await deleteEmployee(employeeId);
      showToast(response.data?.message || 'Employee deregistered successfully', 'success');
      setEmployees((prev) => prev.filter((emp) => emp.employee_id !== employeeId));
    } catch (err) {
      showToast(err.response?.data?.detail || 'Failed to deregister employee', 'error');
    } finally {
      setDeletingId(null);
    }
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div>
      <div style={{ marginBottom: '16px' }}>
        <input
          type="text"
          placeholder="Search by employee ID or name"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          style={{
            width: '100%',
            padding: '10px 12px',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--border-radius-sm)',
            fontSize: '14px',
            background: 'var(--color-white)',
          }}
        />
      </div>

      <p style={{ marginBottom: '16px', color: 'var(--color-text-muted)', fontSize: '14px' }}>
        Showing {filteredEmployees.length} employee{filteredEmployees.length !== 1 ? 's' : ''}
      </p>

      {filteredEmployees.length === 0 ? (
        <div style={{ textAlign: 'center', color: 'var(--color-text-muted)', padding: '32px 20px' }}>
          No employees found.
        </div>
      ) : (
        <div style={{ display: 'grid', gap: '12px' }}>
          {filteredEmployees.map((emp) => (
            <div
              key={emp.employee_id}
              style={{
                background: 'var(--color-white)',
                padding: '16px',
                borderRadius: 'var(--border-radius-md)',
                boxShadow: 'var(--shadow-sm)',
              }}
            >
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
                  gap: '12px',
                  marginBottom: '12px',
                  fontSize: '14px',
                }}
              >
                <div><strong>ID:</strong> {emp.employee_id}</div>
                <div><strong>Name:</strong> {emp.name || 'N/A'}</div>
                <div><strong>Supervisor:</strong> {emp.supervisor_name || 'N/A'}</div>
                <div><strong>Contact:</strong> {emp.contact_number || 'N/A'}</div>
                <div><strong>Status:</strong> {emp.registration_status}</div>
                <div><strong>Active:</strong> {emp.is_active ? 'Yes' : 'No'}</div>
              </div>

              <button
                onClick={() => handleDelete(emp.employee_id)}
                disabled={deletingId === emp.employee_id}
                style={{
                  padding: '8px 14px',
                  background: 'var(--color-error)',
                  color: 'white',
                  border: 'none',
                  borderRadius: 'var(--border-radius-sm)',
                  fontSize: '13px',
                  fontWeight: 600,
                  cursor: 'pointer',
                }}
              >
                {deletingId === emp.employee_id ? 'Deleting...' : 'Deregister'}
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
