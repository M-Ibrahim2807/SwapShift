import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Calendar, Mail, History, Search, LogOut } from 'lucide-react';
import axios from 'axios';

export default function EmployeeDashboard() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('schedule');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Auth state
  const [token, setToken] = useState('');
  const [role, setRole] = useState('');
  const [employeeId, setEmployeeId] = useState('');
  
  // My Schedule tab
  const [schedule, setSchedule] = useState(null);
  const [employeeInfo, setEmployeeInfo] = useState(null);
  
  // Find Swap tab
  const [findSwapForm, setFindSwapForm] = useState({ date: '', shift_type: '' });
  const [availableSwaps, setAvailableSwaps] = useState([]);
  const [swapSearchDone, setSwapSearchDone] = useState(false);
  
  // Inbox tab
  const [inboxRequests, setInboxRequests] = useState([]);
  
  // History tab
  const [historyData, setHistoryData] = useState([]);

  // Auth check on mount
  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    const storedRole = localStorage.getItem('role');
    const storedEmployeeId = localStorage.getItem('employee_id');
    
    if (!storedToken) {
      navigate('/');
      return;
    }
    
    if (storedRole !== 'employee') {
      navigate('/');
      return;
    }
    
    setToken(storedToken);
    setRole(storedRole);
    setEmployeeId(storedEmployeeId);
  }, [navigate]);

  // Load My Schedule on tab change
  useEffect(() => {
    if (activeTab === 'schedule' && token) {
      loadSchedule();
    }
  }, [activeTab, token]);

  // Load Inbox on tab change
  useEffect(() => {
    if (activeTab === 'inbox' && token) {
      loadInbox();
    }
  }, [activeTab, token]);

  // Load History on tab change
  useEffect(() => {
    if (activeTab === 'history' && token) {
      loadHistory();
    }
  }, [activeTab, token]);

  const getAxiosInstance = () => {
    return axios.create({
      baseURL: 'http://localhost:8000',
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
  };

  const loadSchedule = async () => {
    setLoading(true);
    setError('');
    try {
      const api = getAxiosInstance();
      const res = await api.get('/api/v1/employee/timetable');
      setSchedule(res.data.timetable);
      setEmployeeInfo(res.data.employee_info);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load schedule');
    } finally {
      setLoading(false);
    }
  };

  const handleFindSwapChange = (e) => {
    setFindSwapForm({ ...findSwapForm, [e.target.name]: e.target.value });
  };

  const findSwaps = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');
    
    if (!findSwapForm.date || !findSwapForm.shift_type) {
      setError('Please fill in all fields');
      setLoading(false);
      return;
    }

    try {
      const api = getAxiosInstance();
      const res = await api.post('/api/v1/swap/find', {
        date: findSwapForm.date,
        shift_type: findSwapForm.shift_type
      });
      setAvailableSwaps(res.data.swaps || []);
      setSwapSearchDone(true);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to find swaps');
    } finally {
      setLoading(false);
    }
  };

  const requestSwap = async (targetEmployeeId) => {
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      const api = getAxiosInstance();
      await api.post('/api/v1/swap/request', {
        target_employee_id: targetEmployeeId,
        date: findSwapForm.date,
        shift_type: findSwapForm.shift_type
      });
      setSuccess('Swap request sent successfully!');
      setAvailableSwaps(availableSwaps.filter(s => s.employee_id !== targetEmployeeId));
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to request swap');
    } finally {
      setLoading(false);
    }
  };

  const loadInbox = async () => {
    setLoading(true);
    setError('');
    try {
      const api = getAxiosInstance();
      const res = await api.get('/api/v1/swap/inbox');
      setInboxRequests(res.data.requests || []);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load inbox');
    } finally {
      setLoading(false);
    }
  };

  const respondToRequest = async (requestId, decision) => {
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      const api = getAxiosInstance();
      await api.post(`/api/v1/swap/requests/${requestId}/decision`, {
        decision: decision
      });
      setSuccess(`Request ${decision}!`);
      await loadInbox();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to respond to request');
    } finally {
      setLoading(false);
    }
  };

  const loadHistory = async () => {
    setLoading(true);
    setError('');
    try {
      const api = getAxiosInstance();
      const res = await api.get('/api/v1/swap/history');
      setHistoryData(res.data.history || []);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load history');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    localStorage.removeItem('employee_id');
    navigate('/');
  };

  if (!token) {
    return null;
  }

  const getDayName = (dateStr) => {
    const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    const date = new Date(dateStr);
    return days[date.getDay()];
  };

  const getStatusBadgeColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'approved': return '#10b981';
      case 'rejected': return '#ef4444';
      case 'pending': return '#f59e0b';
      default: return '#a1a1aa';
    }
  };

  return (
    <div className="app-container">
      {/* Navbar */}
      <nav className="navbar">
        <div className="navbar-brand">SwapShift</div>
        <div className="navbar-nav">
          <span style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Welcome, {employeeId}</span>
          <button 
            onClick={handleLogout}
            className="btn btn-outline"
            style={{ padding: '0.5rem 1rem', fontSize: '0.875rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}
          >
            <LogOut size={16} /> Logout
          </button>
        </div>
      </nav>

      <div className="main-content">
        {/* Tab Navigation */}
        <div className="tab-navigation">
          <button
            className={`tab-btn ${activeTab === 'schedule' ? 'active' : ''}`}
            onClick={() => setActiveTab('schedule')}
          >
            <Calendar size={18} /> My Schedule
          </button>
          <button
            className={`tab-btn ${activeTab === 'find' ? 'active' : ''}`}
            onClick={() => setActiveTab('find')}
          >
            <Search size={18} /> Find Swap
          </button>
          <button
            className={`tab-btn ${activeTab === 'inbox' ? 'active' : ''}`}
            onClick={() => setActiveTab('inbox')}
          >
            <Mail size={18} /> Inbox
          </button>
          <button
            className={`tab-btn ${activeTab === 'history' ? 'active' : ''}`}
            onClick={() => setActiveTab('history')}
          >
            <History size={18} /> History
          </button>
        </div>

        {/* Error & Success Messages */}
        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">{success}</div>}

        {/* Tab Content */}
        {activeTab === 'schedule' && (
          <div className="tab-content">
            {loading ? (
              <p style={{ textAlign: 'center', color: 'var(--text-secondary)' }}>Loading schedule...</p>
            ) : (
              <>
                {employeeInfo && (
                  <div className="card" style={{ marginBottom: '1.5rem' }}>
                    <h3>{employeeInfo.name}</h3>
                    <p style={{ color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>
                      Department: {employeeInfo.department}
                    </p>
                    <p style={{ color: 'var(--text-secondary)' }}>
                      Designation: {employeeInfo.designation}
                    </p>
                  </div>
                )}
                {schedule && (
                  <div className="card" style={{ overflowX: 'auto' }}>
                    <table className="data-table">
                      <thead>
                        <tr>
                          {Object.keys(schedule).map((day) => (
                            <th key={day}>{getDayName(day)} ({day})</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        <tr>
                          {Object.values(schedule).map((shift, idx) => (
                            <td key={idx}>
                              {shift ? (
                                <>
                                  <strong>{shift.shift_type}</strong>
                                  <br />
                                  <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                                    {shift.start_time} - {shift.end_time}
                                  </span>
                                </>
                              ) : (
                                <span style={{ color: 'var(--text-tertiary)' }}>Day Off</span>
                              )}
                            </td>
                          ))}
                        </tr>
                      </tbody>
                    </table>
                  </div>
                )}
              </>
            )}
          </div>
        )}

        {activeTab === 'find' && (
          <div className="tab-content">
            <div className="card" style={{ marginBottom: '1.5rem' }}>
              <h3 style={{ marginBottom: '1rem' }}>Find Available Swaps</h3>
              <form onSubmit={findSwaps}>
                <div className="input-group">
                  <label className="input-label">Date</label>
                  <input
                    type="date"
                    name="date"
                    className="input-field"
                    value={findSwapForm.date}
                    onChange={handleFindSwapChange}
                    required
                  />
                </div>
                <div className="input-group">
                  <label className="input-label">Shift Type</label>
                  <select
                    name="shift_type"
                    className="input-field"
                    value={findSwapForm.shift_type}
                    onChange={handleFindSwapChange}
                    required
                  >
                    <option value="">Select shift type</option>
                    <option value="morning">Morning</option>
                    <option value="evening">Evening</option>
                    <option value="night">Night</option>
                  </select>
                </div>
                <button type="submit" className="btn btn-primary" disabled={loading} style={{ width: '100%' }}>
                  {loading ? 'Searching...' : 'Find Available Swaps'}
                </button>
              </form>
            </div>

            {swapSearchDone && (
              <div>
                {availableSwaps.length === 0 ? (
                  <p style={{ textAlign: 'center', color: 'var(--text-secondary)' }}>
                    No available swaps found
                  </p>
                ) : (
                  <div style={{ display: 'grid', gap: '1rem' }}>
                    {availableSwaps.map((swap) => (
                      <div key={swap.employee_id} className="card">
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
                          <div style={{ flex: 1, minWidth: '200px' }}>
                            <h4 style={{ marginBottom: '0.5rem' }}>{swap.employee_name}</h4>
                            <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginBottom: '0.25rem' }}>
                              Shift: {swap.shift_type} ({swap.start_time} - {swap.end_time})
                            </p>
                            <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                              Department: {swap.department}
                            </p>
                          </div>
                          <button
                            onClick={() => requestSwap(swap.employee_id)}
                            className="btn btn-primary"
                            disabled={loading}
                            style={{ whiteSpace: 'nowrap' }}
                          >
                            Request Swap
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {activeTab === 'inbox' && (
          <div className="tab-content">
            {loading ? (
              <p style={{ textAlign: 'center', color: 'var(--text-secondary)' }}>Loading requests...</p>
            ) : (
              <>
                {inboxRequests.length === 0 ? (
                  <p style={{ textAlign: 'center', color: 'var(--text-secondary)' }}>
                    No swap requests in your inbox
                  </p>
                ) : (
                  <div style={{ display: 'grid', gap: '1rem' }}>
                    {inboxRequests.map((request) => (
                      <div key={request.request_id} className="card">
                        <div>
                          <h4 style={{ marginBottom: '0.5rem' }}>{request.requester_name}</h4>
                          <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginBottom: '0.25rem' }}>
                            Date: {request.date}
                          </p>
                          <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginBottom: '1rem' }}>
                            Shift: {request.shift_type}
                          </p>
                          <div style={{ display: 'flex', gap: '0.5rem' }}>
                            <button
                              onClick={() => respondToRequest(request.request_id, 'approved')}
                              className="btn"
                              style={{
                                backgroundColor: 'var(--success-color)',
                                color: 'white',
                                flex: 1
                              }}
                              disabled={loading}
                            >
                              Accept
                            </button>
                            <button
                              onClick={() => respondToRequest(request.request_id, 'rejected')}
                              className="btn"
                              style={{
                                backgroundColor: 'var(--danger-color)',
                                color: 'white',
                                flex: 1
                              }}
                              disabled={loading}
                            >
                              Decline
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </>
            )}
          </div>
        )}

        {activeTab === 'history' && (
          <div className="tab-content">
            {loading ? (
              <p style={{ textAlign: 'center', color: 'var(--text-secondary)' }}>Loading history...</p>
            ) : (
              <div className="card" style={{ overflowX: 'auto' }}>
                {historyData.length === 0 ? (
                  <p style={{ textAlign: 'center', color: 'var(--text-secondary)' }}>
                    No swap history yet
                  </p>
                ) : (
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>Date</th>
                        <th>Shift</th>
                        <th>With</th>
                        <th>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {historyData.map((item) => (
                        <tr key={item.request_id}>
                          <td>{item.date}</td>
                          <td>{item.shift_type}</td>
                          <td>{item.employee_name}</td>
                          <td>
                            <span
                              className="badge"
                              style={{
                                backgroundColor: getStatusBadgeColor(item.status),
                                color: 'white',
                                padding: '0.25rem 0.75rem'
                              }}
                            >
                              {item.status}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
