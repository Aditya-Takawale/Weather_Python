/**
 * Hourly Bar Chart Component
 * Shows temperature by hour in a compact bar chart
 */

import React from 'react';
import { Box, Typography } from '@mui/material';
import { format, parseISO } from 'date-fns';
import { useTheme } from '../../context/ThemeContext';
import type { HourlyTrend, DailyTrend } from '../../types/weather.types';

interface HourlyBarChartProps {
  data: HourlyTrend[];
  dailyFallback?: DailyTrend[];
}

const HourlyBarChart: React.FC<HourlyBarChartProps> = ({ data, dailyFallback = [] }) => {
  const { isDarkMode } = useTheme();
  
  // If no hourly data, use daily data as fallback
  const useDaily = !data || data.length === 0;
  const displayData = useDaily ? dailyFallback.slice(-7) : data.slice(-8);
  
  // If no data available at all, show message
  if (!displayData || displayData.length === 0) {
    return (
      <Box>
        <Typography variant="h6" fontWeight={700} gutterBottom sx={{ color: isDarkMode ? 'white' : '#1a1a2e' }}>
          {useDaily ? 'Recent Days' : 'Today'}
        </Typography>
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            height: 120,
            px: 2,
          }}
        >
          <Typography
            variant="body2"
            sx={{
              color: isDarkMode ? 'rgba(255,255,255,0.6)' : 'rgba(26,26,46,0.6)',
              fontStyle: 'italic',
            }}
          >
            Collecting weather data... Check back soon!
          </Typography>
        </Box>
      </Box>
    );
  }
  
  const temps = useDaily 
    ? displayData.map((d: any) => d.temp_avg)
    : displayData.map((d: any) => d.temperature);
  const maxTemp = Math.max(...temps);
  const minTemp = Math.min(...temps);

  return (
    <Box>
      <Typography variant="h6" fontWeight={700} gutterBottom sx={{ color: isDarkMode ? 'white' : '#1a1a2e' }}>
        {useDaily ? 'Recent Days' : 'Today'}
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
        {displayData.map((item: any, index: number) => {
          const temp = useDaily ? item.temp_avg : item.temperature;
          const heightPercent = ((temp - minTemp) / (maxTemp - minTemp)) * 100;
          const timeLabel = useDaily 
            ? format(parseISO(item.date), 'MMM d')
            : format(new Date(item.hour), 'ha');
          
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
                {Math.round(temp)}°
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
                {timeLabel}
              </Typography>
            </Box>
          );
        })}
      </Box>
    </Box>
  );
};

export default HourlyBarChart;
