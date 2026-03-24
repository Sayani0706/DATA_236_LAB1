import React, { useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AuthContext } from '../../context/AuthContext.js';

const Navbar = () => {
  const { token, role, logout } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-danger px-4">
      <Link className="navbar-brand fw-bold" to="/">🍽️ Yelp Clone</Link>
      <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navMenu">
        <span className="navbar-toggler-icon"></span>
      </button>
      <div className="collapse navbar-collapse" id="navMenu">
        <ul className="navbar-nav me-auto">
          <li className="nav-item"><Link className="nav-link" to="/">Home</Link></li>
          <li className="nav-item"><Link className="nav-link" to="/explore">Explore</Link></li>
          {token && (
            <>
              <li className="nav-item"><Link className="nav-link" to="/add-restaurant">Add Restaurant</Link></li>
              <li className="nav-item"><Link className="nav-link" to="/activity">My Activity</Link></li>
              <li className="nav-item"><Link className="nav-link" to="/profile">Profile</Link></li>
            </>
          )}
        </ul>
        <ul className="navbar-nav ms-auto">
          {token ? (
            <>
              <li className="nav-item">
                <span className="nav-link text-white-50">
                  {role === 'owner' ? '👑 Owner' : '👤 User'}
                </span>
              </li>
              <li className="nav-item">
                <button className="btn btn-outline-light btn-sm mt-1" onClick={handleLogout}>
                  Logout
                </button>
              </li>
            </>
          ) : (
            <>
              <li className="nav-item"><Link className="nav-link" to="/login">Login</Link></li>
              <li className="nav-item"><Link className="nav-link" to="/signup">Sign Up</Link></li>
            </>
          )}
        </ul>
      </div>
    </nav>
  );
};

export default Navbar;
