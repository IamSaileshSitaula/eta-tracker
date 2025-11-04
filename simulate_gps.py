#!/usr/bin/env python
"""
Synthetic GPS Data Generator for Live Tracking Demo
Simulates a truck moving along the route Dallas -> Houston -> Beaumont
"""
import requests
import time
from datetime import datetime
import math

API_URL = "http://localhost:5000"
SHIPMENT_ID = 1
VEHICLE_ID = 1

# Route waypoints (Dallas -> Houston -> Beaumont)
route_points = [
    # Dallas to Houston (I-45 South)
    {"lat": 32.896, "lon": -97.036, "name": "Dallas Facility"},
    {"lat": 32.850, "lon": -96.950, "name": "South Dallas"},
    {"lat": 32.750, "lon": -96.850, "name": "Ennis"},
    {"lat": 32.350, "lon": -96.600, "name": "Corsicana"},
    {"lat": 31.950, "lon": -96.450, "name": "Fairfield"},
    {"lat": 31.550, "lon": -96.300, "name": "Buffalo"},
    {"lat": 31.150, "lon": -96.050, "name": "Centerville"},
    {"lat": 30.750, "lon": -95.800, "name": "Madisonville"},
    {"lat": 30.350, "lon": -95.600, "name": "Huntsville"},
    {"lat": 30.100, "lon": -95.450, "name": "Conroe"},
    {"lat": 29.990, "lon": -95.336, "name": "Houston Hub"},
    # Houston to Beaumont (I-10 East)
    {"lat": 29.950, "lon": -95.250, "name": "East Houston"},
    {"lat": 29.920, "lon": -95.100, "name": "Channelview"},
    {"lat": 29.880, "lon": -94.900, "name": "Baytown"},
    {"lat": 29.840, "lon": -94.700, "name": "Mont Belvieu"},
    {"lat": 29.800, "lon": -94.500, "name": "Wallisville"},
    {"lat": 29.850, "lon": -94.350, "name": "Winnie"},
    {"lat": 29.950, "lon": -94.200, "name": "Hamshire"},
    {"lat": 30.050, "lon": -94.150, "name": "Nome"},
    {"lat": 30.080, "lon": -94.126, "name": "Beaumont DC"}
]

def send_gps_position(lat, lon, speed_kph=80, heading=90):
    """Send GPS position to backend"""
    try:
        data = {
            "vehicle_id": VEHICLE_ID,
            "points": [{
                "ts": datetime.utcnow().isoformat() + "Z",
                "lat": lat,
                "lon": lon,
                "speed_kph": speed_kph,
                "heading_deg": heading
            }]
        }
        response = requests.post(f"{API_URL}/v1/positions", json=data)
        if response.status_code == 200:
            print(f"✓ GPS: {lat:.4f}, {lon:.4f} @ {speed_kph:.1f} km/h")
            return True
        else:
            print(f"✗ Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"✗ Connection error: {e}")
        return False

def calculate_heading(lat1, lon1, lat2, lon2):
    """Calculate bearing between two points"""
    dlon = math.radians(lon2 - lon1)
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)
    
    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    
    bearing = math.degrees(math.atan2(x, y))
    return (bearing + 360) % 360

def interpolate_points(start, end, num_points=5):
    """Create intermediate points between two waypoints"""
    points = []
    for i in range(num_points):
        t = i / (num_points - 1)
        lat = start["lat"] + t * (end["lat"] - start["lat"])
        lon = start["lon"] + t * (end["lon"] - start["lon"])
        points.append({"lat": lat, "lon": lon})
    return points

def simulate_truck_movement(delay_seconds=2, speed_variation=True):
    """Simulate truck moving along the route"""
    print("=" * 60)
    print("🚚 Synthetic GPS Data Generator")
    print("=" * 60)
    print(f"Shipment ID: {SHIPMENT_ID}")
    print(f"Vehicle ID: {VEHICLE_ID}")
    print(f"Route: {len(route_points)} waypoints")
    print(f"Update interval: {delay_seconds} seconds")
    print("=" * 60)
    print("\nStarting simulation... (Press Ctrl+C to stop)\n")
    
    try:
        point_idx = 0
        while True:
            # Cycle through waypoints
            if point_idx >= len(route_points):
                print("\n🏁 Reached final destination! Restarting from Dallas...\n")
                point_idx = 0
                time.sleep(10)  # Pause before restarting
            
            current = route_points[point_idx]
            
            # Get next point for heading calculation
            next_idx = min(point_idx + 1, len(route_points) - 1)
            next_point = route_points[next_idx]
            
            # Calculate heading
            heading = calculate_heading(
                current["lat"], current["lon"],
                next_point["lat"], next_point["lon"]
            )
            
            # Vary speed to simulate traffic
            if speed_variation:
                import random
                # Speed varies between 60-100 km/h
                speed = 60 + random.random() * 40
                # Slow down near stops
                if "Hub" in current["name"] or "Facility" in current["name"] or "DC" in current["name"]:
                    speed = 20 + random.random() * 30
            else:
                speed = 80
            
            # Send GPS position
            send_gps_position(current["lat"], current["lon"], speed, heading)
            
            # If between major waypoints, add interpolated points
            if point_idx < len(route_points) - 1:
                next_major = route_points[point_idx + 1]
                interpolated = interpolate_points(current, next_major, num_points=3)
                
                for interp in interpolated[1:-1]:  # Skip first and last (already covered)
                    time.sleep(delay_seconds)
                    heading = calculate_heading(
                        interp["lat"], interp["lon"],
                        next_major["lat"], next_major["lon"]
                    )
                    send_gps_position(interp["lat"], interp["lon"], speed, heading)
            
            point_idx += 1
            time.sleep(delay_seconds)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Simulation stopped by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")

if __name__ == "__main__":
    # Wait for backend to be ready
    print("Checking backend connection...")
    for i in range(5):
        try:
            response = requests.get(f"{API_URL}/health")
            if response.status_code == 200:
                print("✓ Backend is ready!\n")
                break
        except:
            print(f"Waiting for backend... ({i+1}/5)")
            time.sleep(2)
    else:
        print("❌ Could not connect to backend. Make sure it's running on port 5000.")
        exit(1)
    
    # Start simulation
    simulate_truck_movement(delay_seconds=3, speed_variation=True)
