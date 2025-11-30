/**
 * Custom React Hook: useAlerts
 * Fetches and manages weather alerts
 */

import { useState, useEffect, useCallback } from 'react';
import { alertsAPI } from '../services/api';
import type { Alert, AlertStats } from '../types/weather.types';

interface UseAlertsResult {
  alerts: Alert[];
  stats: AlertStats | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
  acknowledgeAlert: (alertId: string) => Promise<void>;
}

export const useAlerts = (
  city: string = 'Pune',
  autoRefresh: boolean = true,
  refreshInterval: number = 60000 // 1 minute
): UseAlertsResult => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [stats, setStats] = useState<AlertStats | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const [alertsData, statsData] = await Promise.all([
        alertsAPI.getActive(city, 50),
        alertsAPI.getStatistics(city),
      ]);

      setAlerts(alertsData);
      setStats(statsData);
    } catch (err: any) {
      console.error('Error fetching alerts:', err);
      setError(err.response?.data?.detail || 'Failed to fetch alerts');
    } finally {
      setLoading(false);
    }
  }, [city]);

  const refetch = useCallback(async () => {
    await fetchData();
  }, [fetchData]);

  const acknowledgeAlert = useCallback(async (alertId: string) => {
    try {
      await alertsAPI.acknowledge(alertId);
      // Update local state
      setAlerts((prev) =>
        prev.map((alert) =>
          alert.id === alertId ? { ...alert, is_acknowledged: true } : alert
        )
      );
    } catch (err: any) {
      console.error('Error acknowledging alert:', err);
      throw err;
    }
  }, []);

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
    alerts,
    stats,
    loading,
    error,
    refetch,
    acknowledgeAlert,
  };
};
