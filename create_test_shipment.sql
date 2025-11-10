-- Create Test Shipment PO-98765 for ETA Tracker
-- This creates a shipment with Dallas to Beaumont route and 5 retail stops

-- Insert test organization
INSERT INTO organizations (name, api_key) 
VALUES ('Test Logistics', 'test_key_logistics')
ON CONFLICT DO NOTHING;

-- Insert test vehicle
INSERT INTO vehicles (id, license_plate, vehicle_type, status)
VALUES (1, 'TX-TRUCK-001', 'truck', 'active')
ON CONFLICT (id) DO NOTHING;

-- Insert test shipment PO-98765
INSERT INTO shipments (id, reference_number, origin, destination, status, vehicle_id, created_at)
VALUES (
    1,
    'PO-98765',
    ST_SetSRID(ST_MakePoint(-96.7970, 32.7767), 4326),  -- Dallas Distribution Center
    ST_SetSRID(ST_MakePoint(-94.1266, 30.0802), 4326),  -- Beaumont
    'in_transit',
    1,
    NOW()
) ON CONFLICT (id) DO UPDATE SET 
    reference_number = 'PO-98765',
    origin = ST_SetSRID(ST_MakePoint(-96.7970, 32.7767), 4326),
    destination = ST_SetSRID(ST_MakePoint(-94.1266, 30.0802), 4326),
    status = 'in_transit',
    vehicle_id = 1;

-- Insert stops for the shipment (ROUTE-RETAIL-001)
INSERT INTO stops (shipment_id, sequence, name, location, address, stop_type, status, estimated_arrival)
VALUES 
(1, 1, 'Parkdale Mall', ST_SetSRID(ST_MakePoint(-94.1579, 30.0901), 4326), '6155 Eastex Fwy, Beaumont, TX 77706', 'delivery', 'pending', NOW() + INTERVAL '4 hours'),
(1, 2, 'Target Beaumont', ST_SetSRID(ST_MakePoint(-94.1275, 30.0860), 4326), '3745 Dowlen Rd, Beaumont, TX 77706', 'delivery', 'pending', NOW() + INTERVAL '4.5 hours'),
(1, 3, 'Walmart Supercenter', ST_SetSRID(ST_MakePoint(-94.1015, 30.0330), 4326), '6250 Eastex Fwy, Beaumont, TX 77708', 'delivery', 'pending', NOW() + INTERVAL '5 hours'),
(1, 4, 'Best Buy', ST_SetSRID(ST_MakePoint(-94.1450, 30.0785), 4326), '4375 Dowlen Rd, Beaumont, TX 77706', 'delivery', 'pending', NOW() + INTERVAL '5.5 hours'),
(1, 5, 'Home Depot', ST_SetSRID(ST_MakePoint(-94.1320, 30.0920), 4326), '6375 Eastex Fwy, Beaumont, TX 77708', 'delivery', 'pending', NOW() + INTERVAL '6 hours')
ON CONFLICT (shipment_id, sequence) DO UPDATE SET
    name = EXCLUDED.name,
    location = EXCLUDED.location,
    address = EXCLUDED.address,
    stop_type = EXCLUDED.stop_type,
    status = EXCLUDED.status,
    estimated_arrival = EXCLUDED.estimated_arrival;

-- Verify data was created
SELECT 
    'Shipment created:' as result,
    id,
    reference_number,
    status,
    ST_AsText(origin) as origin,
    ST_AsText(destination) as destination
FROM shipments 
WHERE reference_number = 'PO-98765';

SELECT 
    'Stops created:' as result,
    COUNT(*) as stop_count
FROM stops 
WHERE shipment_id = 1;
