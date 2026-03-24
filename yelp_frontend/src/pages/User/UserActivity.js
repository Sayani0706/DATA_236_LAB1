import React, { useState, useEffect } from 'react';
import api from '../../services/api.js';
import RestaurantCard from '../../components/Restaurant/RestaurantCard.js';

const UserActivity = () => {
  const [activeTab, setActiveTab] = useState('history');
  const [history, setHistory] = useState({ reviews: [], restaurants_added: [] });
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchActivity = async () => {
      try {
        const histRes = await api.get('/users/me/history');
        const favRes = await api.get('/favorites/');
        setHistory(histRes.data);
        setFavorites(favRes.data);
      } catch (err) {
        console.error("Error fetching activity:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchActivity();
  }, []);

  if (loading) return <div className="text-center mt-5"><div className="spinner-border text-danger" /></div>;

  return (
    <div className="container mt-4">
      <h3>My Activity</h3>
      <ul className="nav nav-tabs mb-4">
        <li className="nav-item">
          <button
            className={`nav-link ${activeTab === 'history' ? 'active' : ''}`}
            onClick={() => setActiveTab('history')}
          >
            History
          </button>
        </li>
        <li className="nav-item">
          <button
            className={`nav-link ${activeTab === 'favorites' ? 'active' : ''}`}
            onClick={() => setActiveTab('favorites')}
          >
            Favourites
          </button>
        </li>
      </ul>

      <div className="row">
        {activeTab === 'history' ? (
          <div>
            <h5>Reviews</h5>
            {history.reviews && history.reviews.length > 0 ? (
              history.reviews.map(item => (
                <div key={item.id} className="card p-3 mb-2 shadow-sm">
                  <strong>Rating: {item.rating} ⭐</strong>
                  <p className="mb-0">{item.comment}</p>
                  <small className="text-muted">{new Date(item.review_date).toLocaleDateString()}</small>
                </div>
              ))
            ) : <p className="text-muted">No reviews yet.</p>}

            <h5 className="mt-4">Restaurants Added</h5>
            {history.restaurants_added && history.restaurants_added.length > 0 ? (
              <div className="row">
                {history.restaurants_added.map(item => (
                  <div key={item.id} className="col-md-4">
                    <RestaurantCard restaurant={item} />
                  </div>
                ))}
              </div>
            ) : <p className="text-muted">No restaurants added yet.</p>}
          </div>
        ) : (
          <div className="row">
            {favorites.length > 0 ? (
              favorites.map(item => (
                <div key={item.id} className="col-md-4">
                  <RestaurantCard restaurant={item} />
                </div>
              ))
            ) : <p className="text-muted ms-3">No favourites saved yet.</p>}
          </div>
        )}
      </div>
    </div>
  );
};

export default UserActivity;
