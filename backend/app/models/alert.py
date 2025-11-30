"""
Alert Data Models
Models for weather alert notifications and logging
"""

from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class AlertType(str, Enum):
    """Alert type enumeration"""
    HIGH_TEMPERATURE = "HIGH_TEMPERATURE"
    LOW_TEMPERATURE = "LOW_TEMPERATURE"
    HIGH_HUMIDITY = "HIGH_HUMIDITY"
    EXTREME_WEATHER = "EXTREME_WEATHER"
    WIND_SPEED = "WIND_SPEED"
    VISIBILITY = "VISIBILITY"


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertCondition(BaseModel):
    """Alert condition details"""
    threshold_type: str = Field(..., description="Type of threshold (temperature, humidity, etc.)")
    threshold_value: float = Field(..., description="Threshold value that triggered alert")
    actual_value: float = Field(..., description="Actual measured value")
    operator: str = Field(..., description="Comparison operator (>, <, ==)")
    unit: Optional[str] = Field(None, description="Unit of measurement")


class AlertLog(BaseModel):
    """
    Alert Log Model
    Records weather alerts triggered by threshold violations
    """
    
    city: str = Field(..., description="City where alert was triggered")
    alert_type: AlertType = Field(..., description="Type of alert")
    severity: AlertSeverity = Field(..., description="Alert severity level")
    
    message: str = Field(..., description="Human-readable alert message")
    triggered_at: datetime = Field(default_factory=datetime.utcnow, description="Alert trigger time")
    
    condition: AlertCondition = Field(..., description="Condition that triggered alert")
    
    is_acknowledged: bool = Field(default=False, description="Whether alert has been acknowledged")
    acknowledged_at: Optional[datetime] = Field(None, description="Acknowledgment timestamp")
    
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context data"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "city": "Pune",
                "alert_type": "HIGH_TEMPERATURE",
                "severity": "warning",
                "message": "Temperature exceeded 35°C threshold",
                "triggered_at": "2025-11-28T14:30:00Z",
                "condition": {
                    "threshold_type": "temperature",
                    "threshold_value": 35.0,
                    "actual_value": 36.5,
                    "operator": ">",
                    "unit": "°C"
                },
                "is_acknowledged": False,
                "metadata": {
                    "temperature": 36.5,
                    "humidity": 70.0,
                    "weather_main": "Clear"
                }
            }
        }


class AlertResponse(BaseModel):
    """API response model for alerts"""
    id: str = Field(..., description="Alert ID")
    city: str
    alert_type: AlertType
    severity: AlertSeverity
    message: str
    triggered_at: datetime
    is_acknowledged: bool
    condition: AlertCondition
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "city": "Pune",
                "alert_type": "HIGH_TEMPERATURE",
                "severity": "warning",
                "message": "Temperature exceeded 35°C",
                "triggered_at": "2025-11-28T14:30:00Z",
                "is_acknowledged": False,
                "condition": {
                    "threshold_type": "temperature",
                    "threshold_value": 35.0,
                    "actual_value": 36.5,
                    "operator": ">"
                }
            }
        }


class AlertAcknowledgeRequest(BaseModel):
    """Request model for acknowledging an alert"""
    alert_id: str = Field(..., description="Alert ID to acknowledge")


class AlertStatsResponse(BaseModel):
    """Alert statistics response"""
    total_alerts: int = Field(..., description="Total alerts count")
    active_alerts: int = Field(..., description="Active (unacknowledged) alerts")
    by_severity: Dict[str, int] = Field(..., description="Count by severity")
    by_type: Dict[str, int] = Field(..., description="Count by alert type")
    recent_alerts: int = Field(..., description="Alerts in last 24 hours")
