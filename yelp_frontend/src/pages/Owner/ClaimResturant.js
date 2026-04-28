import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../services/api.js';

const ClaimRestaurant = () => {
  const navigate = useNavigate();
  const [restaurants, setRestaurants] = useState([]);
  const [loading, setLoading]         = useState(true);
  const [searchTerm, setSearchTerm]   = useState('');
  const [claiming, setClaiming]       = useState(null);
  const [msg, setMsg]                 = useState({ type: '', text: '' });

  const showMsg = (type, text) => {
    setMsg({ type, text });
    setTimeout(() => setMsg({ type: '', text: '' }), 4000);
  };

  useEffect(() => {
    api.get('/restaurants/?limit=100')
      .then(res => setRestaurants(res.data))
      .catch(err => console.error('Error fetching restaurants:', err))
      .finally(() => setLoading(false));
  }, []);

  const handleClaim = async (restaurantId) => {
    if (!window.confirm('Are you sure you want to claim this restaurant?')) return;
    setClaiming(restaurantId);
    try {
      await api.post(`/restaurants/${restaurantId}/claim`);
      showMsg('success', 'Restaurant claimed successfully! Redirecting to dashboard...');
      setTimeout(() => navigate('/owner/dashboard'), 1500);
    } catch (err) {
      const detail = err.response?.data?.detail || 'Error claiming restaurant.';
      showMsg('danger', detail);
    } finally {
      setClaiming(null);
    }
  };

  const filtered = restaurants.filter(item => {
    const r = item.restaurant || item;
    const term = searchTerm.trim().toLowerCase();
    if (!term) return true;
    return (
      (r.name          || '').toLowerCase().includes(term) ||
      (r.city          || '').toLowerCase().includes(term) ||
      (r.cuisine_type  || '').toLowerCase().includes(term) ||
      (r.description   || '').toLowerCase().includes(term)
    );
  });

  if (loading) return (
    <div className="text-center mt-5">
      <div className="spinner-border text-danger" />
    </div>
  );

  return (
    <div className="container mt-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h3>🏷️ Claim a Restaurant</h3>
          <p className="text-muted mb-0">Find your restaurant and claim ownership to manage it.</p>
        </div>
        <button
          className="btn btn-outline-secondary btn-sm"
          onClick={() => navigate('/owner/dashboard')}
        >
          ← Back to Dashboard
        </button>
      </div>

      {msg.text && (
        <div className={`alert alert-${msg.type} py-2 mb-3`}>{msg.text}</div>
      )}

      <input
        className="form-control mb-2"
        placeholder="Search by name, city, cuisine, or description..."
        value={searchTerm}
        onChange={e => setSearchTerm(e.target.value)}
      />

      <p className="text-muted small mb-3">
        Showing {filtered.length} restaurant{filtered.length !== 1 ? 's' : ''}
      </p>

      {filtered.length > 0 ? (
        filtered.map(item => {
          const r = item.restaurant || item;
          return (
            <div key={r.id} className="card p-3 mb-3 shadow-sm">
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <h5 className="mb-1">{r.name}</h5>
                  <p className="text-muted mb-1 small">
                    {r.cuisine_type} · {r.pricing_tier} · 📍 {r.city}, {r.state}
                  </p>
                  {r.description && (
                    <p className="text-muted small mb-0">
                      {r.description.substring(0, 100)}...
                    </p>
                  )}
                </div>
                <div className="text-end ms-3">
                  {r.is_claimed ? (
                    <span className="badge bg-secondary">Already Claimed</span>
                  ) : (
                    <button
                      className="btn btn-danger btn-sm"
                      onClick={() => handleClaim(r.id)}
                      disabled={claiming === r.id}
                    >
                      {claiming === r.id ? (
                        <><span className="spinner-border spinner-border-sm me-1" />Claiming...</>
                      ) : 'Claim'}
                    </button>
                  )}
                </div>
              </div>
            </div>
          );
        })
      ) : (
        <p className="text-muted">No restaurants found matching your search.</p>
      )}
    </div>
  );
};

export default ClaimRestaurant;
