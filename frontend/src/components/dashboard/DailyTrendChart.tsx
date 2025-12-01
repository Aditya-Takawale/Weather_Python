/**
 * Daily Trend Chart Component
 * Bar chart showing 7-day temperature trends
 */

import React from 'react';
import { Card, CardContent, Typography, Box } from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { format, parseISO } from 'date-fns';
import { useTheme } from '../../context/ThemeContext';
import type { DailyTrend } from '../../types/weather.types';

interface DailyTrendChartProps {
  data: DailyTrend[];
}

const DailyTrendChart: React.FC<DailyTrendChartProps> = ({ data }) => {
  const { isDarkMode } = useTheme();
  
  // Debug: Log the data to see what we're receiving
  console.log('DailyTrendChart received data:', data);
  
  const formattedData = data.map((item) => ({
    date: format(parseISO(item.date), 'MMM dd'),
    avg: item.temp_avg,
    min: item.temp_min,
    max: item.temp_max,
    humidity: item.humidity_avg,
    weather: item.weather_main,
  }));

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <Box
          sx={{
            backgroundColor: isDarkMode ? 'rgba(30, 30, 46, 0.95)' : 'rgba(255, 255, 255, 0.95)',
            p: 2,
            borderRadius: 1,
            boxShadow: 3,
            border: isDarkMode ? '1px solid rgba(255, 255, 255, 0.2)' : '1px solid #e0e0e0',
          }}
        >
          <Typography variant="body2" fontWeight={700} gutterBottom sx={{ color: isDarkMode ? 'white' : '#1a1a2e' }}>
            {label}
          </Typography>
          <Typography variant="caption" sx={{ display: 'block', color: '#EF4444' }}>
            Max: {data.max.toFixed(1)}°C
          </Typography>
          <Typography variant="caption" sx={{ display: 'block', color: '#F59E0B' }}>
            Avg: {data.avg.toFixed(1)}°C
          </Typography>
          <Typography variant="caption" sx={{ display: 'block', color: '#3B82F6' }}>
            Min: {data.min.toFixed(1)}°C
          </Typography>
          <Typography variant="caption" sx={{ display: 'block', color: isDarkMode ? '#94a3b8' : '#64748B', mt: 0.5 }}>
            Humidity: {data.humidity.toFixed(1)}%
          </Typography>
          <Typography variant="caption" sx={{ display: 'block', color: isDarkMode ? '#94a3b8' : '#64748B' }}>
            {data.weather}
          </Typography>
        </Box>
      );
    }
    return null;
  };

  return (
    <Card sx={{ 
      height: '100%', 
      background: isDarkMode ? 'rgba(30, 30, 46, 0.6)' : 'rgba(255, 255, 255, 0.85)',
      backdropFilter: 'blur(20px)',
      border: isDarkMode ? '1px solid rgba(255, 255, 255, 0.1)' : '1px solid rgba(102, 126, 234, 0.3)',
      transition: 'background 0.3s ease, border 0.3s ease',
    }}>
      <CardContent sx={{ p: 3 }}>
        <Box sx={{ mb: 2 }}>
          <Typography variant="h6" fontWeight={700} gutterBottom sx={{ color: isDarkMode ? 'white' : '#1a1a2e' }}>
            7-Day Temperature Trend
          </Typography>
          <Typography variant="caption" sx={{ color: isDarkMode ? 'rgba(255, 255, 255, 0.6)' : '#64748B' }}>
            Daily min, max, and average temperatures
          </Typography>
        </Box>

        {formattedData.length === 0 ? (
          <Box sx={{ textAlign: 'center', py: 8, color: isDarkMode ? 'rgba(255, 255, 255, 0.6)' : '#64748B' }}>
            <Typography variant="body2">No data available for the 7-day trend</Typography>
          </Box>
        ) : (
          <ResponsiveContainer width="100%" height={350}>
          <BarChart data={formattedData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke={isDarkMode ? 'rgba(255, 255, 255, 0.1)' : '#E5E7EB'} vertical={false} />
            <XAxis
              dataKey="date"
              stroke={isDarkMode ? 'rgba(255, 255, 255, 0.6)' : '#6B7280'}
              style={{ fontSize: '12px', fontWeight: 500 }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              stroke={isDarkMode ? 'rgba(255, 255, 255, 0.6)' : '#6B7280'}
              style={{ fontSize: '12px', fontWeight: 500 }}
              label={{ value: '°C', angle: -90, position: 'insideLeft', style: { fontWeight: 600, fill: isDarkMode ? 'rgba(255, 255, 255, 0.6)' : '#6B7280' } }}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: isDarkMode ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0,0,0,0.05)' }} />
            <Legend
              wrapperStyle={{ fontSize: '13px', paddingTop: '20px', fontWeight: 600, color: isDarkMode ? 'white' : '#1a1a2e' }}
              iconType="circle"
            />
            <Bar dataKey="max" name="Max Temp" radius={[8, 8, 0, 0]} barSize={40}>
              {formattedData.map((_entry, index) => (
                <Cell key={`cell-max-${index}`} fill="#EF4444" />
              ))}
            </Bar>
            <Bar dataKey="avg" name="Avg Temp" radius={[8, 8, 0, 0]} barSize={40}>
              {formattedData.map((_entry, index) => (
                <Cell key={`cell-avg-${index}`} fill="#F59E0B" />
              ))}
            </Bar>
            <Bar dataKey="min" name="Min Temp" radius={[8, 8, 0, 0]} barSize={40}>
              {formattedData.map((_entry, index) => (
                <Cell key={`cell-min-${index}`} fill="#3B82F6" />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
};

export default DailyTrendChart;
