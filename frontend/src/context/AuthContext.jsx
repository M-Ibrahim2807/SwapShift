import React, { createContext, useContext, useState, useEffect } from 'react';
import { loginEmployee as apiLoginEmployee, loginAdmin as apiLoginAdmin } from '../services/api';

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [token, setToken] = useState(null);
  const [role, setRole] = useState(null);
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    const storedRole = localStorage.getItem('role');
    const storedUser = localStorage.getItem('user');
    
    if (storedToken) {
      setToken(storedToken);
      setRole(storedRole);
      try {
        setUser(storedUser && storedUser !== 'undefined' ? JSON.parse(storedUser) : null);
      } catch (error) {
        console.error('Failed to parse user from localStorage:', error);
        setUser(null);
        localStorage.removeItem('user');
      }
    }
    setIsLoading(false);
  }, []);

  const loginEmployee = async (employee_id, password) => {
    try {
      const response = await apiLoginEmployee({ employee_id, password });
      const { access_token } = response.data;
      const userData = { employee_id };
      
      localStorage.setItem('token', access_token);
      localStorage.setItem('role', 'employee');
      localStorage.setItem('user', JSON.stringify(userData));
      
      setToken(access_token);
      setRole('employee');
      setUser(userData);
      
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Login failed',
      };
    }
  };

  const loginAdmin = async (username, password) => {
    try {
      const response = await apiLoginAdmin({ username, password });
      const { access_token } = response.data;
      const userData = { username };
      
      localStorage.setItem('token', access_token);
      localStorage.setItem('role', 'admin');
      localStorage.setItem('user', JSON.stringify(userData));
      
      setToken(access_token);
      setRole('admin');
      setUser(userData);
      
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Login failed',
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    localStorage.removeItem('user');
    setToken(null);
    setRole(null);
    setUser(null);
    window.location.href = '/';
  };

  const value = {
    token,
    role,
    user,
    isLoading,
    loginEmployee,
    loginAdmin,
    logout,
    isAuthenticated: !!token,
    isAdmin: role === 'admin',
    isEmployee: role === 'employee',
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
