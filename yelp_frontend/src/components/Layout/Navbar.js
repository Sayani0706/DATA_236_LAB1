import React, { useContext, useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AuthContext } from '../../context/AuthContext.js';
import api from '../../services/api.js';

const Navbar = () => {
  const { token, role, logout } = useContext(AuthContext);
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const res = await api.get('/users/me');
        setUser(res.data);
      } catch (err) {
        console.error("Failed to load user", err);
      }
    };

    if (token) fetchUser();
  }, [token]);

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

          {token && role === 'user' && (
            <>
              <li className="nav-item"><Link className="nav-link" to="/add-restaurant">Add Restaurant</Link></li>
              <li className="nav-item"><Link className="nav-link" to="/activity">My Activity</Link></li>
              <li className="nav-item"><Link className="nav-link" to="/profile">Profile</Link></li>
            </>
          )}

          {token && role === 'owner' && (
            <>
              <li className="nav-item"><Link className="nav-link" to="/owner/dashboard">Owner Dashboard</Link></li>
              <li className="nav-item"><Link className="nav-link" to="/owner/add-restaurant">Add Restaurant</Link></li>
              <li className="nav-item"><Link className="nav-link" to="/owner/claim-restaurant">Claim Restaurant</Link></li>
              <li className="nav-item"><Link className="nav-link" to="/profile">Profile</Link></li>
            </>
          )}
        </ul>

        <ul className="navbar-nav ms-auto">
          {token ? (
            <>
              <li className="nav-item d-flex align-items-center">
                {user?.profile_picture ? (
                  <img
                    src={`http://localhost:8000${user.profile_picture}`}
                    alt="profile"
                    style={{
                      width: '32px',
                      height: '32px',
                      borderRadius: '50%',
                      objectFit: 'cover',
                      marginRight: '8px'
                    }}
                  />
                ) : (
                  <span className="me-2">
                    {role === 'owner' ? '👑' : '👤'}
                  </span>
                )}
                <span className="nav-link text-white-50">
                  {user?.name || 'User'}
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