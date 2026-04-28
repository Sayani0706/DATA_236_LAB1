import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  submitReview,
  resetSubmitStatus,
  selectReviewSubmitting,
  selectReviewSubmitSuccess,
  selectReviewError,
} from '../../store/slices/reviewSlice.js';

const WriteReview = ({ restaurantId, onReviewAdded }) => {
  const dispatch = useDispatch();
  const submitting = useSelector(selectReviewSubmitting);
  const submitSuccess = useSelector(selectReviewSubmitSuccess);
  const error = useSelector(selectReviewError);

  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState('');
  const [photo, setPhoto] = useState(null);

  useEffect(() => {
    if (submitSuccess) {
      setComment('');
      setRating(5);
      setPhoto(null);
      if (onReviewAdded) onReviewAdded();
      dispatch(resetSubmitStatus());
    }
  }, [submitSuccess, onReviewAdded, dispatch]);

  const handleSubmit = (e) => {
    e.preventDefault();
    dispatch(submitReview({ restaurantId, rating, comment, photo }));
  };

  return (
    <div className="card p-3 mt-3 shadow-sm">
      <h5>Add a Review</h5>
      {error && <div className="alert alert-danger py-2">{error}</div>}
      <form onSubmit={handleSubmit}>
        <div className="mb-2">
          <label className="form-label small fw-bold">Rating</label>
          <select className="form-select" value={rating} onChange={(e) => setRating(e.target.value)}>
            {[5, 4, 3, 2, 1].map((num) => (
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
          {photo && <small className="text-success mt-1 d-block">✓ {photo.name} selected</small>}
        </div>
        <button type="submit" className="btn btn-danger w-100" disabled={submitting}>
          {submitting ? (
            <><span className="spinner-border spinner-border-sm me-2" />Submitting...</>
          ) : 'Submit Review'}
        </button>
      </form>
    </div>
  );
};

export default WriteReview;
