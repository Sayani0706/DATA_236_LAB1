import React, { useState, useEffect } from 'react';
import api from '../../services/api.js';
import Preferences from './Preferences.js';

const ProfileEditor = () => {
  const [profile, setProfile] = useState({
    name: '', email: '', phone: '', city: '', state: '',
    country: '', languages: '', gender: '', about_me: ''
  });

  const countries = ["USA", "Canada", "UK", "India", "Mexico", "France", "Germany",
    "Australia", "Japan", "China", "Brazil", "Italy", "Spain", "South Korea"];

  useEffect(() => {
    api.get('/users/me').then(res => setProfile(res.data));
  }, []);

  const handleUpdate = async (e) => {
    e.preventDefault();
    try {
      await api.put('/users/me', profile);
      alert("Profile updated!");
    } catch (err) {
      alert("Error updating profile. Remember state must be 2 letters (e.g. CA).");
    }
  };

  const handlePhotoUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);
    try {
      const res = await api.post('/users/me/photo', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setProfile(prev => ({ ...prev, profile_picture: res.data.profile_picture }));
      alert('Profile picture updated!');
    } catch (err) {
      alert('Error uploading photo.');
    }
  };

  return (
    <div className="container mt-5">
      <div className="row">
        <div className="col-md-6">
          <form onSubmit={handleUpdate} className="card p-4 shadow-sm">
            <h3>Personal Information</h3>

            {/* Show current profile picture */}
            {profile.profile_picture && (
              <div className="mb-3 text-center">
                <img
                  src={`http://localhost:8000${profile.profile_picture}`}
                  alt="Profile"
                  style={{
                    width: '100px',
                    height: '100px',
                    borderRadius: '50%',
                    objectFit: 'cover',
                    border: '3px solid #dc3545'
                  }}
                />
              </div>
            )}

            {/* Profile Picture Upload */}
            <div className="mb-3">
              <label className="form-label small fw-bold">Profile Picture</label>
              <input
                type="file"
                className="form-control"
                accept="image/*"
                onChange={handlePhotoUpload}
              />
            </div>

            <input
              className="form-control mb-2"
              value={profile.name || ''}
              placeholder="Name"
              onChange={e => setProfile({...profile, name: e.target.value})}
            />
            <input
              className="form-control mb-2"
              value={profile.email || ''}
              placeholder="Email"
              type="email"
              onChange={e => setProfile({...profile, email: e.target.value})}
            />
            <input
              className="form-control mb-2"
              value={profile.phone || ''}
              placeholder="Phone Number"
              onChange={e => setProfile({...profile, phone: e.target.value})}
            />
            <input
              className="form-control mb-2"
              value={profile.city || ''}
              placeholder="City"
              onChange={e => setProfile({...profile, city: e.target.value})}
            />
            <input
              className="form-control mb-2"
              value={profile.languages || ''}
              placeholder="Languages (e.g. English, Spanish)"
              onChange={e => setProfile({...profile, languages: e.target.value})}
            />

            <div className="row mb-2">
              <div className="col">
                <label className="small">Country</label>
                <select
                  className="form-select"
                  value={profile.country || ''}
                  onChange={e => setProfile({...profile, country: e.target.value})}
                >
                  <option value="">Select Country</option>
                  {countries.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>
              <div className="col">
                <label className="small">State (Abbreviated)</label>
                <input
                  className="form-control"
                  value={profile.state || ''}
                  placeholder="e.g. CA"
                  maxLength="2"
                  onChange={e => setProfile({...profile, state: e.target.value.toUpperCase()})}
                />
              </div>
            </div>

            <div className="mb-2">
              <label className="small">Gender</label>
              <select
                className="form-select"
                value={profile.gender || ''}
                onChange={e => setProfile({...profile, gender: e.target.value})}
              >
                <option value="">Select Gender</option>
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other</option>
                <option value="prefer_not_to_say">Prefer not to say</option>
              </select>
            </div>

            <textarea
              className="form-control mb-3"
              value={profile.about_me || ''}
              placeholder="About Me"
              rows={3}
              onChange={e => setProfile({...profile, about_me: e.target.value})}
            />
            <button type="submit" className="btn btn-primary w-100">
              Save Changes
            </button>
          </form>
        </div>
        <div className="col-md-6">
          <Preferences />
        </div>
      </div>
    </div>
  );
};

export default ProfileEditor;