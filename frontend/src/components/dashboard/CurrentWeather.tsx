/**
 * Current Weather Card Component
 * Displays current weather conditions with beautiful visuals
 */

import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Grid,
  Divider,
  Chip,
} from '@mui/material';
import {
  Water,
  Air,
  Visibility,
  CompressOutlined,
  Cloud,
  WbSunny,
  NightsStay,
} from '@mui/icons-material';
import type { CurrentWeather } from '../../types/weather.types';
import { format } from 'date-fns';

interface CurrentWeatherCardProps {
  weather: CurrentWeather;
  city: string;
}

const CurrentWeatherCard: React.FC<CurrentWeatherCardProps> = ({ weather, city }) => {
  const getWeatherIcon = (main: string) => {
    switch (main.toLowerCase()) {
      case 'clear':
        return <WbSunny sx={{ fontSize: 80, color: '#FFA726' }} />;
      case 'clouds':
        return <Cloud sx={{ fontSize: 80, color: '#78909C' }} />;
      case 'rain':
      case 'drizzle':
        return <Water sx={{ fontSize: 80, color: '#42A5F5' }} />;
      default:
        return <WbSunny sx={{ fontSize: 80, color: '#FFA726' }} />;
    }
  };

  const getBackgroundGradient = (main: string) => {
    switch (main.toLowerCase()) {
      case 'clear':
        return 'linear-gradient(135deg, #F093FB 0%, #F5576C 100%)';
      case 'clouds':
        return 'linear-gradient(135deg, #4FACFE 0%, #00F2FE 100%)';
      case 'rain':
        return 'linear-gradient(135deg, #43E97B 0%, #38F9D7 100%)';
      case 'snow':
        return 'linear-gradient(135deg, #A8EDEA 0%, #FED6E3 100%)';
      case 'mist':
      case 'fog':
        return 'linear-gradient(135deg, #D299C2 0%, #FEF9D7 100%)';
      case 'thunderstorm':
        return 'linear-gradient(135deg, #667EEA 0%, #764BA2 100%)';
      default:
        return 'linear-gradient(135deg, #FA8BFF 0%, #2BD2FF 90%, #2BFF88 100%)';
    }
  };

  return (
    <Card
      sx={{
        height: '100%',
        background: getBackgroundGradient(weather.weather_main),
        color: 'white',
      }}
    >
      <CardContent sx={{ p: 2 }}>
        <Box sx={{ textAlign: 'center', mb: 2 }}>
          <Typography variant="h5" fontWeight={700} gutterBottom>
            {city}
          </Typography>
          <Chip
            label={weather.weather_description}
            size="small"
            sx={{
              backgroundColor: 'rgba(255,255,255,0.2)',
              color: 'white',
              fontWeight: 600,
              mb: 1,
            }}
          />
        </Box>

        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            mb: 2,
          }}
        >
          {getWeatherIcon(weather.weather_main)}
          <Box sx={{ ml: 2, textAlign: 'left' }}>
            <Typography variant="h2" fontWeight={700} sx={{ lineHeight: 1 }}>
              {Math.round(weather.temperature)}°
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.9 }}>
              Feels like {Math.round(weather.feels_like)}°
            </Typography>
          </Box>
        </Box>
        <Divider sx={{ my: 1.5, backgroundColor: 'rgba(255,255,255,0.2)' }} />

        <Grid container spacing={2}>
          <Grid item xs={6}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Water sx={{ opacity: 0.8 }} />
              <Box>
                <Typography variant="caption" sx={{ opacity: 0.8, fontSize: '0.7rem' }}>
                  Humidity
                </Typography>
                <Typography variant="body1" fontWeight={600}>
                  {weather.humidity}%
                </Typography>
              </Box>
            </Box>
          </Grid>

          <Grid item xs={6}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Air sx={{ opacity: 0.8 }} />
              <Box>
                <Typography variant="caption" sx={{ opacity: 0.8 }}>
                  Wind Speed
                </Typography>
                <Typography variant="h6" fontWeight={600}>
                  {weather.wind_speed} m/s
                </Typography>
              </Box>
            </Box>
          </Grid>

          <Grid item xs={6}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <CompressOutlined sx={{ opacity: 0.8 }} />
              <Box>
                <Typography variant="caption" sx={{ opacity: 0.8 }}>
                  Pressure
                </Typography>
                <Typography variant="h6" fontWeight={600}>
                  {weather.pressure} hPa
                </Typography>
              </Box>
            </Box>
          </Grid>

          <Grid item xs={6}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Visibility sx={{ opacity: 0.8 }} />
              <Box>
                <Typography variant="caption" sx={{ opacity: 0.8 }}>
                  Visibility
                </Typography>
                <Typography variant="h6" fontWeight={600}>
                  {(weather.visibility / 1000).toFixed(1)} km
                </Typography>
              </Box>
            </Box>
          </Grid>
        </Grid>

        {weather.sunrise && weather.sunset && (
          <>
            <Divider sx={{ my: 2, backgroundColor: 'rgba(255,255,255,0.2)' }} />
            <Box sx={{ display: 'flex', justifyContent: 'space-around' }}>
              <Box sx={{ textAlign: 'center' }}>
                <WbSunny sx={{ opacity: 0.8, mb: 0.5 }} />
                <Typography variant="caption" sx={{ opacity: 0.8, display: 'block' }}>
                  Sunrise
                </Typography>
                <Typography variant="body2" fontWeight={600}>
                  {format(new Date(weather.sunrise), 'HH:mm')}
                </Typography>
              </Box>
              <Box sx={{ textAlign: 'center' }}>
                <NightsStay sx={{ opacity: 0.8, mb: 0.5 }} />
                <Typography variant="caption" sx={{ opacity: 0.8, display: 'block' }}>
                  Sunset
                </Typography>
                <Typography variant="body2" fontWeight={600}>
                  {format(new Date(weather.sunset), 'HH:mm')}
                </Typography>
              </Box>
            </Box>
          </>
        )}
      </CardContent>
    </Card>
  );
};

export default CurrentWeatherCard;
