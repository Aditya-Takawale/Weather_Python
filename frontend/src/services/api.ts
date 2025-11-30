/**
 * API Service
 * Centralized API communication layer
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import type {
  DashboardSummaryResponse,
  Alert,
  AlertStats,
  WeatherData,
} from '../types/weather.types';

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_PREFIX = '/api/v1';

// Create Axios instance with default config
const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL}${API_PREFIX}`,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add any auth headers here if needed
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error: AxiosError) => {
    // Handle errors globally
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// ==================== Dashboard API ====================

export const dashboardAPI = {
  /**
   * Get comprehensive dashboard summary
   */
  getSummary: async (city: string = 'Pune'): Promise<DashboardSummaryResponse> => {
    const response = await apiClient.get<DashboardSummaryResponse>('/dashboard/summary', {
      params: { city },
    });
    return response.data;
  },

  /**
   * Trigger manual dashboard refresh
   */
  refresh: async (city: string = 'Pune'): Promise<any> => {
    const response = await apiClient.post('/dashboard/refresh', null, {
      params: { city },
    });
    return response.data;
  },

  /**
   * Check dashboard health
   */
  health: async (city: string = 'Pune'): Promise<any> => {
    const response = await apiClient.get('/dashboard/health', {
      params: { city },
    });
    return response.data;
  },
};

// ==================== Weather API ====================

export const weatherAPI = {
  /**
   * Get current weather
   */
  getCurrent: async (city: string = 'Pune'): Promise<WeatherData> => {
    const response = await apiClient.get<WeatherData>('/weather/current', {
      params: { city },
    });
    return response.data;
  },

  /**
   * Get weather history
   */
  getHistory: async (city: string = 'Pune', hours: number = 24): Promise<WeatherData[]> => {
    const response = await apiClient.get<WeatherData[]>('/weather/history', {
      params: { city, hours },
    });
    return response.data;
  },

  /**
   * Trigger manual weather fetch
   */
  fetch: async (city: string = 'Pune'): Promise<any> => {
    const response = await apiClient.post('/weather/fetch', null, {
      params: { city },
    });
    return response.data;
  },

  /**
   * Get weather statistics
   */
  getStatistics: async (city: string = 'Pune', hours: number = 24): Promise<any> => {
    const response = await apiClient.get('/weather/statistics', {
      params: { city, hours },
    });
    return response.data;
  },
};

// ==================== Alerts API ====================

export const alertsAPI = {
  /**
   * Get active alerts
   */
  getActive: async (city?: string, limit: number = 50): Promise<Alert[]> => {
    const response = await apiClient.get<Alert[]>('/alerts/active', {
      params: { city, limit },
    });
    return response.data;
  },

  /**
   * Get recent alerts
   */
  getRecent: async (city: string = 'Pune', hours: number = 24): Promise<Alert[]> => {
    const response = await apiClient.get<Alert[]>('/alerts/recent', {
      params: { city, hours },
    });
    return response.data;
  },

  /**
   * Acknowledge an alert
   */
  acknowledge: async (alertId: string): Promise<any> => {
    const response = await apiClient.post('/alerts/acknowledge', {
      alert_id: alertId,
    });
    return response.data;
  },

  /**
   * Get alert statistics
   */
  getStatistics: async (city?: string): Promise<AlertStats> => {
    const response = await apiClient.get<AlertStats>('/alerts/statistics', {
      params: { city },
    });
    return response.data;
  },

  /**
   * Trigger manual alert check
   */
  check: async (city: string = 'Pune'): Promise<any> => {
    const response = await apiClient.post('/alerts/check', null, {
      params: { city },
    });
    return response.data;
  },
};

// ==================== System API ====================

export const systemAPI = {
  /**
   * Health check
   */
  health: async (): Promise<any> => {
    const response = await axios.get(`${API_BASE_URL}/health`);
    return response.data;
  },

  /**
   * System info
   */
  info: async (): Promise<any> => {
    const response = await axios.get(`${API_BASE_URL}/info`);
    return response.data;
  },
};

export default apiClient;
