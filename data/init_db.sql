-- Live ETA & Delay Explanation System - Database Schema v1.0
-- Enable PostGIS extension for geometry support
CREATE EXTENSION IF NOT EXISTS postgis;

-- Organizations table (for multi-tenancy)
CREATE TABLE IF NOT EXISTS organizations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Vehicles table
CREATE TABLE IF NOT EXISTS vehicles (
    id SERIAL PRIMARY KEY,
    org_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE,
    plate VARCHAR(50) UNIQUE NOT NULL,
    height_m DECIMAL(5,2),
    width_m DECIMAL(5,2),
    weight_tons DECIMAL(8,2),
    hazmat_allowed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Shipments table
CREATE TABLE IF NOT EXISTS shipments (
    id SERIAL PRIMARY KEY,
    ref VARCHAR(100) UNIQUE NOT NULL,
    org_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE,
    vehicle_id INTEGER REFERENCES vehicles(id),
    origin_stop_id INTEGER,
    dest_stop_id INTEGER,
    promised_eta_ts TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Stops table
CREATE TABLE IF NOT EXISTS stops (
    id SERIAL PRIMARY KEY,
    shipment_id INTEGER REFERENCES shipments(id) ON DELETE CASCADE,
    seq INTEGER NOT NULL,
    name VARCHAR(200) NOT NULL,
    lat DOUBLE PRECISION NOT NULL,
    lon DOUBLE PRECISION NOT NULL,
    location GEOMETRY(Point, 4326),
    planned_arr_ts TIMESTAMP,
    planned_dep_ts TIMESTAMP,
    planned_service_min INTEGER DEFAULT 0,
    actual_arr_ts TIMESTAMP,
    actual_dep_ts TIMESTAMP,
    dwell_min INTEGER,
    completed BOOLEAN DEFAULT FALSE,
    UNIQUE(shipment_id, seq)
);

-- Create spatial index on stops
CREATE INDEX IF NOT EXISTS idx_stops_location ON stops USING GIST(location);

-- Positions table (GPS pings)
CREATE TABLE IF NOT EXISTS positions (
    id SERIAL PRIMARY KEY,
    vehicle_id INTEGER REFERENCES vehicles(id) ON DELETE CASCADE,
    ts TIMESTAMP NOT NULL,
    lat DOUBLE PRECISION NOT NULL,
    lon DOUBLE PRECISION NOT NULL,
    location GEOMETRY(Point, 4326),
    speed_kph DECIMAL(6,2),
    heading_deg DECIMAL(5,2),
    source VARCHAR(50) DEFAULT 'gps',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes on positions
CREATE INDEX IF NOT EXISTS idx_positions_vehicle_ts ON positions(vehicle_id, ts DESC);
CREATE INDEX IF NOT EXISTS idx_positions_location ON positions USING GIST(location);

-- ETAs table (computed ETAs with delay reasons)
CREATE TABLE IF NOT EXISTS etas (
    id SERIAL PRIMARY KEY,
    shipment_id INTEGER REFERENCES shipments(id) ON DELETE CASCADE,
    stop_id INTEGER REFERENCES stops(id) ON DELETE CASCADE,
    ts TIMESTAMP NOT NULL,
    eta_ts TIMESTAMP NOT NULL,
    on_time_bool BOOLEAN DEFAULT TRUE,
    late_by_min INTEGER DEFAULT 0,
    reason_code VARCHAR(50),
    confidence DECIMAL(3,2),
    explanation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes on etas
CREATE INDEX IF NOT EXISTS idx_etas_shipment_ts ON etas(shipment_id, ts DESC);
CREATE INDEX IF NOT EXISTS idx_etas_stop_ts ON etas(stop_id, ts DESC);

-- Events table (audit log)
CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    shipment_id INTEGER REFERENCES shipments(id) ON DELETE CASCADE,
    ts TIMESTAMP NOT NULL,
    type VARCHAR(100) NOT NULL,
    payload_json JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on events
CREATE INDEX IF NOT EXISTS idx_events_shipment_ts ON events(shipment_id, ts DESC);
CREATE INDEX IF NOT EXISTS idx_events_type ON events(type);

-- Reroutes table
CREATE TABLE IF NOT EXISTS reroutes (
    id SERIAL PRIMARY KEY,
    shipment_id INTEGER REFERENCES shipments(id) ON DELETE CASCADE,
    ts TIMESTAMP NOT NULL,
    old_eta_ts TIMESTAMP,
    new_eta_ts TIMESTAMP,
    time_saved_min INTEGER,
    old_path GEOMETRY(LineString, 4326),
    new_path GEOMETRY(LineString, 4326),
    reason TEXT,
    accepted_bool BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on reroutes
CREATE INDEX IF NOT EXISTS idx_reroutes_shipment_ts ON reroutes(shipment_id, ts DESC);

-- Traffic data cache table
CREATE TABLE IF NOT EXISTS traffic_data (
    id SERIAL PRIMARY KEY,
    edge_id VARCHAR(100) NOT NULL,
    ts TIMESTAMP NOT NULL,
    live_speed_kph DECIMAL(6,2),
    freeflow_speed_kph DECIMAL(6,2),
    congestion_ratio DECIMAL(4,3),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on traffic_data
CREATE INDEX IF NOT EXISTS idx_traffic_edge_ts ON traffic_data(edge_id, ts DESC);

-- Weather data cache table
CREATE TABLE IF NOT EXISTS weather_data (
    id SERIAL PRIMARY KEY,
    lat DOUBLE PRECISION NOT NULL,
    lon DOUBLE PRECISION NOT NULL,
    location GEOMETRY(Point, 4326),
    ts TIMESTAMP NOT NULL,
    precipitation_mm_h DECIMAL(6,2),
    wind_speed_kph DECIMAL(6,2),
    temperature_c DECIMAL(5,2),
    conditions VARCHAR(100),
    alerts JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create spatial index on weather_data
CREATE INDEX IF NOT EXISTS idx_weather_location_ts ON weather_data USING GIST(location);
CREATE INDEX IF NOT EXISTS idx_weather_ts ON weather_data(ts DESC);

-- Insert sample organization
INSERT INTO organizations (id, name) VALUES (1, 'Demo Logistics Inc') ON CONFLICT DO NOTHING;

-- Insert sample vehicle
INSERT INTO vehicles (id, org_id, plate, height_m, width_m, weight_tons, hazmat_allowed) 
VALUES (1, 1, 'TX123', 4.1, 2.5, 15.0, FALSE) ON CONFLICT DO NOTHING;

-- Insert sample shipment (Dallas → Houston → Beaumont)
INSERT INTO shipments (id, ref, org_id, vehicle_id, promised_eta_ts, status)
VALUES (1, 'PO-98765', 1, 1, '2025-10-30T18:00:00Z', 'in_transit') ON CONFLICT DO NOTHING;

-- Insert sample stops
INSERT INTO stops (id, shipment_id, seq, name, lat, lon, location, planned_service_min, planned_arr_ts, planned_dep_ts)
VALUES 
    (1, 1, 1, 'Dallas Facility', 32.896, -97.036, ST_SetSRID(ST_MakePoint(-97.036, 32.896), 4326), 60, '2025-10-27T10:00:00Z', '2025-10-27T11:00:00Z'),
    (2, 1, 2, 'Houston Hub', 29.990, -95.336, ST_SetSRID(ST_MakePoint(-95.336, 29.990), 4326), 120, '2025-10-27T15:00:00Z', '2025-10-27T17:00:00Z'),
    (3, 1, 3, 'Beaumont DC', 30.080, -94.126, ST_SetSRID(ST_MakePoint(-94.126, 30.080), 4326), 180, '2025-10-27T18:00:00Z', '2025-10-27T21:00:00Z')
ON CONFLICT DO NOTHING;

-- Update shipment with origin and destination
UPDATE shipments SET origin_stop_id = 1, dest_stop_id = 3 WHERE id = 1;

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for shipments
DROP TRIGGER IF EXISTS update_shipments_updated_at ON shipments;
CREATE TRIGGER update_shipments_updated_at
    BEFORE UPDATE ON shipments
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
