import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
});

// Request interceptor: attach token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor: handle 401
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('role');
      localStorage.removeItem('user');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

// EMPLOYEE APIs
export const registerEmployee = (data) => 
  api.post('/api/v1/employee/register', data);

export const loginEmployee = (data) => 
  api.post('/api/v1/employee/login', data);

export const getTimetable = () => 
  api.get('/api/v1/employee/timetable');

export const getAvailableShifts = (workDate) =>
  api.get(`/api/v1/employee/timetable/available-shifts/${workDate}`);

export const getEmployeeSummary = () =>
  api.get('/api/v1/employee/summary');

// ADMIN APIs
export const loginAdmin = (data) => 
  api.post('/api/v1/admin/login', data);

export const uploadTimetable = (formData) =>
  api.post('/api/v1/admin/timetable/upload', formData);

export const getPendingRegistrations = () =>
  api.get('/api/v1/admin/registration-requests');

export const approveRegistration = (employee_id) =>
  api.post(`/api/v1/admin/registration-requests/${employee_id}/approve`);

export const rejectRegistration = (employee_id) =>
  api.post(`/api/v1/admin/registration-requests/${employee_id}/reject`);

// SWAP APIs
export const findSwap = (data) =>
  api.post('/api/v1/swap/find', data);

export const requestSwap = (data) =>
  api.post('/api/v1/swap/request', data);

export const decideSwap = (request_id, decision) =>
  api.post(`/api/v1/swap/requests/${request_id}/decision`, { decision });

export const getSwapHistory = () =>
  api.get('/api/v1/swap/history');

export const getSwapInbox = () =>
  api.get('/api/v1/swap/inbox');

// HEALTH
export const checkHealth = () =>
  api.get('/health');

export default api;

