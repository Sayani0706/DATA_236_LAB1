import React from 'react';
import { useNavigate } from 'react-router-dom';

const RestaurantCard = ({ restaurant, avgRating, reviewCount, isCompact }) => {
  const navigate = useNavigate();

  if (!restaurant) return null;

  const rating = avgRating || restaurant.avg_rating || 0;
  const count = reviewCount || restaurant.review_count || 0;

  const handleClick = () => {
    if (restaurant.id) navigate(`/restaurants/${restaurant.id}`);
  };

  return (
    <div
      className="card shadow-sm mb-3 h-100"
      onClick={handleClick}
      style={{ cursor: restaurant.id ? 'pointer' : 'default' }}
    >
      <div className="card-body">
        <h6 className="card-title fw-bold text-danger mb-1">{restaurant.name}</h6>
        <p className="card-text text-muted mb-1" style={{ fontSize: '13px' }}>
          {restaurant.cuisine_type || restaurant.cuisine} · {restaurant.pricing_tier}
        </p>
        {!isCompact && (
          <p className="card-text mb-1" style={{ fontSize: '13px' }}>
            📍 {restaurant.city}
          </p>
        )}
        {restaurant.description && !isCompact && (
          <p className="card-text text-muted" style={{ fontSize: '12px' }}>
            {restaurant.description?.substring(0, 80)}...
          </p>
        )}
        <div className="d-flex justify-content-between align-items-center mt-2">
          <span className="text-warning fw-bold">{"⭐".repeat(Math.round(rating))} {rating}</span>
          {count > 0 && <small className="text-muted">{count} reviews</small>}
        </div>
      </div>
    </div>
  );
};

export default RestaurantCard;
