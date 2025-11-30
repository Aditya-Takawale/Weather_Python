/**
 * Weather Distribution Component
 * Pie chart showing weather condition distribution
 */

import React from 'react';
import { Card, CardContent, Typography, Box, Chip } from '@mui/material';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from 'recharts';

interface WeatherDistributionProps {
  distribution: Record<string, number>;
}

const WeatherDistribution: React.FC<WeatherDistributionProps> = ({ distribution }) => {
  const COLORS = {
    Clear: '#F59E0B',
    Clouds: '#6366F1',
    Rain: '#3B82F6',
    Drizzle: '#60A5FA',
    Thunderstorm: '#8B5CF6',
    Snow: '#06B6D4',
    Mist: '#64748B',
    Haze: '#94A3B8',
  };

  const data = Object.entries(distribution).map(([name, value]) => ({
    name,
    value,
    percentage: ((value / Object.values(distribution).reduce((a, b) => a + b, 0)) * 100).toFixed(1),
  }));

  const getColor = (name: string) => {
    return COLORS[name as keyof typeof COLORS] || '#9E9E9E';
  };

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <Box
          sx={{
            backgroundColor: 'white',
            p: 1.5,
            borderRadius: 1,
            boxShadow: 2,
            border: '1px solid #e0e0e0',
          }}
        >
          <Typography variant="body2" fontWeight={600}>
            {data.name}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            {data.value} records ({data.percentage}%)
          </Typography>
        </Box>
      );
    }
    return null;
  };

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent sx={{ p: 2 }}>
        <Typography variant="h6" fontWeight={700} gutterBottom>
          Weather Distribution
        </Typography>
        <Typography variant="caption" color="text.secondary" mb={1.5} display="block">
          Last 24 hours
        </Typography>

        <ResponsiveContainer width="100%" height={220}>
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              labelLine={false}
              outerRadius={90}
              fill="#8884d8"
              dataKey="value"
              label={({ name, percentage }) => `${name} ${percentage}%`}
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={getColor(entry.name)} />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
          </PieChart>
        </ResponsiveContainer>

        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 2 }}>
          {data.map((item) => (
            <Chip
              key={item.name}
              label={`${item.name}: ${item.value}`}
              size="small"
              sx={{
                backgroundColor: `${getColor(item.name)}20`,
                color: getColor(item.name),
                fontWeight: 600,
              }}
            />
          ))}
        </Box>
      </CardContent>
    </Card>
  );
};

export default WeatherDistribution;
