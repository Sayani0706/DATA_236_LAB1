import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../services/api.js';

const Signup = () => {
  const [formData, setFormData] = useState({
    name: '', email: '', password: '', role: 'user', restaurant_location: ''
  });
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.post('/auth/signup', formData);
      alert("Signup successful! Please login.");
      navigate('/login');
    } catch (err) { alert("Signup failed."); }
  };

  return (
    <div className="container mt-5" style={{ maxWidth: '500px' }}>
      <form onSubmit={handleSubmit} className="card p-4 shadow">
        <h2 className="text-center mb-4">Create Account</h2>
        <input className="form-control mb-2" placeholder="Full Name" onChange={e => setFormData({...formData, name: e.target.value})} required />
        <input className="form-control mb-2" type="email" placeholder="Email" onChange={e => setFormData({...formData, email: e.target.value})} required />
        <input className="form-control mb-2" type="password" placeholder="Password" onChange={e => setFormData({...formData, password: e.target.value})} required />
        
        <div className="mb-3">
          <label className="form-label">Register as:</label>
          <select className="form-select" value={formData.role} onChange={e => setFormData({...formData, role: e.target.value})}>
            <option value="user">User (Reviewer)</option>
            <option value="owner">Restaurant Owner</option>
          </select>
        </div>

        {formData.role === 'owner' && (
          <input className="form-control mb-3" placeholder="Primary Restaurant Location" onChange={e => setFormData({...formData, restaurant_location: e.target.value})} required />
        )}
        
        <button className="btn btn-primary w-100" type="submit">Sign Up</button>
      </form>
    </div>
  );
};

export default Signup;