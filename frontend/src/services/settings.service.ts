import axios from "axios";
import authService from "./auth.service";

const API_URL = `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/settings`;

class SettingsService {
  changePassword(oldPassword: string, newPassword: string) {
    return axios.post(
      `${API_URL}/change-password`,
      { old_password: oldPassword, new_password: newPassword },
      { headers: authService.getAuthHeader() },
    );
  }

  getSiteUrls() {
    return axios.get(`${API_URL}/site-urls`, { headers: authService.getAuthHeader() });
  }

  addSiteUrl(url: string) {
    return axios.post(`${API_URL}/site-urls`, { url }, { headers: authService.getAuthHeader() });
  }

  updateSiteUrl(id: string, url: string) {
    return axios.put(`${API_URL}/site-urls/${id}`, { url }, { headers: authService.getAuthHeader() });
  }

  deleteSiteUrl(id: string) {
    return axios.delete(`${API_URL}/site-urls/${id}`, { headers: authService.getAuthHeader() });
  }
}

const settingsService = new SettingsService();
export default settingsService;
