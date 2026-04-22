import React, { useState } from 'react';
import { findSwap, requestSwap } from '../../../services/api';
import LoadingSpinner from '../../../components/LoadingSpinner/LoadingSpinner';

export default function FindSwapTab({ showToast }) {
  const [formData, setFormData] = useState({ date: '', wantedHour: '10', wantedMeridiem: 'AM' });
  const [results, setResults] = useState([]);
  const [searched, setSearched] = useState(false);
  const [loading, setLoading] = useState(false);
  const [requestingId, setRequestingId] = useState(null);
  const [myIntentId, setMyIntentId] = useState(null);

  const handleChange = (e) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!formData.date) {
      showToast('Please select a date', 'warning');
      return;
    }

    try {
      setLoading(true);
      const response = await findSwap({
        swap_type: 'DAILY',
        daily_mode: 'SINGLE_DAY',
        target_date: formData.date,
        wanted_hour: Number(formData.wantedHour),
        wanted_meridiem: formData.wantedMeridiem,
      });

      setMyIntentId(response.data.my_intent_id);
      setResults(Array.isArray(response.data.matches) ? response.data.matches : []);
      setSearched(true);
    } catch (err) {
      showToast(err.response?.data?.detail || 'Search failed', 'error');
      setResults([]);
      setSearched(true);
    } finally {
      setLoading(false);
    }
  };

  const handleRequestSwap = async (otherIntentId) => {
    if (!myIntentId) {
      showToast('Please search again to create your intent', 'warning');
      return;
    }

    try {
      setRequestingId(otherIntentId);
      await requestSwap({
        my_intent_id: myIntentId,
        other_intent_id: otherIntentId,
        expires_in_minutes: 360,
      });
      showToast('Swap request sent!', 'success');
      setResults((prev) => prev.filter((s) => s.other_intent_id !== otherIntentId));
    } catch (err) {
      showToast(err.response?.data?.detail || 'Request failed', 'error');
    } finally {
      setRequestingId(null);
    }
  };

  return (
    <div>
      <div
        style={{
          background: 'var(--color-white)',
          padding: '24px',
          borderRadius: 'var(--border-radius-md)',
          marginBottom: '24px',
          boxShadow: 'var(--shadow-sm)',
        }}
      >
        <h3 style={{ marginBottom: '20px' }}>Find Available Swaps</h3>
        <form onSubmit={handleSearch}>
          <div style={{ display: 'grid', gap: '20px', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))' }}>
            <div>
              <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500, fontSize: '14px' }}>
                Date
              </label>
              <input
                type="date"
                name="date"
                value={formData.date}
                onChange={handleChange}
                min={new Date().toISOString().split('T')[0]}
                style={{
                  width: '100%',
                  padding: '10px',
                  border: '1px solid var(--color-border)',
                  borderRadius: 'var(--border-radius-sm)',
                  fontSize: '14px',
                }}
              />
            </div>
            <div>
              <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500, fontSize: '14px' }}>
                Desired Hour
              </label>
              <select
                name="wantedHour"
                value={formData.wantedHour}
                onChange={handleChange}
                style={{
                  width: '100%',
                  padding: '10px',
                  border: '1px solid var(--color-border)',
                  borderRadius: 'var(--border-radius-sm)',
                  fontSize: '14px',
                }}
              >
                {Array.from({ length: 12 }, (_, idx) => idx + 1).map((hour) => (
                  <option key={hour} value={hour}>
                    {hour}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500, fontSize: '14px' }}>
                AM/PM
              </label>
              <select
                name="wantedMeridiem"
                value={formData.wantedMeridiem}
                onChange={handleChange}
                style={{
                  width: '100%',
                  padding: '10px',
                  border: '1px solid var(--color-border)',
                  borderRadius: 'var(--border-radius-sm)',
                  fontSize: '14px',
                }}
              >
                <option value="AM">AM</option>
                <option value="PM">PM</option>
              </select>
            </div>
          </div>
          <button
            type="submit"
            disabled={loading}
            style={{
              marginTop: '20px',
              width: '100%',
              padding: '12px',
              background: 'var(--color-primary)',
              color: 'white',
              border: 'none',
              borderRadius: 'var(--border-radius-sm)',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'var(--transition)',
            }}
          >
            {loading ? 'Searching...' : 'Search Available Swaps'}
          </button>
        </form>
      </div>

      {loading && <LoadingSpinner />}

      {searched && !loading && (
        <>
          {results.length === 0 ? (
            <div style={{ textAlign: 'center', color: 'var(--color-text-muted)', padding: '40px 20px' }}>
              No reciprocal swap match found yet.
            </div>
          ) : (
            <div style={{ display: 'grid', gap: '16px' }}>
              {results.map((swap) => (
                <div
                  key={swap.other_intent_id}
                  style={{
                    background: 'var(--color-white)',
                    padding: '20px',
                    borderRadius: 'var(--border-radius-md)',
                    boxShadow: 'var(--shadow-sm)',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    gap: '20px',
                    flexWrap: 'wrap',
                  }}
                >
                  <div>
                    <h4 style={{ marginBottom: '8px' }}>{swap.employee_id}</h4>
                    <p style={{ fontSize: '14px', color: 'var(--color-text-muted)', marginBottom: '4px' }}>
                      Contact: {swap.contact_number}
                    </p>
                    <p style={{ fontSize: '14px', color: 'var(--color-text-muted)' }}>
                      Their current shift: {swap.other_current_payload?.shift}
                    </p>
                  </div>
                  <button
                    onClick={() => handleRequestSwap(swap.other_intent_id)}
                    disabled={requestingId === swap.other_intent_id}
                    style={{
                      padding: '10px 20px',
                      background: 'var(--color-success)',
                      color: 'white',
                      border: 'none',
                      borderRadius: 'var(--border-radius-sm)',
                      fontWeight: 500,
                      cursor: 'pointer',
                      fontSize: '14px',
                      whiteSpace: 'nowrap',
                      transition: 'var(--transition)',
                    }}
                  >
                    {requestingId === swap.other_intent_id ? 'Requesting...' : 'Request Swap'}
                  </button>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
