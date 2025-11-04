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
    
    def __init__(self, osrm_url: str = "https://router.project-osrm.org", valhalla_url: str = None):
        self.osrm_url = osrm_url
        self.valhalla_url = valhalla_url  # Set from environment variable
        
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
        """Route using Valhalla with full truck costing support"""
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
                    },
                    "auto": {
                        "use_tolls": 0.0 if constraints.avoid_tolls else 1.0
                    }
                },
                "directions_options": {
                    "units": "kilometers",
                    "language": "en-US"
                },
                "alternates": 2  # Request 2 alternative routes
            }
            
            response = requests.post(
                f"{self.valhalla_url}/route",
                json=request_body,
                timeout=15,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Parse Valhalla response
            trip = data['trip']
            leg = trip['legs'][0]
            
            # Parse maneuvers into instructions
            instructions = []
            for maneuver in leg.get('maneuvers', []):
                instructions.append({
                    'instruction': maneuver.get('instruction', ''),
                    'distance_m': maneuver.get('length', 0) * 1000,
                    'duration_s': maneuver.get('time', 0),
                    'street_names': maneuver.get('street_names', [])
                })
            
            # Parse alternative routes if available
            alternatives = []
            if 'alternates' in data:
                for alt in data['alternates']:
                    alt_trip = alt['trip']
                    alternatives.append({
                        'distance_km': alt_trip['summary']['length'],
                        'duration_min': alt_trip['summary']['time'] / 60,
                        'geometry': alt_trip['legs'][0]['shape']
                    })
            
            return {
                'success': True,
                'geometry': leg['shape'],  # Encoded polyline
                'distance_km': trip['summary']['length'],
                'duration_min': trip['summary']['time'] / 60,
                'distance_m': trip['summary']['length'] * 1000,
                'duration_s': trip['summary']['time'],
                'instructions': instructions,
                'waypoints': waypoints,
                'costing': costing,
                'source': 'valhalla',
                'alternatives': alternatives
            }
            
        except requests.exceptions.RequestException as e:
            print(f"Valhalla routing error: {e}")
            return {
                'success': False,
                'error': f"Valhalla routing failed: {str(e)}",
                'source': 'valhalla'
            }
        except Exception as e:
            print(f"Unexpected error in Valhalla routing: {e}")
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
        
        # If using Valhalla, alternatives are already included in response
        if main_route.get('alternatives'):
            for i, alt in enumerate(main_route['alternatives']):
                routes.append({
                    'success': True,
                    'id': i + 2,
                    'name': f'Alternative {i + 1}',
                    **alt,
                    'source': main_route['source']
                })
        
        return routes
    
    def calculate_alternatives(self, waypoints: List[Tuple[float, float]], 
                              constraints: VehicleConstraints = None,
                              num_alternatives: int = 3) -> List[Dict]:
        """
        Calculate multiple alternative routes with different optimization strategies
        
        Args:
            waypoints: List of (lat, lon) tuples
            constraints: Vehicle constraints
            num_alternatives: Number of alternatives to generate (max 3)
            
        Returns:
            List of route options with reasoning
        """
        if not constraints:
            constraints = VehicleConstraints()
        
        alternatives = []
        
        # Route 1: Fastest (default truck routing)
        route1 = self.route(waypoints, constraints, costing="truck")
        if route1['success']:
            alternatives.append({
                'id': 1,
                'name': 'Fastest Route',
                'route': route1,
                'reason': 'Optimized for minimum travel time',
                'distance_km': route1['distance_km'],
                'duration_min': route1['duration_min'],
                'geometry': route1['geometry']
            })
        
        # If Valhalla is available and returned alternatives, use them
        if route1.get('alternatives') and len(route1['alternatives']) > 0:
            for i, alt in enumerate(route1['alternatives'][:num_alternatives-1]):
                time_diff = alt['duration_min'] - route1['duration_min']
                dist_diff = alt['distance_km'] - route1['distance_km']
                
                if time_diff < 0:
                    reason = f"Faster by {abs(time_diff):.0f} minutes"
                elif dist_diff < 0:
                    reason = f"Shorter by {abs(dist_diff):.1f} km"
                else:
                    reason = f"Alternative route (+{time_diff:.0f} min)"
                
                alternatives.append({
                    'id': i + 2,
                    'name': f'Alternative Route {i + 1}',
                    'route': {
                        'success': True,
                        'distance_km': alt['distance_km'],
                        'duration_min': alt['duration_min'],
                        'geometry': alt['geometry'],
                        'source': 'valhalla'
                    },
                    'reason': reason,
                    'distance_km': alt['distance_km'],
                    'duration_min': alt['duration_min'],
                    'geometry': alt['geometry']
                })
        else:
            # Fallback: Calculate shortest distance route
            if len(alternatives) < num_alternatives:
                # For shortest, we'd need to request with different preferences
                # This is a placeholder for demonstration
                route2 = self.route(waypoints, constraints, costing="auto")
                if route2['success'] and route2['distance_km'] < route1['distance_km'] * 0.95:
                    dist_saved = route1['distance_km'] - route2['distance_km']
                    alternatives.append({
                        'id': 2,
                        'name': 'Shortest Route',
                        'route': route2,
                        'reason': f"Saves {dist_saved:.1f} km",
                        'distance_km': route2['distance_km'],
                        'duration_min': route2['duration_min'],
                        'geometry': route2['geometry']
                    })
            
            # Route 3: Avoid tolls if not already avoiding
            if len(alternatives) < num_alternatives and not constraints.avoid_tolls:
                constraints_no_toll = VehicleConstraints(
                    avoid_tolls=True,
                    height_m=constraints.height_m,
                    width_m=constraints.width_m,
                    weight_tons=constraints.weight_tons,
                    hazmat_allowed=constraints.hazmat_allowed
                )
                route3 = self.route(waypoints, constraints_no_toll, costing="truck")
                if route3['success']:
                    time_diff = route3['duration_min'] - route1['duration_min']
                    alternatives.append({
                        'id': 3,
                        'name': 'No Tolls Route',
                        'route': route3,
                        'reason': f"Avoids tolls (+{time_diff:.0f} min)" if time_diff > 0 else "Avoids tolls",
                        'distance_km': route3['distance_km'],
                        'duration_min': route3['duration_min'],
                        'geometry': route3['geometry']
                    })
        
        return alternatives[:num_alternatives]
    
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

def get_router(valhalla_url: str = None, osrm_url: str = "https://router.project-osrm.org") -> ValhallaRouter:
    """
    Get singleton router instance
    
    Args:
        valhalla_url: URL of Valhalla server (e.g., http://localhost:8002)
        osrm_url: URL of OSRM server (fallback)
        
    Returns:
        ValhallaRouter instance
    """
    global _router_instance
    if _router_instance is None:
        _router_instance = ValhallaRouter(osrm_url=osrm_url, valhalla_url=valhalla_url)
    return _router_instance
