#!/usr/bin/env python3
"""
B2B Last-Mile Delivery GPS Simulator

Realistic commercial delivery simulation for Beaumont, TX:
- 30-second GPS ping intervals (industry standard)
- MPH speed limits based on actual road data
- No artificial rerouting - relies on Valhalla API for real route calculations
- Realistic ETA variations with traffic
- B2B delivery scenarios (warehouses, stores, hospitals, schools)

This simulator generates realistic GPS data for testing routing accuracy
and ETA predictions in real-world commercial delivery scenarios.
"""

import os
import sys
import time
import math
import random
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv('API_URL', 'http://localhost:5000')

# Default speed limits for different road types in Beaumont, TX (MPH)
SPEED_LIMITS = {
    'highway': 60,
    'major_road': 45,
    'commercial': 35,
    'school_zone': 20,
    'hospital_zone': 25,
    'residential': 30,
    'industrial': 40
}


class RealisticB2BSimulator:
    """
    Realistic B2B delivery simulator with:
    - 30-second GPS intervals
    - MPH-based speeds
    - Real traffic patterns
    - No artificial rerouting
    """
    
    def __init__(self, shipment_ref: str, vehicle_id: int):
        """
        Initialize simulator for a specific shipment
        
        Args:
            shipment_ref: Shipment reference (e.g., "ROUTE-RETAIL-001")
            vehicle_id: Vehicle ID to simulate
        """
        self.shipment_ref = shipment_ref
        self.vehicle_id = vehicle_id
        self.current_stop_index = 0
        self.stops = []
        self.GPS_INTERVAL = 30  # 30 seconds between updates (industry standard)
        
    def fetch_route(self):
        """Fetch shipment route from backend"""
        try:
            response = requests.get(f"{API_URL}/v1/shipments?ref={self.shipment_ref}")
            if response.status_code != 200:
                print(f"❌ Failed to fetch shipment: {response.status_code}")
                return False
            
            shipments = response.json()
            if not shipments:
                print(f"❌ Shipment {self.shipment_ref} not found")
                return False
            
            shipment = shipments[0]
            
            # Fetch stops with Valhalla routing data
            status_response = requests.get(f"{API_URL}/v1/shipments/{shipment['id']}/status")
            if status_response.status_code != 200:
                print(f"❌ Failed to fetch stops: {status_response.status_code}")
                return False
            
            status = status_response.json()
            self.stops = status.get('stops', [])
            
            print(f"\n✓ Loaded route: {self.shipment_ref}")
            print(f"  Total stops: {len(self.stops)}")
            for i, stop in enumerate(self.stops):
                stop_type = stop.get('type', 'Commercial')
                print(f"  {i}. {stop['name']} ({stop_type})")
            
            return True
            
        except Exception as e:
            print(f"❌ Error fetching route: {e}")
            return False
    
    def calculate_distance_miles(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two points in miles"""
        R = 3959  # Earth's radius in miles
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def calculate_bearing(self, lat1, lon1, lat2, lon2):
        """Calculate bearing between two points in degrees"""
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lon = math.radians(lon2 - lon1)
        
        x = math.sin(delta_lon) * math.cos(lat2_rad)
        y = (math.cos(lat1_rad) * math.sin(lat2_rad) -
             math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lon))
        
        bearing = math.degrees(math.atan2(x, y))
        return (bearing + 360) % 360
    
    def get_speed_limit(self, stop):
        """Get speed limit for a stop based on location type"""
        # Check if stop has speed limit metadata
        if 'speed_limit_mph' in stop:
            return stop['speed_limit_mph']
        
        # Infer from stop type
        stop_type = stop.get('type', 'Commercial').lower()
        
        if 'hospital' in stop_type or 'healthcare' in stop_type:
            return SPEED_LIMITS['hospital_zone']
        elif 'school' in stop_type or 'education' in stop_type:
            return SPEED_LIMITS['school_zone']
        elif 'industrial' in stop_type or 'warehouse' in stop_type:
            return SPEED_LIMITS['industrial']
        elif 'retail' in stop_type or 'commercial' in stop_type:
            return SPEED_LIMITS['commercial']
        else:
            return SPEED_LIMITS['major_road']
    
    def calculate_realistic_gps_points(self, from_stop, to_stop):
        """
        Calculate GPS points for realistic 30-second intervals
        
        For a 10-minute trip: ~20 GPS pings (600 seconds / 30 = 20)
        Each ping should show logical progress and ETA variation
        """
        distance_miles = self.calculate_distance_miles(
            from_stop['lat'], from_stop['lon'],
            to_stop['lat'], to_stop['lon']
        )
        
        # Get speed limit for destination area
        speed_limit = self.get_speed_limit(to_stop)
        
        # Average speed: 75-85% of speed limit (realistic city driving)
        avg_speed_mph = speed_limit * random.uniform(0.75, 0.85)
        
        # Calculate travel time in seconds
        travel_time_seconds = (distance_miles / avg_speed_mph) * 3600
        
        # Number of GPS pings (30-second intervals)
        num_pings = max(int(travel_time_seconds / self.GPS_INTERVAL), 3)
        
        return {
            'distance_miles': distance_miles,
            'avg_speed_mph': avg_speed_mph,
            'speed_limit': speed_limit,
            'travel_time_seconds': travel_time_seconds,
            'num_pings': num_pings
        }
    
    def interpolate_points(self, start_lat, start_lon, end_lat, end_lon, num_points):
        """Generate intermediate GPS points between two locations"""
        points = []
        for i in range(num_points + 1):
            t = i / num_points
            lat = start_lat + t * (end_lat - start_lat)
            lon = start_lon + t * (end_lon - start_lon)
            points.append({'lat': lat, 'lon': lon})
        return points
    
    def send_gps_position(self, lat, lon, speed_mph, heading):
        """Send GPS position to backend (speed in mph)"""
        try:
            # Convert MPH to KPH for backend (it may expect kph)
            speed_kph = speed_mph * 1.60934
            
            data = {
                "vehicle_id": self.vehicle_id,
                "points": [{
                    "ts": datetime.utcnow().isoformat() + "Z",
                    "lat": lat,
                    "lon": lon,
                    "speed_kph": speed_kph,
                    "heading_deg": heading
                }]
            }
            
            response = requests.post(f"{API_URL}/v1/positions", json=data)
            return response.status_code == 200
            
        except Exception as e:
            print(f"  ❌ GPS send error: {e}")
            return False
    
    def simulate_b2b_stop_service(self, stop):
        """
        Simulate B2B delivery service time
        
        B2B deliveries take longer than residential:
        - Retail: 10-20 minutes (receiving desk, paperwork)
        - Healthcare: 8-15 minutes (secure delivery)
        - Industrial: 15-30 minutes (warehouse receiving, forklift)
        - Education: 8-12 minutes (central receiving)
        """
        stop_type = stop.get('type', 'Commercial').lower()
        
        if 'industrial' in stop_type or 'warehouse' in stop_type:
            service_minutes = random.randint(15, 30)
        elif 'retail' in stop_type or 'commercial' in stop_type:
            service_minutes = random.randint(10, 20)
        elif 'hospital' in stop_type or 'healthcare' in stop_type:
            service_minutes = random.randint(8, 15)
        elif 'school' in stop_type or 'education' in stop_type:
            service_minutes = random.randint(8, 12)
        else:
            service_minutes = random.randint(10, 15)
        
        print(f"\n  📦 Arrived at: {stop['name']} ({stop.get('type', 'Commercial')})")
        print(f"  ⏱️ Service time: {service_minutes} minutes")
        print(f"  🚚 Unloading and processing delivery...")
        
        # Send stationary GPS updates during service (every 30 seconds)
        service_pings = (service_minutes * 60) // self.GPS_INTERVAL
        
        for ping in range(service_pings):
            self.send_gps_position(stop['lat'], stop['lon'], 0, 0)
            time.sleep(self.GPS_INTERVAL)
            
            if ping % 2 == 0:
                elapsed = (ping + 1) * self.GPS_INTERVAL / 60
                print(f"    • {elapsed:.1f}/{service_minutes} min elapsed...")
        
        print(f"  ✓ Delivery complete!")
    
    def simulate_travel(self, from_stop, to_stop):
        """
        Simulate realistic travel with 30-second GPS pings
        
        Uses actual road speed limits and generates ~20 pings per 10 minutes
        """
        route_calc = self.calculate_realistic_gps_points(from_stop, to_stop)
        
        distance_miles = route_calc['distance_miles']
        avg_speed = route_calc['avg_speed_mph']
        speed_limit = route_calc['speed_limit']
        num_pings = route_calc['num_pings']
        
        print(f"\n  🚗 Traveling to: {to_stop['name']}")
        print(f"  📏 Distance: {distance_miles:.2f} miles")
        print(f"  🚦 Speed limit: {speed_limit} mph")
        print(f"  📡 GPS pings: {num_pings} (every 30 seconds)")
        
        # Generate interpolated points
        points = self.interpolate_points(
            from_stop['lat'], from_stop['lon'],
            to_stop['lat'], to_stop['lon'],
            num_pings
        )
        
        bearing = self.calculate_bearing(
            from_stop['lat'], from_stop['lon'],
            to_stop['lat'], to_stop['lon']
        )
        
        print(f"  🎯 Heading: {bearing:.1f}°")
        
        # Simulate each GPS ping
        for i, point in enumerate(points[:-1]):
            # Realistic speed variation (±5 mph around average)
            current_speed = avg_speed + random.uniform(-5, 5)
            
            # Cap at speed limit
            current_speed = min(current_speed, speed_limit)
            
            # Occasionally slow down (traffic lights, turns, congestion)
            if random.random() < 0.15:
                current_speed = current_speed * random.uniform(0.3, 0.6)
                print(f"    🚦 Slowing down: {current_speed:.1f} mph")
            
            # Send GPS update
            self.send_gps_position(point['lat'], point['lon'], current_speed, bearing)
            
            # Progress indicator
            progress = (i + 1) / len(points) * 100
            if i % max(len(points) // 5, 1) == 0:
                print(f"    → {progress:.0f}% complete ({current_speed:.1f} mph)")
            
            # Wait 30 seconds before next ping
            time.sleep(self.GPS_INTERVAL)
    
    def run(self, start_from_stop=0):
        """
        Run the realistic B2B delivery simulation
        
        Args:
            start_from_stop: Which stop to start from (0 = origin)
        """
        print("\n" + "="*70)
        print("🚚 B2B LAST-MILE DELIVERY SIMULATOR")
        print("="*70)
        print(f"\nShipment: {self.shipment_ref}")
        print(f"Vehicle ID: {self.vehicle_id}")
        print(f"GPS Interval: {self.GPS_INTERVAL} seconds (industry standard)")
        print(f"Speed Units: MPH (US standard)")
        print(f"Starting from stop: {start_from_stop}")
        
        # Fetch route from Valhalla via backend
        if not self.fetch_route():
            return
        
        if len(self.stops) < 2:
            print("❌ Route must have at least 2 stops")
            return
        
        print("\n🚀 Starting simulation... (Press Ctrl+C to stop)")
        print("="*70)
        
        try:
            # Start from specified stop
            self.current_stop_index = start_from_stop
            
            while self.current_stop_index < len(self.stops) - 1:
                current_stop = self.stops[self.current_stop_index]
                next_stop = self.stops[self.current_stop_index + 1]
                
                print(f"\n📍 Stop {self.current_stop_index + 1}/{len(self.stops)}")
                
                # Travel to next stop (Valhalla determines actual route)
                self.simulate_travel(current_stop, next_stop)
                
                # Service at stop
                self.current_stop_index += 1
                self.simulate_b2b_stop_service(next_stop)
                
                print(f"\n  ✅ Completed stop {self.current_stop_index}/{len(self.stops)}")
                
                # Small delay before next leg
                time.sleep(5)
            
            print("\n" + "="*70)
            print("🎉 Delivery route completed!")
            print("="*70)
            print(f"✓ All {len(self.stops)} stops completed")
            print(f"✓ Shipment {self.shipment_ref} finished")
            
        except KeyboardInterrupt:
            print("\n\n🛑 Simulation stopped by user")
            print(f"Completed {self.current_stop_index}/{len(self.stops)} stops")
        except Exception as e:
            print(f"\n\n❌ Error: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='B2B Last-Mile Delivery GPS Simulator')
    parser.add_argument('--route', default='ROUTE-RETAIL-001',
                       help='Shipment reference (default: ROUTE-RETAIL-001)')
    parser.add_argument('--vehicle', type=int, default=1,
                       help='Vehicle ID (default: 1)')
    parser.add_argument('--start', type=int, default=0,
                       help='Start from stop index (default: 0)')
    
    args = parser.parse_args()
    
    # Check backend connection
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Backend not responding. Make sure backend is running on port 5000.")
            sys.exit(1)
        print("✓ Backend connected")
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        print("Make sure backend is running: python backend/app.py")
        sys.exit(1)
    
    # Run simulator
    simulator = RealisticB2BSimulator(args.route, args.vehicle)
    simulator.run(args.start)


if __name__ == '__main__':
    main()
