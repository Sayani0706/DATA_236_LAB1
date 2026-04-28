import { createSlice } from '@reduxjs/toolkit';

const authSlice = createSlice({
  name: 'auth',
  initialState: {
    token: localStorage.getItem('access_token') || null,
    role:  localStorage.getItem('role') || null,
    user:  null,
  },
  reducers: {
    loginSuccess(state, action) {
      state.token = action.payload.token;
      state.role  = action.payload.role;
      localStorage.setItem('access_token', action.payload.token);
      localStorage.setItem('role', action.payload.role);
    },
    logoutSuccess(state) {
      state.token = null;
      state.role  = null;
      state.user  = null;
      localStorage.clear();
    },
    setUser(state, action) {
      state.user = action.payload;
    },
  },
});

export const { loginSuccess, logoutSuccess, setUser } = authSlice.actions;
export default authSlice.reducer;
// Selectors
export const selectToken = (state) => state.auth.token;
export const selectRole = (state) => state.auth.role;
export const selectIsAuthenticated = (state) => !!state.auth.token;
