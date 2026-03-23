import React, { useState } from 'react';
import api from '../../services/api.js';

const WriteReview = ({ restaurantId, onReviewAdded }) => {
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState('');
  const [photo, setPhoto] = useState(null);
  const [uploading, setUploading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setUploading(true);
    try {
      // Step 1 — submit the review
      const reviewRes = await api.post('/reviews/', {
        restaurant_id: restaurantId,
        rating: parseInt(rating),
        comment: comment
      });

      const reviewId = reviewRes.data.id;

      // Step 2 — upload photo if selected
      if (photo) {
        const formData = new FormData();
        formData.append('file', photo);
        await api.post(`/reviews/${reviewId}/photos`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
      }

      alert("Review posted!");
      setComment('');
      setRating(5);
      setPhoto(null);
      if (onReviewAdded) onReviewAdded();
    } catch (err) {
      alert("Error posting review. Check your login status.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="card p-3 mt-3 shadow-sm">
      <h5>Add a Review</h5>
      <form onSubmit={handleSubmit}>
        <div className="mb-2">
          <label className="form-label small fw-bold">Rating</label>
          <select
            className="form-select"
            value={rating}
            onChange={(e) => setRating(e.target.value)}
          >
            {[5, 4, 3, 2, 1].map(num => (
              <option key={num} value={num}>{num} Stars ⭐</option>
            ))}
          </select>
        </div>

        <div className="mb-2">
          <label className="form-label small fw-bold">Comment</label>
          <textarea
            className="form-control"
            placeholder="Write your comment..."
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            rows={3}
            required
          />
        </div>

        <div className="mb-3">
          <label className="form-label small fw-bold">
            Attach Photo <span className="text-muted fw-normal">(optional)</span>
          </label>
          <input
            type="file"
            className="form-control"
            accept="image/*"
            onChange={(e) => setPhoto(e.target.files[0])}
          />
          {photo && (
            <small className="text-success mt-1 d-block">
              ✓ {photo.name} selected
            </small>
          )}
        </div>

        <button
          type="submit"
          className="btn btn-danger w-100"
          disabled={uploading}
        >
          {uploading ? (
            <>
              <span className="spinner-border spinner-border-sm me-2" />
              Submitting...
            </>
          ) : "Submit Review"}
        </button>
      </form>
    </div>
  );
};

export default WriteReview;