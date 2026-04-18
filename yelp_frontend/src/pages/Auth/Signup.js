import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { signup } from '../../services/authService.js';

const Signup = () => {
  const [formData, setFormData] = useState({
    name: '', email: '', password: '', confirmPassword: '',
    role: 'user', restaurant_location: ''
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    try {
      await signup({
        name:                formData.name,
        email:               formData.email,
        password:            formData.password,
        role:                formData.role,
        restaurant_location: formData.restaurant_location,
      });
      setSuccess('Account created successfully! Redirecting to login...');
      setTimeout(() => navigate('/login'), 1500);
    } catch (err) {
      setError(err.response?.data?.detail || 'Signup failed. Please try again.');
    }
  };

  return (
    <div className="container mt-5" style={{ maxWidth: '500px' }}>
      <form onSubmit={handleSubmit} className="card p-4 shadow">
        <h2 className="text-center mb-4">Create Account</h2>

        {error   && <div className="alert alert-danger py-2">{error}</div>}
        {success && <div className="alert alert-success py-2">{success}</div>}

        <input
          className="form-control mb-2"
          placeholder="Full Name"
          value={formData.name}
          onChange={e => setFormData({ ...formData, name: e.target.value })}
          required
        />
        <input
          className="form-control mb-2"
          type="email"
          placeholder="Email"
          value={formData.email}
          onChange={e => setFormData({ ...formData, email: e.target.value })}
          required
        />
        <input
          className="form-control mb-2"
          type="password"
          placeholder="Password"
          value={formData.password}
          onChange={e => setFormData({ ...formData, password: e.target.value })}
          required
        />
        <input
          className="form-control mb-3"
          type="password"
          placeholder="Confirm Password"
          value={formData.confirmPassword}
          onChange={e => setFormData({ ...formData, confirmPassword: e.target.value })}
          required
        />

        <div className="mb-3">
          <label className="form-label">Register as:</label>
          <select
            className="form-select"
            value={formData.role}
            onChange={e => setFormData({ ...formData, role: e.target.value })}
          >
            <option value="user">User (Reviewer)</option>
            <option value="owner">Restaurant Owner</option>
          </select>
        </div>

        {formData.role === 'owner' && (
          <input
            className="form-control mb-3"
            placeholder="Primary Restaurant Location"
            value={formData.restaurant_location}
            onChange={e => setFormData({ ...formData, restaurant_location: e.target.value })}
            required
          />
        )}

        <button className="btn btn-danger w-100" type="submit">
          Sign Up
        </button>

        <div className="text-center mt-3">
          <small>
            Already have an account? <Link to="/login" className="text-danger">Login</Link>
          </small>
        </div>
      </form>
    </div>
  );
};

export default Signup;
