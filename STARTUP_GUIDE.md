# 🚀 ETA Tracker - Complete Startup Guide

## 🎯 Two Ways to Start

### ⚡ Method 1: One-Click Startup (RECOMMENDED!)

```powershell
# Start everything at once
.\start_all.bat
```

**What happens:**
1. Checks Docker Desktop is running
2. Starts PostgreSQL (port 5432)
3. Starts Valhalla (port 8002) in separate window
4. Starts Backend API (port 5000) in separate window
5. Starts Frontend (port 3000) in separate window
6. Asks if you want to start GPS Simulator
7. Opens interactive control menu

**Benefits:**
- ✅ No manual steps - everything automated
- ✅ Checks if services already running
- ✅ Each component in own terminal window
- ✅ Interactive menu for status/control
- ✅ One command to stop everything

**After running, you get a control menu:**
```
1. Check Status (all services)
2. Open Manager Dashboard in browser
3. Open Customer Tracking in browser
4. Start GPS Simulator (if not running)
5. Stop All Services
6. Exit (keep services running)
```

---

### 🔧 Method 2: Manual Step-by-Step

Use this if you want full control over each component.

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│  COMPONENT         │  COMMAND                │  PORT  │ ORDER│
├─────────────────────────────────────────────────────────────┤
│ PostgreSQL + PostGIS│ docker compose up -d   │  5432  │  1   │
│ Valhalla Routing    │ start_valhalla.bat     │  8002  │  2   │
│ Backend API         │ python backend/app.py  │  5000  │  3   │
│ Frontend (React)    │ npm run dev            │  3000  │  4   │
│ GPS Simulator       │ python unified_gps... │   -    │  5   │
└─────────────────────────────────────────────────────────────┘
```

---

## Step-by-Step Startup

### ✅ Step 1: Start PostgreSQL Database

```powershell
# Navigate to project directory
cd C:\Users\saile\OneDrive\Desktop\eta_tracker

# Start PostgreSQL with PostGIS
docker compose up -d postgres

# Wait 10 seconds for initialization
Start-Sleep -Seconds 10

# Verify it's running
docker ps --filter name=eta-tracker-db
```

**Expected Output:**
```
✔ Container eta-tracker-db  Started
CONTAINER ID   IMAGE                              STATUS
abc123...      postgis/postgis:15-3.3-alpine      Up 12 seconds (healthy)
```

**What it does:**
- Creates PostgreSQL 15 database with PostGIS extension
- Initializes schema: shipments, routes, stops, gps_logs tables
- Enables geometry types for GPS coordinates
- Runs on localhost:5432

---

### ✅ Step 2: Start Valhalla Routing Engine

```powershell
# Start Valhalla
.\start_valhalla.bat
```

**First Run (10-15 minutes):**
```
[INFO] Downloading Texas OSM data (valhalla_data/texas-latest.osm.pbf)...
[INFO] Building Valhalla routing tiles...
[INFO] Valhalla server starting on port 8002...
✔ Container eta-tracker-valhalla  Started
```

**Subsequent Runs (instant):**
```
[INFO] Using cached tiles from valhalla_data/
[INFO] Valhalla server starting on port 8002...
✔ Container eta-tracker-valhalla  Started
```

**What it does:**
- Downloads OpenStreetMap data for Texas
- Builds routing tiles with truck constraints
- Provides routing API at http://localhost:8002
- Supports weight limits, height restrictions, highway preferences

---

### ✅ Step 3: Start Backend API

```powershell
# Install dependencies (first time only)
pip install -r requirements.txt

# Start Flask backend
python backend/app.py
```

**Expected Output:**
```
Database: PostgreSQL at localhost:5432
  ✓ Database: eta_tracker
  ✓ Tables: shipments, routes, stops, gps_logs

Routing: Valhalla (Truck costing enabled)
  URL: http://localhost:8002

Weather: OpenWeatherMap API
  ✓ API Key configured

🚀 Backend API running on http://localhost:5000
 * Serving Flask app 'app'
 * Debug mode: on
```

**What it does:**
- Connects to PostgreSQL database
- Connects to Valhalla routing engine
- Sets up Weather API integration
- Provides REST API endpoints:
  - `POST /v1/gps` - Receive GPS updates
  - `GET /v1/shipments/{id}` - Get shipment details
  - `POST /v1/shipments` - Create new shipment
  - `GET /v1/stops` - Get delivery stops
  - `GET /v1/weather/{lat}/{lng}` - Get weather data

---

### ✅ Step 4: Start Frontend

```powershell
# Install dependencies (first time only)
npm install

# Start React dev server
npm run dev
```

**Expected Output:**
```
VITE v6.0.1  ready in 1234 ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: http://192.168.1.100:3000/
  ➜  press h + enter to show help
```

**What it does:**
- Starts React 19 + Vite development server
- Serves Manager Dashboard at http://localhost:3000/
- Serves Customer Tracking at http://localhost:3000/tracking/{po_number}
- Polls Backend API every 5 seconds for GPS updates

---

### ✅ Step 5: Run GPS Simulator (Optional)

```powershell
# Retail route (5 stops in Beaumont)
python unified_gps_simulator.py --route ROUTE-RETAIL-001

# Healthcare route (6 stops)
python unified_gps_simulator.py --route ROUTE-HEALTH-001

# Industrial route (7 stops)
python unified_gps_simulator.py --route ROUTE-IND-001

# Skip long-haul, go straight to last-mile
python unified_gps_simulator.py --route ROUTE-RETAIL-001 --skip-longhaul
```

**Expected Output:**
```
🚛 Unified GPS Simulator - Long Haul + Last Mile Delivery
================================================================

📍 PHASE 1: Long-Haul Route (Dallas → Houston → Beaumont)
   Distance: 440.2 km
   Waypoints: 19
   Speed: 90 km/h (highway)

[2025-11-10 10:00:00] 📍 Dallas Distribution Center
✅ GPS Update #1 sent - 32.7767°N, 96.7970°W

[2025-11-10 10:05:00] 📍 Waypoint 2/19 - I-45 South
✅ GPS Update #2 sent - 32.6890°N, 96.8025°W

...

📍 PHASE 2: Last-Mile Deliveries (Beaumont Area)
   Route: ROUTE-RETAIL-001
   Stops: 5
   Speed: 40 km/h (city)

[2025-11-10 15:30:00] 📍 Parkdale Mall
✅ GPS Update #45 sent - 30.0901°N, 94.1579°W
✅ Stop completed: Parkdale Mall

[2025-11-10 16:00:00] 📍 Target Beaumont
✅ GPS Update #51 sent - 30.0860°N, 94.1275°W
✅ Stop completed: Target Beaumont

...

🎉 Simulation Complete!
   Total GPS Updates: 87
   Total Distance: 465.8 km
   Total Time: 6 hours 15 minutes
```

**What it does:**
- Simulates truck GPS movement every 5 seconds
- Sends POST requests to `http://localhost:5000/v1/gps`
- Updates shipment PO-98765 in database
- Triggers ETA recalculation on backend
- Frontend map updates automatically

---

## 🔍 Verification Checklist

### 1. Check All Services Running

```powershell
# PostgreSQL
docker ps --filter name=eta-tracker-db
# Should show: Up X seconds (healthy)

# Valhalla
docker ps --filter name=eta-tracker-valhalla
# Should show: Up X seconds

# Backend
Get-Process python
# Should show: 1 or 2 Python processes

# Frontend
# Browser should show: http://localhost:3000
```

### 2. Test Backend API

```powershell
# PowerShell
Invoke-WebRequest -Uri http://localhost:5000/v1/status | Select-Object -ExpandProperty Content
```

**Expected Response:**
```json
{
  "status": "ok",
  "database": "connected",
  "valhalla": "available",
  "weather_api": "configured"
}
```

### 3. Test Frontend

Open browser: http://localhost:3000

**Manager Dashboard should show:**
- Map with Texas centered
- "📦 Load PO-98765" button
- "🧪 Test Data" button
- "Create Shipment" form

**Customer Tracking should show:**
Visit: http://localhost:3000/tracking/PO-98765
- Map with truck icon (if GPS simulator running)
- ETA countdown
- Delivery stops list
- Confidence score

---

## 🚨 Troubleshooting

### Issue: "Docker not running"
```
Error: Cannot connect to the Docker daemon
```

**Solution:**
1. Open Docker Desktop
2. Wait for "Docker Desktop is running"
3. Retry: `docker compose up -d postgres`

---

### Issue: "Port 5432 already in use"
```
Error: bind: address already in use
```

**Solution:**
```powershell
# Stop existing PostgreSQL
docker compose down

# Or stop other PostgreSQL instances
Get-Process postgres | Stop-Process
```

---

### Issue: "Valhalla tiles not found"
```
Error: No tile data found in valhalla_data/
```

**Solution:**
1. Delete `valhalla_data/` folder
2. Run `start_valhalla.bat` again
3. Wait 10-15 minutes for tile building

---

### Issue: "Backend can't connect to Valhalla"
```
Routing: OSRM (Fallback - limited truck support)
```

**Solution:**
1. Check Valhalla is running: `docker ps --filter name=valhalla`
2. Verify port 8002: `Test-NetConnection localhost -Port 8002`
3. Restart backend: `python backend/app.py`

---

### Issue: "GPS Simulator fails with 500 error"
```
❌ Failed to fetch shipment: 500
```

**Solution:**
1. Check database initialized:
   ```powershell
   docker exec eta-tracker-db psql -U postgres -d eta_tracker -c "\dt"
   ```
   Should show: shipments, routes, stops, gps_logs tables

2. If no tables, initialize schema:
   ```powershell
   docker exec -i eta-tracker-db psql -U postgres -d eta_tracker < data/init_db.sql
   ```

---

### Issue: "Frontend shows blank map"
```
Map loads but no markers visible
```

**Solution:**
1. Check backend API: http://localhost:5000/v1/status
2. Check shipment exists: http://localhost:5000/v1/shipments/1
3. Run GPS simulator to create data
4. Clear browser cache (Ctrl + Shift + R)

---

## 📊 Component Dependencies

```
PostgreSQL
    ↓
    ├─→ Backend (requires DB tables)
    │       ↓
    │       ├─→ Frontend (calls API)
    │       │
    │       └─→ GPS Simulator (sends data)
    │
    └─→ Valhalla
            ↓
            └─→ Backend (routing calculations)
```

**Key Point:** Start components in order listed above. Backend won't fully work without PostgreSQL + Valhalla.

---

## 🎯 Quick Test Scenario

After starting all components:

1. **Open Manager Dashboard**: http://localhost:3000
2. **Click "📦 Load PO-98765"** - Loads existing test shipment
3. **Open Customer Tracking**: http://localhost:3000/tracking/PO-98765
4. **Run GPS Simulator**:
   ```powershell
   python unified_gps_simulator.py --route ROUTE-RETAIL-001
   ```
5. **Watch truck move on map** - Updates every 5 seconds
6. **See ETA update** - Backend recalculates with weather/traffic
7. **View confidence score** - Changes based on route conditions

---

## 📚 Additional Documentation

- **GPS_SIMULATOR_GUIDE.md** - Detailed GPS simulator usage
- **README.md** - Complete project documentation
- **data/init_db.sql** - Database schema reference

---

## 🆘 Need Help?

If services don't start correctly:

1. Check Docker Desktop is running
2. Verify ports not in use: 3000, 5000, 5432, 8002
3. Read error messages carefully
4. Check logs: `docker compose logs postgres` or `docker compose logs valhalla`
5. Restart in order: DB → Valhalla → Backend → Frontend

**All components must be running for full functionality!**
