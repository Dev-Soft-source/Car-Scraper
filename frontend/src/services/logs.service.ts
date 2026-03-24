import axios from "axios";
import authService from "./auth.service";

const API_URL = `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/logs`;

class LogsService {
  getAllLogs(filters: Record<string, unknown> = {}) {
    return axios.get(API_URL, { headers: authService.getAuthHeader(), params: filters });
  }
}

const logsService = new LogsService();
export default logsService;
