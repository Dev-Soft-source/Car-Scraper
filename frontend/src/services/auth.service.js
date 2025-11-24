import axios from 'axios';

const API_URL = `${process.env.REACT_APP_BACKEND_URL}/api/auth`;

class AuthService {
  login(email, password) {
    return axios
      .post(`${API_URL}/login`, { email, password })
      .then(response => {
        if (response.data.access_token) {
          localStorage.setItem('user', JSON.stringify(response.data));
        }
        return response.data;
      });
  }

  logout() {
    localStorage.removeItem('user');
  }

  register(email, password) {
    return axios.post(`${API_URL}/register`, {
      email,
      password
    });
  }

  getCurrentUser() {
    return JSON.parse(localStorage.getItem('user'));
  }

  getAuthHeader() {
    const user = JSON.parse(localStorage.getItem('user'));
    if (user && user.access_token) {
      return { Authorization: 'Bearer ' + user.access_token };
    }
    return {};
  }
}

export default new AuthService();
