import axios from 'axios';
import authService from './auth.service';

const API_URL = `${process.env.REACT_APP_BACKEND_URL}/api/logs`;

class LogsService {
  getAllLogs(filters = {}) {
    return axios.get(API_URL, { 
      headers: authService.getAuthHeader(),
      params: filters
    });
  }

  getLogById(id) {
    return axios.get(`${API_URL}/${id}`, { headers: authService.getAuthHeader() });
  }
}

export default new LogsService();
