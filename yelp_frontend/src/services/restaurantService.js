import api from './api.js';

export const getRestaurants = async (params) => {
  const response = await api.get('/restaurants/', { params });
  return response.data;
};

export const getRestaurantDetails = async (id) => {
  const response = await api.get(`/restaurants/${id}`);
  return response.data;
};

export const addToFavorites = async (id) => {
  return await api.post(`/favorites/${id}`);
};
