import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext.js';
import Navbar from './components/Layout/Navbar.js';
import Dashboard from './pages/Dashboard/Dashboard.js';
import Login from './pages/Auth/Login.js';
import Signup from './pages/Auth/Signup.js';
import ProfileEditor from './pages/Profile/ProfileEditor.js';
import UserActivity from './pages/User/UserActivity.js';
import AddRestaurant from './pages/Restaurant/AddResturant.js';
import RestaurantDetails from './pages/Restaurant/RestaurantDetails.js';
import Explore from './pages/Restaurant/Explore.js';
import WriteReview from './pages/Reviews/WriteReview.js';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Navbar />
        <div className="container-fluid">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/explore" element={<Explore />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/profile" element={<ProfileEditor />} />
            <Route path="/activity" element={<UserActivity />} />
            <Route path="/add-restaurant" element={<AddRestaurant />} />
            <Route path="/restaurants/:id" element={<RestaurantDetails />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
