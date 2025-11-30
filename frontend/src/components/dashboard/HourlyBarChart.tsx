/**
 * Hourly Bar Chart Component
 * Shows temperature by hour in a compact bar chart
 */

import React from 'react';
import { Box, Typography } from '@mui/material';
import { format } from 'date-fns';
import { useTheme } from '../../context/ThemeContext';
import type { HourlyTrend } from '../../types/weather.types';

interface HourlyBarChartProps {
  data: HourlyTrend[];
}

const HourlyBarChart: React.FC<HourlyBarChartProps> = ({ data }) => {
  const { isDarkMode } = useTheme();
  const recentData = data.slice(-8);
  const maxTemp = Math.max(...recentData.map(d => d.temperature));
  const minTemp = Math.min(...recentData.map(d => d.temperature));

  return (
    <Box>
      <Typography variant="h6" fontWeight={700} gutterBottom sx={{ color: isDarkMode ? 'white' : '#1a1a2e' }}>
        Today
      </Typography>
      <Box
        sx={{
          display: 'flex',
          alignItems: 'flex-end',
          justifyContent: 'space-between',
          height: 120,
          gap: 1,
          px: 2,
        }}
      >
        {recentData.map((item, index) => {
          const heightPercent = ((item.temperature - minTemp) / (maxTemp - minTemp)) * 100;
          return (
            <Box
              key={index}
              sx={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                flex: 1,
                position: 'relative',
              }}
            >
              <Typography
                variant="caption"
                sx={{
                  color: isDarkMode ? 'white' : '#1a1a2e',
                  fontSize: '1rem',
                  fontWeight: 700,
                  mb: 0.5,
                }}
              >
                {Math.round(item.temperature)}°
              </Typography>
              <Box
                sx={{
                  width: '100%',
                  height: `${Math.max(heightPercent, 20)}%`,
                  background: isDarkMode ? 'rgba(255,255,255,0.8)' : 'rgba(30,30,46,0.8)',
                  borderRadius: '4px 4px 0 0',
                  transition: 'all 0.3s ease',
                  animation: 'slideUp 0.5s ease-out',
                  animationDelay: `${index * 0.1}s`,
                  animationFillMode: 'backwards',
                  '@keyframes slideUp': {
                    from: { height: 0, opacity: 0 },
                    to: { height: `${Math.max(heightPercent, 20)}%`, opacity: 1 },
                  },
                  '&:hover': {
                    background: isDarkMode ? 'rgba(255,255,255,1)' : 'rgba(30,30,46,1)',
                    transform: 'scaleY(1.05)',
                  },
                }}
              />
              <Typography
                variant="caption"
                sx={{
                  color: isDarkMode ? 'rgba(255,255,255,0.9)' : 'rgba(26,26,46,0.9)',
                  fontSize: '0.875rem',
                  fontWeight: 600,
                  mt: 0.5,
                }}
              >
                {format(new Date(item.hour), 'ha')}
              </Typography>
            </Box>
          );
        })}
      </Box>
    </Box>
  );
};

export default HourlyBarChart;
