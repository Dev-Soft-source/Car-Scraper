import axios from "axios";

const API_URL = `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/auth`;

export type AuthUser = {
  access_token: string;
  token_type?: string;
  [key: string]: unknown;
};

class AuthService {
  login(email: string, password: string) {
    return axios.post<AuthUser>(`${API_URL}/login`, { email, password }).then((response) => {
      if (response.data.access_token) {
        localStorage.setItem("user", JSON.stringify(response.data));
      }
      return response.data;
    });
  }

  logout() {
    localStorage.removeItem("user");
  }

  register(email: string, password: string) {
    return axios.post(`${API_URL}/register`, { email, password });
  }

  getCurrentUser(): AuthUser | null {
    if (typeof window === "undefined") return null;
    const user = localStorage.getItem("user");
    return user ? (JSON.parse(user) as AuthUser) : null;
  }

  getAuthHeader() {
    if (typeof window === "undefined") return {};
    const user = this.getCurrentUser();
    if (user && user.access_token) {
      return { Authorization: `Bearer ${user.access_token}` };
    }
    return {};
  }
}

const authService = new AuthService();
export default authService;
