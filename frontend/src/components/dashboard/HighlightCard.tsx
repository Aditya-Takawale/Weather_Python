/**
 * Highlight Card Component
 * Displays weather metrics in card format
 */

import React from 'react';
import { Card, CardContent, Typography, Box } from '@mui/material';
import { useTheme } from '../../context/ThemeContext';

interface HighlightCardProps {
  title: string;
  value: string | number;
  unit?: string;
  subtitle?: string;
  icon?: React.ReactNode;
  color?: string;
}

const HighlightCard: React.FC<HighlightCardProps> = ({
  title,
  value,
  unit,
  subtitle,
  icon,
  color = '#3B82F6',
}) => {
  const { isDarkMode } = useTheme();

  return (
    <Card
      sx={{
        height: '100%',
        background: isDarkMode 
          ? 'rgba(30, 30, 46, 0.6)'
          : 'rgba(255, 255, 255, 0.85)',
        backdropFilter: 'blur(20px)',
        border: isDarkMode 
          ? '1px solid rgba(255, 255, 255, 0.1)'
          : '1px solid rgba(255, 255, 255, 0.5)',
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        '&:hover': {
          transform: 'translateY(-6px) scale(1.02)',
          boxShadow: isDarkMode 
            ? '0 12px 32px rgba(0,0,0,0.4)'
            : '0 12px 32px rgba(0,0,0,0.2)',
          border: isDarkMode 
            ? '1px solid rgba(255, 255, 255, 0.2)'
            : '1px solid rgba(255, 255, 255, 0.7)',
          background: isDarkMode 
            ? 'rgba(30, 30, 46, 0.8)'
            : 'rgba(255, 255, 255, 0.95)',
        },
      }}
    >
      <CardContent sx={{ p: 2 }}>
        <Typography
          variant="caption"
          sx={{
            color: isDarkMode ? 'rgba(255, 255, 255, 0.6)' : '#64748B',
            textTransform: 'uppercase',
            fontWeight: 600,
            letterSpacing: 0.5,
            display: 'block',
            mb: 1,
          }}
        >
          {title}
        </Typography>

        <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 0.5, mb: 1 }}>
          <Typography
            variant="h4"
            sx={{
              color: color,
              fontWeight: 700,
              textShadow: `0 0 20px ${color}40`,
            }}
          >
            {value}
          </Typography>
          {unit && (
            <Typography
              variant="body2"
              sx={{
                color: color,
                fontWeight: 600,
                opacity: 0.9,
              }}
            >
              {unit}
            </Typography>
          )}
        </Box>

        {subtitle && (
          <Typography
            variant="caption"
            sx={{
              color: isDarkMode ? 'rgba(255, 255, 255, 0.5)' : 'rgba(26, 26, 46, 0.6)',
              display: 'block',
              fontWeight: 500,
            }}
          >
            {subtitle}
          </Typography>
        )}

        {icon && (
          <Box
            sx={{
              position: 'absolute',
              right: 16,
              bottom: 16,
              opacity: 0.2,
            }}
          >
            {icon}
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default HighlightCard;
