"""
Database layer for Live ETA & Delay Explanation System
Implements the data model from MVP spec v1.0
"""
import psycopg2
from psycopg2.extras import RealDictCursor, execute_batch
from psycopg2 import sql
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple

load_dotenv()


class Database:
    def __init__(self):
        """Initialize database connection with PostGIS support"""
        database_url = os.getenv('DATABASE_URL')
        if database_url:
            self.conn = psycopg2.connect(database_url)
        else:
            self.conn = psycopg2.connect(
                dbname=os.getenv('DB_NAME', 'postgres'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', ''),
                host=os.getenv('DB_HOST', 'localhost'),
                port=os.getenv('DB_PORT', '5432')
            )
        self.conn.autocommit = False
        
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    # ==================== Shipment Management ====================
    
    def create_shipment(self, ref: str, vehicle_id: int, stops: List[Dict], 
                       promised_eta_ts: str, org_id: int = 1) -> Dict:
        """
        Create a new shipment with stops
        
        Args:
            ref: Shipment reference (e.g., "PO-98765")
            vehicle_id: Vehicle ID
            stops: List of stop dicts with seq, name, lat, lon, planned_service_min
            promised_eta_ts: Promised delivery timestamp
            org_id: Organization ID
            
        Returns:
            Dict with shipment_id and stop_ids
        """
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Insert shipment
                cur.execute("""
                    INSERT INTO shipments (ref, org_id, vehicle_id, promised_eta_ts, status)
                    VALUES (%s, %s, %s, %s, 'pending')
                    RETURNING id
                """, (ref, org_id, vehicle_id, promised_eta_ts))
                
                shipment_id = cur.fetchone()['id']
                
                # Insert stops
                stop_ids = []
                for stop in stops:
                    cur.execute("""
                        INSERT INTO stops (
                            shipment_id, seq, name, lat, lon, location,
                            planned_service_min, planned_arr_ts, planned_dep_ts
                        )
                        VALUES (
                            %s, %s, %s, %s, %s, 
                            ST_SetSRID(ST_MakePoint(%s, %s), 4326),
                            %s, %s, %s
                        )
                        RETURNING id
                    """, (
                        shipment_id, stop['seq'], stop['name'], 
                        stop['lat'], stop['lon'], stop['lon'], stop['lat'],
                        stop.get('planned_service_min', 0),
                        stop.get('planned_arr_ts'),
                        stop.get('planned_dep_ts')
                    ))
                    stop_ids.append(cur.fetchone()['id'])
                
                # Update origin and destination
                if stop_ids:
                    cur.execute("""
                        UPDATE shipments 
                        SET origin_stop_id = %s, dest_stop_id = %s
                        WHERE id = %s
                    """, (stop_ids[0], stop_ids[-1], shipment_id))
                
                self.conn.commit()
                
                return {
                    'shipment_id': shipment_id,
                    'stop_ids': stop_ids,
                    'ref': ref
                }
                
        except Exception as e:
            self.conn.rollback()
            raise e
    
    def get_shipment(self, shipment_id: int) -> Optional[Dict]:
        """Get shipment details"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT s.*, v.plate as vehicle_plate
                FROM shipments s
                LEFT JOIN vehicles v ON s.vehicle_id = v.id
                WHERE s.id = %s
            """, (shipment_id,))
            return cur.fetchone()
    
    def get_shipment_by_ref(self, ref: str) -> Optional[Dict]:
        """Get shipment by reference number"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT s.*, v.plate as vehicle_plate
                FROM shipments s
                LEFT JOIN vehicles v ON s.vehicle_id = v.id
                WHERE s.ref = %s
            """, (ref,))
            return cur.fetchone()
    
    def get_shipment_stops(self, shipment_id: int) -> List[Dict]:
        """Get all stops for a shipment ordered by sequence"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT id, shipment_id, seq, name, lat, lon,
                       planned_arr_ts, planned_dep_ts, planned_service_min,
                       actual_arr_ts, actual_dep_ts, dwell_min, completed
                FROM stops
                WHERE shipment_id = %s
                ORDER BY seq
            """, (shipment_id,))
            return cur.fetchall()
    
    # ==================== Position Management ====================
    
    def insert_positions(self, vehicle_id: int, points: List[Dict]) -> int:
        """
        Batch insert GPS positions
        
        Args:
            vehicle_id: Vehicle ID
            points: List of dicts with ts, lat, lon, speed_kph, heading_deg
            
        Returns:
            Number of positions inserted
        """
        try:
            with self.conn.cursor() as cur:
                data = [
                    (
                        vehicle_id,
                        point['ts'],
                        point['lat'],
                        point['lon'],
                        point['lon'],  # For ST_MakePoint (lon, lat)
                        point['lat'],
                        point.get('speed_kph'),
                        point.get('heading_deg'),
                        point.get('source', 'gps')
                    )
                    for point in points
                ]
                
                execute_batch(cur, """
                    INSERT INTO positions (
                        vehicle_id, ts, lat, lon, location, speed_kph, heading_deg, source
                    )
                    VALUES (
                        %s, %s, %s, %s, 
                        ST_SetSRID(ST_MakePoint(%s, %s), 4326),
                        %s, %s, %s
                    )
                """, data, page_size=100)
                
                self.conn.commit()
                return len(points)
                
        except Exception as e:
            self.conn.rollback()
            raise e
    
    def get_latest_position(self, vehicle_id: int) -> Optional[Dict]:
        """Get most recent position for a vehicle"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT id, vehicle_id, ts, lat, lon, speed_kph, heading_deg, source
                FROM positions
                WHERE vehicle_id = %s
                ORDER BY ts DESC
                LIMIT 1
            """, (vehicle_id,))
            return cur.fetchone()
    
    def get_positions_since(self, vehicle_id: int, since_ts: datetime) -> List[Dict]:
        """Get all positions for a vehicle since a timestamp"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT id, vehicle_id, ts, lat, lon, speed_kph, heading_deg, source
                FROM positions
                WHERE vehicle_id = %s AND ts >= %s
                ORDER BY ts ASC
            """, (vehicle_id, since_ts))
            return cur.fetchall()
    
    # ==================== ETA Management ====================
    
    def insert_eta(self, shipment_id: int, stop_id: int, eta_ts: datetime,
                   on_time: bool, late_by_min: int, reason_code: str,
                   confidence: float, explanation: str) -> int:
        """Insert computed ETA with delay reason"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO etas (
                        shipment_id, stop_id, ts, eta_ts, on_time_bool,
                        late_by_min, reason_code, confidence, explanation
                    )
                    VALUES (%s, %s, CURRENT_TIMESTAMP, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    shipment_id, stop_id, eta_ts, on_time,
                    late_by_min, reason_code, confidence, explanation
                ))
                
                eta_id = cur.fetchone()[0]
                self.conn.commit()
                return eta_id
                
        except Exception as e:
            self.conn.rollback()
            raise e
    
    def get_latest_eta(self, shipment_id: int, stop_id: int) -> Optional[Dict]:
        """Get most recent ETA for a shipment-stop"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT * FROM etas
                WHERE shipment_id = %s AND stop_id = %s
                ORDER BY ts DESC
                LIMIT 1
            """, (shipment_id, stop_id))
            return cur.fetchone()
    
    # ==================== Event Logging ====================
    
    def log_event(self, shipment_id: int, event_type: str, payload: Dict) -> int:
        """Log an event for audit trail"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO events (shipment_id, ts, type, payload_json)
                    VALUES (%s, CURRENT_TIMESTAMP, %s, %s::jsonb)
                    RETURNING id
                """, (shipment_id, event_type, psycopg2.extras.Json(payload)))
                
                event_id = cur.fetchone()[0]
                self.conn.commit()
                return event_id
                
        except Exception as e:
            self.conn.rollback()
            raise e
    
    # ==================== Reroute Management ====================
    
    def insert_reroute(self, shipment_id: int, old_eta_ts: datetime,
                      new_eta_ts: datetime, time_saved_min: int,
                      reason: str) -> int:
        """Insert a reroute suggestion"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO reroutes (
                        shipment_id, ts, old_eta_ts, new_eta_ts,
                        time_saved_min, reason, accepted_bool
                    )
                    VALUES (%s, CURRENT_TIMESTAMP, %s, %s, %s, %s, FALSE)
                    RETURNING id
                """, (shipment_id, old_eta_ts, new_eta_ts, time_saved_min, reason))
                
                reroute_id = cur.fetchone()[0]
                self.conn.commit()
                return reroute_id
                
        except Exception as e:
            self.conn.rollback()
            raise e
    
    def accept_reroute(self, reroute_id: int) -> bool:
        """Mark a reroute as accepted"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    UPDATE reroutes
                    SET accepted_bool = TRUE
                    WHERE id = %s
                """, (reroute_id,))
                
                self.conn.commit()
                return True
                
        except Exception as e:
            self.conn.rollback()
            return False
    
    # ==================== Traffic & Weather Cache ====================
    
    def cache_traffic_data(self, edge_id: str, live_speed: float,
                          freeflow_speed: float) -> None:
        """Cache traffic data for an edge"""
        try:
            with self.conn.cursor() as cur:
                congestion_ratio = live_speed / freeflow_speed if freeflow_speed > 0 else 1.0
                cur.execute("""
                    INSERT INTO traffic_data (
                        edge_id, ts, live_speed_kph, freeflow_speed_kph, congestion_ratio
                    )
                    VALUES (%s, CURRENT_TIMESTAMP, %s, %s, %s)
                """, (edge_id, live_speed, freeflow_speed, congestion_ratio))
                
                self.conn.commit()
                
        except Exception as e:
            self.conn.rollback()
            raise e
    
    def cache_weather_data(self, lat: float, lon: float, precipitation: float,
                          wind_speed: float, temperature: float,
                          conditions: str, alerts: Dict = None) -> None:
        """Cache weather data for a location"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO weather_data (
                        lat, lon, location, ts, precipitation_mm_h,
                        wind_speed_kph, temperature_c, conditions, alerts
                    )
                    VALUES (
                        %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326),
                        CURRENT_TIMESTAMP, %s, %s, %s, %s, %s::jsonb
                    )
                """, (
                    lat, lon, lon, lat, precipitation, wind_speed,
                    temperature, conditions, psycopg2.extras.Json(alerts or {})
                ))
                
                self.conn.commit()
                
        except Exception as e:
            self.conn.rollback()
            raise e
    
    def get_weather_near(self, lat: float, lon: float, 
                        radius_km: float = 30) -> Optional[Dict]:
        """Get recent weather data near a location"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT * FROM weather_data
                WHERE ST_DWithin(
                    location::geography,
                    ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography,
                    %s
                )
                AND ts >= NOW() - INTERVAL '30 minutes'
                ORDER BY ts DESC
                LIMIT 1
            """, (lon, lat, radius_km * 1000))  # Convert km to meters
            return cur.fetchone()
    
    # ==================== Vehicle Management ====================
    
    def get_vehicle(self, vehicle_id: int) -> Optional[Dict]:
        """Get vehicle details"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT * FROM vehicles WHERE id = %s
            """, (vehicle_id,))
            return cur.fetchone()
    
    def get_vehicle_by_plate(self, plate: str) -> Optional[Dict]:
        """Get vehicle by plate number"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT * FROM vehicles WHERE plate = %s
            """, (plate,))
            return cur.fetchone()
