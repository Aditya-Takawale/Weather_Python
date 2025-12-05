/**
 * Dashboard Page Component
 * Main dashboard layout with all weather components
 */

import React from 'react';
import {
  Container,
  Grid,
  Box,
  CircularProgress,
  Alert,
  Typography,
} from '@mui/material';

import { format } from 'date-fns';
import { useTheme } from '../context/ThemeContext';
import Header from '../components/layout/Header';
import TemperatureGauge from '../components/dashboard/TemperatureGauge';
import HourlyBarChart from '../components/dashboard/HourlyBarChart';
import HighlightCard from '../components/dashboard/HighlightCard';
import DailyTrendChart from '../components/dashboard/DailyTrendChart';
import WeatherAnimation from '../components/weather/WeatherAnimation';
import { useWeatherData } from '../hooks/useWeatherData';

const Dashboard: React.FC = () => {
  const { isDarkMode } = useTheme();
  
  const {
    data: weatherData,
    loading: weatherLoading,
    error: weatherError,
    refetch: refetchWeather,
    lastUpdated,
  } = useWeatherData('Pune', true, 300000); // Auto-refresh every 5 minutes

  const handleRefresh = () => {
    refetchWeather();
  };

  // Loading State
  if (weatherLoading && !weatherData) {
    return (
      <>
        <Header lastUpdated={lastUpdated} onRefresh={handleRefresh} loading={false} />
        <Container maxWidth="xl" sx={{ mt: 4 }}>
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              minHeight: '60vh',
            }}
          >
            <CircularProgress size={60} thickness={4} />
            <Typography variant="h6" sx={{ mt: 3, color: 'text.secondary' }}>
              Loading weather data...
            </Typography>
          </Box>
        </Container>
      </>
    );
  }

  // Show error message at top but still render dashboard with empty data
  const hasError = weatherError && !weatherData;
  const hasNoData = !weatherData || !weatherData.current_weather;

  // Additional safety checks for nested data - handle null/undefined weatherData
  const currentWeather = (weatherData && weatherData.current_weather) || {};
  const todayStats = (weatherData && weatherData.today_stats) || { temp_min: 0, temp_max: 0 };
  const hourlyTrend = (weatherData && weatherData.hourly_trend) || [];
  const dailyTrend = (weatherData && weatherData.daily_trend) || [];

  return (
    <>
      <Header
        lastUpdated={lastUpdated}
        onRefresh={handleRefresh}
        loading={weatherLoading}
      />
      
      {/* Show error/info alert at top if there's an issue */}
      {(hasError || hasNoData) && (
        <Container maxWidth="xl" sx={{ mt: 2 }}>
          <Alert severity={hasError ? "error" : "info"} sx={{ borderRadius: 2 }}>
            <Typography variant="h6" gutterBottom>
              {hasError ? "Failed to Load Weather Data" : "No Weather Data Available"}
            </Typography>
            <Typography variant="body2">
              {hasError ? weatherError : "Please wait for the system to collect weather data."}
            </Typography>
          </Alert>
        </Container>
      )}
      
      {/* Weather Animation - Full Screen */}
      {currentWeather.weather_main && <WeatherAnimation weather={currentWeather.weather_main} />}

      <Container maxWidth={false} sx={{ mt: 2, mb: 2, px: 3, maxWidth: '1600px', mx: 'auto', position: 'relative', zIndex: 2 }}>
        <Grid container spacing={2.5}>
          {/* Left Column: Temperature Gauge + High/Low + Hourly Chart */}
          <Grid item xs={12} lg={3}>
            <Box
              sx={{
                background: isDarkMode 
                  ? 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)' 
                  : 'linear-gradient(135deg, #5DADE2 0%, #48C9B0 100%)',
                borderRadius: 4,
                p: 3,
                height: '100%',
                minHeight: 500,
                boxShadow: isDarkMode 
                  ? '0 4px 20px rgba(0, 0, 0, 0.5)' 
                  : '0 4px 20px rgba(93, 173, 226, 0.3)',
                transition: 'background 0.3s ease, box-shadow 0.3s ease',
              }}
            >
              <TemperatureGauge
                temperature={currentWeather.temperature || 0}
                min={todayStats.temp_min || 0}
                max={todayStats.temp_max || 0}
                weather={currentWeather.weather_main || 'Unknown'}
                date={format(new Date(), 'EEEE, HH:mm')}
              />
            </Box>
          </Grid>
          {/* Right Column: Hourly Chart + Highlights */}
          <Grid item xs={12} lg={9}>
            {/* Hourly Bar Chart */}
            <Box
              sx={{
                background: isDarkMode 
                  ? 'linear-gradient(135deg, #16213e 0%, #1a1a2e 100%)' 
                  : 'linear-gradient(135deg, #F5A962 0%, #F7DC6F 100%)',
                borderRadius: 4,
                p: 3,
                mb: 2.5,
                minHeight: 220,
                boxShadow: isDarkMode 
                  ? '0 4px 20px rgba(0, 0, 0, 0.5)' 
                  : '0 4px 20px rgba(245, 169, 98, 0.3)',
                transition: 'background 0.3s ease, box-shadow 0.3s ease',
              }}
            >
              <HourlyBarChart data={hourlyTrend} dailyFallback={dailyTrend} />
            </Box>

            {/* Highlights Section */}
            <Typography variant="h6" fontWeight={700} gutterBottom sx={{ ml: 0.5, mb: 1.5, color: isDarkMode ? 'white' : '#1a1a2e' }}>
              Highlights
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={6} md={4} sx={{
                animation: 'fadeInUp 0.5s ease-out',
                animationDelay: '0.1s',
                animationFillMode: 'backwards',
                '@keyframes fadeInUp': {
                  from: { opacity: 0, transform: 'translateY(20px)' },
                  to: { opacity: 1, transform: 'translateY(0)' },
                },
              }}>
                <HighlightCard
                  title="Pressure"
                  value={currentWeather.pressure || 0}
                  unit="hPa"
                  subtitle={(currentWeather.pressure || 0) > 1013 ? 'High' : (currentWeather.pressure || 0) < 1013 ? 'Low' : 'Normal'}
                  color="#FF6B35"
                />
              </Grid>
              <Grid item xs={6} md={4}>
                <HighlightCard
                  title="Wind Status"
                  value={(currentWeather.wind_speed || 0).toFixed(1)}
                  unit="km/h"
                  subtitle={(currentWeather.wind_speed || 0) < 5 ? 'Light breeze' : (currentWeather.wind_speed || 0) < 20 ? 'Moderate wind' : 'Strong wind'}
                  color="#00D9FF"
                />
              </Grid>
              <Grid item xs={6} md={4}>
                <HighlightCard
                  title="Sunrise & Sunset"
                  value={currentWeather.sunrise ? format(new Date(currentWeather.sunrise), 'h:mm a') : 'N/A'}
                  subtitle={currentWeather.sunset ? format(new Date(currentWeather.sunset), 'h:mm a') : 'N/A'}
                  color="#FFD700"
                />
              </Grid>
              <Grid item xs={6} md={4}>
                <HighlightCard
                  title="Humidity"
                  value={currentWeather.humidity || 0}
                  unit="%"
                  subtitle={(currentWeather.humidity || 0) > 70 ? 'High' : (currentWeather.humidity || 0) < 30 ? 'Low' : 'Normal'}
                  color="#4FC3F7"
                />
              </Grid>
              <Grid item xs={6} md={4}>
                <HighlightCard
                  title="Visibility"
                  value={((currentWeather.visibility || 0) / 1000).toFixed(1)}
                  unit="km"
                  subtitle={((currentWeather.visibility || 0) / 1000) > 10 ? 'Excellent' : ((currentWeather.visibility || 0) / 1000) > 5 ? 'Good' : 'Poor'}
                  color="#00E676"
                />
              </Grid>
              <Grid item xs={6} md={4}>
                <HighlightCard
                  title="Cloud Cover"
                  value={currentWeather.clouds || 0}
                  unit="%"
                  subtitle={(currentWeather.clouds || 0) < 20 ? 'Clear sky' : (currentWeather.clouds || 0) < 60 ? 'Partly cloudy' : 'Overcast'}
                  color="#B388FF"
                />
              </Grid>
            </Grid>
          </Grid>
        </Grid>

        {/* Bottom Section: 7-Day Trend (Full Width) */}
        <Box sx={{ mt: 2.5 }}>
          <DailyTrendChart data={dailyTrend} />
        </Box>
      </Container>
    </>
  );
};

export default Dashboard;
