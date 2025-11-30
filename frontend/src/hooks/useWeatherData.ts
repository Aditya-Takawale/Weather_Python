/**
 * Custom React Hook: useWeatherData
 * Fetches and manages dashboard weather data
 */

import { useState, useEffect, useCallback } from 'react';
import { dashboardAPI } from '../services/api';
import type { DashboardSummary } from '../types/weather.types';

interface UseWeatherDataResult {
  data: DashboardSummary | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
  lastUpdated: Date | null;
}

export const useWeatherData = (
  city: string = 'Pune',
  autoRefresh: boolean = true,
  refreshInterval: number = 300000 // 5 minutes
): UseWeatherDataResult => {
  const [data, setData] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await dashboardAPI.getSummary(city);
      
      if (response.success && response.data) {
        setData(response.data);
        setLastUpdated(new Date());
      } else {
        setError('Failed to fetch dashboard data');
      }
    } catch (err: any) {
      console.error('Error fetching weather data:', err);
      setError(err.response?.data?.detail || 'Failed to fetch weather data');
    } finally {
      setLoading(false);
    }
  }, [city]);

  const refetch = useCallback(async () => {
    await fetchData();
  }, [fetchData]);

  // Initial fetch
  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Auto-refresh
  useEffect(() => {
    if (!autoRefresh) return;

    const intervalId = setInterval(() => {
      fetchData();
    }, refreshInterval);

    return () => clearInterval(intervalId);
  }, [autoRefresh, refreshInterval, fetchData]);

  return {
    data,
    loading,
    error,
    refetch,
    lastUpdated,
  };
};
