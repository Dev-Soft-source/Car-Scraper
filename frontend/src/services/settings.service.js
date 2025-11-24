import axios from 'axios';
import authService from './auth.service';

const API_URL = `${process.env.REACT_APP_BACKEND_URL}/api/settings`;

class SettingsService {
  getSettings() {
    return axios.get(API_URL, { headers: authService.getAuthHeader() });
  }

  updateSettings(settings) {
    return axios.put(API_URL, settings, { headers: authService.getAuthHeader() });
  }

  changePassword(oldPassword, newPassword) {
    return axios.post(`${API_URL}/change-password`, 
      { old_password: oldPassword, new_password: newPassword },
      { headers: authService.getAuthHeader() }
    );
  }

  getSiteUrls() {
    return axios.get(`${API_URL}/site-urls`, { headers: authService.getAuthHeader() });
  }

  addSiteUrl(url) {
    return axios.post(`${API_URL}/site-urls`, { url }, { headers: authService.getAuthHeader() });
  }

  deleteSiteUrl(id) {
    return axios.delete(`${API_URL}/site-urls/${id}`, { headers: authService.getAuthHeader() });
  }
}

export default new SettingsService();
