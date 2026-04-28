import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchRestaurants } from '../../store/slices/restaurantSlice.js';
import ChatWindow from '../../components/Chat/ChatWindow.js';
import RestaurantCard from '../../components/Restaurant/RestaurantCard.js';

const Dashboard = () => {
  const dispatch = useDispatch();
  const { list: restaurants, loading, error } = useSelector((state) => state.restaurants);

  useEffect(() => {
    dispatch(fetchRestaurants());
  }, [dispatch]);

  return (
    <div className="container-fluid p-4">
      <div className="row">
        <div className="col-md-8">
          <h2 className="mb-4">Recommended for You</h2>

          {loading && (
            <div className="text-center my-4">
              <div className="spinner-border text-danger" role="status">
                <span className="visually-hidden">Loading...</span>
              </div>
            </div>
          )}

          {error && (
            <div className="alert alert-danger">Failed to load restaurants.</div>
          )}

          <div className="row">
            {restaurants.map(item => (
              <div key={item.restaurant?.id || item.id} className="col-md-6">
                <RestaurantCard
                  restaurant={item.restaurant || item}
                  avgRating={item.avg_rating}
                  reviewCount={item.review_count}
                />
              </div>
            ))}
          </div>
        </div>

        <div className="col-md-4">
          <div className="sticky-top" style={{ top: '20px' }}>
            <h4 className="text-danger fw-bold">AI Assistant</h4>
            <ChatWindow />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;