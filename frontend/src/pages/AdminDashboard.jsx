import React, { useEffect, useState } from 'react';
import Navbar from '../components/Navbar';
import { getPendingRegistrations, approveRegistration, rejectRegistration, uploadTimetable } from '../services/api';
import { Upload, Users, Check, X } from 'lucide-react';

export default function AdminDashboard() {
  const [registrations, setRegistrations] = useState([]);
  const [loadingReg, setLoadingReg] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState('');

  const fetchRegistrations = async () => {
    setLoadingReg(true);
    try {
      const res = await getPendingRegistrations();
      setRegistrations(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingReg(false);
    }
  };

  useEffect(() => {
    fetchRegistrations();
  }, []);

  const handleApprove = async (id) => {
    try {
      await approveRegistration(id);
      fetchRegistrations();
    } catch (err) {
      alert('Error approving registration');
    }
  };

  const handleReject = async (id) => {
    try {
      await rejectRegistration(id);
      fetchRegistrations();
    } catch (err) {
      alert('Error rejecting registration');
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    setUploadMessage('');
    try {
      const res = await uploadTimetable(file);
      setUploadMessage(`Success! Inserted ${res.data.inserted_rows} rows from ${file.name}`);
    } catch (err) {
      const detail = err.response?.data?.detail || err.message || 'Upload failed';
      setUploadMessage(`Upload failed: ${detail}`);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="app-container">
      <Navbar />
      
      <main className="main-content">
        <h1 style={{ marginBottom: '2rem' }}>Admin Dashboard</h1>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 1fr)', gap: '2rem', alignItems: 'start' }}>
          
          {/* File Upload Section */}
          <div className="card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
              <Upload size={24} color="var(--accent-color)" />
              <h2 style={{ margin: 0 }}>Upload Weekly Timetable</h2>
            </div>
            
            <p>Upload the weekly CSV exported from the scheduling system. The backend reads only the first seven date columns.</p>
            
            <div style={{ position: 'relative', marginTop: '1.5rem' }}>
              <label 
                className="btn btn-outline" 
                style={{ width: '100%', borderStyle: 'dashed', padding: '2rem', display: 'flex', flexDirection: 'column', gap: '1rem', cursor: uploading ? 'not-allowed' : 'pointer' }}
              >
                <div style={{ margin: '0 auto', background: 'var(--bg-secondary)', padding: '1rem', borderRadius: '50%' }}>
                  <Upload size={24} color="var(--text-secondary)" />
                </div>
                <span style={{ fontWeight: 500 }}>{uploading ? 'Uploading...' : 'Click to select CSV file'}</span>
                <input 
                  type="file" 
                  accept=".csv,text/csv" 
                  onChange={handleFileUpload} 
                  style={{ opacity: 0, position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', cursor: uploading ? 'not-allowed' : 'pointer' }} 
                  disabled={uploading}
                />
              </label>
            </div>

            {uploadMessage && (
              <div style={{ marginTop: '1rem', padding: '1rem', background: uploadMessage.startsWith('Success') ? 'var(--success-color)' : 'var(--danger-color)', color: 'white', borderRadius: 'var(--border-radius)', fontSize: '0.875rem' }}>
                {uploadMessage}
              </div>
            )}
          </div>

          {/* Pending Registrations */}
          <div className="card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
              <Users size={24} color="var(--accent-color)" />
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                 <h2 style={{ margin: 0 }}>Pending Registrations</h2>
                 {registrations.length > 0 && (
                   <span className="badge warning" style={{ fontSize: '1rem' }}>{registrations.length}</span>
                 )}
              </div>
            </div>

            {loadingReg ? (
              <p>Loading requests...</p>
            ) : registrations.length === 0 ? (
              <p style={{ color: 'var(--text-tertiary)' }}>No pending registrations.</p>
            ) : (
              <div style={{ overflowX: 'auto' }}>
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Employee ID</th>
                      <th>Contact Number</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {registrations.map(reg => (
                      <tr key={reg.employee_id}>
                        <td style={{ fontWeight: 500 }}>{reg.employee_id}</td>
                        <td>{reg.contact_number}</td>
                        <td>
                          <div style={{ display: 'flex', gap: '0.5rem' }}>
                            <button onClick={() => handleApprove(reg.employee_id)} className="btn btn-outline" style={{ padding: '0.5rem', color: 'var(--success-color)' }} title="Approve">
                              <Check size={16} />
                            </button>
                            <button onClick={() => handleReject(reg.employee_id)} className="btn btn-outline" style={{ padding: '0.5rem', color: 'var(--danger-color)' }} title="Reject">
                              <X size={16} />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

        </div>
      </main>
    </div>
  );
}
