import api from './api.js';

export const signup = async (userData) => {
  // role must be 'user' or 'owner' [cite: 247]
  const response = await api.post('/auth/signup', userData);
  return response.data;
};

export const logout = () => {
  localStorage.clear();
  window.location.href = '/login';
};