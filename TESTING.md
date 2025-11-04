# 🧪 Testing Guide - ETA Tracker

Complete guide for testing last-mile delivery optimization with comprehensive test data.

---

## 📋 Table of Contents

1. [Setup & Preparation](#setup--preparation)
2. [Test Data Overview](#test-data-overview)
3. [Testing Workflows](#testing-workflows)
4. [Rerouting Scenarios](#rerouting-scenarios)
5. [Troubleshooting](#troubleshooting)

---

## 🚀 Setup & Preparation

### 1. Database Setup

Ensure PostgreSQL is running and database is initialized:

```bash
# Check PostgreSQL status
psql -U postgres -c "SELECT version();"

# Initialize database
psql -U postgres -f data/init_db.sql
```

### 2. Populate Test Data

Run the test data population script:

```bash
# Windows
populate_test_data.bat

# Linux/Mac
python create_test_data.py
```

This creates:
- ✅ 2 Organizations (FastTrack Logistics, QuickShip Express)
- ✅ 5 Vehicles (3 trucks, 2 vans)
- ✅ 4 Shipment routes (20+ total stops)
- ✅ Initial GPS positions at Beaumont DC

### 3. Start Backend

```bash
# Windows
start_backend.bat

# Linux/Mac
python backend/app.py
```

Backend runs on: `http://localhost:5000`

### 4. Start Frontend

```bash
npm run dev
```

Frontend runs on: `http://localhost:5173`

---

## 📊 Test Data Overview

### Beaumont Delivery Locations

**20 locations** across **6 neighborhoods**:

| Neighborhood | Locations | Count |
|-------------|-----------|-------|
| Downtown | City Hall, Convention Center, Civic Center | 3 |
| West End | Community Center, West End Hospital, Plaza | 3 |
| South End | Public Library, Memorial Park, Shopping Center | 3 |
| North End | High School, Sports Complex, North Mall | 3 |
| East End | Medical Plaza, Senior Center, Recreation Center | 3 |
| Residential | Oak Drive, Maple Street | 2 |
| Industrial | Industrial Park, Distribution Center, Warehouse District | 3 |

### Test Routes

#### Route 1: Downtown + West End Express (`ROUTE-DW-001`)
- **Stops**: 5
- **Focus**: Quick urban delivery
- **Vehicles**: Truck-001 (V1)
- **Distance**: ~8 km
- **Est. Time**: 45 min

**Stops**:
1. Beaumont Distribution Center (Origin)
2. Beaumont City Hall
3. West End Community Center
4. West End Hospital
5. Downtown Civic Center

**Use for**: Basic routing, simple ETA calculation

---

#### Route 2: Residential Delivery Route (`ROUTE-RES-001`)
- **Stops**: 8
- **Focus**: Dense residential area
- **Vehicles**: Van-004 (V4)
- **Distance**: ~12 km
- **Est. Time**: 2 hours

**Stops**:
1. Beaumont DC (Origin)
2. Beaumont City Hall
3. Oak Drive Residence
4. Maple Street Residence
5. South End Library
6. Memorial Park
7. West End Plaza
8. Downtown Convention Center

**Use for**: Multi-stop optimization, residential delivery patterns

---

#### Route 3: North-South Corridor (`ROUTE-NS-001`)
- **Stops**: 6
- **Focus**: Cross-city delivery
- **Vehicles**: Truck-002 (V2)
- **Distance**: ~15 km
- **Est. Time**: 1.5 hours

**Stops**:
1. Beaumont DC (Origin)
2. North End High School
3. North End Sports Complex
4. Downtown City Hall
5. South End Shopping Center
6. Memorial Park

**Use for**: Long-distance routing, traffic impact testing

---

#### Route 4: Full City Coverage (`ROUTE-FULL-001`)
- **Stops**: 10
- **Focus**: Complete coverage
- **Vehicles**: Truck-003 (V3)
- **Distance**: ~22 km
- **Est. Time**: 3 hours

**Stops**:
1. Beaumont DC (Origin)
2. Industrial Park
3. North End High School
4. East End Medical Plaza
5. East End Recreation Center
6. Downtown City Hall
7. South End Library
8. West End Hospital
9. West End Community Center
10. Downtown Convention Center

**Use for**: Complex optimization, full system testing

---

## 🧪 Testing Workflows

### Basic Workflow: Single Route Test

**Objective**: Verify basic GPS tracking and ETA calculation

1. **Start Backend**
   ```bash
   start_backend.bat
   ```

2. **Start Frontend**
   ```bash
   npm run dev
   ```

3. **Run Simulator for Express Route**
   ```bash
   start_last_mile_simulator.bat ROUTE-DW-001 1
   ```

4. **Verify in Dashboard**
   - Open `http://localhost:5173`
   - Select "Downtown + West End Express"
   - Watch real-time GPS updates
   - Monitor ETA changes

5. **Expected Results**
   - ✅ GPS position updates every 5 seconds
   - ✅ Vehicle moves stop-by-stop
   - ✅ ETA recalculates automatically
   - ✅ Completed stops marked green
   - ✅ Service time delays visible

---

### Advanced Workflow: Multi-Vehicle Testing

**Objective**: Test multiple simultaneous deliveries

1. **Terminal 1: Start Express Route**
   ```bash
   start_last_mile_simulator.bat ROUTE-DW-001 1
   ```

2. **Terminal 2: Start Residential Route**
   ```bash
   start_last_mile_simulator.bat ROUTE-RES-001 4
   ```

3. **Terminal 3: Start Full Coverage**
   ```bash
   start_last_mile_simulator.bat ROUTE-FULL-001 3
   ```

4. **Verify in Dashboard**
   - Switch between shipments
   - Compare ETAs
   - Monitor all vehicle positions

---

### Rerouting Test Workflow

**Objective**: Trigger and test rerouting suggestions

#### Scenario 1: Traffic Delay on North-South Route

1. **Start North-South Corridor**
   ```bash
   start_last_mile_simulator.bat ROUTE-NS-001 2
   ```

2. **Observe Route**
   - Watch progress for first 2-3 stops
   - Note baseline ETA

3. **Simulate Traffic**
   - Simulator automatically introduces traffic delays (20% chance per segment)
   - Look for "⚠️ Traffic delay" messages in console

4. **Expected Behavior**
   - ETA increases when traffic detected
   - Rerouting suggestion triggered if delay > 5 minutes
   - Alternative route proposed in backend logs

#### Scenario 2: Mid-Route Restart

**Objective**: Test recovery from stop

1. **Start Full Coverage Route**
   ```bash
   start_last_mile_simulator.bat ROUTE-FULL-001 3
   ```

2. **Stop After 4 Stops** (Ctrl+C)

3. **Resume from Stop 5**
   ```bash
   start_last_mile_simulator.bat ROUTE-FULL-001 3 5
   ```

4. **Expected Results**
   - Route continues from stop 5
   - Previous stops show as completed
   - ETA calculated for remaining stops

---

## 🔄 Rerouting Scenarios

### Scenario Types

#### 1. Traffic Congestion
**Trigger**: Random delays during simulation (20% probability)
**Impact**: +30s to +3min delay
**Expected Response**: 
- ETA updated immediately
- If delay > 5min, suggest alternative route
- Backend logs reroute calculation

#### 2. Road Closure
**Manual Test**:
```bash
# Simulate road closure between stops 3-4
curl -X POST http://localhost:5000/v1/simulate/road-closure \
  -H "Content-Type: application/json" \
  -d '{"from_stop": 3, "to_stop": 4, "duration_min": 30}'
```

**Expected**: Backend calculates alternative route avoiding closed segment

#### 3. Priority Delivery Change
**Manual Test**:
```bash
# Change stop priority
curl -X POST http://localhost:5000/v1/shipments/{id}/reorder \
  -H "Content-Type: application/json" \
  -d '{"new_order": [1, 3, 2, 4, 5]}'
```

**Expected**: Route recalculated with new stop order

---

## 📈 Performance Testing

### Load Test: 10 Simultaneous Routes

```python
# test_load.py
import subprocess
import time

routes = [
    ("ROUTE-DW-001", 1),
    ("ROUTE-RES-001", 4),
    ("ROUTE-NS-001", 2),
    ("ROUTE-FULL-001", 3),
]

processes = []
for route, vehicle in routes:
    proc = subprocess.Popen([
        "python", "simulate_last_mile.py",
        "--route", route,
        "--vehicle", str(vehicle)
    ])
    processes.append(proc)
    time.sleep(5)  # Stagger starts

# Wait for completion
for proc in processes:
    proc.wait()
```

**Metrics to Monitor**:
- Database connection pool usage
- API response times
- WebSocket message latency
- Memory usage

---

## 🐛 Troubleshooting

### Backend Not Responding

**Symptoms**: Simulator shows "Backend not responding"

**Solutions**:
1. Check backend is running:
   ```bash
   curl http://localhost:5000/health
   ```

2. Check backend logs for errors

3. Restart backend:
   ```bash
   start_backend.bat
   ```

---

### GPS Updates Not Showing

**Symptoms**: Dashboard not updating positions

**Solutions**:
1. Check WebSocket connection in browser console
2. Verify shipment ID matches in simulator and dashboard
3. Check backend logs for GPS processing errors

---

### Route Not Found

**Symptoms**: "Shipment ROUTE-XXX-XXX not found"

**Solutions**:
1. Verify test data is populated:
   ```bash
   psql -U postgres -d eta_tracker -c "SELECT ref FROM shipments;"
   ```

2. Re-run test data population:
   ```bash
   populate_test_data.bat
   ```

---

### Slow ETA Calculations

**Symptoms**: ETA updates take > 2 seconds

**Solutions**:
1. Check Valhalla routing service is running
2. Verify PostgreSQL query performance:
   ```sql
   EXPLAIN ANALYZE SELECT * FROM stops WHERE shipment_id = ?;
   ```
3. Add database indexes if needed

---

## 📝 Test Checklist

### Basic Features
- [ ] GPS position updates every 5 seconds
- [ ] Stop-by-stop progression works
- [ ] Service time delays apply correctly
- [ ] ETAs recalculate automatically
- [ ] Completed stops marked properly

### Rerouting
- [ ] Traffic delays detected
- [ ] Alternative routes suggested
- [ ] Route optimization works
- [ ] ETA accuracy improves post-reroute

### UI/UX
- [ ] Map displays all stops
- [ ] Current position highlighted
- [ ] Route polyline visible
- [ ] Stop details show on click
- [ ] Real-time updates smooth

### Performance
- [ ] Handles 5+ simultaneous routes
- [ ] No memory leaks over 1-hour test
- [ ] API response < 500ms
- [ ] WebSocket latency < 100ms

---

## 🎯 Next Steps

1. **Add More Scenarios**: Create additional test routes for edge cases
2. **Automated Testing**: Build pytest suite for backend API
3. **Load Testing**: Use locust.io for stress testing
4. **Data Analysis**: Export metrics to analyze ETA accuracy
5. **CI/CD**: Integrate tests into GitHub Actions

---

## 📚 Related Documentation

- [README.md](README.md) - Project overview
- [CONTRIBUTING.md](CONTRIBUTING.md) - Development guidelines
- [API Documentation](backend/README.md) - Backend API reference

---

**Happy Testing! 🚚💨**
