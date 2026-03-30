import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [role, setRole] = useState(localStorage.getItem('userRole'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // If we have token but want to fetch the employee data on load, we can do it here.
    // For now, simple JWT storage is sufficient.
    setLoading(false);
  }, [token]);

  const login = (jwtData, userRole) => {
    localStorage.setItem('token', jwtData.access_token);
    localStorage.setItem('userRole', userRole);
    setToken(jwtData.access_token);
    setRole(userRole);
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('userRole');
    setToken(null);
    setRole(null);
  };

  return (
    <AuthContext.Provider value={{ token, role, login, logout, isAuthenticated: !!token, loading }}>
        {!loading && children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
