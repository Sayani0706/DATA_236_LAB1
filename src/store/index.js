import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import restaurantReducer from './slices/restaurantSlice';
import reviewReducer from './slices/reviewSlice';
import favouritesReducer from './slices/favouritesSlice';

const store = configureStore({
  reducer: {
    auth: authReducer,
    restaurants: restaurantReducer,
    reviews: reviewReducer,
    favourites: favouritesReducer,
  },
});

export default store;