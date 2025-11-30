/**
 * Alerts Panel Component
 * Displays active weather alerts
 */

import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
  Chip,
  Alert as MuiAlert,
  Collapse,
  Divider,
} from '@mui/material';
import {
  Warning,
  Error,
  Info,
  CheckCircle,
  ExpandMore,
  ExpandLess,
} from '@mui/icons-material';
import { format } from 'date-fns';
import type { Alert } from '../../types/weather.types';

interface AlertsPanelProps {
  alerts: Alert[];
  onAcknowledge: (alertId: string) => void;
}

const AlertsPanel: React.FC<AlertsPanelProps> = ({ alerts, onAcknowledge }) => {
  const [expanded, setExpanded] = React.useState<string | null>(null);

  const handleExpandClick = (alertId: string) => {
    setExpanded(expanded === alertId ? null : alertId);
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return <Error sx={{ color: '#EF4444' }} />;
      case 'warning':
        return <Warning sx={{ color: '#F59E0B' }} />;
      case 'info':
        return <Info sx={{ color: '#3B82F6' }} />;
      default:
        return <Info />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'error';
      case 'warning':
        return 'warning';
      case 'info':
        return 'info';
      default:
        return 'default';
    }
  };

  const activeAlerts = alerts.filter((alert) => !alert.is_acknowledged);
  const acknowledgedAlerts = alerts.filter((alert) => alert.is_acknowledged);

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent sx={{ p: 2 }}>
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            mb: 1.5,
          }}
        >
          <Typography variant="h6" fontWeight={700}>
            Weather Alerts
          </Typography>
          <Chip
            label={`${activeAlerts.length} Active`}
            color={activeAlerts.length > 0 ? 'error' : 'success'}
            size="small"
            sx={{ fontWeight: 600 }}
          />
        </Box>

        {activeAlerts.length === 0 ? (
          <MuiAlert severity="success" sx={{ borderRadius: 2 }}>
            <Typography variant="caption" fontWeight={600} display="block">
              All Clear! No active alerts.
            </Typography>
            <Typography variant="caption" sx={{ fontSize: '0.7rem' }}>
              Weather conditions are within normal thresholds.
            </Typography>
          </MuiAlert>
        ) : (
          <List sx={{ maxHeight: 320, overflow: 'auto' }}>
            {activeAlerts.map((alert) => (
              <Box key={alert.id}>
                <ListItem
                  sx={{
                    borderRadius: 2,
                    mb: 1,
                    backgroundColor: `${
                      alert.severity === 'critical'
                        ? '#FFF5F5'
                        : alert.severity === 'warning'
                        ? '#FFF8E1'
                        : '#E3F2FD'
                    }`,
                    '&:hover': {
                      backgroundColor: `${
                        alert.severity === 'critical'
                          ? '#FFEBEE'
                          : alert.severity === 'warning'
                          ? '#FFF3E0'
                          : '#BBDEFB'
                      }`,
                    },
                  }}
                >
                  <ListItemIcon>{getSeverityIcon(alert.severity)}</ListItemIcon>
                  <ListItemText
                    primary={
                      <Box
                        sx={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: 1,
                          flexWrap: 'wrap',
                        }}
                      >
                        <Typography variant="body1" fontWeight={600}>
                          {alert.message}
                        </Typography>
                        <Chip
                          label={alert.alert_type.replace('_', ' ')}
                          size="small"
                          color={getSeverityColor(alert.severity) as any}
                          sx={{ fontSize: '0.7rem' }}
                        />
                      </Box>
                    }
                    secondary={
                      <Typography variant="caption" color="text.secondary">
                        {format(new Date(alert.triggered_at), 'MMM dd, HH:mm')} • {alert.city}
                      </Typography>
                    }
                  />
                  <IconButton
                    size="small"
                    onClick={() => handleExpandClick(alert.id)}
                  >
                    {expanded === alert.id ? <ExpandLess /> : <ExpandMore />}
                  </IconButton>
                  <IconButton
                    size="small"
                    onClick={() => onAcknowledge(alert.id)}
                    sx={{ ml: 1 }}
                  >
                    <CheckCircle />
                  </IconButton>
                </ListItem>

                <Collapse in={expanded === alert.id} timeout="auto" unmountOnExit>
                  <Box sx={{ px: 2, pb: 2, pt: 1 }}>
                    <Typography variant="caption" color="text.secondary" display="block" mb={1}>
                      <strong>Threshold:</strong> {alert.condition.threshold_type}{' '}
                      {alert.condition.operator} {alert.condition.threshold_value}
                      {alert.condition.unit}
                    </Typography>
                    <Typography variant="caption" color="text.secondary" display="block">
                      <strong>Actual Value:</strong> {alert.condition.actual_value}
                      {alert.condition.unit}
                    </Typography>
                  </Box>
                </Collapse>
              </Box>
            ))}
          </List>
        )}

        {acknowledgedAlerts.length > 0 && (
          <>
            <Divider sx={{ my: 2 }} />
            <Typography variant="body2" color="text.secondary" mb={1}>
              Recently Acknowledged ({acknowledgedAlerts.length})
            </Typography>
            <List dense>
              {acknowledgedAlerts.slice(0, 3).map((alert) => (
                <ListItem key={alert.id} sx={{ opacity: 0.6, fontSize: '0.875rem' }}>
                  <ListItemIcon sx={{ minWidth: 32 }}>
                    <CheckCircle fontSize="small" color="success" />
                  </ListItemIcon>
                  <ListItemText
                    primary={alert.message}
                    primaryTypographyProps={{ variant: 'body2' }}
                    secondary={format(new Date(alert.triggered_at), 'MMM dd, HH:mm')}
                    secondaryTypographyProps={{ variant: 'caption' }}
                  />
                </ListItem>
              ))}
            </List>
          </>
        )}
      </CardContent>
    </Card>
  );
};

export default AlertsPanel;
