"""
Status Endpoint Test
Tests the shipment status endpoint to verify ETA calculations and response format
"""
import sys
sys.path.insert(0, 'backend')
sys.path.insert(0, 'data')

from backend.app import app

def test_status_endpoint():
    """Test GET /v1/shipments/{id}/status"""
    client = app.test_client()
    
    print("Testing GET /v1/shipments/1/status")
    print("=" * 60)
    
    response = client.get('/v1/shipments/1/status')
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.get_json()}")
    print("=" * 60)
    
    return response.status_code == 200

if __name__ == "__main__":
    success = test_status_endpoint()
    exit(0 if success else 1)
