import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../../services/api.js';
import RestaurantCard from '../../components/Restaurant/RestaurantCard.js';

const UserActivity = () => {
  const [activeTab, setActiveTab]     = useState('history');
  const [history, setHistory]         = useState({ reviews: [], restaurants_added: [] });
  const [favorites, setFavorites]     = useState([]);
  const [loading, setLoading]         = useState(true);
  const [editingReview, setEditingReview] = useState(null);
  const [actionMsg, setActionMsg]     = useState({ type: '', text: '' });

  const showMsg = (type, text) => {
    setActionMsg({ type, text });
    setTimeout(() => setActionMsg({ type: '', text: '' }), 3000);
  };

  const fetchActivity = async () => {
    try {
      const [histRes, favRes] = await Promise.all([
        api.get('/users/me/history'),
        api.get('/favorites/'),
      ]);
      setHistory(histRes.data);
      setFavorites(favRes.data);
    } catch (err) {
      console.error('Error fetching activity:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchActivity(); }, []);

  const handleDeleteReview = async (reviewId) => {
    if (!window.confirm('Are you sure you want to delete this review?')) return;
    try {
      await api.delete(`/reviews/${reviewId}`);
      showMsg('success', 'Review deleted.');
      fetchActivity();
    } catch (err) {
      showMsg('danger', 'Error deleting review.');
    }
  };

  const handleEditSave = async (reviewId) => {
    try {
      await api.put(`/reviews/${reviewId}`, {
        rating:  parseInt(editingReview.rating),
        comment: editingReview.comment,
      });
      setEditingReview(null);
      showMsg('success', 'Review updated.');
      fetchActivity();
    } catch (err) {
      showMsg('danger', 'Error updating review.');
    }
  };

  const handleRemoveFavorite = async (restaurantId) => {
    try {
      await api.delete(`/favorites/${restaurantId}`);
      showMsg('success', 'Removed from favourites.');
      fetchActivity();
    } catch (err) {
      showMsg('danger', 'Error removing from favourites.');
    }
  };

  if (loading) return (
    <div className="text-center mt-5">
      <div className="spinner-border text-danger" />
    </div>
  );

  return (
    <div className="container mt-4">
      <h3>My Activity</h3>

      {actionMsg.text && (
        <div className={`alert alert-${actionMsg.type} py-2 mt-2`}>{actionMsg.text}</div>
      )}

      <ul className="nav nav-tabs mb-4 mt-3">
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

      {activeTab === 'history' ? (
        <div>
          <h5>My Reviews</h5>
          {history.reviews && history.reviews.length > 0 ? (
            history.reviews.map(item => (
              <div key={item.id} className="card p-3 mb-3 shadow-sm">
                {editingReview?.id !== item.id ? (
                  <div className="d-flex justify-content-between align-items-start">
                    <div>
                      <strong>
                        <Link to={`/restaurants/${item.restaurant_id}`} className="text-danger text-decoration-none">
                          {item.restaurant_name}
                        </Link>
                      </strong>
                      <div className="text-warning mt-1">{'⭐'.repeat(item.rating)}</div>
                      <p className="mb-1 mt-1">{item.comment}</p>
                      <small className="text-muted">
                        {new Date(item.review_date).toLocaleDateString()}
                      </small>
                    </div>
                    <div className="d-flex gap-2">
                      <button
                        className="btn btn-sm btn-outline-primary"
                        onClick={() => setEditingReview({ id: item.id, rating: item.rating, comment: item.comment })}
                      >
                        Edit
                      </button>
                      <button
                        className="btn btn-sm btn-outline-danger"
                        onClick={() => handleDeleteReview(item.id)}
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                ) : (
                  <>
                    <h6 className="text-muted mb-2">Editing review for <strong>{item.restaurant_name}</strong></h6>
                    <select
                      className="form-select mb-2"
                      value={editingReview.rating}
                      onChange={e => setEditingReview({ ...editingReview, rating: e.target.value })}
                    >
                      {[5, 4, 3, 2, 1].map(n => (
                        <option key={n} value={n}>{n} Stars ⭐</option>
                      ))}
                    </select>
                    <textarea
                      className="form-control mb-2"
                      rows={3}
                      value={editingReview.comment}
                      onChange={e => setEditingReview({ ...editingReview, comment: e.target.value })}
                    />
                    <div className="d-flex gap-2">
                      <button className="btn btn-sm btn-success" onClick={() => handleEditSave(item.id)}>
                        Save
                      </button>
                      <button className="btn btn-sm btn-secondary" onClick={() => setEditingReview(null)}>
                        Cancel
                      </button>
                    </div>
                  </>
                )}
              </div>
            ))
          ) : (
            <p className="text-muted">No reviews yet.</p>
          )}

          <h5 className="mt-4">Restaurants Added</h5>
          {history.restaurants_added && history.restaurants_added.length > 0 ? (
            <div className="row">
              {history.restaurants_added.map(item => (
                <div key={item.id} className="col-md-4">
                  <RestaurantCard restaurant={item} />
                </div>
              ))}
            </div>
          ) : (
            <p className="text-muted">No restaurants added yet.</p>
          )}
        </div>
      ) : (
        <div className="row">
          {favorites.length > 0 ? (
            favorites.map(item => (
              <div key={item.id} className="col-md-4 mb-3">
                <RestaurantCard
                  restaurant={item}
                  avgRating={item.avg_rating}
                  reviewCount={item.review_count}
                />
                <button
                  className="btn btn-sm btn-outline-danger w-100 mt-1"
                  onClick={() => handleRemoveFavorite(item.id)}
                >
                  ❤️ Remove from Favourites
                </button>
              </div>
            ))
          ) : (
            <p className="text-muted ms-3">No favourites saved yet.</p>
          )}
        </div>
      )}
    </div>
  );
};

export default UserActivity;
