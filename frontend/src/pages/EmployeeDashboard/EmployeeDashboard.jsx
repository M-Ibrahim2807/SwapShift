import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  Bell,
  BellRing,
  CalendarDays,
  Check,
  CheckCircle2,
  Hand,
  HeartHandshake,
  House,
  MoonStar,
  MessageCircle,
  Repeat,
  Search,
  SunMedium,
  UserRound,
  X,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import {
  decideSwap,
  findSwap,
  getAvailableShifts,
  getEmployeeSummary,
  getSwapInbox,
  getTimetable,
  requestSwap,
} from '../../services/api';
import { useNotifications } from '../../hooks/useNotifications';
import LoadingSpinner from '../../components/LoadingSpinner/LoadingSpinner';
import CoverbacksTab from './tabs/CoverbacksTab';
import { adjustTimeForPKST } from '../../utils/timeUtils';
import './EmployeeDashboard.css';

export default function EmployeeDashboard() {
  const navigate = useNavigate();
  const { token, role, user, logout } = useAuth();
  const { showToast } = useToast();
  const [activeTab, setActiveTab] = useState('home');
  const [timetable, setTimetable] = useState(null);
  const [swapInbox, setSwapInbox] = useState([]);
  const [loading, setLoading] = useState(true);
  const [upcomingShifts, setUpcomingShifts] = useState([]);
  const [weekSummary, setWeekSummary] = useState({ morning: 0, evening: 0, off: 0 });
  const [employeeSummary, setEmployeeSummary] = useState(null);

  // Enable real-time notifications for logged-in employees
  useNotifications(token && role === 'employee', 2000);

  useEffect(() => {
    if (!token || role !== 'employee') {
      navigate('/');
    }
  }, [token, role, navigate]);

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    if (timetable && Array.isArray(timetable.rows)) {
      const today = new Date();
      today.setHours(0, 0, 0, 0);

      const shifts = timetable.rows
        .map((row) => ({
          date: new Date(row.date),
          dateStr: row.date,
          shift_name: row.shift_name,
        }))
        .filter((shift) => shift.date >= today)
        .sort((a, b) => a.date - b.date);

      setUpcomingShifts(shifts);

      if (!employeeSummary) {
        const thisWeek = shifts.filter((shift) => {
          const currentDate = new Date(shift.date);
          const weekStart = new Date(today);
          const weekEnd = new Date(today);
          weekEnd.setDate(weekEnd.getDate() + 6);
          return currentDate >= weekStart && currentDate <= weekEnd;
        });

        let morningCount = 0;
        let eveningCount = 0;
        let offCount = 0;

        thisWeek.forEach((shift) => {
          const lower = shift.shift_name.toLowerCase();
          if (lower.includes('morning') || lower.includes('early')) {
            morningCount += 1;
          } else if (lower.includes('evening') || lower.includes('night') || lower.includes('late')) {
            eveningCount += 1;
          } else if (lower.includes('off') || lower.includes('leave')) {
            offCount += 1;
          }
        });

        setWeekSummary({ morning: morningCount, evening: eveningCount, off: offCount });
      }
    }
  }, [timetable, employeeSummary]);

  const fetchData = async () => {
    try {
      setLoading(true);

      try {
        const summaryRes = await getEmployeeSummary();
        if (summaryRes.data) {
          setEmployeeSummary(summaryRes.data);
          setWeekSummary({
            morning: summaryRes.data.morning_shifts,
            evening: summaryRes.data.evening_shifts,
            off: summaryRes.data.off_days,
          });
        }
      } catch (err) {
        console.log('Employee summary endpoint not available yet');
        setEmployeeSummary(null);
      }

      const timetableRes = await getTimetable();
      setTimetable(timetableRes.data);

      if (timetableRes.data && Array.isArray(timetableRes.data.rows)) {
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        const shifts = timetableRes.data.rows
          .map((row) => ({
            date: new Date(row.date),
            dateStr: row.date,
            shift_name: row.shift_name,
          }))
          .filter((shift) => shift.date >= today)
          .sort((a, b) => a.date - b.date);

        setUpcomingShifts(shifts);
      }

      try {
        const inboxRes = await getSwapInbox();
        const inboxItems = Array.isArray(inboxRes.data) ? inboxRes.data : [];
        setSwapInbox(inboxItems);
      } catch (err) {
        // Silently fail if inbox endpoint is unavailable.
      }
    } catch (err) {
      showToast(err.response?.data?.detail || 'Failed to load data', 'error');
    } finally {
      setLoading(false);
    }
  };

  if (!token || role !== 'employee') {
    return null;
  }

  const userName = employeeSummary?.name || user?.full_name || user?.employee_id || 'Employee';
  const hour = new Date().getHours();
  const greeting = hour < 12 ? 'Good Morning' : hour < 18 ? 'Good Afternoon' : 'Good Evening';
  const GreetingIcon = hour < 12 ? Hand : hour < 18 ? SunMedium : MoonStar;

  const getShiftBadgeColor = (shiftName) => {
    const lower = shiftName.toLowerCase();
    if (lower.includes('morning')) return 'shift-morning';
    if (lower.includes('evening')) return 'shift-evening';
    if (lower.includes('night')) return 'shift-night';
    if (lower.includes('off')) return 'shift-off';
    return 'shift-default';
  };

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  const getDayName = (dateStr) => {
    const date = new Date(dateStr);
    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    return days[date.getDay()];
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="employee-dashboard">
      <div className="dashboard-header">
        <div className="greeting-section">
          <p className="greeting-text">
            <GreetingIcon size={18} className="greeting-icon" />
            <span>{greeting}</span>
          </p>
          <h1 className="user-name">{userName}</h1>
        </div>
      </div>

      {typeof Notification !== 'undefined' && Notification.permission === 'granted' && (
        <div
          style={{
            background: '#d4edda',
            border: '1px solid #c3e6cb',
            borderRadius: '8px',
            padding: '12px 16px',
            marginBottom: '16px',
            color: '#155724',
            fontSize: '13px',
            fontWeight: '500',
          }}
        >
          <Bell size={16} style={{ marginRight: '8px', verticalAlign: 'text-bottom' }} />
          Notifications enabled - You'll receive alerts for swap requests
        </div>
      )}

      <div className="dashboard-content">
        {activeTab === 'home' && (
          <>
            {upcomingShifts.length > 0 && (
              <div className="upcoming-section">
                <h2 className="section-title">Upcoming Shifts</h2>
                <div className="shifts-list">
                  {upcomingShifts.slice(0, 5).map((shift, idx) => (
                    <div key={idx} className="shift-item">
                      <div className="shift-info">
                        <p className="shift-day">{getDayName(shift.dateStr)}</p>
                        <p className="shift-date">{formatDate(shift.dateStr)}</p>
                      </div>
                      <span className={`shift-badge ${getShiftBadgeColor(shift.shift_name)}`}>
                        {adjustTimeForPKST(shift.shift_name)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {upcomingShifts.length === 0 && (
              <div className="empty-state">
                <p>No upcoming shifts</p>
              </div>
            )}
          </>
        )}

        {activeTab === 'schedule' && <ScheduleView timetable={timetable} />}
        {activeTab === 'find' && (
          <FindSwapView
            showToast={showToast}
            timetable={timetable}
            onBack={() => setActiveTab('home')}
            findSwapAction={findSwap}
            requestSwapAction={requestSwap}
            getAvailableShiftsAction={getAvailableShifts}
          />
        )}
        {activeTab === 'coverbacks' && <CoverbacksTab showToast={showToast} />}
        {activeTab === 'inbox' && (
          <InboxView
            swapInbox={swapInbox}
            showToast={showToast}
            onRemoveAlert={(id) => setSwapInbox(swapInbox.filter((item) => item.id !== id))}
            onSwapCompleted={fetchData}
          />
        )}
      </div>

      <div className="bottom-nav">
        <button className={`nav-item ${activeTab === 'home' ? 'active' : ''}`} onClick={() => setActiveTab('home')}>
          <span className="nav-icon">
            <House size={20} />
          </span>
          <span className="nav-label">Home</span>
        </button>
        <button className={`nav-item ${activeTab === 'schedule' ? 'active' : ''}`} onClick={() => setActiveTab('schedule')}>
          <span className="nav-icon">
            <CalendarDays size={20} />
          </span>
          <span className="nav-label">Schedule</span>
        </button>
        <button className={`nav-item ${activeTab === 'find' ? 'active' : ''}`} onClick={() => setActiveTab('find')}>
          <span className="nav-icon">
            <Repeat size={20} />
          </span>
          <span className="nav-label">Swap</span>
        </button>
        <button className={`nav-item ${activeTab === 'coverbacks' ? 'active' : ''}`} onClick={() => setActiveTab('coverbacks')}>
          <span className="nav-icon">
            <HeartHandshake size={20} />
          </span>
          <span className="nav-label">Coverbacks</span>
        </button>
        <button className={`nav-item ${activeTab === 'inbox' ? 'active' : ''}`} onClick={() => setActiveTab('inbox')}>
          <span className="nav-icon">
            <BellRing size={20} />
          </span>
          <span className="nav-label">Alerts</span>
          {swapInbox.length > 0 && <span className="badge-small">{swapInbox.length}</span>}
        </button>
        <button className="nav-item" onClick={() => navigate('/')}>
          <span className="nav-icon">
            <House size={20} />
          </span>
          <span className="nav-label">Home</span>
        </button>
        <button className="nav-item" onClick={logout}>
          <span className="nav-icon">
            <X size={20} />
          </span>
          <span className="nav-label">Logout</span>
        </button>
      </div>
    </div>
  );
}

function ScheduleView({ timetable }) {
  if (!timetable || !Array.isArray(timetable.rows) || timetable.rows.length === 0) {
    return <div className="empty-state">No schedule assigned yet</div>;
  }

  return (
    <div className="schedule-view">
      <div className="schedule-info">
        <p>
          Employee: <strong>{timetable.employee_id}</strong>
        </p>
        <p>
          Week: {timetable.week_start} to {timetable.week_end}
        </p>
      </div>
      <div className="schedule-table">
        {timetable.rows.map((row, idx) => (
          <div key={idx} className="schedule-row">
            <div className="schedule-date">{row.date}</div>
            <div className="schedule-shift">{adjustTimeForPKST(row.shift_name)}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

function FindSwapView({
  showToast,
  timetable,
  onBack,
  findSwapAction,
  requestSwapAction,
  getAvailableShiftsAction,
}) {
  const [selectedDate, setSelectedDate] = React.useState('');
  const [wantedShift, setWantedShift] = React.useState('');
  const [loading, setLoading] = React.useState(false);
  const [results, setResults] = React.useState([]);
  const [searched, setSearched] = React.useState(false);
  const [requestingId, setRequestingId] = React.useState(null);
  const [availableShifts, setAvailableShifts] = React.useState([]);
  const [fetchingShifts, setFetchingShifts] = React.useState(false);
  const [requestSent, setRequestSent] = React.useState(false);
  const [sentToEmployee, setSentToEmployee] = React.useState(null);
  const [sentToContact, setSentToContact] = React.useState(null);
  const [sentToWhatsappLink, setSentToWhatsappLink] = React.useState(null);

  const getTodayStr = () => {
    const today = new Date();
    return today.toISOString().split('T')[0];
  };

  React.useEffect(() => {
    if (!selectedDate) {
      setAvailableShifts([]);
      return;
    }

    const fetchShifts = async () => {
      try {
        setFetchingShifts(true);
        const response = await getAvailableShiftsAction(selectedDate);
        setAvailableShifts(response.data.shifts || []);
      } catch (err) {
        showToast('Failed to load available shifts', 'error');
        setAvailableShifts([]);
      } finally {
        setFetchingShifts(false);
      }
    };

    fetchShifts();
  }, [selectedDate, getAvailableShiftsAction, showToast]);

  const getCurrentShift = () => {
    if (!selectedDate || !timetable || !Array.isArray(timetable.rows)) {
      return null;
    }

    const shift = timetable.rows.find((row) => row.date === selectedDate);
    return shift ? shift.shift_name : null;
  };

  const getShiftTime = (shiftName) => {
    const match = shiftName.match(/\(([^)]+)\)/);
    const timeStr = match ? match[1] : shiftName;
    return adjustTimeForPKST(timeStr);
  };

  const buildWhatsAppLink = (contactNumber) => {
    if (!contactNumber) {
      return null;
    }

    const compact = String(contactNumber).replace(/[^\d]/g, '');
    if (!compact) {
      return null;
    }

    return `https://wa.me/${compact}`;
  };

  const handleSearch = async (e) => {
    e.preventDefault();

    if (!selectedDate) {
      showToast('Please select a date', 'warning');
      return;
    }
    if (!wantedShift) {
      showToast('Please select desired shift', 'warning');
      return;
    }

    try {
      setLoading(true);
      setRequestSent(false);

      if (wantedShift.toUpperCase().includes('OFF')) {
        const response = await findSwapAction({
          swap_type: 'DAILY',
          daily_mode: 'SINGLE_DAY',
          target_date: selectedDate,
          wanted_hour: 12,
          wanted_meridiem: 'OFF',
        });

        setResults(Array.isArray(response.data.matches) ? response.data.matches : []);
        setSearched(true);
      } else {
        const shiftMatch = wantedShift.match(/(\d{1,2}):?(\d{0,2})\s*(AM|PM)/i);
        if (!shiftMatch) {
          showToast('Invalid shift format', 'warning');
          return;
        }

        const response = await findSwapAction({
          swap_type: 'DAILY',
          daily_mode: 'SINGLE_DAY',
          target_date: selectedDate,
          wanted_hour: parseInt(shiftMatch[1], 10),
          wanted_meridiem: shiftMatch[3],
        });

        setResults(Array.isArray(response.data.matches) ? response.data.matches : []);
        setSearched(true);
      }
    } catch (err) {
      let errorMsg = 'Search failed';
      if (err.response?.data?.detail) {
        errorMsg = typeof err.response.data.detail === 'string' ? err.response.data.detail : 'Search failed';
      } else if (err.message) {
        errorMsg = err.message;
      }

      showToast(errorMsg, 'error');
      setResults([]);
      setSearched(true);
    } finally {
      setLoading(false);
    }
  };

  const handleRequestSwap = async (candidate) => {
    if (!candidate?.employee_id) {
      showToast('Invalid request - receiver employee is missing', 'warning');
      return;
    }

    try {
      setRequestingId(candidate.employee_id);
      await requestSwapAction({
        receiver_employee_id: candidate.employee_id,
        swap_type: candidate.swap_type,
        target_date: candidate.target_date,
        requester_current_shift: candidate.requester_current_shift,
        receiver_current_shift: candidate.candidate_current_shift,
        expires_in_minutes: 360,
      });

      const whatsappLink = buildWhatsAppLink(candidate.contact_number);
      setRequestSent(true);
      setSentToEmployee(candidate.name || candidate.employee_id);
      setSentToContact(candidate.contact_number || 'Not available');
      setSentToWhatsappLink(whatsappLink);
      setResults((prev) => prev.filter((item) => item.employee_id !== candidate.employee_id));
    } catch (err) {
      let errorDetail = 'Request failed';
      if (err.response?.data?.detail) {
        errorDetail = typeof err.response.data.detail === 'string' ? err.response.data.detail : 'Request failed';
      } else if (err.message) {
        errorDetail = err.message;
      }

      if (errorDetail.includes('already closed')) {
        showToast('The other person already accepted a different swap for this time', 'error');
      } else if (errorDetail.includes('does not belong')) {
        showToast('Your intent is no longer valid. Please search again.', 'error');
      } else if (errorDetail.includes('does not match')) {
        showToast('The shifts do not match. Please search again.', 'error');
      } else {
        showToast(errorDetail, 'error');
      }
    } finally {
      setRequestingId(null);
    }
  };

  const currentShift = getCurrentShift();

  return (
    <div className="find-swap-container">
      <div className="find-swap-header">
        <button className="back-button" onClick={onBack} aria-label="Back to home">
          <ArrowLeft size={22} />
        </button>
        <h1>Find a Swap</h1>
      </div>

      <div className="swap-form">
        <div className="form-section">
          <label className="form-label">Select Date</label>
          <div className="date-input-wrapper">
            <input
              type="date"
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
              min={getTodayStr()}
              className="date-input"
            />
            <span className="calendar-icon">
              <CalendarDays size={18} />
            </span>
          </div>
        </div>

        {currentShift && (
          <div className="current-shift-section">
            <p className="shift-label">YOUR SHIFT ON THIS DATE</p>
            <div className="current-shift-display">
              <span className="shift-name">{adjustTimeForPKST(currentShift)}</span>
              <span className="shift-time">{getShiftTime(currentShift)}</span>
              <span className="shift-icon">
                <UserRound size={18} />
              </span>
            </div>
          </div>
        )}

        <div className="form-section">
          <label className="form-label">I want to work</label>
          <select
            value={wantedShift}
            onChange={(e) => setWantedShift(e.target.value)}
            className="shift-select"
            disabled={!selectedDate}
          >
            <option value="">{fetchingShifts ? 'Loading shifts...' : 'Select shift'}</option>
            {availableShifts.map((shift) => (
              <option key={shift.shift} value={shift.shift}>
                {adjustTimeForPKST(shift.shift)} - {shift.count} {shift.count === 1 ? 'person' : 'persons'} available
              </option>
            ))}
          </select>
        </div>

        <button
          onClick={handleSearch}
          disabled={loading || !selectedDate || !wantedShift}
          className="find-matches-button"
        >
          <span className="button-icon">
            <Search size={18} />
          </span>
          {loading ? 'Searching...' : 'Find Matches'}
        </button>

        {requestSent && sentToEmployee && (
          <div
            style={{
              marginTop: '16px',
              padding: '16px',
              background: '#d4edda',
              border: '1px solid #c3e6cb',
              borderRadius: '8px',
              textAlign: 'center',
              color: '#155724',
            }}
          >
            <p style={{ fontSize: '16px', fontWeight: '600', marginBottom: '4px' }}>
              <CheckCircle2 size={18} style={{ marginRight: '8px', verticalAlign: 'text-bottom' }} />
              Your request has been sent to {sentToEmployee}
            </p>
            <p style={{ fontSize: '13px', margin: '0 0 6px' }}>
              Account WhatsApp number: <strong>{sentToContact || 'Not available'}</strong>
            </p>
            {sentToWhatsappLink ? (
              <div style={{ marginTop: '10px' }}>
                <button
                  type="button"
                  onClick={() => window.open(sentToWhatsappLink, '_blank', 'noopener,noreferrer')}
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '8px',
                    padding: '10px 16px',
                    background: '#128c7e',
                    color: '#ffffff',
                    border: 'none',
                    borderRadius: '8px',
                    fontSize: '14px',
                    fontWeight: '600',
                    cursor: 'pointer',
                  }}
                >
                  <MessageCircle size={16} />
                  Open WhatsApp
                </button>
              </div>
            ) : (
              <p style={{ fontSize: '13px', margin: 0 }}>WhatsApp number is not available for this account.</p>
            )}
          </div>
        )}

        {searched && results.length > 0 && (
          <div className="swap-results" style={{ marginTop: '16px' }}>
            {!loading && results.length > 0 && (
              <div className="results-list">
                {results.map((match, idx) => (
                  <div key={`${match.employee_id}-${match.target_date}-${idx}`} className="match-card">
                    <div className="match-info">
                      <p className="match-name">{match.name || match.employee_id}</p>
                      <p className="match-contact">Employee ID: {match.employee_id}</p>
                      <p className="match-contact">{match.contact_number}</p>
                      <p className="match-contact">Shift: {adjustTimeForPKST(match.candidate_current_shift)}</p>
                      {wantedShift.toUpperCase().includes('OFF') && (
                        <p style={{ fontSize: '13px', color: '#28a745', fontWeight: '500', marginTop: '4px' }}>
                          <HeartHandshake size={14} style={{ marginRight: '6px', verticalAlign: 'text-bottom' }} />
                          Wants your shift - You'll get OFF
                        </p>
                      )}
                    </div>
                    <button
                      onClick={() => handleRequestSwap(match)}
                      disabled={requestingId === match.employee_id}
                      className="request-button"
                    >
                      {requestingId === match.employee_id ? 'Requesting...' : 'Request'}
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {searched && !loading && results.length === 0 && (
          <div className="no-results" style={{ marginTop: '16px' }}>
            <p style={{ fontSize: '16px', fontWeight: '500', marginBottom: '8px' }}>
              No swap candidates found for this shift/date.
            </p>
            <p style={{ fontSize: '14px', color: 'var(--color-text-muted)' }}>Try another date or shift.</p>
          </div>
        )}

      </div>
    </div>
  );
}

function InboxView({ swapInbox, showToast, onRemoveAlert, onSwapCompleted }) {
  const [processingId, setProcessingId] = React.useState(null);

  const getDayName = (dateStr) => {
    const date = new Date(dateStr);
    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    return days[date.getDay()];
  };

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  const getShiftTime = (shiftName) => {
    if (!shiftName) return shiftName;
    const match = shiftName.match(/\(([^)]+)\)/);
    const timeStr = match ? match[1] : shiftName;
    return adjustTimeForPKST(timeStr);
  };

  const handleSwapAccept = async (requestId) => {
    try {
      setProcessingId(requestId);
      const response = await decideSwap(requestId, 'ACCEPT');
      showToast('Swap accepted! Shifts have been swapped.', 'success');
      const requesterWhatsApp = response?.data?.requester_whatsapp;
      const receiverWhatsApp = response?.data?.receiver_whatsapp;
      if (requesterWhatsApp || receiverWhatsApp) {
        const url = requesterWhatsApp || receiverWhatsApp;
        const openNow = window.confirm('Swap successful. Open WhatsApp redirect link now?');
        if (openNow) {
          window.open(url, '_blank', 'noopener,noreferrer');
        }
      }
      onRemoveAlert(requestId);
      if (onSwapCompleted) {
        await onSwapCompleted();
      }
    } catch (err) {
      showToast(err.response?.data?.detail || 'Failed to accept swap', 'error');
    } finally {
      setProcessingId(null);
    }
  };

  const handleSwapReject = async (requestId) => {
    try {
      setProcessingId(requestId);
      await decideSwap(requestId, 'REJECT');
      showToast('Swap request rejected.', 'info');
      onRemoveAlert(requestId);
    } catch (err) {
      showToast(err.response?.data?.detail || 'Failed to reject swap', 'error');
    } finally {
      setProcessingId(null);
    }
  };

  if (swapInbox.length === 0) {
    return <div className="empty-state">No alerts yet</div>;
  }

  return (
    <div className="inbox-view">
      {swapInbox.map((item) => (
        <div
          key={item.id}
          className="inbox-item"
          style={{
            padding: '16px',
            background: '#f8f9fa',
            borderRadius: '8px',
            marginBottom: '12px',
            border: '1px solid #e0e0e0',
          }}
        >
          <p style={{ fontSize: '16px', fontWeight: '600', marginBottom: '8px', color: '#333' }}>
            <Repeat size={18} style={{ marginRight: '8px', verticalAlign: 'text-bottom' }} />
            New swap request
          </p>
          <p style={{ fontSize: '14px', marginBottom: '6px' }}>
            <strong>Person ID:</strong>{' '}
            {item.requester_employee_id && item.requester_employee_id !== 'Unknown' ? item.requester_employee_id : 'N/A'}
          </p>
          <p style={{ fontSize: '14px', marginBottom: '6px' }}>
            <strong>WhatsApp:</strong>{' '}
            {item.requester_contact && item.requester_contact !== 'N/A' ? item.requester_contact : 'Not available'}
          </p>
          <p style={{ fontSize: '13px', color: '#666', margin: '8px 0 0' }}>
            <strong>Type:</strong> {item.swap_type} | <strong>Status:</strong> {item.status}
          </p>

          {item.viewer_current_shift && item.other_person_shift && item.start_date && (
            <div
              style={{
                background: '#e7f3ff',
                border: '1px solid #b3d9ff',
                borderRadius: '6px',
                padding: '10px 12px',
                margin: '12px 0 0 0',
                fontSize: '14px',
                color: '#004085',
                fontWeight: '500',
                lineHeight: '1.6',
              }}
            >
              Your current time slot for this <strong>{formatDate(item.start_date)}</strong>{' '}
              <strong>{getDayName(item.start_date)}</strong> is <strong>{getShiftTime(item.viewer_current_shift)}</strong>{' '}
              and after swap you will receive <strong>{getShiftTime(item.other_person_shift)}</strong> for same day.
            </div>
          )}

          <p style={{ fontSize: '12px', color: '#999', margin: '8px 0 0' }}>
            {new Date(item.created_at).toLocaleDateString()} {new Date(item.created_at).toLocaleTimeString()}
          </p>

          <div style={{ display: 'flex', gap: '8px', marginTop: '12px' }}>
            <button
              onClick={() => handleSwapAccept(item.id)}
              disabled={processingId === item.id}
              style={{
                flex: 1,
                padding: '10px 16px',
                background: '#28a745',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                fontSize: '14px',
                fontWeight: '600',
                cursor: processingId === item.id ? 'not-allowed' : 'pointer',
                opacity: processingId === item.id ? 0.7 : 1,
              }}
            >
              {processingId === item.id ? (
                'Processing...'
              ) : (
                <>
                  <Check size={16} style={{ marginRight: '6px', verticalAlign: 'text-bottom' }} />
                  Swap
                </>
              )}
            </button>
            <button
              onClick={() => handleSwapReject(item.id)}
              disabled={processingId === item.id}
              style={{
                flex: 1,
                padding: '10px 16px',
                background: '#dc3545',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                fontSize: '14px',
                fontWeight: '600',
                cursor: processingId === item.id ? 'not-allowed' : 'pointer',
                opacity: processingId === item.id ? 0.7 : 1,
              }}
            >
              {processingId === item.id ? (
                'Processing...'
              ) : (
                <>
                  <X size={16} style={{ marginRight: '6px', verticalAlign: 'text-bottom' }} />
                  Reject
                </>
              )}
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
