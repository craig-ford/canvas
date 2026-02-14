import axios from 'axios';

export const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api'
});

apiClient.interceptors.request.use((config) => {
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    return Promise.reject(error);
  }
);
