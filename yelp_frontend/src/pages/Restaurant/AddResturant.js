import React, { useState } from 'react';
import api from '../../services/api.js';

const AddRestaurant = () => {
  const [formData, setFormData] = useState({
    name: '',
    cuisine_type: '',
    address: '',
    city: '',
    state: '',
    zip: '',
    pricing_tier: '$$',
    description: '',
    contact: '',
    hours: '',
    amenities: ''
  });

  const [photo, setPhoto] = useState(null);
  const [loading, setLoading] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setSuccessMsg('');
    setErrorMsg('');

    try {
      const res = await api.post('/restaurants/', formData);
      const restaurantId = res.data.id;

      if (photo) {
        const formDataPhoto = new FormData();
        formDataPhoto.append('file', photo);
        await api.post(`/restaurants/${restaurantId}/photos`, formDataPhoto, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
      }

      setSuccessMsg('Restaurant added successfully!');
      setTimeout(() => setSuccessMsg(''), 4000);
      setFormData({
        name: '', cuisine_type: '', address: '', city: '', state: '',
        zip: '', pricing_tier: '$$', description: '', contact: '', hours: '', amenities: ''
      });
      setPhoto(null);
    } catch (err) {
      setErrorMsg('Error adding restaurant. Ensure state is 2 letters (e.g., CA).');
      setTimeout(() => setErrorMsg(''), 4000);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mt-4">
      <form onSubmit={handleSubmit} className="card p-4 shadow-sm">
        <h3>Add New Restaurant</h3>

        {successMsg && <div className="alert alert-success py-2 mt-2">{successMsg}</div>}
        {errorMsg   && <div className="alert alert-danger  py-2 mt-2">{errorMsg}</div>}

        <input
          className="form-control mb-2"
          placeholder="Restaurant Name"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          required
        />

        <input
          className="form-control mb-2"
          placeholder="Cuisine Type (e.g. Italian, Chinese)"
          value={formData.cuisine_type}
          onChange={(e) => setFormData({ ...formData, cuisine_type: e.target.value })}
          required
        />

        <input
          className="form-control mb-2"
          placeholder="Address"
          value={formData.address}
          onChange={(e) => setFormData({ ...formData, address: e.target.value })}
        />

        <div className="row mb-2">
          <div className="col-md-4">
            <input
              className="form-control"
              placeholder="City"
              value={formData.city}
              onChange={(e) => setFormData({ ...formData, city: e.target.value })}
            />
          </div>
          <div className="col-md-4">
            <input
              className="form-control"
              placeholder="State (e.g. CA)"
              maxLength="2"
              value={formData.state}
              onChange={(e) =>
                setFormData({ ...formData, state: e.target.value.toUpperCase() })
              }
            />
          </div>
          <div className="col-md-4">
            <input
              className="form-control"
              placeholder="ZIP Code"
              value={formData.zip}
              onChange={(e) => setFormData({ ...formData, zip: e.target.value })}
            />
          </div>
        </div>

        <select
          className="form-select mb-2"
          value={formData.pricing_tier}
          onChange={(e) => setFormData({ ...formData, pricing_tier: e.target.value })}
        >
          <option value="$">$ (Cheap)</option>
          <option value="$$">$$ (Moderate)</option>
          <option value="$$$">$$$ (Expensive)</option>
          <option value="$$$$">$$$$ (Fine Dining)</option>
        </select>

        <input
          className="form-control mb-2"
          placeholder="Contact Info (optional) e.g. 408-123-4567"
          value={formData.contact}
          onChange={(e) => setFormData({ ...formData, contact: e.target.value })}
        />

        <input
          className="form-control mb-2"
          placeholder="Hours (optional) e.g. Mon-Sun 10am-10pm"
          value={formData.hours}
          onChange={(e) => setFormData({ ...formData, hours: e.target.value })}
        />

        <input
          className="form-control mb-2"
          placeholder="Amenities (optional) e.g. wifi, vegan options, outdoor seating"
          value={formData.amenities}
          onChange={(e) => setFormData({ ...formData, amenities: e.target.value })}
        />

        <textarea
          className="form-control mb-2"
          placeholder="Description"
          rows={3}
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
        />

        <div className="mb-3">
          <label className="form-label small fw-bold">
            Restaurant Photo <span className="text-muted fw-normal">(optional)</span>
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
          className="btn btn-success w-100"
          disabled={loading}
        >
          {loading ? (
            <>
              <span className="spinner-border spinner-border-sm me-2" />
              Creating...
            </>
          ) : (
            'Create Listing'
          )}
        </button>
      </form>
    </div>
  );
};

export default AddRestaurant;
