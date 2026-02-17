import axios from 'axios';

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
});

apiClient.interceptors.request.use((config) => {
  // Auth token injection is handled by AuthProvider
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Error handling is managed by AuthProvider
    return Promise.reject(error);
  }
);
