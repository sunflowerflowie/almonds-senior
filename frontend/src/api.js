import axios from "axios";
import { ACCESS_TOKEN } from "./constants";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
});

// Interceptor to add the token to request headers
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem(ACCESS_TOKEN); // Retrieve AccessToken
    if (token) {
      config.headers.Authorization = `Bearer ${token}`; // Add token to headers
    }
    return config;
  },
  (error) => {
    console.log("ERROR"); // Log the error
    return Promise.reject(error);
  }
);

export default api;
