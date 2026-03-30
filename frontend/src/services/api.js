import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor: Attach token if exists
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response Interceptor: Handle auth errors globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Clear token on unauthorized
      localStorage.removeItem('token');
      localStorage.removeItem('userRole');
      window.location.href = '/auth';
    }
    return Promise.reject(error);
  }
);

// Auth endpoints
export const loginEmployee = (data) => api.post('/employee/login', data);
export const registerEmployee = (data) => api.post('/employee/register', data);
export const loginAdmin = (data) => api.post('/admin/login', data);

// Employee endpoints
export const getMyTimetable = () => api.get('/employee/timetable');
export const getRequestsInbox = () => api.get('/swap/inbox');
export const getSwapHistory = () => api.get('/swap/history');
export const findSwap = (data) => api.post('/swap/find', data);
export const requestSwap = (data) => api.post('/swap/request', data);
export const decideSwapRequest = (requestId, decision) =>
  api.post(`/swap/requests/${requestId}/decision`, { decision });

// Admin endpoints
export const getPendingRegistrations = () => api.get('/admin/registration-requests');
export const approveRegistration = (employeeId) => api.post(`/admin/registration-requests/${employeeId}/approve`);
export const rejectRegistration = (employeeId) => api.post(`/admin/registration-requests/${employeeId}/reject`);

export const uploadTimetable = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/admin/timetable/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

export default api;
