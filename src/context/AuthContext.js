import React, { createContext } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { loginSuccess, logoutSuccess } from '../store/slices/authSlice.js';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const dispatch = useDispatch();
  const { token, role } = useSelector((state) => state.auth);

  const login = (newToken, newRole) => {
    dispatch(loginSuccess({ token: newToken, role: newRole }));
  };

  const logout = () => {
    dispatch(logoutSuccess());
  };

  return (
    <AuthContext.Provider value={{ token, role, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};