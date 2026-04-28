import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../services/api.js';

// Async thunk — fetches restaurants from the backend
export const fetchRestaurants = createAsyncThunk(
  'restaurants/fetchAll',
  async (filters = {}, { rejectWithValue }) => {
    try {
      const params = {};
      if (filters.name)    params.name    = filters.name;
      if (filters.cuisine) params.cuisine = filters.cuisine;
      if (filters.keyword) params.keyword = filters.keyword;
      if (filters.city)    params.city    = filters.city;
      if (filters.zip)     params.zip     = filters.zip;
      if (filters.sort_by) params.sort_by = filters.sort_by;
      const res = await api.get('/restaurants/', { params });
      return res.data;
    } catch (err) {
      return rejectWithValue(err.response?.data || 'Failed to fetch restaurants');
    }
  }
);

const restaurantSlice = createSlice({
  name: 'restaurants',
  initialState: {
    list:    [],
    loading: false,
    error:   null,
    filters: {
      name: '', cuisine: '', keyword: '', city: '', zip: '', sort_by: ''
    },
  },
  reducers: {
    setFilters(state, action) {
      state.filters = { ...state.filters, ...action.payload };
    },
    clearFilters(state) {
      state.filters = { name: '', cuisine: '', keyword: '', city: '', zip: '', sort_by: '' };
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchRestaurants.pending, (state) => {
        state.loading = true;
        state.error   = null;
      })
      .addCase(fetchRestaurants.fulfilled, (state, action) => {
        state.loading = false;
        state.list    = action.payload;
      })
      .addCase(fetchRestaurants.rejected, (state, action) => {
        state.loading = false;
        state.error   = action.payload;
      });
  },
});

export const { setFilters, clearFilters } = restaurantSlice.actions;
export default restaurantSlice.reducer;