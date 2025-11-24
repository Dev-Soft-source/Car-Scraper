import axios from 'axios';
import authService from './auth.service';

const API_URL = `${process.env.REACT_APP_BACKEND_URL}/api/searches`;

class SearchService {
  getAllSearches() {
    return axios.get(API_URL, { headers: authService.getAuthHeader() });
  }

  getSearchById(id) {
    return axios.get(`${API_URL}/${id}`, { headers: authService.getAuthHeader() });
  }

  createSearch(searchData) {
    return axios.post(API_URL, searchData, { headers: authService.getAuthHeader() });
  }

  updateSearch(id, searchData) {
    return axios.put(`${API_URL}/${id}`, searchData, { headers: authService.getAuthHeader() });
  }

  deleteSearch(id) {
    return axios.delete(`${API_URL}/${id}`, { headers: authService.getAuthHeader() });
  }

  startSearch(id) {
    return axios.post(`${API_URL}/${id}/start`, {}, { headers: authService.getAuthHeader() });
  }

  stopSearch(id) {
    return axios.post(`${API_URL}/${id}/stop`, {}, { headers: authService.getAuthHeader() });
  }

  toggleFavorite(searchId) {
    return axios.post(`${API_URL}/${searchId}/favorite`, {}, { headers: authService.getAuthHeader() });
  }
}

export default new SearchService();
