import axios from 'axios';

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api'
});

apiClient.interceptors.request.use((config) => {
  // Auth token injection is handled by AuthProvider
  // Add CSRF token for mutating requests
  if (config.method && ['post', 'put', 'patch', 'delete'].includes(config.method)) {
    config.headers['X-CSRF-Token'] = '1';
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Error handling is managed by AuthProvider
    return Promise.reject(error);
  }
);
