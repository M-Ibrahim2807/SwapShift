export function useAuth() {
  const token = localStorage.getItem('token');
  const role = localStorage.getItem('role');

  return {
    token,
    role,
    isAuthenticated: !!token,
    isEmployee: role === 'employee',
    isAdmin: role === 'admin',
  };
}
