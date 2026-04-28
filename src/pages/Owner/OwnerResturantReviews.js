import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../../services/api.js';

const OwnerRestaurantReviews = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [reviews, setReviews] = useState([]);
  const [restaurantName, setRestaurantName] = useState('');
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    const fetchReviews = async () => {
      try {
        const res = await api.get(`/owner/restaurants/${id}/reviews`);
        setReviews(res.data);

        const restRes = await api.get('/owner/restaurants');
        const restaurant = restRes.data.find(r => r.id === id);
        if (restaurant) setRestaurantName(restaurant.name);
      } catch (err) {
        console.error('Error fetching reviews:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchReviews();
  }, [id]);

  const filteredReviews = reviews.filter(r => {
    if (filter === 'all') return true;
    if (filter === 'positive') return r.rating >= 4;
    if (filter === 'neutral') return r.rating === 3;
    if (filter === 'negative') return r.rating <= 2;
    return true;
  });

  const avgRating = reviews.length > 0
    ? (reviews.reduce((sum, r) => sum + r.rating, 0) / reviews.length).toFixed(1)
    : 0;

  if (loading) return (
    <div className="text-center mt-5">
      <div className="spinner-border text-danger" />
    </div>
  );

  return (
    <div className="container mt-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h3>Reviews — {restaurantName}</h3>
          <p className="text-muted mb-0">
            {reviews.length} total reviews · avg {avgRating} ⭐
          </p>
        </div>
        <button
          className="btn btn-outline-secondary btn-sm"
          onClick={() => navigate('/owner/dashboard')}
        >
          ← Back to Dashboard
        </button>
      </div>

      {/* Filter Tabs */}
      <ul className="nav nav-tabs mb-4">
        {[
          { key: 'all', label: `All (${reviews.length})` },
          { key: 'positive', label: `Positive (${reviews.filter(r => r.rating >= 4).length})` },
          { key: 'neutral', label: `Neutral (${reviews.filter(r => r.rating === 3).length})` },
          { key: 'negative', label: `Negative (${reviews.filter(r => r.rating <= 2).length})` },
        ].map(tab => (
          <li key={tab.key} className="nav-item">
            <button
              className={`nav-link ${filter === tab.key ? 'active' : ''}`}
              onClick={() => setFilter(tab.key)}
            >
              {tab.label}
            </button>
          </li>
        ))}
      </ul>

      {filteredReviews.length > 0 ? (
        filteredReviews.map(rev => (
          <div key={rev.id} className="card p-3 mb-3 shadow-sm">
            <div className="d-flex justify-content-between align-items-start">
              <div>
                <strong>{rev.reviewer_name}</strong>
                <div className="text-warning mt-1">{'⭐'.repeat(rev.rating)}</div>
                <p className="mb-1 mt-2">{rev.comment}</p>
                <small className="text-muted">
                  {new Date(rev.review_date).toLocaleDateString()}
                  {rev.updated_at && rev.updated_at !== rev.review_date && (
                    <span className="ms-2">(edited)</span>
                  )}
                </small>
              </div>
              <span className={`badge ${
                rev.rating >= 4 ? 'bg-success' :
                rev.rating === 3 ? 'bg-warning text-dark' : 'bg-danger'
              }`}>
                {rev.rating}/5
              </span>
            </div>
          </div>
        ))
      ) : (
        <p className="text-muted">No reviews in this category.</p>
      )}
    </div>
  );
};

export default OwnerRestaurantReviews;