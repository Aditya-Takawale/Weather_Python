/**
 * Header Component
 * Top navigation bar with title and actions
 */

import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Box,
  Tooltip,
  Chip,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  WbSunny as SunnyIcon,
  Info as InfoIcon,
  DarkMode as DarkModeIcon,
  LightMode as LightModeIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import { useTheme } from '../../context/ThemeContext';

interface HeaderProps {
  lastUpdated: Date | null;
  onRefresh: () => void;
  loading: boolean;
}

const Header: React.FC<HeaderProps> = ({ lastUpdated, onRefresh, loading }) => {
  const { isDarkMode, toggleTheme } = useTheme();

  return (
    <AppBar
      position="static"
      elevation={0}
      sx={{
        background: isDarkMode 
          ? 'linear-gradient(90deg, #1a1a2e 0%, #16213e 100%)'
          : 'linear-gradient(90deg, #667EEA 0%, #764BA2 50%, #F093FB 100%)',
        borderRadius: 0,
        boxShadow: isDarkMode ? '0 2px 8px rgba(0, 0, 0, 0.3)' : '0 2px 8px rgba(102, 126, 234, 0.3)',
        transition: 'background 0.5s ease',
      }}
    >
      <Toolbar sx={{ minHeight: '56px !important', py: 1 }}>
        {isDarkMode ? (
          <DarkModeIcon sx={{ mr: 1.5, fontSize: 28 }} />
        ) : (
          <SunnyIcon sx={{ mr: 1.5, fontSize: 28 }} />
        )}
        <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 700 }}>
          Weather Monitoring System
        </Typography>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          {lastUpdated && (
            <Chip
              label={`Updated: ${format(lastUpdated, 'HH:mm:ss')}`}
              size="small"
              sx={{
                backgroundColor: 'rgba(255,255,255,0.2)',
                color: 'white',
                fontWeight: 600,
              }}
            />
          )}

          <Tooltip title="Refresh Data">
            <IconButton
              color="inherit"
              onClick={onRefresh}
              disabled={loading}
              sx={{
                '&:hover': {
                  backgroundColor: 'rgba(255,255,255,0.1)',
                },
              }}
            >
              <RefreshIcon
                sx={{
                  animation: loading ? 'spin 1s linear infinite' : 'none',
                  '@keyframes spin': {
                    '0%': { transform: 'rotate(0deg)' },
                    '100%': { transform: 'rotate(360deg)' },
                  },
                }}
              />
            </IconButton>
          </Tooltip>

          <Tooltip title={isDarkMode ? "Switch to Light Mode" : "Switch to Dark Mode"}>
            <Box
              onClick={toggleTheme}
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 0.5,
                padding: '4px 8px',
                borderRadius: '20px',
                backgroundColor: 'rgba(255,255,255,0.15)',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                '&:hover': {
                  backgroundColor: 'rgba(255,255,255,0.25)',
                  transform: 'scale(1.05)',
                },
              }}
            >
              <DarkModeIcon
                sx={{
                  fontSize: 20,
                  color: isDarkMode ? 'rgba(255,255,255,0.5)' : '#9D9FFF',
                  transition: 'all 0.3s ease',
                }}
              />
              <Box
                sx={{
                  width: 36,
                  height: 20,
                  borderRadius: '10px',
                  backgroundColor: 'rgba(255,255,255,0.2)',
                  position: 'relative',
                  transition: 'all 0.3s ease',
                }}
              >
                <Box
                  sx={{
                    width: 16,
                    height: 16,
                    borderRadius: '50%',
                    backgroundColor: 'white',
                    position: 'absolute',
                    top: 2,
                    left: isDarkMode ? 2 : 18,
                    transition: 'left 0.3s ease',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
                  }}
                />
              </Box>
              <LightModeIcon
                sx={{
                  fontSize: 20,
                  color: isDarkMode ? '#FFD700' : 'rgba(255,255,255,0.5)',
                  transition: 'all 0.3s ease',
                }}
              />
            </Box>
          </Tooltip>

          <Tooltip title="System Info">
            <IconButton
              color="inherit"
              sx={{
                '&:hover': {
                  backgroundColor: 'rgba(255,255,255,0.1)',
                },
              }}
            >
              <InfoIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
