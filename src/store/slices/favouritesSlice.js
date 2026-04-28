import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../services/api.js';

// Fetch user's favourites
export const fetchFavourites = createAsyncThunk(
  'favourites/fetchFavourites',
  async (_, { rejectWithValue }) => {
    try {
      const res = await api.get('/favorites/');
      return res.data;
    } catch (err) {
      return rejectWithValue(err.response?.data?.detail || 'Failed to fetch favourites');
    }
  }
);

// Add a restaurant to favourites
export const addFavourite = createAsyncThunk(
  'favourites/addFavourite',
  async (restaurantId, { rejectWithValue }) => {
    try {
      await api.post(`/favorites/${restaurantId}`);
      return restaurantId;
    } catch (err) {
      return rejectWithValue(err.response?.data?.detail || 'Failed to add favourite');
    }
  }
);

// Remove a restaurant from favourites
export const removeFavourite = createAsyncThunk(
  'favourites/removeFavourite',
  async (restaurantId, { rejectWithValue }) => {
    try {
      await api.delete(`/favorites/${restaurantId}`);
      return restaurantId;
    } catch (err) {
      return rejectWithValue(err.response?.data?.detail || 'Failed to remove favourite');
    }
  }
);

const favouritesSlice = createSlice({
  name: 'favourites',
  initialState: {
    list: [],       // array of restaurant objects
    ids: [],        // array of restaurant IDs (quick lookup)
    loading: false,
    error: null,
  },
  reducers: {
    clearFavouritesError(state) {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // fetchFavourites
      .addCase(fetchFavourites.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchFavourites.fulfilled, (state, action) => {
        state.loading = false;
        state.list = action.payload;
        state.ids = action.payload.map((r) => r.id);
      })
      .addCase(fetchFavourites.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // addFavourite
      .addCase(addFavourite.fulfilled, (state, action) => {
        if (!state.ids.includes(action.payload)) {
          state.ids.push(action.payload);
        }
      })
      .addCase(addFavourite.rejected, (state, action) => {
        state.error = action.payload;
      })
      // removeFavourite
      .addCase(removeFavourite.fulfilled, (state, action) => {
        state.ids = state.ids.filter((id) => id !== action.payload);
        state.list = state.list.filter((r) => r.id !== action.payload);
      })
      .addCase(removeFavourite.rejected, (state, action) => {
        state.error = action.payload;
      });
  },
});

export const { clearFavouritesError } = favouritesSlice.actions;

// Selectors
export const selectFavouritesList = (state) => state.favourites.list;
export const selectFavouriteIds = (state) => state.favourites.ids;
export const selectFavouritesLoading = (state) => state.favourites.loading;
export const selectIsFavourite = (restaurantId) => (state) =>
  state.favourites.ids.includes(restaurantId);

export default favouritesSlice.reducer;