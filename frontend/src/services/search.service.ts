import axios from "axios";
import authService from "./auth.service";

const API_URL = `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/searches`;

class SearchService {
  getAllSearches() {
    return axios.get(API_URL, { headers: authService.getAuthHeader() });
  }

  getState() {
    return axios.get(`${API_URL}/state`, { headers: authService.getAuthHeader() });
  }

  createSearch(searchData: Record<string, unknown>) {
    return axios.post(API_URL, searchData, { headers: authService.getAuthHeader() });
  }

  updateSearch(id: string, searchData: Record<string, unknown>) {
    return axios.put(`${API_URL}/${id}`, searchData, { headers: authService.getAuthHeader() });
  }

  deleteSearch(id: string) {
    return axios.delete(`${API_URL}/${id}`, { headers: authService.getAuthHeader() });
  }

  startSearch(id: string) {
    return axios.post(`${API_URL}/${id}/start`, {}, { headers: authService.getAuthHeader() });
  }

  stopSearch(id: string) {
    return axios.post(`${API_URL}/${id}/stop`, {}, { headers: authService.getAuthHeader() });
  }
}

const searchService = new SearchService();
export default searchService;
