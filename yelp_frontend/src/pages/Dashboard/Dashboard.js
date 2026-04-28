import React, { useState, useEffect } from 'react';
import ChatWindow from '../../components/Chat/ChatWindow.js';
import RestaurantCard from '../../components/Restaurant/RestaurantCard.js';
import api from '../../services/api.js';

const Dashboard = () => {
  const [restaurants, setRestaurants] = useState([]);

  useEffect(() => {
    api.get('/restaurants/').then(res => setRestaurants(res.data));
  }, []);

  return (
    <div className="container-fluid p-4">
      <div className="row">
        <div className="col-md-8">
          <h2 className="mb-4">Recommended for You</h2>
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