import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import api from '../../services/api.js';
import WriteReview from '../Reviews/WriteReview.js';

const RestaurantDetails = () => {
  const { id } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchDetails = async () => {
    try {
      const res = await api.get(`/restaurants/${id}`);
      setData(res.data);
    } catch (err) {
      console.error("Error fetching restaurant:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchDetails(); }, [id]);

  const handleFavorite = async () => {
    try {
      await api.post(`/favorites/${id}`);
      alert("Added to favourites!");
    } catch (err) {
      alert("Could not add to favourites. Already added or not logged in.");
    }
  };

  if (loading) return (
    <div className="text-center mt-5">
      <div className="spinner-border text-danger" />
    </div>
  );

  if (!data) return (
    <div className="container mt-5">
      <p>Restaurant not found.</p>
    </div>
  );

  const { restaurant, avg_rating, review_count, reviews } = data;

  return (
    <div className="container mt-4">

      {/* Restaurant Photos */}
      {restaurant.photos && restaurant.photos.length > 0 && (
        <div className="mb-4 d-flex flex-wrap gap-3">
          {restaurant.photos.map((photo, idx) => (
            <img
              key={idx}
              src={`http://localhost:8000${photo.photo_url}`}
              alt={`${restaurant.name} photo`}
              style={{
                width: '220px',
                height: '160px',
                objectFit: 'contain',
                borderRadius: '8px',
                border: '1px solid #dee2e6',
                backgroundColor: '#fff',
                padding: '6px'
              }}
            />
          ))}
        </div>
      )}

      {/* Restaurant Header */}
      <div className="card shadow-sm p-4 mb-4">
        <div className="d-flex justify-content-between align-items-start">
          <div>
            <h2>{restaurant.name}</h2>
            <p className="text-muted mb-1">
              {restaurant.cuisine_type} · {restaurant.pricing_tier}
            </p>
            <p className="mb-1">
              📍 {restaurant.address}, {restaurant.city}, {restaurant.state}
            </p>
            {restaurant.hours && (
              <p className="mb-1">
                <strong>Hours:</strong> {restaurant.hours}
              </p>
            )}
            {restaurant.contact && (
              <p className="mb-1">
                <strong>Contact:</strong> {restaurant.contact}
              </p>
            )}
            {restaurant.amenities && (
              <p className="mb-1">
                <strong>Amenities:</strong> {restaurant.amenities}
              </p>
            )}
            <p className="mt-2">{restaurant.description}</p>
          </div>
          <div className="text-end">
            <div className="fs-4 fw-bold text-warning">
              {avg_rating} ⭐
            </div>
            <small className="text-muted">{review_count} reviews</small>
            <br />
            <button
              className="btn btn-outline-danger mt-2"
              onClick={handleFavorite}
            >
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
                <div className="d-flex justify-content-between">
                  <strong>{r.reviewer_name || "Anonymous"}</strong>
                  <span className="text-warning">
                    {"⭐".repeat(r.rating)}
                  </span>
                </div>
                <p className="mb-1 mt-1">{r.comment}</p>
                <small className="text-muted">
                  {new Date(r.review_date).toLocaleDateString()}
                </small>

                {/* Review Photos */}
                {r.photos && r.photos.length > 0 && (
                  <div className="mt-2 d-flex flex-wrap gap-2">
                    {r.photos.map((photo, idx) => (
                      <img
                        key={idx}
                        src={`http://localhost:8000${photo.photo_url}`}
                        alt="Review photo"
                        style={{
                          width: '90px',
                          height: '90px',
                          objectFit: 'contain',
                          borderRadius: '8px',
                          border: '1px solid #dee2e6',
                          backgroundColor: '#fff',
                          padding: '4px'
                        }}
                      />
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
          <WriteReview
            restaurantId={parseInt(id)}
            onReviewAdded={fetchDetails}
          />
        </div>
      </div>
    </div>
  );
};

export default RestaurantDetails;