"""
Weather API Integration
Fetches weather data for delay reason scoring
Uses OpenWeatherMap API (free tier)
"""
import requests
import os
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()


class WeatherAPI:
    """Weather data provider for ETA calculations"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY', '')
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.cache = {}  # Simple in-memory cache
        self.cache_duration = timedelta(minutes=10)
        
    def get_weather(self, lat: float, lon: float) -> Optional[Dict]:
        """
        Get current weather for a location
        
        Returns: {
            'precipitation_mm_h': float,
            'wind_speed_kph': float,
            'temperature_c': float,
            'conditions': str,
            'alerts': []
        }
        """
        if not self.api_key:
            return self._mock_weather_data(lat, lon)
        
        # Check cache
        cache_key = f"{lat:.3f},{lon:.3f}"
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if datetime.utcnow() - cached_time < self.cache_duration:
                return cached_data
        
        try:
            # Get current weather
            url = f"{self.base_url}/weather"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            
            # Parse response
            weather_data = {
                'precipitation_mm_h': self._get_precipitation(data),
                'wind_speed_kph': data['wind']['speed'] * 3.6,  # m/s to km/h
                'temperature_c': data['main']['temp'],
                'conditions': data['weather'][0]['main'],
                'description': data['weather'][0]['description'],
                'alerts': []
            }
            
            # Get weather alerts if available
            alerts = self._get_alerts(lat, lon)
            if alerts:
                weather_data['alerts'] = alerts
            
            # Cache result
            self.cache[cache_key] = (weather_data, datetime.utcnow())
            
            return weather_data
            
        except Exception as e:
            print(f"Weather API error: {e}")
            return self._mock_weather_data(lat, lon)
    
    def _get_precipitation(self, data: Dict) -> float:
        """Extract precipitation rate in mm/h"""
        # Check for rain
        if 'rain' in data and '1h' in data['rain']:
            return data['rain']['1h']
        
        # Check for snow (convert to rain equivalent)
        if 'snow' in data and '1h' in data['snow']:
            return data['snow']['1h'] * 0.1  # Rough conversion
        
        return 0.0
    
    def _get_alerts(self, lat: float, lon: float) -> list:
        """Get weather alerts for location"""
        if not self.api_key:
            return []
        
        try:
            url = f"{self.base_url}/onecall"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'exclude': 'minutely,hourly,daily',
                'units': 'metric'
            }
            
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            
            if 'alerts' in data:
                return [
                    {
                        'event': alert['event'],
                        'description': alert['description'],
                        'start': alert['start'],
                        'end': alert['end']
                    }
                    for alert in data['alerts']
                ]
            
        except Exception as e:
            print(f"Weather alerts error: {e}")
        
        return []
    
    def _mock_weather_data(self, lat: float, lon: float) -> Dict:
        """
        Mock weather data for testing without API key
        Simulates various conditions based on location
        """
        # Simulate different conditions for different areas
        import random
        
        # Base conditions
        conditions = ['Clear', 'Clouds', 'Rain', 'Drizzle']
        weights = [0.5, 0.3, 0.15, 0.05]
        
        condition = random.choices(conditions, weights=weights)[0]
        
        if condition == 'Rain':
            precip = random.uniform(5, 15)
        elif condition == 'Drizzle':
            precip = random.uniform(1, 5)
        else:
            precip = 0.0
        
        return {
            'precipitation_mm_h': precip,
            'wind_speed_kph': random.uniform(5, 25),
            'temperature_c': random.uniform(15, 30),
            'conditions': condition,
            'description': condition.lower(),
            'alerts': [],
            'mock': True
        }
    
    def calculate_weather_multiplier(self, weather: Dict) -> Tuple[float, str]:
        """
        Calculate speed multiplier based on weather conditions
        
        Returns: (multiplier, reason)
            multiplier: 0.4 to 1.0 (lower = slower)
            reason: Human-readable explanation
        """
        precip = weather.get('precipitation_mm_h', 0)
        wind = weather.get('wind_speed_kph', 0)
        
        # Precipitation impact (spec: > 10 mm/h)
        if precip > 10:
            multiplier = 0.6
            reason = f"Heavy rain ({precip:.1f} mm/h) reducing speeds by 40%"
        elif precip > 5:
            multiplier = 0.8
            reason = f"Moderate rain ({precip:.1f} mm/h) reducing speeds by 20%"
        elif precip > 0:
            multiplier = 0.9
            reason = f"Light rain ({precip:.1f} mm/h) reducing speeds by 10%"
        # Wind impact (spec: > 40 km/h)
        elif wind > 40:
            multiplier = 0.7
            reason = f"High winds ({wind:.1f} km/h) reducing speeds by 30%"
        elif wind > 30:
            multiplier = 0.85
            reason = f"Moderate winds ({wind:.1f} km/h) reducing speeds by 15%"
        else:
            multiplier = 1.0
            reason = "Clear weather conditions"
        
        # Check for weather alerts
        if weather.get('alerts'):
            multiplier = min(multiplier, 0.7)
            alert_types = [a['event'] for a in weather['alerts']]
            reason = f"Weather alerts: {', '.join(alert_types)}"
        
        return multiplier, reason
    
    def get_weather_along_route(self, waypoints: list, 
                                num_samples: int = 5) -> list:
        """
        Sample weather conditions along a route
        
        Args:
            waypoints: List of (lat, lon) tuples
            num_samples: Number of points to sample
            
        Returns:
            List of weather data dicts
        """
        if len(waypoints) < 2:
            return []
        
        weather_samples = []
        
        # Sample evenly along route
        indices = [int(i * (len(waypoints) - 1) / (num_samples - 1)) 
                  for i in range(num_samples)]
        
        for idx in indices:
            lat, lon = waypoints[idx]
            weather = self.get_weather(lat, lon)
            if weather:
                weather_samples.append(weather)
        
        return weather_samples
    
    def get_worst_weather_condition(self, weather_samples: list) -> Tuple[float, str]:
        """
        Find worst weather condition along route
        
        Returns: (worst_multiplier, reason)
        """
        if not weather_samples:
            return 1.0, "No weather data available"
        
        worst_multiplier = 1.0
        worst_reason = "Clear conditions"
        
        for weather in weather_samples:
            multiplier, reason = self.calculate_weather_multiplier(weather)
            if multiplier < worst_multiplier:
                worst_multiplier = multiplier
                worst_reason = reason
        
        return worst_multiplier, worst_reason


# Singleton instance
_weather_instance = None

def get_weather_api() -> WeatherAPI:
    """Get singleton weather API instance"""
    global _weather_instance
    if _weather_instance is None:
        _weather_instance = WeatherAPI()
    return _weather_instance
