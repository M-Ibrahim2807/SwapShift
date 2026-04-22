import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../../components/Navbar/Navbar';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import { getPendingRegistrations } from '../../services/api';
import RegistrationsTab from './tabs/RegistrationsTab';
import UploadTimetableTab from './tabs/UploadTimetableTab';
import SwapOverviewTab from './tabs/SwapOverviewTab';
import './AdminDashboard.css';

export default function AdminDashboard() {
  const navigate = useNavigate();
  const { token, role, user, logout } = useAuth();
  const { showToast } = useToast();
  const [activeTab, setActiveTab] = useState('registrations');
  const [registrationCount, setRegistrationCount] = useState(0);

  useEffect(() => {
    if (!token || role !== 'admin') {
      navigate('/');
    }
  }, [token, role, navigate]);

  useEffect(() => {
    fetchRegistrationCount();
  }, []);

  const fetchRegistrationCount = async () => {
    try {
      const response = await getPendingRegistrations();
      setRegistrationCount(Array.isArray(response.data) ? response.data.length : 0);
    } catch (err) {
      console.error('Failed to fetch registration count');
    }
  };

  if (!token || role !== 'admin') {
    return null;
  }

  const userName = user?.username || 'Admin';

  return (
    <>
      <Navbar userName={userName} role="admin" onLogout={logout} />
      <div className="dashboard">
        <div className="tab-bar">
          <button
            className={`tab-button ${activeTab === 'registrations' ? 'active' : ''}`}
            onClick={() => setActiveTab('registrations')}
          >
            Pending Registrations
            {registrationCount > 0 && <span className="badge-count">{registrationCount}</span>}
          </button>
          <button
            className={`tab-button ${activeTab === 'upload' ? 'active' : ''}`}
            onClick={() => setActiveTab('upload')}
          >
            Upload Timetable
          </button>
          <button
            className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            Swap Overview
          </button>
        </div>

        <div className="tab-content">
          {activeTab === 'registrations' && (
            <RegistrationsTab
              showToast={showToast}
              onCountChange={setRegistrationCount}
            />
          )}
          {activeTab === 'upload' && <UploadTimetableTab showToast={showToast} />}
          {activeTab === 'overview' && <SwapOverviewTab showToast={showToast} />}
        </div>
      </div>
    </>
  );
}
