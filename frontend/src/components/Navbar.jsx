import React from 'react';
import { useAuth } from '../context/AuthContext';
import { LogOut } from 'lucide-react';

export default function Navbar() {
  const { role, logout } = useAuth();
  
  return (
    <nav className="navbar">
      <div className="navbar-brand">
        SwapShift <span style={{ fontWeight: 400, fontSize: '0.875rem', color: 'var(--text-tertiary)', marginLeft: '0.5rem' }}>{role === 'admin' ? 'Admin Portal' : 'Employee Portal'}</span>
      </div>
      
      <div className="navbar-nav">
        <span className="nav-link active">Dashboard</span>
        <button onClick={logout} className="btn btn-outline" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.5rem 1rem' }}>
          <LogOut size={16} /> Logout
        </button>
      </div>
    </nav>
  );
}
