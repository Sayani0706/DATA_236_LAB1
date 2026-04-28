import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../services/api.js';

// Submit a review (triggers Kafka flow on backend)
export const submitReview = createAsyncThunk(
  'reviews/submitReview',
  async ({ restaurantId, rating, comment, photo }, { rejectWithValue }) => {
    try {
      // Step 1 — post the review (backend publishes to Kafka review.created topic)
      const reviewRes = await api.post('/reviews/', {
        restaurant_id: restaurantId,
        rating: parseInt(rating),
        comment,
      });

      const reviewId = reviewRes.data.id;

      // Step 2 — upload photo if provided
      if (photo) {
        const formData = new FormData();
        formData.append('file', photo);
        await api.post(`/reviews/${reviewId}/photos`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
      }

      return reviewRes.data;
    } catch (err) {
      return rejectWithValue(err.response?.data?.detail || 'Failed to submit review');
    }
  }
);

// Fetch reviews for a restaurant
export const fetchReviews = createAsyncThunk(
  'reviews/fetchReviews',
  async (restaurantId, { rejectWithValue }) => {
    try {
      const res = await api.get(`/restaurants/${restaurantId}/reviews`);
      return res.data;
    } catch (err) {
      return rejectWithValue(err.response?.data?.detail || 'Failed to fetch reviews');
    }
  }
);

const reviewSlice = createSlice({
  name: 'reviews',
  initialState: {
    list: [],
    submitting: false,
    loading: false,
    submitSuccess: false,
    error: null,
  },
  reducers: {
    resetSubmitStatus(state) {
      state.submitSuccess = false;
      state.error = null;
    },
    clearReviewError(state) {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // submitReview
      .addCase(submitReview.pending, (state) => {
        state.submitting = true;
        state.submitSuccess = false;
        state.error = null;
      })
      .addCase(submitReview.fulfilled, (state, action) => {
        state.submitting = false;
        state.submitSuccess = true;
        state.list.unshift(action.payload); // prepend new review
      })
      .addCase(submitReview.rejected, (state, action) => {
        state.submitting = false;
        state.error = action.payload;
      })
      // fetchReviews
      .addCase(fetchReviews.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchReviews.fulfilled, (state, action) => {
        state.loading = false;
        state.list = action.payload;
      })
      .addCase(fetchReviews.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export const { resetSubmitStatus, clearReviewError } = reviewSlice.actions;

// Selectors
export const selectReviewList = (state) => state.reviews.list;
export const selectReviewSubmitting = (state) => state.reviews.submitting;
export const selectReviewLoading = (state) => state.reviews.loading;
export const selectReviewSubmitSuccess = (state) => state.reviews.submitSuccess;
export const selectReviewError = (state) => state.reviews.error;

export default reviewSlice.reducer;