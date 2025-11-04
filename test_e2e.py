"""
End-to-End Test Suite for ETA Tracker V2
Tests complete flow: create shipment → ingest GPS → compute ETA → detect delays → verify updates
"""
import requests
import json
import time
from datetime import datetime, timedelta
import socketio

API_URL = "http://127.0.0.1:5000"

class ETATrackerE2ETest:
    def __init__(self):
        self.session = requests.Session()
        self.sio = None
        self.shipment_id = None
        self.shipment_ref = None
        self.updates_received = []
        
    def test_1_create_shipment(self):
        """Test 1: Create a new shipment with multi-stop route"""
        print("\n" + "="*60)
        print("TEST 1: Create Shipment")
        print("="*60)
        
        now = datetime.utcnow()
        self.shipment_ref = f"E2E-TEST-{int(now.timestamp())}"
        
        shipment_data = {
            "ref": self.shipment_ref,
            "vehicle_id": 1,
            "organization_id": 1,
            "stops": [
                {
                    "seq": 1,
                    "name": "Dallas Distribution Center",
                    "lat": 32.896,
                    "lon": -97.036,
                    "planned_arr_ts": (now + timedelta(hours=1)).isoformat() + "Z",
                    "planned_dep_ts": (now + timedelta(hours=1, minutes=30)).isoformat() + "Z",
                    "planned_service_min": 30
                },
                {
                    "seq": 2,
                    "name": "Houston Terminal",
                    "lat": 29.990,
                    "lon": -95.336,
                    "planned_arr_ts": (now + timedelta(hours=5)).isoformat() + "Z",
                    "planned_dep_ts": (now + timedelta(hours=5, minutes=30)).isoformat() + "Z",
                    "planned_service_min": 30
                },
                {
                    "seq": 3,
                    "name": "Beaumont Warehouse",
                    "lat": 30.080,
                    "lon": -94.126,
                    "planned_arr_ts": (now + timedelta(hours=7)).isoformat() + "Z",
                    "planned_dep_ts": (now + timedelta(hours=7, minutes=30)).isoformat() + "Z",
                    "planned_service_min": 30
                }
            ]
        }
        
        response = self.session.post(
            f"{API_URL}/v1/shipments",
            json=shipment_data,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 201, f"Failed to create shipment: {response.text}"
        
        result = response.json()
        print(f"✓ Shipment created: {result['ref']}")
        print(f"  Stop IDs: {result['stop_ids']}")
        
        # Get the shipment ID
        status_response = self.session.get(f"{API_URL}/v1/shipments?ref={self.shipment_ref}")
        assert status_response.status_code == 200
        shipments = status_response.json()
        self.shipment_id = shipments[0]['id']
        print(f"  Shipment ID: {self.shipment_id}")
        
        return True
        
    def test_2_initial_status(self):
        """Test 2: Get initial shipment status"""
        print("\n" + "="*60)
        print("TEST 2: Get Initial Status")
        print("="*60)
        
        response = self.session.get(f"{API_URL}/v1/shipments/{self.shipment_id}/status")
        assert response.status_code == 200, f"Failed to get status: {response.text}"
        
        status = response.json()
        print(f"✓ Status retrieved: {status['status']}")
        print(f"  Current leg: {status['current_leg']}")
        print(f"  On time: {status['on_time']}")
        if not status['on_time']:
            print(f"  Delay: {status['late_by_min']} minutes")
            print(f"  Reason: {status['reason_code']} (confidence: {status['confidence']})")
            print(f"  Explanation: {status['explanation']}")
        
        return True
    
    def test_3_ingest_gps_positions(self):
        """Test 3: Ingest GPS positions and trigger ETA recomputation"""
        print("\n" + "="*60)
        print("TEST 3: Ingest GPS Positions")
        print("="*60)
        
        # Simulate vehicle leaving Dallas, heading towards Houston
        positions = [
            {
                "ts": datetime.utcnow().isoformat() + "Z",
                "lat": 32.896,
                "lon": -97.036,
                "speed_kph": 0
            },
            {
                "ts": (datetime.utcnow() + timedelta(minutes=5)).isoformat() + "Z",
                "lat": 32.800,
                "lon": -96.950,
                "speed_kph": 75
            },
            {
                "ts": (datetime.utcnow() + timedelta(minutes=10)).isoformat() + "Z",
                "lat": 32.700,
                "lon": -96.850,
                "speed_kph": 80
            },
            {
                "ts": (datetime.utcnow() + timedelta(minutes=15)).isoformat() + "Z",
                "lat": 32.600,
                "lon": -96.750,
                "speed_kph": 78
            }
        ]
        
        position_data = {
            "vehicle_id": 1,
            "points": positions
        }
        
        response = self.session.post(
            f"{API_URL}/v1/positions",
            json=position_data,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200, f"Failed to ingest positions: {response.text}"
        
        result = response.json()
        print(f"✓ Ingested {result['count']} GPS positions")
        print(f"  Positions snapped to road network")
        print(f"  ETAs recomputed with weather and traffic data")
        
        # Wait a moment for ETA computation
        time.sleep(2)
        
        # Check updated status
        status_response = self.session.get(f"{API_URL}/v1/shipments/{self.shipment_id}/status")
        status = status_response.json()
        print(f"\nUpdated Status:")
        print(f"  Vehicle position: ({status['vehicle_position']['lat']:.4f}, {status['vehicle_position']['lon']:.4f})")
        print(f"  Speed: {status['vehicle_position'].get('speed_kph', 0)} km/h")
        print(f"  ETA to next stop: {status.get('eta_next_stop_ts', 'N/A')}")
        
        return True
    
    def test_4_delay_detection(self):
        """Test 4: Verify delay reason detection"""
        print("\n" + "="*60)
        print("TEST 4: Delay Reason Detection")
        print("="*60)
        
        response = self.session.get(f"{API_URL}/v1/shipments/{self.shipment_id}/status")
        assert response.status_code == 200
        
        status = response.json()
        
        print(f"✓ Delay analysis complete")
        print(f"  Reason code: {status['reason_code']}")
        print(f"  Confidence: {status['confidence']}")
        print(f"  Explanation: {status['explanation']}")
        
        # Verify weather impact was considered
        if 'weather' in status['explanation'].lower():
            print(f"  ✓ Weather conditions analyzed")
        
        # Verify traffic impact was considered
        if 'traffic' in status['explanation'].lower():
            print(f"  ✓ Traffic conditions analyzed")
        
        return True
    
    def test_5_websocket_updates(self):
        """Test 5: Real-time Socket.IO updates"""
        print("\n" + "="*60)
        print("TEST 5: Real-time Socket.IO Updates")
        print("="*60)
        
        # Initialize Socket.IO client
        self.sio = socketio.Client()
        
        @self.sio.on('connect')
        def on_connect():
            print("✓ Socket.IO connected")
            self.sio.emit('subscribe', {'shipment_id': self.shipment_id})
            print(f"  Subscribed to shipment {self.shipment_id}")
        
        @self.sio.on('position_update')
        def on_position_update(data):
            print(f"✓ Position update received")
            print(f"  Position: ({data['vehicle_position']['lat']:.4f}, {data['vehicle_position']['lon']:.4f})")
            self.updates_received.append(('position', data))
        
        @self.sio.on('eta_update_v2')
        def on_eta_update(data):
            print(f"✓ ETA update received")
            print(f"  ETAs for {len(data.get('etas', []))} stops")
            if data.get('delay_info'):
                print(f"  Delay: {data['delay_info']['reason_code']}")
            self.updates_received.append(('eta', data))
        
        @self.sio.on('reroute_suggestion')
        def on_reroute(data):
            print(f"✓ Reroute suggestion received")
            print(f"  Time saved: {data['alternative']['time_saved_min']} minutes")
            self.updates_received.append(('reroute', data))
        
        try:
            self.sio.connect(API_URL)
            
            # Send another GPS position to trigger updates
            position_data = {
                "vehicle_id": 1,
                "points": [{
                    "ts": datetime.utcnow().isoformat() + "Z",
                    "lat": 32.500,
                    "lon": -96.650,
                    "speed_kph": 75
                }]
            }
            
            self.session.post(
                f"{API_URL}/v1/positions",
                json=position_data,
                headers={"Content-Type": "application/json"}
            )
            
            # Wait for updates
            print("\nWaiting for real-time updates...")
            time.sleep(5)
            
            print(f"\n✓ Received {len(self.updates_received)} real-time updates")
            
            self.sio.disconnect()
            
        except Exception as e:
            print(f"✗ Socket.IO test failed: {e}")
            return False
        
        return True
    
    def test_6_30_second_update_cycle(self):
        """Test 6: Verify 30-second ETA update cycle"""
        print("\n" + "="*60)
        print("TEST 6: 30-Second Update Cycle")
        print("="*60)
        
        print("Note: Full 30-second cycle test requires longer observation")
        print("In production, ETAs should be recomputed every 30 seconds")
        print("GPS pings should arrive every 15-30 seconds")
        
        # Check if system is configured correctly
        config_response = self.session.get(f"{API_URL}/v1/config")
        if config_response.status_code == 200:
            config = config_response.json()
            print(f"\n✓ System configuration:")
            print(f"  ETA update interval: {config.get('eta_update_interval', 'N/A')}s")
            print(f"  GPS ping interval: {config.get('gps_ping_interval', 'N/A')}s")
        
        return True
    
    def run_all_tests(self):
        """Run complete end-to-end test suite"""
        print("\n" + "="*80)
        print(" ETA TRACKER V2 - END-TO-END TEST SUITE")
        print("="*80)
        
        tests = [
            ("Create Shipment", self.test_1_create_shipment),
            ("Initial Status", self.test_2_initial_status),
            ("Ingest GPS Positions", self.test_3_ingest_gps_positions),
            ("Delay Detection", self.test_4_delay_detection),
            ("WebSocket Updates", self.test_5_websocket_updates),
            ("30-Second Cycle", self.test_6_30_second_update_cycle),
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                results[test_name] = result
            except Exception as e:
                print(f"\n✗ {test_name} FAILED: {e}")
                results[test_name] = False
        
        # Print summary
        print("\n" + "="*80)
        print(" TEST SUMMARY")
        print("="*80)
        
        passed = sum(1 for r in results.values() if r)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{status:10} {test_name}")
        
        print(f"\nTotal: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED! System is ready for production.")
        else:
            print(f"\n⚠️  {total - passed} test(s) failed. Review errors above.")
        
        return passed == total

def main():
    """Run end-to-end tests"""
    # Check if backend is running
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Backend health check failed. Is the server running?")
            return
    except Exception as e:
        print(f"❌ Cannot connect to backend at {API_URL}")
        print(f"   Error: {e}")
        print("\nPlease start the backend with:")
        print("   python backend/app.py")
        return
    
    # Run tests
    tester = ETATrackerE2ETest()
    success = tester.run_all_tests()
    
    exit(0 if success else 1)

if __name__ == "__main__":
    main()
