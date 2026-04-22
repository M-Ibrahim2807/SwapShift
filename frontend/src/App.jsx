import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ToastProvider } from './context/ToastContext';
import { AuthProvider } from './context/AuthContext';
import { NotificationProvider } from './context/NotificationContext';
import ProtectedRoute from './components/ProtectedRoute/ProtectedRoute';

// Pages
import AuthPage from './pages/Auth/AuthPage';
import PendingApproval from './pages/PendingApproval/PendingApproval';
import EmployeeDashboard from './pages/EmployeeDashboard/EmployeeDashboard';
import AdminDashboard from './pages/AdminDashboard/AdminDashboard';
import NotFound from './pages/NotFound/NotFound';

export default function App() {
  return (
    <Router>
      <AuthProvider>
        <ToastProvider>
          <NotificationProvider>
            <Routes>
              <Route path="/" element={<AuthPage />} />
              <Route path="/pending" element={<PendingApproval />} />
              <Route 
                path="/dashboard" 
                element={
                  <ProtectedRoute requiredRole="employee">
                    <EmployeeDashboard />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/admin" 
                element={
                  <ProtectedRoute requiredRole="admin">
                    <AdminDashboard />
                  </ProtectedRoute>
                } 
              />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </NotificationProvider>
        </ToastProvider>
      </AuthProvider>
    </Router>
  );
}
