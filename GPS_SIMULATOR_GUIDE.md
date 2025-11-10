# 🚚 Unified GPS Simulator - Quick Reference

## Overview

The unified GPS simulator combines **long-haul** and **last-mile** delivery into one seamless simulation, accurately representing a complete B2B logistics journey from Dallas to Beaumont with final deliveries.

---

## Journey Phases

### Phase 1: Long-Haul Delivery (440 km / 273 miles)
**Route**: Dallas Distribution Center → Houston Hub → Beaumont Distribution Center

**Waypoints** (19 total):
- Dallas DC (Origin)
- South Dallas, Ennis, Corsicana, Fairfield, Buffalo, Centerville, Madisonville, Huntsville, Conroe
- Houston Regional Hub (30-minute stop)
- East Houston, Channelview, Baytown, Mont Belvieu, Wallisville, Winnie, Hamshire, Nome
- Beaumont DC (45-minute stop for sorting)

**Speed**: 90 km/h (55 mph) highway driving  
**Duration**: ~2-3 minutes in simulator (compressed from ~5 hours real-time)

---

### Phase 2: Last-Mile Delivery (Beaumont Area)
Three different routes available:

#### ROUTE-RETAIL-001: Retail Express Route
**Stops**: 5 deliveries
- Parkdale Mall - Main Entrance
- Central Mall - Loading Dock
- Target Store #2156
- Walmart Supercenter #573
- Best Buy #1847

**Description**: Downtown Beaumont retail deliveries  
**Speed**: 40 km/h (25 mph) city driving  
**Duration**: ~1-2 minutes in simulator

---

#### ROUTE-HEALTH-001: Healthcare & Education Route
**Stops**: 6 deliveries
- Baptist Hospitals of Southeast Texas
- Christus St. Elizabeth Hospital
- Lamar University - Student Center
- Central High School
- CVS Pharmacy #8745
- Walgreens #5623

**Description**: Medical supplies and educational materials  
**Speed**: 40 km/h (25 mph) city driving  
**Duration**: ~1-2 minutes in simulator

---

#### ROUTE-IND-001: Industrial & Logistics Route
**Stops**: 7 deliveries
- Port of Beaumont - Terminal 1
- ExxonMobil Refinery - Gate 3
- Goodyear Chemical Plant
- Industrial Supply Co.
- Builders FirstSource Warehouse
- Home Depot Pro Desk #4521
- Ferguson Plumbing Supply

**Description**: Port and industrial area deliveries  
**Speed**: 40 km/h (25 mph) city driving  
**Duration**: ~2-3 minutes in simulator

---

## How to Run

### Option 1: Quick Start (Default Route)
```bash
python unified_gps_simulator.py
```
Runs complete journey with ROUTE-RETAIL-001

---

### Option 2: Choose Last-Mile Route
```bash
# Retail deliveries
python unified_gps_simulator.py --route ROUTE-RETAIL-001

# Healthcare deliveries
python unified_gps_simulator.py --route ROUTE-HEALTH-001

# Industrial deliveries
python unified_gps_simulator.py --route ROUTE-IND-001
```

---

### Option 3: Custom Tracking Number
```bash
python unified_gps_simulator.py PO-12345 --route ROUTE-HEALTH-001
```

---

### Option 4: Skip Long-Haul (Start from Beaumont)
```bash
# Start directly at Beaumont DC, skip Dallas→Beaumont drive
python unified_gps_simulator.py --skip-longhaul --route ROUTE-IND-001
```

---

### Option 5: Custom Vehicle ID
```bash
python unified_gps_simulator.py --vehicle 2 --route ROUTE-RETAIL-001
```

---

### Option 6: Windows Batch File
```batch
REM Default route
start_gps_simulator.bat

REM Specific route
start_gps_simulator.bat ROUTE-HEALTH-001

REM Help
start_gps_simulator.bat --help
```

---

## What You'll See

### Long-Haul Phase Output:
```
📦 PHASE 1: LONG-HAUL DELIVERY
Route: Dallas Distribution Center → Houston Hub → Beaumont DC
Distance: ~440 km (273 miles)
Highway Speed: 90 km/h (55 mph)

🚛 En route to: South Dallas
  [10:15:23] 📍 GPS: 32.850000, -96.950000 | Speed: 90.0 km/h | Heading: 135°
  
⏸️ Stopped at Houston Regional Hub for 30 minutes

✅ Long-haul phase complete! Arrived at Beaumont Distribution Center
```

### Last-Mile Phase Output:
```
🏙️ PHASE 2: LAST-MILE DELIVERY
Route: Retail Express Route
Description: Downtown Beaumont retail deliveries
Stops: 5 deliveries

📦 Driving to: Parkdale Mall - Main Entrance
  [10:45:12] 📍 GPS: 30.086700, -94.101500 | Speed: 40.0 km/h | Heading: 45°
  
📦 Delivering at Parkdale Mall (10 min)

✅ Last-mile deliveries complete! All packages delivered
```

---

## GPS Update Details

**Frequency**: Every 5 seconds (industry standard for commercial GPS)  
**Coordinates**: Realistic latitude/longitude for actual Texas locations  
**Speed**: Varies between highway (90 km/h) and city (40 km/h)  
**Heading**: Calculated bearing between waypoints (0-360°)  
**API Endpoint**: `POST http://localhost:5000/v1/positions`

---

## Tracking the Simulation

### Option 1: Customer Tracking Page
1. Run the simulator: `python unified_gps_simulator.py`
2. Open browser: `http://localhost:3000/tracking/PO-98765`
3. Watch the truck icon move in real-time on the map! 🚚

### Option 2: Manager Dashboard
1. Open browser: `http://localhost:3000`
2. Click "Manager Dashboard"
3. See all active shipments with live GPS updates

---

## Time Compression

To make the demo practical, time is compressed:

| Real World | Simulator |
|------------|-----------|
| 30 min stop | 5 seconds |
| 45 min stop | 7.5 seconds |
| 10 min delivery | 3 seconds |
| 5 hour drive | 2-3 minutes |

**GPS updates remain realistic** (every 5 seconds)

---

## Troubleshooting

### "Cannot connect to backend"
- Make sure backend is running: `python backend/app.py`
- Check backend is on port 5000: `http://localhost:5000/health`

### "Failed to send GPS update"
- Backend might be restarting
- Database connection issue
- Simulator continues automatically

### "Unknown route"
- Check route ID spelling: `ROUTE-RETAIL-001` (case-sensitive)
- Use `--help` to see available routes

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Unified GPS Simulator                        │
│                  unified_gps_simulator.py                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP POST every 5 seconds
                              │ /v1/positions
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Flask Backend API                         │
│                      backend/app.py                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Save to database
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  PostgreSQL + PostGIS                           │
│                   (Docker container)                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Socket.io real-time broadcast
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    React Frontend (Vite)                        │
│            Customer Tracking + Manager Dashboard                │
│                   http://localhost:3000                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## Advanced Usage

### Continuous Loop (Multiple Deliveries)
```bash
# Run multiple delivery cycles
for /L %i in (1,1,5) do python unified_gps_simulator.py --route ROUTE-RETAIL-001
```

### Multiple Vehicles
```bash
# Terminal 1
python unified_gps_simulator.py PO-98765 --vehicle 1 --route ROUTE-RETAIL-001

# Terminal 2
python unified_gps_simulator.py PO-98766 --vehicle 2 --route ROUTE-HEALTH-001
```

### Debug Mode
```python
# Edit unified_gps_simulator.py
GPS_UPDATE_INTERVAL = 1  # Faster updates for debugging
```

---

## Next Steps

1. **Test Different Routes**: Try all 3 last-mile routes to see different delivery patterns
2. **Multiple Vehicles**: Run multiple simulators simultaneously
3. **Custom Routes**: Edit `LAST_MILE_ROUTES` in the script to add your own routes
4. **Real GPS Data**: Replace simulated coordinates with actual GPS logger data

---

**Happy Simulating! 🚚📦**
