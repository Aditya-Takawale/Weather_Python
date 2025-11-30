/**
 * Temperature Gauge Component
 * Circular gauge showing current temperature
 */

import React from 'react';
import { Box, Typography } from '@mui/material';
import { Cloud, WbSunny } from '@mui/icons-material';
import { useTheme } from '../../context/ThemeContext';

interface TemperatureGaugeProps {
  temperature: number;
  min: number;
  max: number;
  weather: string;
  date: string;
}

const TemperatureGauge: React.FC<TemperatureGaugeProps> = ({
  temperature,
  min,
  max,
  weather,
  date,
}) => {
  const { isDarkMode } = useTheme();
  const percentage = ((temperature - min) / (max - min)) * 100;
  const rotation = (percentage / 100) * 180 - 90;

  return (
    <Box
      sx={{
        position: 'relative',
        width: '100%',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        p: 3,
        animation: 'fadeIn 0.8s ease-out',
        '@keyframes fadeIn': {
          from: { opacity: 0, transform: 'scale(0.9)' },
          to: { opacity: 1, transform: 'scale(1)' },
        },
      }}
    >
      {/* Gauge Circle */}
      <Box
        sx={{
          position: 'relative',
          width: 180,
          height: 180,
          borderRadius: '50%',
          background: 'linear-gradient(135deg, rgba(255,255,255,0.2) 0%, rgba(255,255,255,0.05) 100%)',
          border: '8px solid rgba(255,255,255,0.3)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          mb: 2,
        }}
      >
        {/* Temperature markers */}
        <Box
          sx={{
            position: 'absolute',
            top: '10%',
            left: '15%',
            color: isDarkMode ? 'rgba(255,255,255,0.7)' : 'rgba(26,26,46,0.7)',
            fontSize: '0.75rem',
            fontWeight: 600,
          }}
        >
          {max}°
        </Box>
        <Box
          sx={{
            position: 'absolute',
            top: '50%',
            right: '8%',
            color: isDarkMode ? 'rgba(255,255,255,0.7)' : 'rgba(26,26,46,0.7)',
            fontSize: '0.75rem',
            fontWeight: 600,
          }}
        >
          30°
        </Box>
        <Box
          sx={{
            position: 'absolute',
            bottom: '15%',
            left: '15%',
            color: isDarkMode ? 'rgba(255,255,255,0.7)' : 'rgba(26,26,46,0.7)',
            fontSize: '0.75rem',
            fontWeight: 600,
          }}
        >
          {min}°
        </Box>

        {/* Pointer */}
        <Box
          sx={{
            position: 'absolute',
            width: 4,
            height: 70,
            background: isDarkMode ? 'rgba(255,255,255,0.9)' : 'rgba(26,26,46,0.9)',
            transformOrigin: 'bottom center',
            transform: `rotate(${rotation}deg)`,
            borderRadius: 2,
            bottom: '50%',
          }}
        >
          <Box
            sx={{
              width: 12,
              height: 12,
              background: isDarkMode ? 'white' : '#1a1a2e',
              borderRadius: '50%',
              position: 'absolute',
              bottom: -6,
              left: -4,
            }}
          />
        </Box>

        {/* Center circle */}
        <Box
          sx={{
            width: 12,
            height: 12,
            background: isDarkMode ? 'rgba(255,255,255,0.5)' : 'rgba(26,26,46,0.5)',
            borderRadius: '50%',
            position: 'absolute',
          }}
        />

        {/* Weather Icon */}
        <Box sx={{ position: 'absolute', top: '35%', opacity: 0.3 }}>
          {weather.toLowerCase().includes('cloud') ? (
            <Cloud sx={{ fontSize: 40, color: isDarkMode ? 'white' : '#1a1a2e' }} />
          ) : (
            <WbSunny sx={{ fontSize: 40, color: isDarkMode ? 'white' : '#1a1a2e' }} />
          )}
        </Box>

        {/* Temperature Display */}
        <Typography
          variant="h1"
          sx={{
            color: isDarkMode ? 'white' : '#1a1a2e',
            fontWeight: 700,
            fontSize: '3.5rem',
            mt: 6,
          }}
        >
          {Math.round(temperature)}°C
        </Typography>
      </Box>

      {/* Date */}
      <Typography variant="body2" sx={{ color: isDarkMode ? 'rgba(255,255,255,0.9)' : 'rgba(26,26,46,0.9)', fontWeight: 600 }}>
        {date}
      </Typography>
    </Box>
  );
};

export default TemperatureGauge;
