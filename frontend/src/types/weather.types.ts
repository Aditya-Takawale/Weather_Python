/**
 * TypeScript Type Definitions
 * Weather Monitoring System
 */

export interface WeatherTemperature {
  current: number;
  feels_like: number;
  min: number;
  max: number;
}

export interface CurrentWeather {
  temperature: number;
  feels_like: number;
  humidity: number;
  pressure: number;
  weather_main: string;
  weather_description: string;
  weather_icon: string;
  wind_speed: number;
  wind_deg: number;
  clouds: number;
  visibility: number;
  sunrise?: string;
  sunset?: string;
}

export interface TodayStats {
  temp_avg: number;
  temp_min: number;
  temp_max: number;
  humidity_avg: number;
  humidity_min: number;
  humidity_max: number;
  pressure_avg: number;
  wind_speed_avg: number;
  records_count: number;
}

export interface HourlyTrend {
  hour: string;
  temperature: number;
  humidity: number;
  weather_main: string;
  wind_speed: number;
}

export interface DailyTrend {
  date: string;
  temp_avg: number;
  temp_min: number;
  temp_max: number;
  humidity_avg: number;
  weather_main: string;
  records_count: number;
}

export interface DashboardSummary {
  city: string;
  summary_type: string;
  generated_at: string;
  current_weather: CurrentWeather;
  today_stats: TodayStats;
  hourly_trend: HourlyTrend[];
  daily_trend: DailyTrend[];
  weather_distribution: Record<string, number>;
}

export interface DashboardSummaryResponse {
  success: boolean;
  data: DashboardSummary;
  timestamp: string;
}

export interface AlertCondition {
  threshold_type: string;
  threshold_value: number;
  actual_value: number;
  operator: string;
  unit?: string;
}

export interface Alert {
  id: string;
  city: string;
  alert_type: string;
  severity: 'info' | 'warning' | 'critical';
  message: string;
  triggered_at: string;
  is_acknowledged: boolean;
  condition: AlertCondition;
  metadata: Record<string, any>;
}

export interface AlertStats {
  total_alerts: number;
  active_alerts: number;
  by_severity: Record<string, number>;
  by_type: Record<string, number>;
  recent_alerts: number;
}

export interface WeatherData {
  id: string;
  city: string;
  timestamp: string;
  temperature: number;
  feels_like: number;
  humidity: number;
  pressure: number;
  weather_main: string;
  weather_description: string;
  wind_speed: number;
  clouds: number;
}
