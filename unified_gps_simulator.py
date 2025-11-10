#!/usr/bin/env python
"""
Unified GPS Simulator for ETA Tracker
Simulates complete delivery journey: Long-haul + Last-mile delivery

Journey Phases:
1. Long-haul: Dallas → Houston → Beaumont Distribution Center
2. Last-mile: Beaumont DC → Various delivery stops in Beaumont area

Author: ETA Tracker Team
Version: 2.0
"""

import requests
import time
import sys
import math
from datetime import datetime, timedelta
from typing import List, Dict, Tuple

# ============================================================================
# CONFIGURATION
# ============================================================================

API_URL = "http://localhost:5000"
DEFAULT_TRACKING_NUMBER = "PO-98765"
DEFAULT_VEHICLE_ID = 1
GPS_UPDATE_INTERVAL = 30  # seconds (realistic for commercial GPS - USA standard)
SPEED_MPH_HIGHWAY = 65    # Highway speed (Interstate speed limit)
SPEED_MPH_CITY = 30       # City speed (Urban areas)
SPEED_KPH_HIGHWAY = SPEED_MPH_HIGHWAY * 1.60934  # Convert to km/h for calculations
SPEED_KPH_CITY = SPEED_MPH_CITY * 1.60934        # Convert to km/h for calculations

# ============================================================================
# ROUTE DEFINITIONS
# ============================================================================

# Phase 1: Long-haul route (Dallas → Houston → Beaumont)
# Real I-45 South highway route with realistic waypoints
LONG_HAUL_ROUTE = [
    # Dallas Origin - I-45 South starting point
    {"lat": 32.7767, "lon": -96.7970, "name": "Dallas Distribution Center", "type": "origin", "dwell_min": 0, "speed_mph": 0},
    
    # South Dallas - merging onto I-45
    {"lat": 32.7200, "lon": -96.8100, "name": "I-45 South Merge", "type": "waypoint", "speed_mph": 55},
    {"lat": 32.6500, "lon": -96.8300, "name": "Red Oak", "type": "waypoint", "speed_mph": 65},
    {"lat": 32.5500, "lon": -96.8500, "name": "Waxahachie", "type": "waypoint", "speed_mph": 65},
    
    # Continuing south on I-45
    {"lat": 32.3500, "lon": -96.6000, "name": "Corsicana", "type": "waypoint", "speed_mph": 70},
    {"lat": 32.1000, "lon": -96.4500, "name": "Richland", "type": "waypoint", "speed_mph": 70},
    {"lat": 31.9500, "lon": -96.4500, "name": "Fairfield", "type": "waypoint", "speed_mph": 65},
    {"lat": 31.5500, "lon": -96.3000, "name": "Buffalo", "type": "waypoint", "speed_mph": 70},
    
    # Approaching Houston area
    {"lat": 31.1500, "lon": -96.0500, "name": "Centerville", "type": "waypoint", "speed_mph": 70},
    {"lat": 30.7500, "lon": -95.8000, "name": "Madisonville", "type": "waypoint", "speed_mph": 65},
    {"lat": 30.3500, "lon": -95.6000, "name": "Huntsville", "type": "waypoint", "speed_mph": 65},
    {"lat": 30.1000, "lon": -95.4500, "name": "Conroe", "type": "waypoint", "speed_mph": 60},
    {"lat": 29.9900, "lon": -95.4000, "name": "Spring", "type": "waypoint", "speed_mph": 55},
    
    # Houston Hub (30 minute rest stop - required by DOT regulations)
    {"lat": 29.7604, "lon": -95.3698, "name": "Houston Regional Hub", "type": "stop", "dwell_min": 30, "speed_mph": 0},
    
    # Houston to Beaumont on I-10 East
    {"lat": 29.7800, "lon": -95.2000, "name": "East Houston I-10", "type": "waypoint", "speed_mph": 60},
    {"lat": 29.8200, "lon": -95.0000, "name": "Channelview", "type": "waypoint", "speed_mph": 65},
    {"lat": 29.8500, "lon": -94.8000, "name": "Baytown", "type": "waypoint", "speed_mph": 65},
    {"lat": 29.8700, "lon": -94.6000, "name": "Mont Belvieu", "type": "waypoint", "speed_mph": 70},
    {"lat": 29.8900, "lon": -94.4000, "name": "Wallisville", "type": "waypoint", "speed_mph": 70},
    {"lat": 29.9200, "lon": -94.2500, "name": "Winnie", "type": "waypoint", "speed_mph": 65},
    {"lat": 30.0000, "lon": -94.1800, "name": "Hamshire", "type": "waypoint", "speed_mph": 60},
    {"lat": 30.0500, "lon": -94.1500, "name": "Nome", "type": "waypoint", "speed_mph": 55},
    
    # Beaumont Distribution Center arrival
    {"lat": 30.0860, "lon": -94.1265, "name": "Beaumont Distribution Center", "type": "hub", "dwell_min": 45, "speed_mph": 0},
]

# Phase 2: Last-mile delivery routes in Beaumont area
LAST_MILE_ROUTES = {
    "ROUTE-RETAIL-001": {
        "name": "Retail Express Route",
        "description": "Downtown Beaumont retail deliveries",
        "stops": [
            {"lat": 30.0860, "lon": -94.1265, "name": "Beaumont DC (Departure)", "type": "origin", "dwell_min": 0},
            {"lat": 30.0867, "lon": -94.1015, "name": "Parkdale Mall - Main Entrance", "type": "delivery", "dwell_min": 10},
            {"lat": 30.0805, "lon": -94.1016, "name": "Central Mall - Loading Dock", "type": "delivery", "dwell_min": 12},
            {"lat": 30.0863, "lon": -94.0998, "name": "Target Store #2156", "type": "delivery", "dwell_min": 8},
            {"lat": 30.0761, "lon": -94.1010, "name": "Walmart Supercenter #573", "type": "delivery", "dwell_min": 15},
            {"lat": 30.0802, "lon": -94.1112, "name": "Best Buy #1847", "type": "delivery", "dwell_min": 10},
            {"lat": 30.0860, "lon": -94.1265, "name": "Return to Beaumont DC", "type": "destination", "dwell_min": 0},
        ]
    },
    "ROUTE-HEALTH-001": {
        "name": "Healthcare & Education Route",
        "description": "Medical supplies and educational materials",
        "stops": [
            {"lat": 30.0860, "lon": -94.1265, "name": "Beaumont DC (Departure)", "type": "origin", "dwell_min": 0},
            {"lat": 30.0691, "lon": -94.1017, "name": "Baptist Hospitals of Southeast Texas", "type": "delivery", "dwell_min": 20},
            {"lat": 30.0866, "lon": -94.1023, "name": "Christus St. Elizabeth Hospital", "type": "delivery", "dwell_min": 18},
            {"lat": 30.0630, "lon": -94.0968, "name": "Lamar University - Student Center", "type": "delivery", "dwell_min": 12},
            {"lat": 30.0742, "lon": -94.1115, "name": "Central High School", "type": "delivery", "dwell_min": 8},
            {"lat": 30.0588, "lon": -94.1302, "name": "CVS Pharmacy #8745", "type": "delivery", "dwell_min": 6},
            {"lat": 30.0777, "lon": -94.1325, "name": "Walgreens #5623", "type": "delivery", "dwell_min": 6},
            {"lat": 30.0860, "lon": -94.1265, "name": "Return to Beaumont DC", "type": "destination", "dwell_min": 0},
        ]
    },
    "ROUTE-IND-001": {
        "name": "Industrial & Logistics Route",
        "description": "Port and industrial area deliveries",
        "stops": [
            {"lat": 30.0860, "lon": -94.1265, "name": "Beaumont DC (Departure)", "type": "origin", "dwell_min": 0},
            {"lat": 30.0813, "lon": -94.0764, "name": "Port of Beaumont - Terminal 1", "type": "delivery", "dwell_min": 25},
            {"lat": 30.0725, "lon": -94.0821, "name": "ExxonMobil Refinery - Gate 3", "type": "delivery", "dwell_min": 30},
            {"lat": 30.0932, "lon": -94.0655, "name": "Goodyear Chemical Plant", "type": "delivery", "dwell_min": 20},
            {"lat": 30.0556, "lon": -94.0933, "name": "Industrial Supply Co.", "type": "delivery", "dwell_min": 12},
            {"lat": 30.0611, "lon": -94.1156, "name": "Builders FirstSource Warehouse", "type": "delivery", "dwell_min": 15},
            {"lat": 30.0701, "lon": -94.1289, "name": "Home Depot Pro Desk #4521", "type": "delivery", "dwell_min": 10},
            {"lat": 30.0923, "lon": -94.1421, "name": "Ferguson Plumbing Supply", "type": "delivery", "dwell_min": 8},
            {"lat": 30.0860, "lon": -94.1265, "name": "Return to Beaumont DC", "type": "destination", "dwell_min": 0},
        ]
    }
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def calculate_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two coordinates using Haversine formula"""
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = (math.sin(dlat / 2) ** 2 + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

def calculate_heading(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate bearing/heading between two points (0-360 degrees)"""
    dlon = math.radians(lon2 - lon1)
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    
    x = math.sin(dlon) * math.cos(lat2_rad)
    y = (math.cos(lat1_rad) * math.sin(lat2_rad) - 
         math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon))
    
    bearing = math.degrees(math.atan2(x, y))
    return (bearing + 360) % 360

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two GPS coordinates using Haversine formula
    Returns distance in kilometers
    """
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c

def interpolate_points(start: Dict, end: Dict, num_points: int = 10) -> List[Dict]:
    """Create intermediate GPS points between two waypoints for smooth movement"""
    points = []
    for i in range(num_points):
        t = i / (num_points - 1) if num_points > 1 else 0
        lat = start["lat"] + t * (end["lat"] - start["lat"])
        lon = start["lon"] + t * (end["lon"] - start["lon"])
        points.append({"lat": lat, "lon": lon})
    return points

def send_gps_update(tracking_number: str, vehicle_id: int, lat: float, lon: float, 
                    speed_mph: float, heading: float) -> bool:
    """Send GPS position update to backend API"""
    try:
        # Convert MPH to KPH for database storage (international standard)
        speed_kph = speed_mph * 1.60934
        
        data = {
            "vehicle_id": vehicle_id,
            "points": [{
                "ts": datetime.utcnow().isoformat() + "Z",
                "lat": lat,
                "lon": lon,
                "speed_kph": speed_kph,
                "heading_deg": heading
            }]
        }
        
        response = requests.post(f"{API_URL}/v1/positions", json=data, timeout=5)
        
        if response.status_code == 200:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"  [{timestamp}] 📍 GPS: {lat:.6f}, {lon:.6f} | Speed: {speed_mph:.1f} mph | Heading: {heading:.0f}°")
            return True
        else:
            print(f"  ❌ API Error: {response.status_code} - {response.text[:100]}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"  ⚠️ Timeout sending GPS update")
        return False
    except requests.exceptions.ConnectionError:
        print(f"  ❌ Cannot connect to backend at {API_URL}")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def check_backend_connection() -> bool:
    """Verify backend API is accessible"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=3)
        return response.status_code == 200
    except:
        return False

# ============================================================================
# SIMULATION PHASES
# ============================================================================

def simulate_long_haul(tracking_number: str, vehicle_id: int) -> bool:
    """Phase 1: Simulate long-haul journey from Dallas to Beaumont"""
    print("\n" + "=" * 80)
    print("📦 PHASE 1: LONG-HAUL DELIVERY")
    print("=" * 80)
    print(f"Route: Dallas Distribution Center → Houston Hub → Beaumont DC")
    print(f"Distance: ~273 miles (440 km)")
    print(f"Highway Speed: {SPEED_MPH_HIGHWAY} mph (Interstate I-45 & I-10)")
    print(f"GPS Updates: Every {GPS_UPDATE_INTERVAL} seconds (USA Commercial Standard)")
    print(f"Waypoints: {len(LONG_HAUL_ROUTE)}")
    print("=" * 80)
    
    for i in range(len(LONG_HAUL_ROUTE) - 1):
        current = LONG_HAUL_ROUTE[i]
        next_point = LONG_HAUL_ROUTE[i + 1]
        
        # Get speed for this segment (considering speed limits)
        segment_speed_mph = next_point.get("speed_mph", SPEED_MPH_HIGHWAY)
        
        # Announce waypoint
        print(f"\n🚛 En route to: {next_point['name']} @ {segment_speed_mph} mph")
        
        # Calculate distance for realistic interpolation
        distance_km = haversine_distance(
            current["lat"], current["lon"],
            next_point["lat"], next_point["lon"]
        )
        
        # Calculate how many GPS pings based on distance and speed
        # GPS pings every 30 seconds
        time_hours = distance_km / (segment_speed_mph * 1.60934)
        time_seconds = time_hours * 3600
        num_pings = max(2, int(time_seconds / GPS_UPDATE_INTERVAL))
        
        # Create smooth movement between waypoints
        interpolated = interpolate_points(current, next_point, num_points=num_pings)
        
        for point in interpolated:
            heading = calculate_heading(point["lat"], point["lon"], next_point["lat"], next_point["lon"])
            
            if not send_gps_update(tracking_number, vehicle_id, 
                                  point["lat"], point["lon"], 
                                  segment_speed_mph, heading):
                print("⚠️ Failed to send GPS update, continuing...")
            
            time.sleep(GPS_UPDATE_INTERVAL)
        
        # Handle stops with dwell time
        if "dwell_min" in next_point and next_point["dwell_min"] > 0:
            print(f"\n  ⏸️ Stopped at {next_point['name']} for {next_point['dwell_min']} minutes")
            print(f"  (Simulated: {next_point['dwell_min'] * 2} seconds - time compressed)")
            
            # Send stationary GPS updates during stop
            for _ in range(next_point['dwell_min'] // 5):  # Update every 5 min of stop
                send_gps_update(tracking_number, vehicle_id,
                              next_point["lat"], next_point["lon"],
                              0.0, heading)  # Speed = 0 when stopped
                time.sleep(10)  # Compressed time
    
    print("\n✅ Long-haul phase complete! Arrived at Beaumont Distribution Center")
    return True

def simulate_last_mile(tracking_number: str, vehicle_id: int, route_id: str) -> bool:
    """Phase 2: Simulate last-mile delivery in Beaumont area"""
    
    if route_id not in LAST_MILE_ROUTES:
        print(f"❌ Unknown route: {route_id}")
        return False
    
    route = LAST_MILE_ROUTES[route_id]
    stops = route["stops"]
    
    print("\n" + "=" * 80)
    print("🏙️ PHASE 2: LAST-MILE DELIVERY")
    print("=" * 80)
    print(f"Route: {route['name']}")
    print(f"Description: {route['description']}")
    print(f"City Speed: {SPEED_KPH_CITY} km/h ({SPEED_KPH_CITY * 0.621371:.0f} mph)")
    print(f"Stops: {len([s for s in stops if s['type'] == 'delivery'])} deliveries")
    print("=" * 80)
    
    for i in range(len(stops) - 1):
        current = stops[i]
        next_stop = stops[i + 1]
        
        # Announce next stop
        stop_type_emoji = {
            "origin": "🏢",
            "delivery": "📦",
            "destination": "🏁"
        }.get(next_stop["type"], "📍")
        
        print(f"\n{stop_type_emoji} Driving to: {next_stop['name']}")
        
        # Create smooth city driving movement
        distance = calculate_distance_km(current["lat"], current["lon"], 
                                        next_stop["lat"], next_stop["lon"])
        num_points = max(8, int(distance * 10))  # More points for city driving
        interpolated = interpolate_points(current, next_stop, num_points=num_points)
        
        for point in interpolated:
            heading = calculate_heading(point["lat"], point["lon"], 
                                       next_stop["lat"], next_stop["lon"])
            
            if not send_gps_update(tracking_number, vehicle_id, 
                                  point["lat"], point["lon"], 
                                  SPEED_KPH_CITY, heading):
                print("⚠️ Failed to send GPS update, continuing...")
            
            time.sleep(GPS_UPDATE_INTERVAL)
        
        # Handle delivery stops
        if next_stop["type"] == "delivery" and next_stop.get("dwell_min", 0) > 0:
            print(f"  📦 Delivering at {next_stop['name']} ({next_stop['dwell_min']} min)")
            print(f"  (Simulated: {next_stop['dwell_min'] // 3} seconds)")
            time.sleep(next_stop['dwell_min'] / 3)  # Compress time for demo
    
    print("\n✅ Last-mile deliveries complete! All packages delivered")
    return True

# ============================================================================
# MAIN SIMULATION
# ============================================================================

def run_simulation(tracking_number: str, vehicle_id: int, 
                   skip_long_haul: bool = False, 
                   last_mile_route: str = "ROUTE-RETAIL-001"):
    """Run complete delivery simulation: Long-haul + Last-mile"""
    
    print("\n" + "=" * 80)
    print("🚚 UNIFIED GPS SIMULATOR - ETA TRACKER")
    print("=" * 80)
    print(f"Tracking Number: {tracking_number}")
    print(f"Vehicle ID: {vehicle_id}")
    print(f"GPS Update Interval: {GPS_UPDATE_INTERVAL} seconds")
    print(f"Backend API: {API_URL}")
    print("=" * 80)
    
    # Check backend connection
    print("\n🔍 Checking backend connection...")
    if not check_backend_connection():
        print(f"❌ Cannot connect to backend at {API_URL}")
        print("   Make sure the backend is running: python backend/app.py")
        return False
    print("✅ Backend connected successfully")
    
    try:
        # Phase 1: Long-haul delivery
        if not skip_long_haul:
            if not simulate_long_haul(tracking_number, vehicle_id):
                return False
        else:
            print("\n⏭️ Skipping long-haul phase (starting from Beaumont)")
        
        # Phase 2: Last-mile delivery
        if not simulate_last_mile(tracking_number, vehicle_id, last_mile_route):
            return False
        
        print("\n" + "=" * 80)
        print("🎉 DELIVERY SIMULATION COMPLETE!")
        print("=" * 80)
        print("Journey completed successfully:")
        print("  ✅ Long-haul: Dallas → Houston → Beaumont (440 km)")
        print(f"  ✅ Last-mile: {LAST_MILE_ROUTES[last_mile_route]['name']}")
        print("=" * 80)
        
        return True
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Simulation stopped by user (Ctrl+C)")
        return False
    except Exception as e:
        print(f"\n❌ Simulation error: {e}")
        return False

# ============================================================================
# CLI INTERFACE
# ============================================================================

def print_usage():
    """Print usage instructions"""
    print("\n" + "=" * 80)
    print("Usage: python unified_gps_simulator.py [OPTIONS]")
    print("=" * 80)
    print("\nOptions:")
    print("  <tracking_number>     Tracking number (default: PO-98765)")
    print("  --vehicle <id>        Vehicle ID (default: 1)")
    print("  --skip-longhaul       Skip long-haul, start from Beaumont")
    print("  --route <route_id>    Last-mile route ID")
    print("\nAvailable Last-Mile Routes:")
    for route_id, route in LAST_MILE_ROUTES.items():
        print(f"  {route_id:20} - {route['name']}")
        print(f"  {'':20}   {route['description']}")
        print(f"  {'':20}   {len([s for s in route['stops'] if s['type'] == 'delivery'])} delivery stops")
    print("\nExamples:")
    print("  python unified_gps_simulator.py")
    print("  python unified_gps_simulator.py PO-12345")
    print("  python unified_gps_simulator.py --skip-longhaul --route ROUTE-HEALTH-001")
    print("  python unified_gps_simulator.py PO-98765 --vehicle 2 --route ROUTE-IND-001")
    print("=" * 80)

if __name__ == "__main__":
    # Parse command line arguments
    tracking_number = DEFAULT_TRACKING_NUMBER
    vehicle_id = DEFAULT_VEHICLE_ID
    skip_long_haul = False
    last_mile_route = "ROUTE-RETAIL-001"
    
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        arg = args[i]
        
        if arg in ["-h", "--help", "help"]:
            print_usage()
            sys.exit(0)
        elif arg == "--vehicle":
            vehicle_id = int(args[i + 1])
            i += 2
        elif arg == "--skip-longhaul":
            skip_long_haul = True
            i += 1
        elif arg == "--route":
            last_mile_route = args[i + 1]
            i += 2
        elif not arg.startswith("--"):
            tracking_number = arg
            i += 1
        else:
            print(f"Unknown option: {arg}")
            print_usage()
            sys.exit(1)
    
    # Validate route
    if last_mile_route not in LAST_MILE_ROUTES:
        print(f"❌ Unknown route: {last_mile_route}")
        print("\nAvailable routes:")
        for route_id in LAST_MILE_ROUTES.keys():
            print(f"  - {route_id}")
        sys.exit(1)
    
    # Run simulation
    success = run_simulation(tracking_number, vehicle_id, skip_long_haul, last_mile_route)
    sys.exit(0 if success else 1)
