import axios from "axios";
import authService from "./auth.service";

const API_URL = `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/listings`;

class ListingService {
  getListingsBySearch(searchId: string, filters: Record<string, unknown> = {}) {
    return axios.get(`${API_URL}/search/${searchId}`, {
      headers: authService.getAuthHeader(),
      params: filters,
    });
  }

  toggleFavorite(listingId: string) {
    return axios.post(`${API_URL}/${listingId}/favorite`, {}, { headers: authService.getAuthHeader() });
  }
}

const listingService = new ListingService();
export default listingService;
