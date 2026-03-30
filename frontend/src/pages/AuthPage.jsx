import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { loginEmployee, loginAdmin, registerEmployee } from '../services/api';
import { Lock, User, Phone, Shield } from 'lucide-react';

export default function AuthPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [isAdmin, setIsAdmin] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const [formData, setFormData] = useState({
    employee_id: '',
    contact_number: '',
    username: '',
    password: ''
  });

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      if (isAdmin) {
        // Admin Login
        const res = await loginAdmin({ username: formData.username, password: formData.password });
        login(res.data, 'admin');
        navigate('/admin');
      } else {
        if (isLogin) {
          // Employee Login
          const res = await loginEmployee({ employee_id: formData.employee_id, contact_number: formData.contact_number });
          login(res.data, 'employee');
          navigate('/dashboard');
        } else {
          // Employee Register
          await registerEmployee({ employee_id: formData.employee_id, contact_number: formData.contact_number });
          alert("Registration request sent! Please wait for admin approval before logging in.");
          setIsLogin(true);
        }
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-wrapper">
      <div className="auth-card">
        <h1 style={{ textAlign: 'center', marginBottom: '1.5rem', fontWeight: 700 }}>SwapShift</h1>
        
        {/* Role Toggle */}
        <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '2rem', background: 'var(--bg-secondary)', padding: '0.25rem', borderRadius: 'var(--border-radius)' }}>
          <button 
            type="button"
            className="btn" 
            style={{ flex: 1, backgroundColor: !isAdmin ? 'var(--bg-tertiary)' : 'transparent', color: !isAdmin ? 'var(--text-primary)' : 'var(--text-secondary)', boxShadow: !isAdmin ? 'var(--shadow-sm)' : 'none' }}
            onClick={() => { setIsAdmin(false); setError(''); }}
          >
            <User size={16} /> Employee
          </button>
          <button 
            type="button" 
            className="btn" 
            style={{ flex: 1, backgroundColor: isAdmin ? 'var(--bg-tertiary)' : 'transparent', color: isAdmin ? 'var(--text-primary)' : 'var(--text-secondary)', boxShadow: isAdmin ? 'var(--shadow-sm)' : 'none' }}
            onClick={() => { setIsAdmin(true); setError(''); }}
          >
            <Shield size={16} /> Admin
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          {error && <div className="error-message">{error}</div>}

          {/* Admin Fields */}
          {isAdmin && (
            <>
              <div className="input-group">
                <label className="input-label">Username</label>
                <div style={{ position: 'relative' }}>
                  <User size={18} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-tertiary)' }} />
                  <input type="text" name="username" className="input-field" style={{ paddingLeft: '2.5rem' }} value={formData.username} onChange={handleChange} required />
                </div>
              </div>
              <div className="input-group">
                <label className="input-label">Password</label>
                <div style={{ position: 'relative' }}>
                  <Lock size={18} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-tertiary)' }} />
                  <input type="password" name="password" className="input-field" style={{ paddingLeft: '2.5rem' }} value={formData.password} onChange={handleChange} required />
                </div>
              </div>
            </>
          )}

          {/* Employee Fields */}
          {!isAdmin && (
            <>
              <div className="input-group">
                <label className="input-label">Employee ID</label>
                <div style={{ position: 'relative' }}>
                  <User size={18} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-tertiary)' }} />
                  <input type="text" name="employee_id" className="input-field" style={{ paddingLeft: '2.5rem' }} value={formData.employee_id} onChange={handleChange} required />
                </div>
              </div>
              <div className="input-group">
                <label className="input-label">Contact Number <span style={{fontWeight: 400, color: 'var(--text-tertiary)'}}>(Serves as password temp)</span></label>
                <div style={{ position: 'relative' }}>
                  <Phone size={18} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-tertiary)' }} />
                  <input type="text" name="contact_number" className="input-field" style={{ paddingLeft: '2.5rem' }} value={formData.contact_number} onChange={handleChange} placeholder="+1234567890" required />
                </div>
              </div>
            </>
          )}

          <button type="submit" className="btn btn-primary" style={{ width: '100%', padding: '0.875rem' }} disabled={loading}>
            {loading ? 'Processing...' : (isAdmin || isLogin ? 'Sign In' : 'Register')}
          </button>
        </form>

        {!isAdmin && (
          <div style={{ textAlign: 'center', marginTop: '1.5rem', fontSize: '0.875rem' }}>
            <span style={{ color: 'var(--text-secondary)' }}>
              {isLogin ? "Don't have an account?" : "Already requested?"}
            </span>
            {' '}
            <button 
              type="button" 
              style={{ background: 'none', border: 'none', color: 'var(--text-primary)', fontWeight: 600, cursor: 'pointer', outline: 'none' }}
              onClick={() => setIsLogin(!isLogin)}
            >
              {isLogin ? 'Register now.' : 'Login here.'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
