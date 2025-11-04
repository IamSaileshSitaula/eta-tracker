"""
Valhalla Integration Tests
Tests for Valhalla routing engine integration

Run with: python test_valhalla_integration.py
"""
import unittest
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.valhalla_client import get_router, VehicleConstraints, ValhallaRouter


class TestValhallaIntegration(unittest.TestCase):
    """Test Valhalla routing integration"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        # Test with Valhalla if available, otherwise OSRM
        valhalla_url = os.getenv('VALHALLA_URL', None)
        cls.router = get_router(valhalla_url=valhalla_url)
        
        # Test waypoints in Beaumont, TX
        cls.waypoints_short = [
            (30.08, -94.126),   # Beaumont DC
            (30.063, -94.134)   # Target
        ]
        
        cls.waypoints_multi = [
            (30.08, -94.126),    # Beaumont DC
            (30.063, -94.134),   # Target
            (30.086, -94.101),   # Hospital
            (30.053, -94.165)    # West End Plaza
        ]
    
    def test_basic_routing(self):
        """Test basic route calculation"""
        result = self.router.route(self.waypoints_short)
        
        self.assertTrue(result['success'], f"Routing failed: {result.get('error')}")
        self.assertIn('source', result)
        self.assertIn(result['source'], ['valhalla', 'osrm'])
        self.assertGreater(result['distance_km'], 0, "Distance should be positive")
        self.assertGreater(result['duration_min'], 0, "Duration should be positive")
        self.assertIn('geometry', result)
        self.assertIn('instructions', result)
        
        print(f"✓ Basic routing works ({result['source']})")
        print(f"  Distance: {result['distance_km']:.2f} km")
        print(f"  Duration: {result['duration_min']:.1f} min")
    
    def test_truck_constraints(self):
        """Test routing with truck constraints"""
        constraints = VehicleConstraints(
            height_m=4.1,
            width_m=2.5,
            weight_tons=15.0,
            hazmat_allowed=False,
            avoid_tolls=False
        )
        
        result = self.router.route(self.waypoints_short, constraints, costing="truck")
        
        self.assertTrue(result['success'], "Routing with constraints failed")
        self.assertEqual(result['costing'], 'truck')
        
        print(f"✓ Truck constraints routing works")
        print(f"  Height: {constraints.height_m}m, Width: {constraints.width_m}m")
        print(f"  Weight: {constraints.weight_tons}t")
    
    def test_avoid_tolls(self):
        """Test toll avoidance"""
        # Route without toll avoidance
        constraints_with_tolls = VehicleConstraints(avoid_tolls=False)
        result1 = self.router.route(self.waypoints_short, constraints_with_tolls)
        
        # Route with toll avoidance
        constraints_no_tolls = VehicleConstraints(avoid_tolls=True)
        result2 = self.router.route(self.waypoints_short, constraints_no_tolls)
        
        self.assertTrue(result1['success'], "Routing with tolls failed")
        self.assertTrue(result2['success'], "Routing without tolls failed")
        
        # Note: Time/distance may be same if no tolls on this route
        print(f"✓ Toll avoidance routing works")
        print(f"  With tolls: {result1['duration_min']:.1f} min")
        print(f"  Without tolls: {result2['duration_min']:.1f} min")
    
    def test_multi_stop_routing(self):
        """Test routing with multiple stops"""
        result = self.router.route(self.waypoints_multi)
        
        self.assertTrue(result['success'], "Multi-stop routing failed")
        self.assertGreater(result['distance_km'], 0)
        self.assertGreater(len(result.get('instructions', [])), 0)
        
        print(f"✓ Multi-stop routing works")
        print(f"  Stops: {len(self.waypoints_multi)}")
        print(f"  Total distance: {result['distance_km']:.2f} km")
        print(f"  Total duration: {result['duration_min']:.1f} min")
    
    def test_alternative_routes(self):
        """Test alternative route calculation"""
        if not self.router.valhalla_url:
            print("⚠ Skipping alternative routes test (Valhalla not available)")
            return
        
        alternatives = self.router.calculate_alternatives(
            self.waypoints_short,
            num_alternatives=3
        )
        
        self.assertGreater(len(alternatives), 0, "Should return at least one route")
        self.assertLessEqual(len(alternatives), 3, "Should not exceed requested alternatives")
        
        print(f"✓ Alternative routes work")
        print(f"  Found {len(alternatives)} alternatives:")
        for alt in alternatives:
            print(f"    {alt['name']}: {alt['duration_min']:.1f} min, {alt['distance_km']:.1f} km")
            print(f"      Reason: {alt['reason']}")
    
    def test_snap_to_road(self):
        """Test GPS point snapping to road network"""
        # Point slightly off road
        lat, lon = 30.08, -94.126
        
        snapped_lat, snapped_lon = self.router.snap_to_road(lat, lon)
        
        self.assertIsInstance(snapped_lat, float)
        self.assertIsInstance(snapped_lon, float)
        
        # Snapped point should be close to original (within ~100m)
        distance = abs(snapped_lat - lat) + abs(snapped_lon - lon)
        self.assertLess(distance, 0.01, "Snapped point too far from original")
        
        print(f"✓ Snap-to-road works")
        print(f"  Original: ({lat:.6f}, {lon:.6f})")
        print(f"  Snapped: ({snapped_lat:.6f}, {snapped_lon:.6f})")
    
    def test_eta_with_traffic(self):
        """Test ETA calculation with traffic multipliers"""
        constraints = VehicleConstraints()
        
        # Normal conditions
        result1 = self.router.calculate_eta_with_traffic(
            self.waypoints_short,
            constraints,
            traffic_multiplier=1.0,
            weather_multiplier=1.0
        )
        
        # Heavy traffic
        result2 = self.router.calculate_eta_with_traffic(
            self.waypoints_short,
            constraints,
            traffic_multiplier=0.4,  # 40% of normal speed
            weather_multiplier=1.0
        )
        
        self.assertTrue(result1['success'], "ETA calculation failed")
        self.assertTrue(result2['success'], "ETA with traffic failed")
        self.assertGreater(
            result2['duration_min'],
            result1['duration_min'],
            "Traffic should increase duration"
        )
        
        print(f"✓ ETA with traffic works")
        print(f"  Normal: {result1['duration_min']:.1f} min")
        print(f"  Heavy traffic: {result2['duration_min']:.1f} min")
        print(f"  Delay: {result2['duration_min'] - result1['duration_min']:.1f} min")
    
    def test_valhalla_availability(self):
        """Test Valhalla server availability"""
        if self.router.valhalla_url:
            print(f"✓ Valhalla is available at {self.router.valhalla_url}")
        else:
            print(f"⚠ Valhalla not configured, using OSRM fallback")
            print(f"  To enable Valhalla:")
            print(f"    1. Run: start_valhalla.bat")
            print(f"    2. Set: VALHALLA_URL=http://localhost:8002")
            print(f"    3. Restart backend")


class TestRouterPerformance(unittest.TestCase):
    """Performance tests for routing engine"""
    
    @classmethod
    def setUpClass(cls):
        valhalla_url = os.getenv('VALHALLA_URL', None)
        cls.router = get_router(valhalla_url=valhalla_url)
        cls.waypoints = [(30.08, -94.126), (30.063, -94.134)]
    
    def test_response_time(self):
        """Test routing response time"""
        import time
        
        start = time.time()
        result = self.router.route(self.waypoints)
        elapsed = time.time() - start
        
        self.assertTrue(result['success'])
        self.assertLess(elapsed, 2.0, "Routing should complete within 2 seconds")
        
        print(f"✓ Response time: {elapsed:.3f} seconds")
    
    def test_concurrent_requests(self):
        """Test handling multiple concurrent requests"""
        import concurrent.futures
        
        def make_request():
            return self.router.route(self.waypoints)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        successful = sum(1 for r in results if r['success'])
        self.assertEqual(successful, 10, "All concurrent requests should succeed")
        
        print(f"✓ Concurrent requests: {successful}/10 successful")


def run_tests():
    """Run all tests with detailed output"""
    print("\n" + "=" * 70)
    print("VALHALLA INTEGRATION TESTS")
    print("=" * 70)
    print()
    
    # Check environment
    valhalla_url = os.getenv('VALHALLA_URL', None)
    if valhalla_url:
        print(f"Testing with: Valhalla at {valhalla_url}")
    else:
        print(f"Testing with: OSRM (fallback)")
        print(f"Note: Some tests will be skipped without Valhalla")
    print()
    
    # Run tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestValhallaIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestRouterPerformance))
    
    # Run with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("✓ ALL TESTS PASSED")
    else:
        print("✗ SOME TESTS FAILED")
    print("=" * 70)
    print()
    
    return result.wasSuccessful()


if __name__ == '__main__':
    import sys
    success = run_tests()
    sys.exit(0 if success else 1)
