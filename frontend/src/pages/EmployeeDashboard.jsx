import React, { useEffect, useState } from 'react';
import Navbar from '../components/Navbar';
import { getMyTimetable, getRequestsInbox, decideSwapRequest, findSwap, requestSwap } from '../services/api';
import { Calendar, CheckCircle, XCircle, Search, ArrowRightLeft } from 'lucide-react';

export default function EmployeeDashboard() {
  const [timetable, setTimetable] = useState(null);
  const [inbox, setInbox] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Swap specific state
  const [isSearching, setIsSearching] = useState(false);
  const [swapCandidates, setSwapCandidates] = useState([]);
  const [swapData, setSwapData] = useState({ target_date: '', wanted_shift: '' });
  const [myIntentId, setMyIntentId] = useState(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [ttRes, inboxRes] = await Promise.all([
        getMyTimetable(),
        getRequestsInbox()
      ]);
      setTimetable(ttRes.data);
      setInbox(inboxRes.data);
    } catch (err) {
      setError('Could not load dashboard data. Are you approved by admin?');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleDecide = async (id, decision) => {
    try {
      await decideSwapRequest(id, decision);
      alert(`Request ${decision.toLowerCase()} successfully.`);
      fetchData(); // refresh inbox & timetable
    } catch (err) {
      alert(err.response?.data?.detail || 'Error processing request');
    }
  };

  const handeFindSwapSearch = async (e) => {
    e.preventDefault();
    try {
      setIsSearching(true);
      const res = await findSwap({
        swap_type: 'DAILY',
        target_date: swapData.target_date,
        wanted_shift: swapData.wanted_shift
      });
      setMyIntentId(res.data.my_intent_id);
      setSwapCandidates(res.data.matches);
    } catch (err) {
      alert(err.response?.data?.detail || 'Error finding swaps');
    } finally {
      setIsSearching(false);
    }
  };

  const handleSendRequest = async (otherIntentId) => {
    try {
      await requestSwap({
        my_intent_id: myIntentId,
        other_intent_id: otherIntentId,
        expires_in_minutes: 120
      });
      alert('Swap requested successfully! Wait for their approval.');
      setSwapCandidates([]);
    } catch (err) {
      alert(err.response?.data?.detail || 'Error sending request');
    }
  };

  return (
    <div className="app-container">
      <Navbar />
      
      <main className="main-content">
        <h1 style={{ marginBottom: '2rem' }}>Welcome to your Dashboard</h1>
        
        {loading && <p>Loading data...</p>}
        {error && <p className="error-message" style={{ background: 'var(--danger-color)', color: 'white', padding: '1rem', borderRadius: 'var(--border-radius)' }}>{error}</p>}

        {!loading && !error && (
          <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 2fr) minmax(0, 1fr)', gap: '2rem', alignItems: 'start' }}>
            
            {/* Left Column - Timetable & Find Swap */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
              
              <div className="card">
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
                  <Calendar size={24} color="var(--accent-color)" />
                  <h2 style={{ margin: 0 }}>My Timetable (This Week)</h2>
                </div>
                
                {timetable?.rows ? (
                  <div style={{ overflowX: 'auto' }}>
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Date</th>
                          <th>Shift</th>
                        </tr>
                      </thead>
                      <tbody>
                        {timetable.rows.map(r => (
                          <tr key={r.date}>
                            <td style={{ fontWeight: 500 }}>{r.date}</td>
                            <td>
                              <span className={`badge ${r.shift_name === 'OFF' ? 'danger' : 'success'}`}>
                                {r.shift_name}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <p>No timetable uploaded for you yet.</p>
                )}
              </div>

              <div className="card">
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
                  <Search size={24} color="var(--accent-color)" />
                  <h2 style={{ margin: 0 }}>Find a Swap (Daily)</h2>
                </div>
                <form onSubmit={handeFindSwapSearch} style={{ display: 'flex', gap: '1rem', alignItems: 'flex-end', marginBottom: '1.5rem' }}>
                  <div className="input-group" style={{ marginBottom: 0, flex: 1 }}>
                    <label className="input-label">Date to Swap</label>
                    <input type="date" className="input-field" value={swapData.target_date} onChange={e => setSwapData({...swapData, target_date: e.target.value})} required />
                  </div>
                  <div className="input-group" style={{ marginBottom: 0, flex: 1 }}>
                    <label className="input-label">Wanted Shift</label>
                    <input
                      type="text"
                      className="input-field"
                      placeholder="e.g. 1:00 AM or OFF"
                      value={swapData.wanted_shift}
                      onChange={e => setSwapData({...swapData, wanted_shift: e.target.value})}
                      required
                    />
                  </div>
                  <button type="submit" className="btn btn-primary" disabled={isSearching}>{isSearching ? '...' : 'Search'}</button>
                </form>

                {swapCandidates.length > 0 && (
                  <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '1.5rem' }}>
                    <h3>Matches ({swapCandidates.length})</h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '1rem' }}>
                      {swapCandidates.map(c => (
                        <div key={c.other_intent_id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1rem', background: 'var(--bg-secondary)', borderRadius: 'var(--border-radius)' }}>
                          <div>
                            <div style={{ fontWeight: 600 }}>Colleague wants: {c.my_wanted_payload.shift}</div>
                            <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>They can offer their {c.other_current_payload.shift} shift</div>
                          </div>
                          <button onClick={() => handleSendRequest(c.other_intent_id)} className="btn btn-secondary">Request Swap</button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

            </div>

            {/* Right Column - Inbox */}
            <div className="card">
               <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
                  <ArrowRightLeft size={24} color="var(--accent-color)" />
                  <h2 style={{ margin: 0 }}>Swap Inbox</h2>
                </div>
                
                {inbox.length === 0 ? (
                  <p style={{ textAlign: 'center', color: 'var(--text-tertiary)', padding: '2rem 0' }}>No pending requests.</p>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    {inbox.map(req => (
                      <div key={req.id} style={{ border: '1px solid var(--border-color)', borderRadius: 'var(--border-radius)', padding: '1rem' }}>
                        <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>Expire: {new Date(req.expires_at).toLocaleString()}</div>
                        <div style={{ fontWeight: 500, marginBottom: '1rem' }}>
                          Swap requested for {req.start_date} <br/> Type: {req.swap_type}
                        </div>
                        <div style={{ display: 'flex', gap: '0.5rem' }}>
                          <button onClick={() => handleDecide(req.id, 'ACCEPT')} className="btn btn-primary" style={{ flex: 1, backgroundColor: 'var(--success-color)' }}><CheckCircle size={16}/> Accept</button>
                          <button onClick={() => handleDecide(req.id, 'REJECT')} className="btn btn-danger" style={{ flex: 1 }}><XCircle size={16}/> Reject</button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
            </div>

          </div>
        )}
      </main>
    </div>
  );
}
