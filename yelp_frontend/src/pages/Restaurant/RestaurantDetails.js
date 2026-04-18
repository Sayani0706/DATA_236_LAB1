import React, { useState, useEffect, useContext } from 'react';
import { useParams } from 'react-router-dom';
import api from '../../services/api.js';
import WriteReview from '../Reviews/WriteReview.js';
import { AuthContext } from '../../context/AuthContext.js';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const RestaurantDetails = () => {
  const { id }                    = useParams();
  const { token }                 = useContext(AuthContext);
  const [data, setData]           = useState(null);
  const [loading, setLoading]     = useState(true);
  const [favMsg, setFavMsg]       = useState('');

  const fetchDetails = async () => {
    try {
      const res = await api.get(`/restaurants/${id}`);
      setData(res.data);
    } catch (err) {
      console.error('Error fetching restaurant:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchDetails(); }, [id]);

  const handleFavorite = async () => {
    try {
      await api.post(`/favorites/${id}`);
      setFavMsg('Added to favourites!');
      setTimeout(() => setFavMsg(''), 3000);
    } catch (err) {
      setFavMsg('Could not add to favourites. Already saved or not logged in.');
      setTimeout(() => setFavMsg(''), 3000);
    }
  };

  if (loading) return (
    <div className="text-center mt-5">
      <div className="spinner-border text-danger" />
    </div>
  );

  if (!data) return (
    <div className="container mt-5"><p>Restaurant not found.</p></div>
  );

  const { restaurant, avg_rating, review_count, reviews } = data;

  return (
    <div className="container mt-4">

      {/* Restaurant Photos */}
      {restaurant.photos && restaurant.photos.length > 0 && (
        <div className="mb-4 d-flex flex-wrap gap-3">
          {restaurant.photos.map((photo, idx) => (
            <img key={idx}
              src={`${API_URL}${photo.photo_url}`}
              alt={`${restaurant.name} photo`}
              style={{ width: '100%', height: '300px', objectFit: 'cover',
                borderRadius: '10px', border: '1px solid #dee2e6', marginBottom: '10px' }}
            />
          ))}
        </div>
      )}

      {/* Favourite feedback */}
      {favMsg && (
        <div className={`alert py-2 ${favMsg.includes('Could not') ? 'alert-warning' : 'alert-success'}`}>
          {favMsg}
        </div>
      )}

      {/* Restaurant Header */}
      <div className="card shadow-sm p-4 mb-4">
        <div className="d-flex justify-content-between align-items-start">
          <div>
            <h2>{restaurant.name}</h2>
            <p className="text-muted mb-1">{restaurant.cuisine_type} · {restaurant.pricing_tier}</p>
            <p className="mb-1">📍 {restaurant.address}, {restaurant.city}, {restaurant.state}</p>
            {restaurant.hours   && <p className="mb-1"><strong>Hours:</strong> {restaurant.hours}</p>}
            {restaurant.contact && <p className="mb-1"><strong>Contact:</strong> {restaurant.contact}</p>}
            {restaurant.amenities && <p className="mb-1"><strong>Amenities:</strong> {restaurant.amenities}</p>}
            <p className="mt-2">{restaurant.description}</p>
          </div>
          <div className="text-end">
            <div className="fs-4 fw-bold text-warning">{avg_rating} ⭐</div>
            <small className="text-muted">{review_count} reviews</small>
            <br />
            <button className="btn btn-outline-danger mt-2" onClick={handleFavorite}>
              ❤️ Save
            </button>
          </div>
        </div>
      </div>

      <div className="row">
        {/* Reviews List */}
        <div className="col-md-7">
          <h4>Reviews</h4>
          {reviews && reviews.length > 0 ? (
            reviews.map((r, i) => (
              <div key={i} className="card p-3 mb-2 shadow-sm">
                <div className="d-flex justify-content-between align-items-start">
                  <div className="d-flex align-items-center gap-2">
                    {r.reviewer_photo ? (
                      <img src={`${API_URL}${r.reviewer_photo}`} alt={r.reviewer_name}
                        style={{ width: '36px', height: '36px', borderRadius: '50%',
                          objectFit: 'cover', border: '2px solid #dee2e6' }} />
                    ) : (
                      <div style={{ width: '36px', height: '36px', borderRadius: '50%',
                        backgroundColor: '#dc3545', display: 'flex', alignItems: 'center',
                        justifyContent: 'center', color: 'white', fontWeight: 'bold',
                        fontSize: '14px', flexShrink: 0 }}>
                        {(r.reviewer_name || 'A')[0].toUpperCase()}
                      </div>
                    )}
                    <strong>{r.reviewer_name || 'Anonymous'}</strong>
                  </div>
                  <span className="text-warning">{'⭐'.repeat(r.rating)}</span>
                </div>
                <p className="mb-1 mt-2">{r.comment}</p>
                <small className="text-muted">{new Date(r.review_date).toLocaleDateString()}</small>

                {r.photos && r.photos.length > 0 && (
                  <div className="mt-2 d-flex flex-wrap gap-2">
                    {r.photos.map((photo, idx) => (
                      <img key={idx} src={`${API_URL}${photo.photo_url}`} alt="Review photo"
                        style={{ width: '90px', height: '90px', objectFit: 'cover',
                          borderRadius: '8px', border: '1px solid #dee2e6' }} />
                    ))}
                  </div>
                )}
              </div>
            ))
          ) : (
            <p className="text-muted">No reviews yet. Be the first!</p>
          )}
        </div>

        {/* Write Review Form */}
        <div className="col-md-5">
          {token ? (
            <WriteReview restaurantId={parseInt(id)} onReviewAdded={fetchDetails} />
          ) : (
            <div className="card p-4 mt-3 text-center shadow-sm">
              <p className="text-muted mb-2">Want to share your experience?</p>
              <a href="/login" className="btn btn-danger">Login to Write a Review</a>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default RestaurantDetails;
