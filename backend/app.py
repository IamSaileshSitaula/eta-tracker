"""
Live ETA & Delay Explanation System - Backend API v1.0
FastAPI implementation of the MVP specification
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask.json.provider import DefaultJSONProvider
from dotenv import load_dotenv
import sys
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from decimal import Decimal
import math
import threading
import time

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.db import Database
from backend.valhalla_client import get_router, VehicleConstraints
from backend.weather_api import get_weather_api
from backend.traffic_client import get_traffic_api

# Custom JSON provider to handle Decimal types
class DecimalJSONProvider(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

app = Flask(__name__)
app.json = DecimalJSONProvider(app)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global state
db = Database()

# Initialize router with Valhalla URL if available
valhalla_url = os.getenv('VALHALLA_URL', None)
osrm_url = os.getenv('OSRM_URL', 'https://router.project-osrm.org')
router = get_router(valhalla_url=valhalla_url, osrm_url=osrm_url)

weather_api = get_weather_api()
traffic_api = get_traffic_api()
active_simulations = {}  # shipment_id -> simulation_thread

# ==================== Delay Reason Codes ====================
REASON_CODES = {
    'ON_TIME': 'on_time',
    'TRAFFIC_CONGESTION': 'traffic_congestion',
    'WEATHER_IMPACT': 'weather_impact',
    'FACILITY_DWELL': 'facility_dwell',
    'VEHICLE_ISSUE': 'vehicle_issue',
    'DRIVER_HOS_RISK': 'driver_hos_risk',
    'ROAD_INCIDENT': 'road_incident'
}

# ==================== Helper Functions ====================

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points in kilometers using Haversine formula"""
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c

def calculate_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate bearing between two points in degrees"""
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlon = math.radians(lon2 - lon1)
    
    y = math.sin(dlon) * math.cos(lat2_rad)
    x = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon)
    bearing = math.degrees(math.atan2(y, x))
    
    return (bearing + 360) % 360

def interpolate_position(start: Dict, end: Dict, progress: float) -> Tuple[float, float]:
    """Interpolate position between two points"""
    lat = start['lat'] + (end['lat'] - start['lat']) * progress
    lon = start['lon'] + (end['lon'] - start['lon']) * progress
    return lat, lon

def compute_eta_with_routing(current_pos: Dict, stops: List[Dict], 
                             vehicle_constraints: VehicleConstraints = None) -> List[Dict]:
    """
    ETA computation with Valhalla routing and weather/traffic multipliers
    
    Formula from spec: ETA = Σ(edge_length / effective_speed) + service_time + dwell_time
    where effective_speed = min(live_speed, historical_speed × weather_multiplier)
    """
    if vehicle_constraints is None:
        vehicle_constraints = VehicleConstraints()
    
    etas = []
    current_lat = current_pos['lat']
    current_lon = current_pos['lon']
    cumulative_time = 0
    
    for stop in stops:
        if stop.get('completed'):
            etas.append({
                'stop_id': stop['id'],
                'eta_ts': stop.get('actual_arr_ts'),
                'on_time': True,
                'late_by_min': 0,
                'reason_code': REASON_CODES['ON_TIME'],
                'confidence': 1.0,
                'distance_km': 0
            })
            continue
        
        # Build waypoints for this leg
        waypoints = [(current_lat, current_lon), (stop['lat'], stop['lon'])]
        
        # Get weather along route
        weather_samples = weather_api.get_weather_along_route(waypoints, num_samples=3)
        weather_multiplier, weather_reason = weather_api.get_worst_weather_condition(weather_samples)
        
        # Get traffic data along route
        traffic_data = traffic_api.get_traffic_on_route(waypoints)
        traffic_multiplier, traffic_reason = traffic_api.calculate_traffic_multiplier(traffic_data)
        
        # Calculate route with weather/traffic
        route_result = router.calculate_eta_with_traffic(
            waypoints=waypoints,
            constraints=vehicle_constraints,
            traffic_multiplier=traffic_multiplier,
            weather_multiplier=weather_multiplier
        )
        
        if not route_result.get('success'):
            # Fallback to simple calculation
            distance_km = calculate_distance(current_lat, current_lon, stop['lat'], stop['lon'])
            travel_time_min = (distance_km / 70.0) * 60
        else:
            distance_km = route_result['distance_km']
            travel_time_min = route_result['duration_min']
        
        # Add service time
        service_time_min = stop.get('planned_service_min', 0)
        total_time_min = cumulative_time + travel_time_min + service_time_min
        
        # Calculate ETA
        eta_ts = datetime.utcnow() + timedelta(minutes=total_time_min)
        
        # Determine if on time
        planned_arr = stop.get('planned_arr_ts')
        on_time = True
        late_by_min = 0
        
        if planned_arr:
            if isinstance(planned_arr, str):
                planned_arr = datetime.fromisoformat(planned_arr.replace('Z', '+00:00'))
            if eta_ts > planned_arr:
                on_time = False
                late_by_min = int((eta_ts - planned_arr).total_seconds() / 60)
        
        etas.append({
            'stop_id': stop['id'],
            'eta_ts': eta_ts,
            'on_time': on_time,
            'late_by_min': late_by_min,
            'reason_code': REASON_CODES['ON_TIME'],
            'confidence': 0.9,
            'distance_km': distance_km,
            'weather_impact': weather_reason if weather_multiplier < 1.0 else None
        })
        
        # Update position for next stop
        current_lat = stop['lat']
        current_lon = stop['lon']
        cumulative_time = total_time_min
    
    return etas

def score_delay_reason(shipment: Dict, stops: List[Dict], 
                       current_pos: Dict, late_by_min: int,
                       weather_impact: str = None,
                       traffic_data: Dict = None) -> Tuple[str, float, str]:
    """
    Score delay reasons using weather data, traffic data, and dwell tracking
    Returns: (reason_code, confidence, explanation)
    
    Delay categories from spec:
    - TRAFFIC_CONGESTION: live_speed / freeflow < 0.4 for ≥5 min
    - WEATHER_IMPACT: precipitation > 10 mm/h or wind > 40 km/h on next 30km
    - FACILITY_DWELL: actual_dwell > planned_service + 20%
    - VEHICLE_ISSUE: reported via manual event
    - DRIVER_HOS_RISK: approaching 11-hour drive limit
    - ROAD_INCIDENT: detected via traffic API
    """
    if late_by_min <= 5:
        return (REASON_CODES['ON_TIME'], 1.0, "On schedule")
    
    scores = {}
    
    # Check traffic congestion (per spec: speed_ratio < 0.4)
    if traffic_data and traffic_api.is_congested(traffic_data):
        speed_ratio = traffic_data.get('speed_ratio', 1.0)
        congestion_level = traffic_data.get('congestion_level', 'unknown')
        scores[REASON_CODES['TRAFFIC_CONGESTION']] = 0.90
        
    # Check for moderate traffic
    elif traffic_data and traffic_data.get('congestion_level') in ['moderate', 'heavy']:
        scores[REASON_CODES['TRAFFIC_CONGESTION']] = 0.75
    
    # Check weather impact
    if weather_impact and "rain" in weather_impact.lower():
        precip_match = __import__('re').search(r'(\d+\.?\d*)\s*mm/h', weather_impact)
        if precip_match:
            precip = float(precip_match.group(1))
            if precip > 10:
                scores[REASON_CODES['WEATHER_IMPACT']] = 0.85
            elif precip > 5:
                scores[REASON_CODES['WEATHER_IMPACT']] = 0.65
    
    if weather_impact and "wind" in weather_impact.lower():
        wind_match = __import__('re').search(r'(\d+\.?\d*)\s*km/h', weather_impact)
        if wind_match:
            wind = float(wind_match.group(1))
            if wind > 40:
                scores[REASON_CODES['WEATHER_IMPACT']] = 0.80
    
    # Check facility dwell (look for completed stops with extended dwell)
    for stop in stops:
        if stop.get('completed') and stop.get('actual_arr_ts') and stop.get('actual_dep_ts'):
            arr = stop['actual_arr_ts']
            dep = stop['actual_dep_ts']
            if isinstance(arr, str):
                arr = datetime.fromisoformat(arr.replace('Z', '+00:00'))
            if isinstance(dep, str):
                dep = datetime.fromisoformat(dep.replace('Z', '+00:00'))
            
            actual_dwell_min = (dep - arr).total_seconds() / 60
            planned_service = stop.get('planned_service_min', 30)
            
            # Dwell threshold: planned + 20%
            if actual_dwell_min > planned_service * 1.2:
                excess_dwell = actual_dwell_min - planned_service
                scores[REASON_CODES['FACILITY_DWELL']] = min(0.90, 0.60 + (excess_dwell / 60))
    
    # Traffic congestion heuristic (will be enhanced with real traffic API)
    # If no specific cause identified and delay > 15 min, likely traffic
    if late_by_min > 30 and not scores:
        scores[REASON_CODES['TRAFFIC_CONGESTION']] = 0.70
    elif late_by_min > 15 and not scores:
        scores[REASON_CODES['TRAFFIC_CONGESTION']] = 0.60
    
    # Select highest scoring reason
    if not scores:
        return (REASON_CODES['TRAFFIC_CONGESTION'], 0.50, 
                f"Moderate delays of {late_by_min} minutes, likely due to traffic conditions.")
    
    reason_code = max(scores, key=scores.get)
    confidence = scores[reason_code]
    
    # Generate explanation
    if reason_code == REASON_CODES['TRAFFIC_CONGESTION']:
        if traffic_data:
            congestion = traffic_data.get('congestion_level', 'moderate')
            speed_ratio = traffic_data.get('speed_ratio', 0.7)
            explanation = f"{congestion.capitalize()} traffic congestion (speeds at {int(speed_ratio * 100)}% of normal) causing {late_by_min} minutes of delay."
        else:
            explanation = f"Traffic congestion is causing approximately {late_by_min} minutes of delay."
    elif reason_code == REASON_CODES['WEATHER_IMPACT']:
        explanation = f"Weather conditions ({weather_impact}) are causing approximately {late_by_min} minutes of delay."
    elif reason_code == REASON_CODES['FACILITY_DWELL']:
        explanation = f"Extended dwell time at previous stop is adding {late_by_min} minutes to the schedule."
    else:
        explanation = f"Delay of {late_by_min} minutes detected, investigating cause."
    
    return (reason_code, confidence, explanation)

# ==================== API Endpoints ====================

@app.route('/v1/shipments', methods=['GET', 'POST'])
def shipments():
    """
    GET /v1/shipments?ref=<tracking_number>
    Get shipment(s) by reference
    
    POST /v1/shipments
    Create a new shipment with stops
    """
    if request.method == 'GET':
        # Get shipment by reference
        ref = request.args.get('ref')
        if not ref:
            return jsonify({'success': False, 'error': 'ref parameter required'}), 400
        
        try:
            # Rollback any existing transaction to ensure clean state
            db.conn.rollback()
            
            # Query database for shipment by reference
            with db.conn.cursor() as cur:
                cur.execute("""
                    SELECT id, ref, vehicle_id, org_id, status, 
                           created_at::text, updated_at::text
                    FROM shipments
                    WHERE ref = %s
                    ORDER BY created_at DESC
                """, (ref,))
                
                rows = cur.fetchall()
                
                # Commit the read transaction
                db.conn.commit()
                
                if not rows:
                    return jsonify([]), 200
                
                # Convert rows to dictionaries
                shipments = []
                for row in rows:
                    shipments.append({
                        'id': row[0],
                        'ref': row[1],
                        'vehicle_id': row[2],
                        'organization_id': row[3],  # Frontend expects organization_id
                        'status': row[4],
                        'created_at': row[5],
                        'updated_at': row[6]
                    })
                
                return jsonify(shipments), 200
                
        except Exception as e:
            db.conn.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # POST - Create shipment
    # Body: {
    #   "ref": "PO-98765",
    #   "vehicle_id": 1,
    #   "stops": [...],
    #   "promised_eta_ts": "2025-10-30T18:00:00Z"
    # }
    try:
        data = request.json
        
        result = db.create_shipment(
            ref=data['ref'],
            vehicle_id=data['vehicle_id'],
            stops=data['stops'],
            promised_eta_ts=data['promised_eta_ts']
        )
        
        # Log event
        db.log_event(result['shipment_id'], 'shipment_created', {
            'ref': data['ref'],
            'stops_count': len(data['stops'])
        })
        
        return jsonify({
            'success': True,
            'shipment_id': result['shipment_id'],
            'ref': result['ref'],
            'stop_ids': result['stop_ids']
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/v1/positions', methods=['POST'])
def ingest_positions():
    """
    POST /v1/positions
    Ingest GPS positions (batch)
    
    Body: {
        "vehicle_id": 1,
        "points": [
            {"ts": "2025-10-27T18:01:02Z", "lat": 30.05, "lon": -94.2, "speed_kph": 64}
        ]
    }
    """
    try:
        data = request.json
        vehicle_id = data['vehicle_id']
        points = data['points']
        
        # Snap GPS points to road network for accuracy
        snapped_points = []
        for point in points:
            snapped_lat, snapped_lon = router.snap_to_road(point['lat'], point['lon'])
            snapped_points.append({
                'ts': point['ts'],
                'lat': snapped_lat,
                'lon': snapped_lon,
                'speed_kph': point.get('speed_kph', 0)
            })
        
        # Insert snapped positions
        count = db.insert_positions(vehicle_id, snapped_points)
        
        # Trigger ETA recompute for active shipments with this vehicle
        shipment = db.get_shipment_by_ref('PO-98765')  # TODO: Get actual active shipment
        if shipment and shipment['vehicle_id'] == vehicle_id:
            # Get latest position
            latest_pos = db.get_latest_position(vehicle_id)
            
            # Get stops
            stops = db.get_shipment_stops(shipment['id'])
            
            # Get vehicle constraints (use defaults for now)
            constraints = VehicleConstraints()
            
            # Compute ETAs with routing and weather
            etas = compute_eta_with_routing(latest_pos, stops, constraints)
            
            # Get traffic data for delay scoring (sample from current position to next stop)
            next_incomplete_stop = next((s for s in stops if not s.get('completed')), None)
            traffic_data = None
            if next_incomplete_stop:
                waypoints = [(latest_pos['lat'], latest_pos['lon']), 
                           (next_incomplete_stop['lat'], next_incomplete_stop['lon'])]
                traffic_data = traffic_api.get_traffic_on_route(waypoints)
            
            # Store ETAs and emit updates
            for eta in etas:
                if not eta.get('eta_ts'):
                    continue
                    
                # Determine delay reason with weather and traffic impact
                weather_impact = eta.get('weather_impact')
                reason_code, confidence, explanation = score_delay_reason(
                    shipment, stops, latest_pos, eta['late_by_min'], 
                    weather_impact, traffic_data
                )
                
                # Insert ETA
                db.insert_eta(
                    shipment['id'],
                    eta['stop_id'],
                    eta['eta_ts'],
                    eta['on_time'],
                    eta['late_by_min'],
                    reason_code,
                    confidence,
                    explanation
                )
            
            # Emit real-time update via Socket.IO
            socketio.emit('position_update', {
                'shipment_id': shipment['id'],
                'vehicle_position': {
                    'lat': float(latest_pos['lat']),
                    'lon': float(latest_pos['lon']),
                    'speed_kph': float(latest_pos['speed_kph']) if latest_pos.get('speed_kph') is not None else 0,
                    'heading_deg': float(latest_pos['heading_deg']) if latest_pos.get('heading_deg') is not None else 0
                },
                'timestamp': latest_pos['ts'].isoformat()
            }, room=f"shipment_{shipment['id']}")
        
        return jsonify({
            'success': True,
            'positions_inserted': count
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/v1/shipments/<int:shipment_id>/status', methods=['GET'])
def get_shipment_status(shipment_id):
    """
    GET /v1/shipments/{id}/status
    Get current shipment status with ETA and delay reason
    """
    try:
        # Rollback any existing transaction
        db.conn.rollback()
        
        # Get shipment
        shipment = db.get_shipment(shipment_id)
        if not shipment:
            return jsonify({'success': False, 'error': 'Shipment not found'}), 404
        
        # Get stops
        stops = db.get_shipment_stops(shipment_id)
        if not stops:
            return jsonify({'success': False, 'error': 'No stops found'}), 404
        
        # Find current leg (first uncompleted stop)
        current_stop_idx = 0
        for i, stop in enumerate(stops):
            if not stop.get('completed'):
                current_stop_idx = i
                break
        
        current_stop = stops[current_stop_idx]
        prev_stop = stops[current_stop_idx - 1] if current_stop_idx > 0 else None
        
        # Get latest ETA for current stop
        eta = db.get_latest_eta(shipment_id, current_stop['id'])
        
        # Get current vehicle position
        vehicle_pos = db.get_latest_position(shipment['vehicle_id'])
        
        # Calculate simple ETA if no ETA data exists
        if not eta and vehicle_pos:
            # Simple distance-based ETA calculation (assuming 80 km/h average speed)
            import math
            def haversine_distance(lat1, lon1, lat2, lon2):
                R = 6371  # Earth radius in km
                dlat = math.radians(float(lat2) - float(lat1))
                dlon = math.radians(float(lon2) - float(lon1))
                a = math.sin(dlat/2)**2 + math.cos(math.radians(float(lat1))) * math.cos(math.radians(float(lat2))) * math.sin(dlon/2)**2
                c = 2 * math.asin(math.sqrt(a))
                return R * c
            
            distance_km = haversine_distance(
                vehicle_pos['lat'], vehicle_pos['lon'],
                current_stop['lat'], current_stop['lon']
            )
            avg_speed_kph = 80
            eta_hours = distance_km / avg_speed_kph
            eta_ts = datetime.utcnow() + timedelta(hours=eta_hours)
            
            eta = {
                'eta_ts': eta_ts,
                'on_time_bool': True,
                'late_by_min': 0,
                'reason_code': 'ON_TIME',
                'confidence': 0.8,
                'explanation': f'En route - approximately {distance_km:.1f} km away'
            }
        
        # Determine current leg
        if prev_stop:
            current_leg = f"{prev_stop['name']} → {current_stop['name']}"
        else:
            current_leg = f"Origin → {current_stop['name']}"
        
        # Prepare response
        response = {
            'success': True,
            'shipment_id': shipment_id,
            'ref': shipment['ref'],
            'status': shipment['status'],
            'current_leg': current_leg,
            'vehicle_position': {
                'lat': float(vehicle_pos['lat']) if vehicle_pos and vehicle_pos.get('lat') is not None else None,
                'lon': float(vehicle_pos['lon']) if vehicle_pos and vehicle_pos.get('lon') is not None else None,
                'speed_kph': float(vehicle_pos['speed_kph']) if vehicle_pos and vehicle_pos.get('speed_kph') is not None else 0,
                'timestamp': vehicle_pos['ts'].isoformat() if vehicle_pos and vehicle_pos.get('ts') else None
            } if vehicle_pos else None,
            'next_stop': {
                'name': current_stop['name'],
                'lat': float(current_stop['lat']) if current_stop.get('lat') is not None else None,
                'lon': float(current_stop['lon']) if current_stop.get('lon') is not None else None,
                'seq': current_stop['seq']
            },
            'eta_next_stop_ts': eta['eta_ts'].isoformat() if eta else None,
            'on_time': eta['on_time_bool'] if eta else True,
            'late_by_min': eta['late_by_min'] if eta else 0,
            'reason_code': eta['reason_code'] if eta else REASON_CODES['ON_TIME'],
            'confidence': float(eta['confidence']) if eta and eta.get('confidence') is not None else 1.0,
            'explanation': eta['explanation'] if eta else "On schedule",
            'stops': []
        }
        
        # Add stops with calculated ETAs
        if vehicle_pos:
            import math as m  # Import at function level to avoid scope issues
            def haversine_distance(lat1, lon1, lat2, lon2):
                R = 6371  # Earth radius in km
                dlat = m.radians(float(lat2) - float(lat1))
                dlon = m.radians(float(lon2) - float(lon1))
                a = m.sin(dlat/2)**2 + m.cos(m.radians(float(lat1))) * m.cos(m.radians(float(lat2))) * m.sin(dlon/2)**2
                c = 2 * m.asin(m.sqrt(a))
                return R * c
            
            avg_speed_kph = 80
            current_pos = vehicle_pos
            cumulative_time_seconds = 0  # Track cumulative travel time
            
            for idx, s in enumerate(stops):
                # First stop is the origin/starting point
                is_origin = (idx == 0)
                
                if s.get('completed'):
                    # Completed stop
                    response['stops'].append({
                        'seq': s['seq'],
                        'name': s['name'],
                        'lat': float(s['lat']) if s.get('lat') is not None else None,
                        'lon': float(s['lon']) if s.get('lon') is not None else None,
                        'completed': True,
                        'planned_arr_ts': s['planned_arr_ts'].isoformat() if s.get('planned_arr_ts') else None,
                        'actual_arr_ts': s['actual_arr_ts'].isoformat() if s.get('actual_arr_ts') else None,
                        'eta_seconds': 0,
                        'eta_timestamp': s['actual_arr_ts'].isoformat() if s.get('actual_arr_ts') else None,
                        'arrival_time': s['actual_arr_ts'].isoformat() if s.get('actual_arr_ts') else None,
                        'is_origin': is_origin
                    })
                elif is_origin:
                    # First stop is the origin - truck starts here
                    from datetime import datetime
                    response['stops'].append({
                        'seq': s['seq'],
                        'name': s['name'],
                        'lat': float(s['lat']) if s.get('lat') is not None else None,
                        'lon': float(s['lon']) if s.get('lon') is not None else None,
                        'completed': False,
                        'planned_arr_ts': s['planned_arr_ts'].isoformat() if s.get('planned_arr_ts') else None,
                        'actual_arr_ts': None,
                        'eta_seconds': 0,
                        'eta_timestamp': datetime.utcnow().isoformat(),
                        'stop_sequence': s['seq'],
                        'is_origin': True,
                        'status': 'Origin (Departed)'
                    })
                else:
                    # Calculate ETA based on distance from current position
                    distance_km = haversine_distance(
                        current_pos['lat'], current_pos['lon'],
                        s['lat'], s['lon']
                    )
                    eta_hours = distance_km / avg_speed_kph
                    eta_seconds = int(eta_hours * 3600)
                    cumulative_time_seconds += eta_seconds
                    
                    # Calculate actual arrival timestamp
                    from datetime import datetime, timedelta
                    eta_timestamp = datetime.utcnow() + timedelta(seconds=cumulative_time_seconds)
                    
                    response['stops'].append({
                        'seq': s['seq'],
                        'name': s['name'],
                        'lat': float(s['lat']) if s.get('lat') is not None else None,
                        'lon': float(s['lon']) if s.get('lon') is not None else None,
                        'completed': False,
                        'planned_arr_ts': s['planned_arr_ts'].isoformat() if s.get('planned_arr_ts') else None,
                        'actual_arr_ts': None,
                        'eta_seconds': eta_seconds,
                        'eta_timestamp': eta_timestamp.isoformat(),
                        'stop_sequence': s['seq'],
                        'is_origin': False
                    })
                    # Update position for next stop calculation (cumulative)
                    current_pos = {'lat': s['lat'], 'lon': s['lon']}
        else:
            # No vehicle position, return stops without ETA
            for s in stops:
                response['stops'].append({
                    'seq': s['seq'],
                    'name': s['name'],
                    'lat': float(s['lat']) if s.get('lat') is not None else None,
                    'lon': float(s['lon']) if s.get('lon') is not None else None,
                    'completed': s.get('completed', False),
                    'planned_arr_ts': s['planned_arr_ts'].isoformat() if s.get('planned_arr_ts') else None,
                    'actual_arr_ts': s['actual_arr_ts'].isoformat() if s.get('actual_arr_ts') else None,
                    'eta_seconds': None,
                    'stop_sequence': s['seq']
                })
        
        # Commit the read transaction
        db.conn.commit()
        
        return jsonify(response), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        db.conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/v1/shipments/<int:shipment_id>/traffic', methods=['GET'])
def get_traffic_segments(shipment_id):
    """
    GET /v1/shipments/{id}/traffic
    Get traffic conditions along the route with color-coded segments
    """
    try:
        # Get shipment stops
        stops = db.get_shipment_stops(shipment_id)
        if not stops:
            return jsonify({'success': False, 'error': 'No stops found'}), 404
        
        # Build waypoints from stops
        waypoints = [(float(s['lat']), float(s['lon'])) for s in stops]
        
        # Get traffic data
        traffic_data = traffic_api.get_traffic_on_route(waypoints)
        
        # Generate mock traffic segments for visualization (simulating real traffic API response)
        # In production, this would come from the traffic provider
        segments = []
        
        for i in range(len(waypoints) - 1):
            start = waypoints[i]
            end = waypoints[i + 1]
            
            # Calculate segment midpoint for traffic sampling
            mid_lat = (start[0] + end[0]) / 2
            mid_lon = (start[1] + end[1]) / 2
            
            # Simulate traffic levels based on congestion data
            congestion = traffic_data.get('congestion_level', 'none')
            if congestion == 'heavy':
                speed_factor = 0.3
                color = '#DC2626'  # Red
                level = 'heavy'
            elif congestion == 'moderate':
                speed_factor = 0.6
                color = '#F59E0B'  # Orange
                level = 'moderate'
            elif congestion == 'light':
                speed_factor = 0.8
                color = '#FBBF24'  # Yellow
                level = 'light'
            else:
                speed_factor = 1.0
                color = '#10B981'  # Green
                level = 'none'
            
            segments.append({
                'start': {'lat': start[0], 'lon': start[1]},
                'end': {'lat': end[0], 'lon': end[1]},
                'traffic_level': level,
                'color': color,
                'speed_factor': speed_factor,
                'current_speed_kph': int(traffic_data.get('average_speed_kph', 80) * speed_factor),
                'freeflow_speed_kph': int(traffic_data.get('freeflow_speed_kph', 80))
            })
        
        return jsonify({
            'success': True,
            'shipment_id': shipment_id,
            'traffic_summary': {
                'congestion_level': traffic_data.get('congestion_level', 'none'),
                'average_speed_kph': traffic_data.get('average_speed_kph', 80),
                'freeflow_speed_kph': traffic_data.get('freeflow_speed_kph', 80)
            },
            'segments': segments
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/v1/reroute/suggest', methods=['POST'])
def suggest_reroute():
    """
    POST /v1/reroute/suggest
    Suggest a reroute if time savings >= 10 minutes
    
    Body: {
        "shipment_id": 1,
        "constraints": {"avoid_tolls": false, "max_height_m": 4.1},
        "min_time_saved_min": 10
    }
    
    Response: {
        "reroute_available": true,
        "time_saved_min": 15,
        "old_eta_ts": "2025-10-27T20:40:00Z",
        "new_eta_ts": "2025-10-27T20:25:00Z",
        "new_path": {...},
        "summary": "Alternative route via US-90 saves 15 minutes"
    }
    """
    try:
        data = request.json
        shipment_id = data['shipment_id']
        min_time_saved = data.get('min_time_saved_min', 10)
        
        # TODO: Implement Valhalla routing comparison
        # For now, return placeholder response
        
        # Get current ETA
        shipment = db.get_shipment(shipment_id)
        stops = db.get_shipment_stops(shipment_id)
        next_stop = next((s for s in stops if not s.get('completed')), None)
        
        if not next_stop:
            return jsonify({
                'success': True,
                'reroute_available': False,
                'reason': 'No pending stops'
            }), 200
        
        current_eta = db.get_latest_eta(shipment_id, next_stop['id'])
        
        # Placeholder: simulate finding alternative route
        # In production, this calls Valhalla with different routing options
        time_saved_min = 12  # Simulated
        
        if time_saved_min >= min_time_saved:
            new_eta_ts = datetime.fromisoformat(current_eta['eta_ts'].replace('Z', '+00:00')) - timedelta(minutes=time_saved_min)
            
            # Store reroute suggestion
            reroute_id = db.insert_reroute(
                shipment_id,
                current_eta['eta_ts'],
                new_eta_ts,
                time_saved_min,
                "Alternative route via US-90 avoids traffic congestion"
            )
            
            return jsonify({
                'success': True,
                'reroute_available': True,
                'reroute_id': reroute_id,
                'time_saved_min': time_saved_min,
                'old_eta_ts': current_eta['eta_ts'].isoformat(),
                'new_eta_ts': new_eta_ts.isoformat(),
                'summary': "Alternative route via US-90 saves 12 minutes by avoiding traffic",
                'instructions': [
                    "Take exit 783 for US-90",
                    "Continue on US-90 E for 15.3 miles",
                    "Merge back onto I-10 E"
                ]
            }), 200
        else:
            return jsonify({
                'success': True,
                'reroute_available': False,
                'reason': f'No alternative route saves >= {min_time_saved} minutes',
                'best_alternative_saves': time_saved_min
            }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/v1/reroutes/<int:reroute_id>/accept', methods=['POST'])
def accept_reroute(reroute_id):
    """Accept a reroute suggestion"""
    try:
        success = db.accept_reroute(reroute_id)
        
        if success:
            return jsonify({'success': True, 'message': 'Reroute accepted'}), 200
        else:
            return jsonify({'success': False, 'error': 'Failed to accept reroute'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== Socket.IO Events ====================

@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid}')
    emit('connected', {'message': 'Connected to ETA tracking server'})

@socketio.on('disconnect')
def handle_disconnect():
    print(f'Client disconnected: {request.sid}')

@socketio.on('subscribe')
def handle_subscribe(data):
    """Subscribe to shipment updates"""
    shipment_id = data.get('shipment_id')
    if shipment_id:
        room = f"shipment_{shipment_id}"
        join_room(room)
        print(f'Client {request.sid} subscribed to {room}')
        emit('subscribed', {'shipment_id': shipment_id, 'room': room})

@socketio.on('unsubscribe')
def handle_unsubscribe(data):
    """Unsubscribe from shipment updates"""
    shipment_id = data.get('shipment_id')
    if shipment_id:
        room = f"shipment_{shipment_id}"
        leave_room(room)
        print(f'Client {request.sid} unsubscribed from {room}')
        emit('unsubscribed', {'shipment_id': shipment_id})

# ==================== Health Check ====================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@app.route('/v1/config', methods=['GET'])
def get_config():
    """Get system configuration"""
    return jsonify({
        'update_interval_seconds': 30,
        'debounce_notifications_min': 1,
        'min_reroute_savings_min': 10,
        'traffic_update_interval_min': 2,
        'weather_update_interval_min': 10
    }), 200

if __name__ == '__main__':
    print("=" * 60)
    print("Live ETA & Delay Explanation System - Backend v1.0")
    print("=" * 60)
    print("\nStarting server...")
    print(f"Database: Connected to PostgreSQL")
    
    # Show routing engine status
    if router.valhalla_url:
        print(f"Routing: Valhalla (Truck costing enabled)")
        print(f"  URL: {router.valhalla_url}")
    else:
        print(f"Routing: OSRM (Fallback - limited truck support)")
        print(f"  URL: {router.osrm_url}")
        print(f"  Note: For full truck routing, run start_valhalla.bat")
    
    print(f"\nAPI Endpoints:")
    print(f"  GET/POST /v1/shipments")
    print(f"  POST   /v1/positions")
    print(f"  GET    /v1/shipments/<id>/status")
    print(f"  POST   /v1/reroute/suggest")
    print(f"  POST   /v1/reroutes/<id>/accept")
    print(f"  GET    /health")
    print(f"  GET    /v1/config")
    print(f"\nSocket.IO Events:")
    print(f"  connect, disconnect, subscribe, unsubscribe")
    print("=" * 60)
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
