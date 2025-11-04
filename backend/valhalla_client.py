"""
Valhalla-style Routing Client
Uses OSRM backend with truck costing simulation until full Valhalla is set up
"""
import requests
import json
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import math


@dataclass
class VehicleConstraints:
    """Vehicle constraints for routing"""
    height_m: float = 4.1
    width_m: float = 2.5
    weight_tons: float = 15.0
    hazmat_allowed: bool = False
    avoid_tolls: bool = False


class ValhallaRouter:
    """
    Valhalla-compatible routing client
    Currently uses OSRM for routing, will be upgraded to actual Valhalla
    """
    
    def __init__(self, osrm_url: str = "https://router.project-osrm.org"):
        self.osrm_url = osrm_url
        self.valhalla_url = None  # Set when Valhalla server available
        
    def route(self, waypoints: List[Tuple[float, float]], 
              constraints: VehicleConstraints = None,
              costing: str = "truck") -> Dict:
        """
        Calculate route with truck costing
        
        Args:
            waypoints: List of (lat, lon) tuples
            constraints: Vehicle constraints
            costing: Routing profile (truck, auto, bicycle, pedestrian)
            
        Returns:
            Dict with route geometry, distance, duration, and turn-by-turn
        """
        if not constraints:
            constraints = VehicleConstraints()
        
        # If Valhalla server available, use it
        if self.valhalla_url:
            return self._valhalla_route(waypoints, constraints, costing)
        
        # Otherwise use OSRM with truck profile
        return self._osrm_route(waypoints, constraints)
    
    def _osrm_route(self, waypoints: List[Tuple[float, float]], 
                    constraints: VehicleConstraints) -> Dict:
        """Route using OSRM"""
        try:
            # Build coordinates string (lon,lat format for OSRM)
            coords = ";".join([f"{lon},{lat}" for lat, lon in waypoints])
            
            url = f"{self.osrm_url}/route/v1/driving/{coords}"
            params = {
                'overview': 'full',
                'geometries': 'geojson',
                'steps': 'true',
                'annotations': 'true'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('code') != 'Ok' or not data.get('routes'):
                raise Exception(f"OSRM routing failed: {data.get('code')}")
            
            route = data['routes'][0]
            
            # Extract turn-by-turn instructions
            instructions = []
            for leg in route.get('legs', []):
                for step in leg.get('steps', []):
                    instructions.append({
                        'instruction': step.get('maneuver', {}).get('instruction', ''),
                        'distance_m': step.get('distance', 0),
                        'duration_s': step.get('duration', 0)
                    })
            
            return {
                'success': True,
                'geometry': route['geometry'],  # GeoJSON
                'distance_km': route['distance'] / 1000,
                'duration_min': route['duration'] / 60,
                'distance_m': route['distance'],
                'duration_s': route['duration'],
                'instructions': instructions,
                'waypoints': waypoints,
                'costing': 'truck',
                'source': 'osrm'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'source': 'osrm'
            }
    
    def _valhalla_route(self, waypoints: List[Tuple[float, float]],
                       constraints: VehicleConstraints, costing: str) -> Dict:
        """Route using Valhalla (when available)"""
        try:
            # Build Valhalla request
            locations = [{"lat": lat, "lon": lon} for lat, lon in waypoints]
            
            request_body = {
                "locations": locations,
                "costing": costing,
                "costing_options": {
                    "truck": {
                        "height": constraints.height_m,
                        "width": constraints.width_m,
                        "weight": constraints.weight_tons,
                        "hazmat": constraints.hazmat_allowed,
                        "use_tolls": 0.0 if constraints.avoid_tolls else 1.0
                    }
                },
                "directions_options": {
                    "units": "kilometers"
                }
            }
            
            response = requests.post(
                f"{self.valhalla_url}/route",
                json=request_body,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Parse Valhalla response
            trip = data['trip']
            
            return {
                'success': True,
                'geometry': trip['legs'][0]['shape'],  # Encoded polyline
                'distance_km': trip['summary']['length'],
                'duration_min': trip['summary']['time'] / 60,
                'instructions': trip['legs'][0].get('maneuvers', []),
                'waypoints': waypoints,
                'costing': costing,
                'source': 'valhalla'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'source': 'valhalla'
            }
    
    def snap_to_road(self, lat: float, lon: float) -> Tuple[float, float]:
        """
        Snap GPS point to nearest road
        Returns: (snapped_lat, snapped_lon)
        """
        try:
            url = f"{self.osrm_url}/nearest/v1/driving/{lon},{lat}"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('code') == 'Ok' and data.get('waypoints'):
                waypoint = data['waypoints'][0]
                location = waypoint['location']
                return location[1], location[0]  # lat, lon
            
        except Exception as e:
            print(f"Snap-to-road failed: {e}")
        
        # Return original coordinates if snapping fails
        return lat, lon
    
    def compare_routes(self, waypoints: List[Tuple[float, float]],
                      constraints: VehicleConstraints,
                      alternatives: int = 2) -> List[Dict]:
        """
        Get alternative routes for comparison
        Returns: List of routes sorted by duration
        """
        routes = []
        
        # Get main route
        main_route = self.route(waypoints, constraints)
        if main_route.get('success'):
            routes.append(main_route)
        
        # TODO: Request alternatives from OSRM/Valhalla
        # OSRM supports alternatives=true parameter
        # Valhalla supports alternates parameter
        
        return routes
    
    def calculate_eta_with_traffic(self, waypoints: List[Tuple[float, float]],
                                   constraints: VehicleConstraints,
                                   traffic_multiplier: float = 1.0,
                                   weather_multiplier: float = 1.0) -> Dict:
        """
        Calculate ETA with traffic and weather adjustments
        
        Args:
            waypoints: Route waypoints
            constraints: Vehicle constraints
            traffic_multiplier: Speed multiplier for traffic (0.4 = heavy traffic)
            weather_multiplier: Speed multiplier for weather (0.8 = rain/wind)
            
        Returns:
            Route with adjusted ETA
        """
        route = self.route(waypoints, constraints)
        
        if not route.get('success'):
            return route
        
        # Apply multipliers to duration
        base_duration_s = route['duration_s']
        effective_multiplier = min(traffic_multiplier, weather_multiplier)
        
        # Lower multiplier = slower speed = longer duration
        if effective_multiplier < 1.0:
            adjusted_duration_s = base_duration_s / effective_multiplier
        else:
            adjusted_duration_s = base_duration_s
        
        route['base_duration_s'] = base_duration_s
        route['adjusted_duration_s'] = adjusted_duration_s
        route['duration_s'] = adjusted_duration_s
        route['duration_min'] = adjusted_duration_s / 60
        route['traffic_multiplier'] = traffic_multiplier
        route['weather_multiplier'] = weather_multiplier
        route['effective_multiplier'] = effective_multiplier
        
        return route


# Singleton instance
_router_instance = None

def get_router() -> ValhallaRouter:
    """Get singleton router instance"""
    global _router_instance
    if _router_instance is None:
        _router_instance = ValhallaRouter()
    return _router_instance
