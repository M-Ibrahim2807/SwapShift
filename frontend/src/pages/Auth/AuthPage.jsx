import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { registerEmployee } from '../../services/api';
import { useToast } from '../../context/ToastContext';
import './AuthPage.css';

export default function AuthPage() {
  const navigate = useNavigate();
  const { loginEmployee, loginAdmin } = useAuth();
  const { showToast } = useToast();
  
  const [mode, setMode] = useState('employee-login');
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    employee_id: '',
    contact_number: '',
    username: '',
    password: '',
  });
  const [errors, setErrors] = useState({});

  // Validation functions
  const validateEmployeeId = (value) => {
    if (!value.trim()) return 'Employee ID is required';
    if (value.trim().length < 2) return 'Employee ID must be at least 2 characters';
    if (!/^[a-zA-Z0-9_-]+$/.test(value)) return 'Employee ID can only contain letters, numbers, hyphens and underscores';
    return '';
  };

  const validatePassword = (value) => {
    if (!value) return 'Password is required';
    if (value.length < 8) return 'Password must be at least 8 characters';
    return '';
  };

  const validateUsername = (value) => {
    if (!value.trim()) return 'Username is required';
    if (value.trim().length < 2) return 'Username must be at least 2 characters';
    return '';
  };

  const validateContactNumber = (value) => {
    if (!value.trim()) return 'Contact number is required';
    if (!/^[0-9\s\-\+\(\)]+$/.test(value)) return 'Contact number is invalid';
    if (value.replace(/\D/g, '').length < 10) return 'Contact number must have at least 10 digits';
    return '';
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    
    // Clear error for this field when user starts typing
    if (errors[name]) {
      setErrors((prev) => ({
        ...prev,
        [name]: '',
      }));
    }
  };

  const validateEmployeeLoginForm = () => {
    const newErrors = {};
    
    const employeeIdError = validateEmployeeId(formData.employee_id);
    if (employeeIdError) newErrors.employee_id = employeeIdError;
    
    const passwordError = validatePassword(formData.password);
    if (passwordError) newErrors.password = passwordError;
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const validateAdminLoginForm = () => {
    const newErrors = {};
    
    const usernameError = validateUsername(formData.username);
    if (usernameError) newErrors.username = usernameError;
    
    const passwordError = validatePassword(formData.password);
    if (passwordError) newErrors.password = passwordError;
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const validateRegisterForm = () => {
    const newErrors = {};
    
    const employeeIdError = validateEmployeeId(formData.employee_id);
    if (employeeIdError) newErrors.employee_id = employeeIdError;
    
    const contactError = validateContactNumber(formData.contact_number);
    if (contactError) newErrors.contact_number = contactError;
    
    const passwordError = validatePassword(formData.password);
    if (passwordError) newErrors.password = passwordError;
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleEmployeeLogin = async (e) => {
    e.preventDefault();
    
    if (!validateEmployeeLoginForm()) return;
    
    setIsLoading(true);
    const result = await loginEmployee(formData.employee_id, formData.password);
    setIsLoading(false);
    
    if (result.success) {
      showToast('Login successful!', 'success');
      navigate('/dashboard');
    } else {
      // Distinguish between invalid credentials and server errors
      if (result.error && result.error.includes('Invalid employee ID or password')) {
        setErrors({
          employee_id: 'Invalid employee ID or password',
          password: 'Invalid employee ID or password',
        });
        showToast('Invalid employee ID or password', 'error');
      } else {
        showToast(result.error || 'Login failed. Please try again.', 'error');
      }
    }
  };

  const handleAdminLogin = async (e) => {
    e.preventDefault();
    
    if (!validateAdminLoginForm()) return;
    
    setIsLoading(true);
    const result = await loginAdmin(formData.username, formData.password);
    setIsLoading(false);
    
    if (result.success) {
      showToast('Login successful!', 'success');
      navigate('/admin');
    } else {
      // Distinguish between invalid credentials and server errors
      if (result.error && result.error.includes('Invalid username or password')) {
        setErrors({
          username: 'Invalid username or password',
          password: 'Invalid username or password',
        });
        showToast('Invalid username or password', 'error');
      } else {
        showToast(result.error || 'Login failed. Please try again.', 'error');
      }
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    
    if (!validateRegisterForm()) return;
    
    setIsLoading(true);
    
    try {
      await registerEmployee({
        employee_id: formData.employee_id,
        contact_number: formData.contact_number,
        password: formData.password,
      });
      showToast('Registration completed. Please login now.', 'success');
      setMode('employee-login');
      setFormData({
        employee_id: '',
        contact_number: '',
        username: '',
        password: '',
      });
      setErrors({});
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Registration failed';
      showToast(errorMessage, 'error');
      
      // Show field-specific errors if available
      if (error.response?.data?.fields) {
        setErrors(error.response.data.fields);
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1 className="auth-title">SwapShift</h1>

        <div className="auth-toggle">
          <button
            className={`toggle-btn ${mode === 'employee-login' ? 'active' : ''}`}
            onClick={() => setMode('employee-login')}
            type="button"
          >
            Employee
          </button>
          <button
            className={`toggle-btn ${mode === 'admin-login' ? 'active' : ''}`}
            onClick={() => setMode('admin-login')}
            type="button"
          >
            Admin
          </button>
        </div>

        {mode === 'employee-login' && (
          <form onSubmit={handleEmployeeLogin} className="auth-form">
            <div className="form-group">
              <label className="form-label">Employee ID</label>
              <input
                type="text"
                name="employee_id"
                className={`form-input ${errors.employee_id ? 'form-input-error' : ''}`}
                value={formData.employee_id}
                onChange={handleChange}
                placeholder="Enter your employee ID"
              />
              {errors.employee_id && (
                <span className="form-error">{errors.employee_id}</span>
              )}
            </div>
            <div className="form-group">
              <label className="form-label">Password</label>
              <input
                type="password"
                name="password"
                className={`form-input ${errors.password ? 'form-input-error' : ''}`}
                value={formData.password}
                onChange={handleChange}
                placeholder="Enter your password"
              />
              {errors.password && (
                <span className="form-error">{errors.password}</span>
              )}
            </div>
            <button
              type="submit"
              className="form-submit"
              disabled={isLoading}
            >
              {isLoading ? 'Signing in...' : 'Sign In'}
            </button>
            <p className="auth-footer">
              Don't have an account?{' '}
              <button
                type="button"
                className="link-btn"
                onClick={() => {
                  setMode('register');
                  setFormData({
                    employee_id: '',
                    contact_number: '',
                    username: '',
                    password: '',
                  });
                  setErrors({});
                }}
              >
                Register here
              </button>
            </p>
          </form>
        )}

        {mode === 'admin-login' && (
          <form onSubmit={handleAdminLogin} className="auth-form">
            <div className="form-group">
              <label className="form-label">Username</label>
              <input
                type="text"
                name="username"
                className={`form-input ${errors.username ? 'form-input-error' : ''}`}
                value={formData.username}
                onChange={handleChange}
                placeholder="Enter your username"
              />
              {errors.username && (
                <span className="form-error">{errors.username}</span>
              )}
            </div>
            <div className="form-group">
              <label className="form-label">Password</label>
              <input
                type="password"
                name="password"
                className={`form-input ${errors.password ? 'form-input-error' : ''}`}
                value={formData.password}
                onChange={handleChange}
                placeholder="Enter your password"
              />
              {errors.password && (
                <span className="form-error">{errors.password}</span>
              )}
            </div>
            <button
              type="submit"
              className="form-submit"
              disabled={isLoading}
            >
              {isLoading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>
        )}

        {mode === 'register' && (
          <form onSubmit={handleRegister} className="auth-form">
            <div className="form-group">
              <label className="form-label">Employee ID</label>
              <input
                type="text"
                name="employee_id"
                className={`form-input ${errors.employee_id ? 'form-input-error' : ''}`}
                value={formData.employee_id}
                onChange={handleChange}
                placeholder="Enter your employee ID"
              />
              {errors.employee_id && (
                <span className="form-error">{errors.employee_id}</span>
              )}
            </div>
            <div className="form-group">
              <label className="form-label">Contact Number</label>
              <input
                type="tel"
                name="contact_number"
                className={`form-input ${errors.contact_number ? 'form-input-error' : ''}`}
                value={formData.contact_number}
                onChange={handleChange}
                placeholder="Enter your contact number"
              />
              {errors.contact_number && (
                <span className="form-error">{errors.contact_number}</span>
              )}
            </div>
            <div className="form-group">
              <label className="form-label">Password</label>
              <input
                type="password"
                name="password"
                className={`form-input ${errors.password ? 'form-input-error' : ''}`}
                value={formData.password}
                onChange={handleChange}
                placeholder="Minimum 6 characters"
              />
              {errors.password && (
                <span className="form-error">{errors.password}</span>
              )}
            </div>
            <button
              type="submit"
              className="form-submit"
              disabled={isLoading}
            >
              {isLoading ? 'Registering...' : 'Register'}
            </button>
            <p className="auth-footer">
              Already registered?{' '}
              <button
                type="button"
                className="link-btn"
                onClick={() => {
                  setMode('employee-login');
                  setFormData({
                    employee_id: '',
                    contact_number: '',
                    username: '',
                    password: '',
                  });
                  setErrors({});
                }}
              >
                Sign in here
              </button>
            </p>
          </form>
        )}
      </div>
    </div>
  );
}
