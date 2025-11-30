/**
 * Hourly Trend Chart Component
 * Line chart showing temperature and humidity over last 24 hours
 */

import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  ToggleButtonGroup,
  ToggleButton,
} from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { format } from 'date-fns';
import type { HourlyTrend } from '../../types/weather.types';

interface HourlyTrendChartProps {
  data: HourlyTrend[];
}

const HourlyTrendChart: React.FC<HourlyTrendChartProps> = ({ data }) => {
  const [metric, setMetric] = React.useState<'temperature' | 'humidity'>('temperature');

  const handleMetricChange = (
    event: React.MouseEvent<HTMLElement>,
    newMetric: 'temperature' | 'humidity' | null
  ) => {
    if (newMetric !== null) {
      setMetric(newMetric);
    }
  };

  const formattedData = data.map((item) => ({
    time: format(new Date(item.hour), 'HH:mm'),
    temperature: item.temperature,
    humidity: item.humidity,
    windSpeed: item.wind_speed,
  }));

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
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
          <Typography variant="body2" fontWeight={600} gutterBottom>
            {label}
          </Typography>
          {payload.map((entry: any, index: number) => (
            <Typography
              key={index}
              variant="caption"
              sx={{ color: entry.color, display: 'block' }}
            >
              {entry.name}: {entry.value.toFixed(1)}
              {entry.name === 'Temperature' ? '°C' : entry.name === 'Humidity' ? '%' : 'm/s'}
            </Typography>
          ))}
        </Box>
      );
    }
    return null;
  };

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent sx={{ p: 2 }}>
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            mb: 2,
          }}
        >
          <Box>
            <Typography variant="h6" fontWeight={700} gutterBottom>
              24-Hour Trend
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Hourly weather patterns
            </Typography>
          </Box>

          <ToggleButtonGroup
            value={metric}
            exclusive
            onChange={handleMetricChange}
            size="small"
          >
            <ToggleButton value="temperature">Temperature</ToggleButton>
            <ToggleButton value="humidity">Humidity</ToggleButton>
          </ToggleButtonGroup>
        </Box>

        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={formattedData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis
              dataKey="time"
              stroke="#94a3b8"
              style={{ fontSize: '12px' }}
              interval="preserveStartEnd"
            />
            <YAxis
              stroke="#94a3b8"
              style={{ fontSize: '12px' }}
              domain={
                metric === 'temperature'
                  ? ['auto', 'auto']
                  : [0, 100]
              }
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              wrapperStyle={{ fontSize: '14px', paddingTop: '20px' }}
              iconType="line"
            />
            {metric === 'temperature' ? (
              <>
                <Line
                  type="monotone"
                  dataKey="temperature"
                  name="Temperature"
                  stroke="#F59E0B"
                  strokeWidth={3}
                  dot={{ r: 4, fill: '#F59E0B' }}
                  activeDot={{ r: 6 }}
                />
                <Line
                  type="monotone"
                  dataKey="windSpeed"
                  name="Wind Speed"
                  stroke="#10B981"
                  strokeWidth={2}
                  dot={{ r: 3, fill: '#10B981' }}
                  strokeDasharray="5 5"
                />
              </>
            ) : (
              <Line
                type="monotone"
                dataKey="humidity"
                name="Humidity"
                stroke="#3B82F6"
                strokeWidth={3}
                dot={{ r: 4, fill: '#3B82F6' }}
                activeDot={{ r: 6 }}
              />
            )}
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};

export default HourlyTrendChart;
