import api from './api';

export const getRestaurants = async (params) => {
  const response = await api.get('/restaurants/', { params }); // [cite: 264]
  return response.data;
};

export const getRestaurantDetails = async (id) => {
  const response = await api.get(`/restaurants/${id}`); // [cite: 267]
  return response.data;
};

export const addToFavorites = async (id) => {
  return await api.post(`/favorites/${id}`); // [cite: 283]
};