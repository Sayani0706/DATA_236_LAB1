import React, { useState, useEffect, useContext } from 'react';
import api from '../../services/api.js';
import RestaurantCard from '../../components/Restaurant/RestaurantCard.js';
import ChatWindow from '../../components/Chat/ChatWindow.js';
import { AuthContext } from '../../context/AuthContext.js';

const Explore = () => {
  const [restaurants, setRestaurants] = useState([]);
  const [loading, setLoading]         = useState(false);
  const [filters, setFilters]         = useState({
    name: '', cuisine: '', keyword: '', city: '', zip: '', sort_by: ''
  });
  const { token } = useContext(AuthContext);

  const fetchRestaurants = async (currentFilters) => {
    setLoading(true);
    try {
      const params = {};
      if (currentFilters.name)    params.name    = currentFilters.name;
      if (currentFilters.cuisine) params.cuisine = currentFilters.cuisine;
      if (currentFilters.keyword) params.keyword = currentFilters.keyword;
      if (currentFilters.city)    params.city    = currentFilters.city;
      if (currentFilters.zip)     params.zip     = currentFilters.zip;
      if (currentFilters.sort_by) params.sort_by = currentFilters.sort_by;
      const res = await api.get('/restaurants/', { params });
      setRestaurants(res.data);
    } catch (err) {
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchRestaurants(filters); }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    fetchRestaurants(filters);
  };

  const handleSortChange = (e) => {
    const newFilters = { ...filters, sort_by: e.target.value };
    setFilters(newFilters);
    fetchRestaurants(newFilters);
  };

  return (
    <div className="container-fluid mt-4 px-4">
      <div className="row">

        {/* Left — Search + Results */}
        <div className={token ? 'col-md-8' : 'col-md-12'}>
          <h3>Explore Restaurants</h3>

          <form onSubmit={handleSearch} className="card p-3 mb-4 shadow-sm">
            <div className="row g-2">
              <div className="col-md-3">
                <input className="form-control" placeholder="Restaurant name"
                  value={filters.name}
                  onChange={e => setFilters({ ...filters, name: e.target.value })} />
              </div>
              <div className="col-md-2">
                <input className="form-control" placeholder="Cuisine"
                  value={filters.cuisine}
                  onChange={e => setFilters({ ...filters, cuisine: e.target.value })} />
              </div>
              <div className="col-md-2">
                <input className="form-control" placeholder="Keyword (e.g. wifi)"
                  value={filters.keyword}
                  onChange={e => setFilters({ ...filters, keyword: e.target.value })} />
              </div>
              <div className="col-md-2">
                <input className="form-control" placeholder="City"
                  value={filters.city}
                  onChange={e => setFilters({ ...filters, city: e.target.value })} />
              </div>
              <div className="col-md-1">
                <input className="form-control" placeholder="ZIP"
                  value={filters.zip}
                  onChange={e => setFilters({ ...filters, zip: e.target.value })} />
              </div>
              <div className="col-md-1">
                <select className="form-select" value={filters.sort_by} onChange={handleSortChange}>
                  <option value="">Sort by</option>
                  <option value="rating">Rating</option>
                  <option value="popularity">Popularity</option>
                  <option value="price">Price</option>
                  <option value="distance">Distance</option>
                </select>
              </div>
              <div className="col-md-1">
                <button type="submit" className="btn btn-danger w-100">Search</button>
              </div>
            </div>
          </form>

          {loading ? (
            <div className="text-center">
              <div className="spinner-border text-danger" />
            </div>
          ) : (
            <div className="row">
              {restaurants.length > 0 ? (
                restaurants.map(item => (
                  <div key={item.restaurant?.id || item.id} className="col-md-4 mb-3">
                    <RestaurantCard
                      restaurant={item.restaurant || item}
                      avgRating={item.avg_rating}
                      reviewCount={item.review_count}
                    />
                  </div>
                ))
              ) : (
                <p className="text-muted">No restaurants found. Try different filters.</p>
              )}
            </div>
          )}
        </div>

        {/* Right — AI Assistant panel (logged-in users only) */}
        {token && (
          <div className="col-md-4">
            <div className="sticky-top" style={{ top: '20px' }}>
              <h4 className="text-danger fw-bold">🤖 Ask Assistant</h4>
              <p className="text-muted small mb-2">Not sure what to eat? Ask me anything!</p>
              <ChatWindow />
            </div>
          </div>
        )}

      </div>
    </div>
  );
};

export default Explore;
