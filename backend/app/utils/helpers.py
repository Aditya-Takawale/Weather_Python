"""
Helper Utilities
Common utility functions used across the application
"""

from datetime import datetime, timezone


def get_current_timestamp() -> datetime:
    """
    Get current UTC timestamp
    
    Returns:
        Current datetime in UTC timezone
    """
    return datetime.now(timezone.utc)


def format_temperature(temp: float, unit: str = "°C") -> str:
    """
    Format temperature with unit
    
    Args:
        temp: Temperature value
        unit: Unit symbol (default: °C)
        
    Returns:
        Formatted temperature string
    """
    return f"{temp:.1f}{unit}"


def kelvin_to_celsius(kelvin: float) -> float:
    """
    Convert Kelvin to Celsius
    
    Args:
        kelvin: Temperature in Kelvin
        
    Returns:
        Temperature in Celsius
    """
    return kelvin - 273.15


def celsius_to_fahrenheit(celsius: float) -> float:
    """
    Convert Celsius to Fahrenheit
    
    Args:
        celsius: Temperature in Celsius
        
    Returns:
        Temperature in Fahrenheit
    """
    return (celsius * 9/5) + 32


def calculate_feels_like(
    temperature: float,
    humidity: float,
    wind_speed: float
) -> float:
    """
    Calculate "feels like" temperature using heat index and wind chill
    Simplified formula for demonstration
    
    Args:
        temperature: Actual temperature in Celsius
        humidity: Relative humidity percentage
        wind_speed: Wind speed in m/s
        
    Returns:
        Feels like temperature in Celsius
    """
    # Heat index approximation for high temperatures
    if temperature >= 27:
        heat_index = (
            -8.78469475556 +
            1.61139411 * temperature +
            2.33854883889 * humidity +
            -0.14611605 * temperature * humidity +
            -0.012308094 * temperature**2 +
            -0.0164248277778 * humidity**2 +
            0.002211732 * temperature**2 * humidity +
            0.00072546 * temperature * humidity**2 +
            -0.000003582 * temperature**2 * humidity**2
        )
        return round(heat_index, 1)
    
    # Wind chill for low temperatures
    elif temperature <= 10 and wind_speed > 1.34:
        wind_chill = (
            13.12 + 0.6215 * temperature -
            11.37 * (wind_speed * 3.6)**0.16 +
            0.3965 * temperature * (wind_speed * 3.6)**0.16
        )
        return round(wind_chill, 1)
    
    # Otherwise, return actual temperature
    return temperature


def truncate_string(text: str, max_length: int = 100) -> str:
    """
    Truncate string to maximum length
    
    Args:
        text: Input string
        max_length: Maximum length
        
    Returns:
        Truncated string with ellipsis if needed
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def safe_float(value: any, default: float = 0.0) -> float:
    """
    Safely convert value to float
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
        
    Returns:
        Float value or default
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_int(value: any, default: int = 0) -> int:
    """
    Safely convert value to integer
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
        
    Returns:
        Integer value or default
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default
