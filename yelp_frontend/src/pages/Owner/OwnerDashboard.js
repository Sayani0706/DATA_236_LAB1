import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../../services/api.js';

const OwnerDashboard = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeRestaurant, setActiveRestaurant] = useState(null);

  useEffect(() => {
    api.get('/owner/dashboard')
      .then(res => {
        setData(res.data);
        if (res.data.length > 0) setActiveRestaurant(res.data[0]);
      })
      .catch(err => console.error("Error fetching dashboard:", err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <div className="text-center mt-5">
      <div className="spinner-border text-danger" />
    </div>
  );

  if (data.length === 0) return (
    <div className="container mt-5 text-center">
      <h4>No restaurants found.</h4>
      <p className="text-muted">Start by adding a restaurant to your account.</p>
      <Link to="/owner/add-restaurant" className="btn btn-danger mt-2">
        Add Your Restaurant
      </Link>
    </div>
  );

  const r = activeRestaurant;

  return (
    <div className="container mt-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h3>👑 Owner Dashboard</h3>
        <Link to="/owner/add-restaurant" className="btn btn-danger btn-sm">
          + Add Restaurant
        </Link>
      </div>

      {/* Restaurant Selector — if owner has multiple */}
      {data.length > 1 && (
        <div className="mb-4">
          <label className="form-label fw-bold">Select Restaurant</label>
          <select
            className="form-select"
            value={activeRestaurant?.restaurant?.id}
            onChange={e => {
              const selected = data.find(d => d.restaurant.id === parseInt(e.target.value));
              setActiveRestaurant(selected);
            }}
          >
            {data.map(d => (
              <option key={d.restaurant.id} value={d.restaurant.id}>
                {d.restaurant.name}
              </option>
            ))}
          </select>
        </div>
      )}

      {r && (
        <>
          {/* Restaurant Info Card */}
          <div className="card shadow-sm p-4 mb-4">
            <div className="d-flex justify-content-between align-items-start">
              <div>
                <h4>{r.restaurant.name}</h4>
                <p className="text-muted mb-1">
                  {r.restaurant.cuisine_type} · {r.restaurant.pricing_tier}
                </p>
                <p className="mb-1">
                  📍 {r.restaurant.city}, {r.restaurant.state}
                </p>
                <span className={`badge ${r.restaurant.is_claimed ? 'bg-success' : 'bg-secondary'}`}>
                  {r.restaurant.is_claimed ? '✓ Claimed' : 'Unclaimed'}
                </span>
              </div>
              <Link
                to={`/restaurants/${r.restaurant.id}`}
                className="btn btn-outline-danger btn-sm"
              >
                View Public Page
              </Link>
            </div>
          </div>

          {/* Analytics Cards */}
          <div className="row mb-4">
            <div className="col-md-3">
              <div className="card text-center p-3 shadow-sm border-0 bg-danger text-white">
                <h2>{r.avg_rating} ⭐</h2>
                <small>Average Rating</small>
              </div>
            </div>
            <div className="col-md-3">
              <div className="card text-center p-3 shadow-sm border-0 bg-warning text-dark">
                <h2>{r.review_count}</h2>
                <small>Total Reviews</small>
              </div>
            </div>
            <div className="col-md-3">
              <div className="card text-center p-3 shadow-sm border-0 bg-info text-white">
                <h2>{r.total_views}</h2>
                <small>Total Views</small>
              </div>
            </div>
            <div className="col-md-3">
              <div className={`card text-center p-3 shadow-sm border-0 text-white ${
                r.sentiment.label === 'Positive' ? 'bg-success' :
                r.sentiment.label === 'Negative' ? 'bg-danger' : 'bg-secondary'
              }`}>
                <h2>{r.sentiment.label}</h2>
                <small>Overall Sentiment</small>
              </div>
            </div>
          </div>

          <div className="row mb-4">
            {/* Ratings Distribution */}
            <div className="col-md-6">
              <div className="card shadow-sm p-4">
                <h5 className="mb-3">Ratings Distribution</h5>
                {[5, 4, 3, 2, 1].map(star => {
                  const count = r.ratings_distribution[String(star)] || 0;
                  const percent = r.review_count > 0
                    ? Math.round((count / r.review_count) * 100)
                    : 0;
                  return (
                    <div key={star} className="d-flex align-items-center mb-2">
                      <span className="me-2" style={{ width: '50px' }}>
                        {star} ⭐
                      </span>
                      <div className="progress flex-grow-1 me-2" style={{ height: '12px' }}>
                        <div
                          className="progress-bar bg-warning"
                          style={{ width: `${percent}%` }}
                        />
                      </div>
                      <span className="text-muted" style={{ width: '40px' }}>
                        {count}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Sentiment Breakdown */}
            <div className="col-md-6">
              <div className="card shadow-sm p-4">
                <h5 className="mb-3">Sentiment Breakdown</h5>
                <div className="mb-3">
                  {[
                    { label: 'Positive', count: r.sentiment.positive, color: 'bg-success' },
                    { label: 'Neutral', count: r.sentiment.neutral, color: 'bg-secondary' },
                    { label: 'Negative', count: r.sentiment.negative, color: 'bg-danger' },
                  ].map(s => {
                    const total = r.sentiment.positive + r.sentiment.neutral + r.sentiment.negative;
                    const percent = total > 0 ? Math.round((s.count / total) * 100) : 0;
                    return (
                      <div key={s.label} className="d-flex align-items-center mb-2">
                        <span className="me-2" style={{ width: '70px' }}>{s.label}</span>
                        <div className="progress flex-grow-1 me-2" style={{ height: '12px' }}>
                          <div className={`progress-bar ${s.color}`} style={{ width: `${percent}%` }} />
                        </div>
                        <span className="text-muted" style={{ width: '30px' }}>{s.count}</span>
                      </div>
                    );
                  })}
                </div>
                <p className="text-muted small mb-0">
                  Sentiment Score: <strong>{r.sentiment.score}</strong>
                </p>
              </div>
            </div>
          </div>

          {/* Recent Reviews */}
          <div className="card shadow-sm p-4 mb-4">
            <div className="d-flex justify-content-between align-items-center mb-3">
              <h5 className="mb-0">Recent Reviews</h5>
              <Link
                to={`/owner/restaurants/${r.restaurant.id}/reviews`}
                className="btn btn-sm btn-outline-danger"
              >
                View All Reviews
              </Link>
            </div>
            {r.recent_reviews.length > 0 ? (
              r.recent_reviews.map(rev => (
                <div key={rev.id} className="border-bottom pb-2 mb-2">
                  <div className="d-flex justify-content-between">
                    <strong>{rev.reviewer_name}</strong>
                    <span className="text-warning">{'⭐'.repeat(rev.rating)}</span>
                  </div>
                  <p className="mb-1 text-muted">{rev.comment}</p>
                  <small className="text-muted">
                    {new Date(rev.review_date).toLocaleDateString()}
                  </small>
                </div>
              ))
            ) : (
              <p className="text-muted">No reviews yet.</p>
            )}
          </div>

          {/* Manage Restaurant */}
          <div className="card shadow-sm p-4 mb-5">
            <h5 className="mb-3">Manage Restaurant</h5>
            <div className="d-flex gap-2 flex-wrap">
              <Link
                to={`/owner/edit-restaurant/${r.restaurant.id}`}
                className="btn btn-outline-primary"
              >
                ✏️ Edit Details
              </Link>
              <Link
                to={`/restaurants/${r.restaurant.id}`}
                className="btn btn-outline-secondary"
              >
                👁️ View Public Page
              </Link>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default OwnerDashboard;