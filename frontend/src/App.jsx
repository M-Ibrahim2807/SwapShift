import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import AuthPage from './pages/AuthPage';

const PrivateRoute = ({ children, allowedRoles }) => {
  const { isAuthenticated, role, loading } = useAuth();
  
  if (loading) return <div>Loading...</div>;

  if (!isAuthenticated) {
    return <Navigate to="/auth" />;
  }

  if (allowedRoles && !allowedRoles.includes(role)) {
    return <Navigate to="/" />; // Or unauthorized page
  }

  return children;
};

import EmployeeDashboard from './pages/EmployeeDashboard';
import AdminDashboard from './pages/AdminDashboard';
function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="app-container">
          <Routes>
            <Route path="/auth" element={<AuthPage />} />
            
            <Route path="/dashboard" element={
              <PrivateRoute allowedRoles={['employee']}>
                <EmployeeDashboard />
              </PrivateRoute>
            } />
            
            <Route path="/admin" element={
              <PrivateRoute allowedRoles={['admin']}>
                <AdminDashboard />
              </PrivateRoute>
            } />
            
            <Route path="/" element={<Navigate to="/auth" />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
