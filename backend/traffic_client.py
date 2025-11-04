"""
Traffic Data Integration
Fetches live traffic speed data for congestion detection
Supports multiple providers: Google Traffic API, HERE Traffic, TomTom Traffic
"""
import requests
import os
from typing import Dict, Optional, List, Tuple
from datetime import datetime, timedelta
from dotenv import load_dotenv
import random

load_dotenv()


class TrafficAPI:
    """Traffic data provider for ETA calculations and congestion detection"""
    
    def __init__(self):
        # API keys for different providers
        self.google_api_key = os.getenv('GOOGLE_MAPS_API_KEY', '')
        self.here_api_key = os.getenv('HERE_API_KEY', '')
        self.tomtom_api_key = os.getenv('TOMTOM_API_KEY', '')
        
        # Cache to reduce API calls
        self.cache = {}
        self.cache_duration = timedelta(minutes=5)
        
        # Determine which provider to use
        self.provider = self._select_provider()
        
    def _select_provider(self) -> str:
        """Select traffic data provider based on available API keys"""
        if self.google_api_key:
            return 'google'
        elif self.here_api_key:
            return 'here'
        elif self.tomtom_api_key:
            return 'tomtom'
        else:
            return 'mock'
    
    def get_traffic_on_route(self, waypoints: List[Tuple[float, float]]) -> Dict:
        """
        Get traffic conditions along a route
        
        Args:
            waypoints: List of (lat, lon) tuples defining the route
            
        Returns: {
            'average_speed_kph': float,
            'freeflow_speed_kph': float,
            'congestion_level': str ('none', 'light', 'moderate', 'heavy'),
            'incidents': [],
            'travel_time_current_s': int,
            'travel_time_freeflow_s': int
        }
        """
        # Check cache
        cache_key = f"{waypoints[0][0]:.3f},{waypoints[0][1]:.3f}_{waypoints[-1][0]:.3f},{waypoints[-1][1]:.3f}"
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if datetime.utcnow() - cached_time < self.cache_duration:
                return cached_data
        
        # Fetch data based on provider
        if self.provider == 'google':
            traffic_data = self._get_google_traffic(waypoints)
        elif self.provider == 'here':
            traffic_data = self._get_here_traffic(waypoints)
        elif self.provider == 'tomtom':
            traffic_data = self._get_tomtom_traffic(waypoints)
        else:
            traffic_data = self._get_mock_traffic(waypoints)
        
        # Cache result
        self.cache[cache_key] = (traffic_data, datetime.utcnow())
        
        return traffic_data
    
    def _get_google_traffic(self, waypoints: List[Tuple[float, float]]) -> Dict:
        """Get traffic data from Google Maps Directions API"""
        try:
            # Build waypoints string
            origin = f"{waypoints[0][0]},{waypoints[0][1]}"
            destination = f"{waypoints[-1][0]},{waypoints[-1][1]}"
            
            # Add intermediate waypoints if any
            via_points = []
            if len(waypoints) > 2:
                for i in range(1, len(waypoints) - 1):
                    via_points.append(f"{waypoints[i][0]},{waypoints[i][1]}")
            
            url = "https://maps.googleapis.com/maps/api/directions/json"
            params = {
                'origin': origin,
                'destination': destination,
                'waypoints': '|'.join(via_points) if via_points else None,
                'departure_time': 'now',
                'traffic_model': 'best_guess',
                'key': self.google_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data['status'] == 'OK' and data['routes']:
                route = data['routes'][0]
                leg = route['legs'][0]
                
                # Calculate speeds
                duration_in_traffic = leg.get('duration_in_traffic', leg['duration'])['value']
                duration_normal = leg['duration']['value']
                distance_m = leg['distance']['value']
                
                current_speed = (distance_m / duration_in_traffic) * 3.6  # m/s to km/h
                freeflow_speed = (distance_m / duration_normal) * 3.6
                
                # Determine congestion level
                speed_ratio = current_speed / freeflow_speed if freeflow_speed > 0 else 1.0
                congestion = self._classify_congestion(speed_ratio)
                
                return {
                    'average_speed_kph': current_speed,
                    'freeflow_speed_kph': freeflow_speed,
                    'congestion_level': congestion,
                    'incidents': [],
                    'travel_time_current_s': duration_in_traffic,
                    'travel_time_freeflow_s': duration_normal,
                    'speed_ratio': speed_ratio,
                    'source': 'google'
                }
            
        except Exception as e:
            print(f"Google Traffic API error: {e}")
        
        return self._get_mock_traffic(waypoints)
    
    def _get_here_traffic(self, waypoints: List[Tuple[float, float]]) -> Dict:
        """Get traffic data from HERE Traffic API"""
        try:
            # Build waypoints string
            waypoint_str = ';'.join([f"{lat},{lon}" for lat, lon in waypoints])
            
            url = "https://router.hereapi.com/v8/routes"
            params = {
                'transportMode': 'truck',
                'origin': f"{waypoints[0][0]},{waypoints[0][1]}",
                'destination': f"{waypoints[-1][0]},{waypoints[-1][1]}",
                'via': waypoint_str if len(waypoints) > 2 else None,
                'return': 'summary,polyline',
                'apiKey': self.here_api_key,
                'departureTime': datetime.utcnow().isoformat()
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('routes'):
                route = data['routes'][0]
                summary = route['sections'][0]['summary']
                
                duration_current = summary['duration']
                duration_baseline = summary.get('baseDuration', duration_current)
                distance_m = summary['length']
                
                current_speed = (distance_m / duration_current) * 3.6 if duration_current > 0 else 0
                freeflow_speed = (distance_m / duration_baseline) * 3.6 if duration_baseline > 0 else current_speed
                
                speed_ratio = current_speed / freeflow_speed if freeflow_speed > 0 else 1.0
                congestion = self._classify_congestion(speed_ratio)
                
                return {
                    'average_speed_kph': current_speed,
                    'freeflow_speed_kph': freeflow_speed,
                    'congestion_level': congestion,
                    'incidents': [],
                    'travel_time_current_s': duration_current,
                    'travel_time_freeflow_s': duration_baseline,
                    'speed_ratio': speed_ratio,
                    'source': 'here'
                }
            
        except Exception as e:
            print(f"HERE Traffic API error: {e}")
        
        return self._get_mock_traffic(waypoints)
    
    def _get_tomtom_traffic(self, waypoints: List[Tuple[float, float]]) -> Dict:
        """Get traffic data from TomTom Traffic API"""
        try:
            # Build waypoints string
            locations = ':'.join([f"{lat},{lon}" for lat, lon in waypoints])
            
            url = f"https://api.tomtom.com/routing/1/calculateRoute/{locations}/json"
            params = {
                'key': self.tomtom_api_key,
                'traffic': 'true',
                'travelMode': 'truck',
                'departAt': 'now'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('routes'):
                route = data['routes'][0]
                summary = route['summary']
                
                duration_traffic = summary['travelTimeInSeconds']
                duration_notraffic = summary.get('noTrafficTravelTimeInSeconds', duration_traffic)
                distance_m = summary['lengthInMeters']
                
                current_speed = (distance_m / duration_traffic) * 3.6 if duration_traffic > 0 else 0
                freeflow_speed = (distance_m / duration_notraffic) * 3.6 if duration_notraffic > 0 else current_speed
                
                speed_ratio = current_speed / freeflow_speed if freeflow_speed > 0 else 1.0
                congestion = self._classify_congestion(speed_ratio)
                
                return {
                    'average_speed_kph': current_speed,
                    'freeflow_speed_kph': freeflow_speed,
                    'congestion_level': congestion,
                    'incidents': [],
                    'travel_time_current_s': duration_traffic,
                    'travel_time_freeflow_s': duration_notraffic,
                    'speed_ratio': speed_ratio,
                    'source': 'tomtom'
                }
            
        except Exception as e:
            print(f"TomTom Traffic API error: {e}")
        
        return self._get_mock_traffic(waypoints)
    
    def _get_mock_traffic(self, waypoints: List[Tuple[float, float]]) -> Dict:
        """
        Generate mock traffic data for testing
        Simulates various traffic conditions based on time of day and location
        """
        # Calculate approximate distance
        distance_km = 0
        for i in range(len(waypoints) - 1):
            lat1, lon1 = waypoints[i]
            lat2, lon2 = waypoints[i + 1]
            distance_km += self._haversine_distance(lat1, lon1, lat2, lon2)
        
        # Simulate traffic based on time of day
        hour = datetime.now().hour
        
        # Rush hour traffic (7-9 AM, 5-7 PM)
        if (7 <= hour <= 9) or (17 <= hour <= 19):
            speed_ratio = random.uniform(0.5, 0.7)  # Heavy traffic
        # Light traffic (10 PM - 5 AM)
        elif (22 <= hour) or (hour <= 5):
            speed_ratio = random.uniform(0.9, 1.0)  # Free flow
        # Normal traffic
        else:
            speed_ratio = random.uniform(0.7, 0.9)  # Moderate traffic
        
        freeflow_speed = 80.0  # km/h
        current_speed = freeflow_speed * speed_ratio
        
        duration_freeflow = int((distance_km / freeflow_speed) * 3600)
        duration_current = int((distance_km / current_speed) * 3600)
        
        congestion = self._classify_congestion(speed_ratio)
        
        return {
            'average_speed_kph': current_speed,
            'freeflow_speed_kph': freeflow_speed,
            'congestion_level': congestion,
            'incidents': [],
            'travel_time_current_s': duration_current,
            'travel_time_freeflow_s': duration_freeflow,
            'speed_ratio': speed_ratio,
            'source': 'mock',
            'mock': True
        }
    
    def _classify_congestion(self, speed_ratio: float) -> str:
        """
        Classify congestion level based on speed ratio
        
        Spec: TRAFFIC_CONGESTION when live_speed/freeflow < 0.4
        """
        if speed_ratio >= 0.9:
            return 'none'
        elif speed_ratio >= 0.7:
            return 'light'
        elif speed_ratio >= 0.4:
            return 'moderate'
        else:
            return 'heavy'
    
    def _haversine_distance(self, lat1: float, lon1: float, 
                           lat2: float, lon2: float) -> float:
        """Calculate distance between two points in kilometers"""
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371  # Earth's radius in km
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c
    
    def calculate_traffic_multiplier(self, traffic_data: Dict) -> Tuple[float, str]:
        """
        Calculate speed multiplier based on traffic conditions
        
        Returns: (multiplier, reason)
            multiplier: 0.4 to 1.0 (lower = slower)
            reason: Human-readable explanation
        """
        speed_ratio = traffic_data.get('speed_ratio', 1.0)
        congestion = traffic_data.get('congestion_level', 'none')
        
        # Use speed ratio as multiplier (capped at minimum 0.4 per spec)
        multiplier = max(speed_ratio, 0.4)
        
        if congestion == 'heavy':
            reason = f"Heavy traffic congestion (speeds {int(speed_ratio * 100)}% of normal)"
        elif congestion == 'moderate':
            reason = f"Moderate traffic delays (speeds {int(speed_ratio * 100)}% of normal)"
        elif congestion == 'light':
            reason = f"Light traffic conditions (speeds {int(speed_ratio * 100)}% of normal)"
        else:
            reason = "Free-flowing traffic conditions"
        
        return multiplier, reason
    
    def is_congested(self, traffic_data: Dict, duration_minutes: int = 5) -> bool:
        """
        Check if route is experiencing congestion per spec
        
        Spec: TRAFFIC_CONGESTION when live_speed/freeflow < 0.4 for ≥5 min
        
        Note: Duration check requires historical data; this checks current conditions
        """
        speed_ratio = traffic_data.get('speed_ratio', 1.0)
        return speed_ratio < 0.4


# Singleton instance
_traffic_instance = None

def get_traffic_api() -> TrafficAPI:
    """Get singleton traffic API instance"""
    global _traffic_instance
    if _traffic_instance is None:
        _traffic_instance = TrafficAPI()
    return _traffic_instance
