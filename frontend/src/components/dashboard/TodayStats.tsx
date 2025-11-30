/**
 * Today's Statistics Card Component
 * Displays aggregated stats for the current day
 */

import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Grid,
  LinearProgress,
} from '@mui/material';
import {
  ThermostatAuto,
  Water,
  Speed,
  DataUsage,
} from '@mui/icons-material';
import type { TodayStats } from '../../types/weather.types';

interface TodayStatsCardProps {
  stats: TodayStats;
}

const TodayStatsCard: React.FC<TodayStatsCardProps> = ({ stats }) => {
  const StatItem = ({
    icon,
    label,
    value,
    unit,
    min,
    max,
    avg,
    color,
  }: {
    icon: React.ReactNode;
    label: string;
    value?: string;
    unit: string;
    min?: number;
    max?: number;
    avg?: number;
    color: string;
  }) => (
    <Box
      sx={{
        p: 2.5,
        borderRadius: 3,
        background: `linear-gradient(135deg, ${color}15 0%, ${color}05 100%)`,
        border: `2px solid ${color}30`,
        transition: 'all 0.3s ease',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: `0 8px 24px ${color}40`,
          border: `2px solid ${color}60`,
        },
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1.5 }}>
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: 40,
            height: 40,
            borderRadius: 2,
            backgroundColor: `${color}20`,
            color: color,
            mr: 1.5,
          }}
        >
          {icon}
        </Box>
        <Typography variant="body2" color="text.secondary" fontWeight={600}>
          {label}
        </Typography>
      </Box>

      {value && (
        <Typography variant="h4" fontWeight={700} color={color}>
          {value}
          <Typography component="span" variant="h6" color="text.secondary" ml={0.5}>
            {unit}
          </Typography>
        </Typography>
      )}

      {min !== undefined && max !== undefined && avg !== undefined && (
        <Box sx={{ mt: 1 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
            <Typography variant="caption" color="text.secondary">
              Min: {min.toFixed(1)}{unit}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Max: {max.toFixed(1)}{unit}
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={((avg - min) / (max - min)) * 100}
            sx={{
              height: 6,
              borderRadius: 3,
              backgroundColor: `${color}20`,
              '& .MuiLinearProgress-bar': {
                backgroundColor: color,
              },
            }}
          />
          <Typography
            variant="caption"
            color="text.secondary"
            sx={{ display: 'block', mt: 0.5, textAlign: 'center' }}
          >
            Avg: {avg.toFixed(1)}{unit}
          </Typography>
        </Box>
      )}
    </Box>
  );

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent sx={{ p: 2 }}>
        <Box sx={{ mb: 2 }}>
          <Typography variant="h6" fontWeight={700} gutterBottom>
            Today's Statistics
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Based on {stats.records_count} data points
          </Typography>
        </Box>

        <Grid container spacing={1.5}>
          <Grid item xs={12} sm={6}>
            <StatItem
              icon={<ThermostatAuto />}
              label="Temperature"
              min={stats.temp_min}
              max={stats.temp_max}
              avg={stats.temp_avg}
              unit="°C"
              color="#F59E0B"
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <StatItem
              icon={<Water />}
              label="Humidity"
              min={stats.humidity_min}
              max={stats.humidity_max}
              avg={stats.humidity_avg}
              unit="%"
              color="#3B82F6"
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <StatItem
              icon={<Speed />}
              label="Pressure"
              value={stats.pressure_avg.toString()}
              unit="hPa"
              color="#8B5CF6"
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <StatItem
              icon={<DataUsage />}
              label="Wind Speed"
              value={stats.wind_speed_avg.toFixed(1)}
              unit="m/s"
              color="#10B981"
            />
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default TodayStatsCard;
