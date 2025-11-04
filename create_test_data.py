#!/usr/bin/env python3
"""
B2B Test Data Generator for ETA Tracker

Creates realistic B2B last-mile delivery scenarios in Beaumont, TX with:
- Commercial, industrial, and institutional delivery locations
- Sample shipments with various routes
- Test vehicles and organizations
- Realistic GPS simulation data for commercial delivery

Focus: B2B deliveries to warehouses, stores, hospitals, schools, and businesses.
No residential addresses - this is for commercial logistics testing.
"""

import os
import sys
import psycopg2
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# Beaumont, TX B2B delivery locations (commercial/industrial only)
BEAUMONT_B2B_LOCATIONS = [
    # Major Retail & Commercial
    {"name": "Parkdale Mall", "lat": 30.1087, "lon": -94.1557, "type": "Retail", "speed_limit_mph": 45},
    {"name": "Walmart Supercenter West", "lat": 30.1095, "lon": -94.1618, "type": "Retail", "speed_limit_mph": 45},
    {"name": "Home Depot Beaumont", "lat": 30.1089, "lon": -94.1513, "type": "Retail", "speed_limit_mph": 40},
    {"name": "Target Beaumont", "lat": 30.1123, "lon": -94.1548, "type": "Retail", "speed_limit_mph": 40},
    {"name": "Lowe's Home Improvement", "lat": 30.1073, "lon": -94.1624, "type": "Retail", "speed_limit_mph": 40},
    
    # Healthcare Facilities
    {"name": "CHRISTUS St. Elizabeth Hospital", "lat": 30.0556, "lon": -94.1289, "type": "Healthcare", "speed_limit_mph": 30},
    {"name": "Baptist Hospital Beaumont", "lat": 30.0863, "lon": -94.1015, "type": "Healthcare", "speed_limit_mph": 25},
    {"name": "Medical Center of Southeast Texas", "lat": 30.0583, "lon": -94.1372, "type": "Healthcare", "speed_limit_mph": 30},
    
    # Educational Institutions
    {"name": "Lamar University Campus", "lat": 30.0479, "lon": -94.0737, "type": "Education", "speed_limit_mph": 25},
    {"name": "Lamar University Library", "lat": 30.0513, "lon": -94.0719, "type": "Education", "speed_limit_mph": 20},
    
    # Industrial & Logistics
    {"name": "Port of Beaumont Industrial", "lat": 30.0756, "lon": -94.0422, "type": "Industrial", "speed_limit_mph": 35},
    {"name": "Beaumont Logistics Hub", "lat": 30.0912, "lon": -94.1632, "type": "Industrial", "speed_limit_mph": 40},
    {"name": "ExxonMobil Beaumont Refinery", "lat": 30.0634, "lon": -94.0289, "type": "Industrial", "speed_limit_mph": 35},
    {"name": "South Texas Industrial Park", "lat": 30.0389, "lon": -94.1178, "type": "Industrial", "speed_limit_mph": 45},
    
    # Public Facilities & Entertainment
    {"name": "Ford Park Entertainment Complex", "lat": 30.1264, "lon": -94.1459, "type": "Entertainment", "speed_limit_mph": 35},
    {"name": "Beaumont Civic Center", "lat": 30.0837, "lon": -94.1017, "type": "Public", "speed_limit_mph": 30},
    {"name": "Beaumont City Hall", "lat": 30.0805, "lon": -94.1266, "type": "Government", "speed_limit_mph": 25},
    
    # Restaurants & Hospitality
    {"name": "Golden Triangle Restaurant Supply", "lat": 30.0723, "lon": -94.1124, "type": "Food Service", "speed_limit_mph": 35},
    {"name": "Beaumont Hotel & Convention Center", "lat": 30.0842, "lon": -94.1054, "type": "Hospitality", "speed_limit_mph": 30},
]

# Beaumont Distribution Center (origin for all deliveries)
BEAUMONT_DC = {
    "name": "Beaumont Distribution Center", 
    "lat": 30.0826, 
    "lon": -94.1544,
    "type": "Warehouse",
    "speed_limit_mph": 45
}


def get_db_connection():
    """Get database connection"""
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        return psycopg2.connect(database_url)
    else:
        return psycopg2.connect(
            dbname=os.getenv('DB_NAME', 'postgres'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', ''),
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432')
        )


def create_organizations(conn):
    """Create sample organizations"""
    print("\n📋 Creating Organizations...")
    
    orgs = [
        ("ETA Logistics", "Primary logistics company"),
        ("FastTrack Delivery", "Express delivery service"),
        ("Local Freight", "Regional shipping company"),
    ]
    
    with conn.cursor() as cur:
        for name, description in orgs:
            cur.execute("""
                INSERT INTO organizations (name, api_key)
                VALUES (%s, %s)
                ON CONFLICT (name) DO NOTHING
                RETURNING id
            """, (name, f"test_key_{name.replace(' ', '_').lower()}"))
            result = cur.fetchone()
            if result:
                print(f"  ✓ Created: {name} (ID: {result[0]})")
    
    conn.commit()


def create_vehicles(conn):
    """Create sample delivery vehicles"""
    print("\n🚚 Creating Vehicles...")
    
    vehicles = [
        ("TX-TRUCK-001", "Ford F-150", 1),
        ("TX-TRUCK-002", "Chevy Silverado", 1),
        ("TX-TRUCK-003", "Ram 2500", 1),
        ("TX-VAN-001", "Mercedes Sprinter", 1),
        ("TX-VAN-002", "Ford Transit", 1),
    ]
    
    with conn.cursor() as cur:
        for plate, description, org_id in vehicles:
            cur.execute("""
                INSERT INTO vehicles (plate, description, org_id)
                VALUES (%s, %s, %s)
                ON CONFLICT (plate) DO NOTHING
                RETURNING id
            """, (plate, description, org_id))
            result = cur.fetchone()
            if result:
                print(f"  ✓ Created: {plate} - {description} (ID: {result[0]})")
    
    conn.commit()


def create_sample_routes(conn):
    """Create sample B2B last-mile delivery routes"""
    print("\n📍 Creating B2B Delivery Routes...")
    
    # Route 1: Retail Express (5 stops - major retail locations)
    route1_stops = [
        BEAUMONT_B2B_LOCATIONS[0],   # Parkdale Mall
        BEAUMONT_B2B_LOCATIONS[1],   # Walmart Supercenter
        BEAUMONT_B2B_LOCATIONS[2],   # Home Depot
        BEAUMONT_B2B_LOCATIONS[3],   # Target
        BEAUMONT_B2B_LOCATIONS[4],   # Lowe's
    ]
    
    # Route 2: Healthcare & Education (6 stops)
    route2_stops = [
        BEAUMONT_B2B_LOCATIONS[5],   # CHRISTUS Hospital
        BEAUMONT_B2B_LOCATIONS[6],   # Baptist Hospital
        BEAUMONT_B2B_LOCATIONS[7],   # Medical Center
        BEAUMONT_B2B_LOCATIONS[8],   # Lamar University Campus
        BEAUMONT_B2B_LOCATIONS[9],   # University Library
        BEAUMONT_B2B_LOCATIONS[16],  # City Hall
    ]
    
    # Route 3: Industrial & Logistics (7 stops)
    route3_stops = [
        BEAUMONT_B2B_LOCATIONS[10],  # Port of Beaumont
        BEAUMONT_B2B_LOCATIONS[11],  # Logistics Hub
        BEAUMONT_B2B_LOCATIONS[12],  # ExxonMobil Refinery
        BEAUMONT_B2B_LOCATIONS[13],  # Industrial Park
        BEAUMONT_B2B_LOCATIONS[17],  # Restaurant Supply
        BEAUMONT_B2B_LOCATIONS[18],  # Hotel & Convention
        BEAUMONT_B2B_LOCATIONS[15],  # Civic Center
    ]
    
    routes = [
        ("ROUTE-RETAIL-001", "Retail Express Route", route1_stops, 1),
        ("ROUTE-HEALTH-001", "Healthcare & Education Route", route2_stops, 2),
        ("ROUTE-IND-001", "Industrial & Logistics Route", route3_stops, 3),
    ]
    
    now = datetime.utcnow()
    
    with conn.cursor() as cur:
        for ref, description, stops, vehicle_id in routes:
            # Calculate promised ETA (last stop + 30 min buffer)
            total_stops = len(stops)
            estimated_time = now + timedelta(hours=2, minutes=15 * total_stops)
            
            # Create shipment
            cur.execute("""
                INSERT INTO shipments (ref, org_id, vehicle_id, promised_eta_ts, status)
                VALUES (%s, 1, %s, %s, 'pending')
                ON CONFLICT (ref) DO NOTHING
                RETURNING id
            """, (ref, vehicle_id, estimated_time))
            
            result = cur.fetchone()
            if not result:
                print(f"  ⚠ Skipped (already exists): {ref}")
                continue
                
            shipment_id = result[0]
            print(f"\n  ✓ Created Shipment: {ref} (ID: {shipment_id})")
            print(f"    Description: {description}")
            print(f"    Total Stops: {total_stops}")
            
            # Add origin stop (Beaumont DC)
            planned_start = now + timedelta(minutes=30)
            cur.execute("""
                INSERT INTO stops (
                    shipment_id, seq, name, lat, lon,
                    planned_arr_ts, planned_dep_ts, planned_service_min
                )
                VALUES (%s, 0, %s, %s, %s, %s, %s, 15)
                RETURNING id
            """, (
                shipment_id, BEAUMONT_DC["name"], BEAUMONT_DC["lat"], BEAUMONT_DC["lon"],
                planned_start, planned_start + timedelta(minutes=15)
            ))
            origin_id = cur.fetchone()[0]
            
            # Add delivery stops
            stop_ids = [origin_id]
            current_time = planned_start + timedelta(minutes=15)
            
            for seq, stop in enumerate(stops, start=1):
                # 10-15 min travel + 10 min service per stop
                current_time += timedelta(minutes=12)
                arrival_time = current_time
                departure_time = current_time + timedelta(minutes=10)
                
                cur.execute("""
                    INSERT INTO stops (
                        shipment_id, seq, name, lat, lon,
                        planned_arr_ts, planned_dep_ts, planned_service_min
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, 10)
                    RETURNING id
                """, (
                    shipment_id, seq, stop["name"], stop["lat"], stop["lon"],
                    arrival_time, departure_time
                ))
                stop_ids.append(cur.fetchone()[0])
                current_time = departure_time
                
                print(f"    • Stop {seq}: {stop['name']} ({stop['neighborhood']})")
            
            # Update origin and destination
            cur.execute("""
                UPDATE shipments
                SET origin_stop_id = %s, destination_stop_id = %s
                WHERE id = %s
            """, (stop_ids[0], stop_ids[-1], shipment_id))
    
    conn.commit()


def create_test_positions(conn):
    """Create initial test positions for vehicles at Beaumont DC"""
    print("\n📡 Creating Initial Vehicle Positions...")
    
    now = datetime.utcnow()
    
    with conn.cursor() as cur:
        # Get all vehicles
        cur.execute("SELECT id, plate FROM vehicles")
        vehicles = cur.fetchall()
        
        for vehicle_id, plate in vehicles:
            # Place all vehicles at Beaumont DC initially
            cur.execute("""
                INSERT INTO positions (
                    vehicle_id, ts, lat, lon, location, speed_kph, heading_deg, source
                )
                VALUES (
                    %s, %s, %s, %s,
                    ST_SetSRID(ST_MakePoint(%s, %s), 4326),
                    0, 0, 'test_data'
                )
            """, (
                vehicle_id, now, BEAUMONT_DC["lat"], BEAUMONT_DC["lon"],
                BEAUMONT_DC["lon"], BEAUMONT_DC["lat"]
            ))
            print(f"  ✓ Positioned: {plate} at Beaumont DC")
    
    conn.commit()


def display_summary(conn):
    """Display summary of created data"""
    print("\n" + "="*60)
    print("📊 DATA CREATION SUMMARY")
    print("="*60)
    
    with conn.cursor() as cur:
        # Organizations
        cur.execute("SELECT COUNT(*) FROM organizations")
        print(f"\n✓ Organizations: {cur.fetchone()[0]}")
        
        # Vehicles
        cur.execute("SELECT COUNT(*) FROM vehicles")
        print(f"✓ Vehicles: {cur.fetchone()[0]}")
        
        # Shipments
        cur.execute("SELECT COUNT(*) FROM shipments")
        print(f"✓ Shipments: {cur.fetchone()[0]}")
        
        # Stops
        cur.execute("SELECT COUNT(*) FROM stops")
        print(f"✓ Stops: {cur.fetchone()[0]}")
        
        # Positions
        cur.execute("SELECT COUNT(*) FROM positions")
        print(f"✓ GPS Positions: {cur.fetchone()[0]}")
    
    print("\n" + "="*60)
    print("✅ Test data creation completed successfully!")
    print("="*60)
    
    print("\n📋 Available Test Routes:")
    print("  1. ROUTE-DW-001  - Downtown + West End (5 stops)")
    print("  2. ROUTE-RES-001 - Residential Delivery (8 stops)")
    print("  3. ROUTE-NS-001  - North-South Corridor (6 stops)")
    print("  4. ROUTE-FULL-001 - Full City Coverage (10 stops)")
    
    print("\n🚀 Next Steps:")
    print("  • Use simulate_last_mile.py to simulate deliveries")
    print("  • Test rerouting scenarios with traffic")
    print("  • Monitor real-time ETAs and optimizations")


def main():
    """Main data creation function"""
    print("="*60)
    print("🎯 ETA TRACKER - B2B TEST DATA GENERATOR")
    print("="*60)
    print("\nCreating realistic B2B last-mile delivery test data...")
    print("Location: Beaumont, TX")
    print(f"Total B2B Delivery Locations: {len(BEAUMONT_B2B_LOCATIONS)}")
    
    try:
        conn = get_db_connection()
        print("\n✓ Connected to database")
        
        # Create data in order
        create_organizations(conn)
        create_vehicles(conn)
        create_sample_routes(conn)
        create_test_positions(conn)
        
        # Display summary
        display_summary(conn)
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
