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
import OwnerDashboard from './pages/Owner/OwnerDashboard.js';
import OwnerAddRestaurant from './pages/Owner/OwnerAddResturant.js';
import OwnerEditRestaurant from './pages/Owner/OwnerEditResturant.js';
import OwnerRestaurantReviews from './pages/Owner/OwnerResturantReviews.js';
import ClaimRestaurant from './pages/Owner/ClaimResturant.js';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Navbar />
        <div className="container-fluid">
          <Routes>
            {/* Public */}
            <Route path="/" element={<Dashboard />} />
            <Route path="/explore" element={<Explore />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/restaurants/:id" element={<RestaurantDetails />} />

            {/* User */}
            <Route path="/profile" element={<ProfileEditor />} />
            <Route path="/preferences" element={<ProfileEditor />} />
            <Route path="/activity" element={<UserActivity />} />
            <Route path="/add-restaurant" element={<AddRestaurant />} />

            {/* Owner */}
            <Route path="/owner/dashboard" element={<OwnerDashboard />} />
            <Route path="/owner/add-restaurant" element={<OwnerAddRestaurant />} />
            <Route path="/owner/edit-restaurant/:id" element={<OwnerEditRestaurant />} />
            <Route path="/owner/restaurants/:id/reviews" element={<OwnerRestaurantReviews />} />
            <Route path="/owner/claim-restaurant" element={<ClaimRestaurant />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
