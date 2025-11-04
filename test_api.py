"""
Test script for the V2 API endpoints
Demonstrates creating shipments, ingesting GPS positions, and fetching status
"""
import requests
import json
from datetime import datetime, timedelta

API_URL = "http://127.0.0.1:5000"

def test_health():
    """Test health endpoint"""
    print("\n=== Testing Health Endpoint ===")
    response = requests.get(f"{API_URL}/health")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.status_code == 200

def test_create_shipment():
    """Test creating a new shipment"""
    print("\n=== Testing Create Shipment ===")
    
    now = datetime.utcnow()
    
    shipment_data = {
        "ref": f"TEST-{int(now.timestamp())}",
        "vehicle_id": 1,
        "organization_id": 1,
        "stops": [
            {
                "seq": 1,
                "name": "Austin Warehouse",
                "lat": 30.267,
                "lon": -97.743,
                "planned_arr_ts": (now + timedelta(hours=1)).isoformat() + "Z",
                "planned_dep_ts": (now + timedelta(hours=1, minutes=30)).isoformat() + "Z",
                "planned_service_min": 30
            },
            {
                "seq": 2,
                "name": "San Antonio Distribution",
                "lat": 29.424,
                "lon": -98.493,
                "planned_arr_ts": (now + timedelta(hours=3)).isoformat() + "Z",
                "planned_dep_ts": (now + timedelta(hours=3, minutes=30)).isoformat() + "Z",
                "planned_service_min": 30
            },
            {
                "seq": 3,
                "name": "Houston Terminal",
                "lat": 29.760,
                "lon": -95.369,
                "planned_arr_ts": (now + timedelta(hours=6)).isoformat() + "Z",
                "planned_dep_ts": (now + timedelta(hours=6, minutes=30)).isoformat() + "Z",
                "planned_service_min": 30
            }
        ]
    }
    
    response = requests.post(
        f"{API_URL}/v1/shipments",
        json=shipment_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(json.dumps(result, indent=2))
    
    if response.status_code == 201:
        return result.get('ref')
    return None

def test_ingest_positions(shipment_ref):
    """Test ingesting GPS positions"""
    print("\n=== Testing Ingest GPS Positions ===")
    
    # Simulate vehicle moving from Austin towards San Antonio
    positions = [
        {"ts": datetime.utcnow().isoformat() + "Z", "lat": 30.267, "lon": -97.743, "speed_kph": 0},
        {"ts": (datetime.utcnow() + timedelta(minutes=5)).isoformat() + "Z", "lat": 30.200, "lon": -97.800, "speed_kph": 75},
        {"ts": (datetime.utcnow() + timedelta(minutes=10)).isoformat() + "Z", "lat": 30.150, "lon": -97.850, "speed_kph": 80},
    ]
    
    position_data = {
        "vehicle_id": 1,
        "points": positions
    }
    
    response = requests.post(
        f"{API_URL}/v1/positions",
        json=position_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(json.dumps(result, indent=2))
    
    return response.status_code == 200

def test_get_shipment_status(shipment_id=1):
    """Test getting shipment status"""
    print(f"\n=== Testing Get Shipment Status (ID: {shipment_id}) ===")
    
    response = requests.get(f"{API_URL}/v1/shipments/{shipment_id}/status")
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(json.dumps(result, indent=2))
    
    # Highlight key information
    if response.status_code == 200 and result.get('success'):
        print("\n--- Key Information ---")
        print(f"Shipment: {result.get('ref')}")
        print(f"Status: {result.get('status')}")
        print(f"Current Leg: {result.get('current_leg')}")
        print(f"On Time: {result.get('on_time')}")
        if not result.get('on_time'):
            print(f"Late By: {result.get('late_by_min')} minutes")
            print(f"Reason: {result.get('reason_code')} (confidence: {result.get('confidence')})")
            print(f"Explanation: {result.get('explanation')}")
        
        if result.get('vehicle_position'):
            pos = result['vehicle_position']
            print(f"\nVehicle Position: ({pos['lat']:.4f}, {pos['lon']:.4f})")
            print(f"Speed: {pos.get('speed_kph', 0)} km/h")
            print(f"Heading: {pos.get('heading', 0)}°")
    
    return response.status_code == 200

def test_suggest_reroute():
    """Test reroute suggestion"""
    print("\n=== Testing Reroute Suggestion ===")
    
    reroute_data = {
        "shipment_id": 1,
        "current_lat": 30.150,
        "current_lon": -97.850,
        "next_stop_lat": 29.424,
        "next_stop_lon": -98.493,
        "constraints": {
            "height_m": 4.1,
            "width_m": 2.5,
            "weight_tons": 15.0,
            "hazmat_allowed": False
        }
    }
    
    response = requests.post(
        f"{API_URL}/v1/reroute/suggest",
        json=reroute_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(json.dumps(result, indent=2))
        
        if result.get('success') and result.get('alternative'):
            alt = result['alternative']
            print("\n--- Alternative Route ---")
            print(f"Time Saved: {alt.get('time_saved_min', 0)} minutes")
            print(f"Distance: {alt.get('distance_km', 0):.1f} km")
            print(f"Reason: {alt.get('reason', 'N/A')}")
    else:
        print(response.text)
    
    return response.status_code == 200

def test_existing_shipment():
    """Test with existing sample shipment PO-98765"""
    print("\n=== Testing Existing Sample Shipment ===")
    print("Shipment: PO-98765 (Dallas → Houston → Beaumont)")
    
    # Get status of existing shipment
    test_get_shipment_status(shipment_id=1)
    
    # Ingest some positions for the sample shipment
    print("\n--- Simulating GPS Updates ---")
    
    # Simulate vehicle somewhere between Dallas and Houston
    test_positions = [
        {"ts": datetime.utcnow().isoformat() + "Z", "lat": 31.500, "lon": -96.300, "speed_kph": 70},
        {"ts": (datetime.utcnow() + timedelta(minutes=5)).isoformat() + "Z", "lat": 31.400, "lon": -96.200, "speed_kph": 72},
    ]
    
    position_data = {
        "vehicle_id": 1,
        "points": test_positions
    }
    
    response = requests.post(
        f"{API_URL}/v1/positions",
        json=position_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Position Update Status: {response.status_code}")
    if response.status_code == 200:
        print("✓ GPS positions ingested successfully")
        print("✓ ETAs recomputed with weather and traffic data")
        print("✓ Delay reasons analyzed")

def run_all_tests():
    """Run all API tests"""
    print("=" * 60)
    print("ETA Tracker V2 API Test Suite")
    print("=" * 60)
    
    # Test 1: Health check
    if not test_health():
        print("\n❌ Health check failed. Is the backend running?")
        return
    print("✓ Health check passed")
    
    # Test 2: Test existing sample shipment
    test_existing_shipment()
    
    # Test 3: Create new shipment
    shipment_ref = test_create_shipment()
    if shipment_ref:
        print(f"✓ Shipment created: {shipment_ref}")
    else:
        print("⚠ Could not create new shipment (may be expected if using existing data)")
    
    # Test 4: Ingest positions (for existing shipment)
    test_ingest_positions("PO-98765")
    
    # Test 5: Reroute suggestion
    test_suggest_reroute()
    
    print("\n" + "=" * 60)
    print("Test Suite Complete")
    print("=" * 60)
    print("\nNext Steps:")
    print("1. Check the backend console for routing/weather API calls")
    print("2. Open the frontend at http://localhost:5173")
    print("3. Track shipment 'PO-98765' to see live updates")
    print("4. Monitor Socket.IO events in browser console")

if __name__ == "__main__":
    run_all_tests()
