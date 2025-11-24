import axios from 'axios';
import authService from './auth.service';

const API_URL = `${process.env.REACT_APP_BACKEND_URL}/api/listings`;

class ListingService {
  getAllListings(filters = {}) {
    return axios.get(API_URL, { 
      headers: authService.getAuthHeader(),
      params: filters
    });
  }

  getListingById(id) {
    return axios.get(`${API_URL}/${id}`, { headers: authService.getAuthHeader() });
  }

  getListingsBySearch(searchId, filters = {}) {
    return axios.get(`${API_URL}/search/${searchId}`, { 
      headers: authService.getAuthHeader(),
      params: filters
    });
  }

  toggleFavorite(listingId) {
    return axios.post(`${API_URL}/${listingId}/favorite`, {}, { headers: authService.getAuthHeader() });
  }

  getStatistics() {
    return axios.get(`${API_URL}/statistics`, { headers: authService.getAuthHeader() });
  }
}

export default new ListingService();
