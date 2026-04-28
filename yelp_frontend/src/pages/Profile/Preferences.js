import React, { useState, useEffect } from 'react';
import api from '../../services/api.js';

const Preferences = () => {
  const [prefs, setPrefs] = useState({
    cuisines:         '',
    price_range:      '$$',
    dietary_needs:    '',
    ambiance:         '',
    sort_preference:  'rating',
    location:         '',
    search_radius:    '',
  });
  const [success, setSuccess] = useState('');
  const [error, setError]     = useState('');

  useEffect(() => {
    api.get('/users/me/preferences')
      .then(res => setPrefs(res.data))
      .catch(() => {});
  }, []);

  const savePrefs = async () => {
    setSuccess('');
    setError('');
    try {
      await api.put('/users/me/preferences', prefs);
      setSuccess('AI Preferences saved!');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError('Error saving preferences. Make sure you are logged in.');
      setTimeout(() => setError(''), 4000);
    }
  };

  return (
    <div className="card p-3 mt-4">
      <h5>AI Assistant Preferences</h5>

      {success && <div className="alert alert-success py-1 mt-2 small">{success}</div>}
      {error   && <div className="alert alert-danger  py-1 mt-2 small">{error}</div>}

      <label className="form-label small fw-bold mt-2">Preferred Cuisines</label>
      <input
        className="form-control mb-2"
        placeholder="e.g. Italian, Indian, Chinese"
        value={prefs.cuisines || ''}
        onChange={e => setPrefs({ ...prefs, cuisines: e.target.value })}
      />

      <label className="form-label small fw-bold">Price Range</label>
      <select
        className="form-select mb-2"
        value={prefs.price_range || '$$'}
        onChange={e => setPrefs({ ...prefs, price_range: e.target.value })}
      >
        <option value="$">$ (Cheap)</option>
        <option value="$$">$$ (Moderate)</option>
        <option value="$$$">$$$ (Expensive)</option>
        <option value="$$$$">$$$$ (Fine Dining)</option>
      </select>

      <label className="form-label small fw-bold">Preferred Location</label>
      <input
        className="form-control mb-2"
        placeholder="e.g. San Jose, San Francisco"
        value={prefs.location || ''}
        onChange={e => setPrefs({ ...prefs, location: e.target.value })}
      />

      <label className="form-label small fw-bold">Search Radius (miles)</label>
      <input
        className="form-control mb-2"
        type="number"
        placeholder="e.g. 10"
        value={prefs.search_radius || ''}
        onChange={e => setPrefs({ ...prefs, search_radius: e.target.value })}
      />

      <label className="form-label small fw-bold">Dietary Restrictions</label>
      <input
        className="form-control mb-2"
        placeholder="e.g. Vegan, Halal, Gluten-free"
        value={prefs.dietary_needs || ''}
        onChange={e => setPrefs({ ...prefs, dietary_needs: e.target.value })}
      />

      <label className="form-label small fw-bold">Ambiance Preference</label>
      <select
        className="form-select mb-2"
        value={prefs.ambiance || ''}
        onChange={e => setPrefs({ ...prefs, ambiance: e.target.value })}
      >
        <option value="">Select Ambiance</option>
        <option value="casual">Casual</option>
        <option value="fine dining">Fine Dining</option>
        <option value="family-friendly">Family Friendly</option>
        <option value="romantic">Romantic</option>
        <option value="outdoor">Outdoor</option>
      </select>

      <label className="form-label small fw-bold">Sort Preference</label>
      <select
        className="form-select mb-3"
        value={prefs.sort_preference || 'rating'}
        onChange={e => setPrefs({ ...prefs, sort_preference: e.target.value })}
      >
        <option value="rating">Rating</option>
        <option value="popularity">Popularity</option>
        <option value="price">Price</option>
        <option value="distance">Distance</option>
      </select>

      <button onClick={savePrefs} className="btn btn-info text-white w-100">
        Update AI Preferences
      </button>
    </div>
  );
};

export default Preferences;
