# 🎯 B2B Testing - Quick Commands

## Updated Test Infrastructure for Realistic B2B Delivery

---

## 🚀 Quick Start (Updated)

### 1. Populate New B2B Test Data
```bash
populate_test_data.bat
```

**Creates**:
- 19 B2B commercial locations (retail, healthcare, industrial)
- 3 B2B delivery routes
- Speed limits for each location (20-60 mph)
- 5 commercial vehicles

---

### 2. Start Backend
```bash
start_backend.bat
```

---

### 3. Start Frontend
```bash
npm run dev
```

Dashboard: http://localhost:5173

---

### 4. Run B2B Simulations

#### Retail Express Route (Fast, 5 stops)
```bash
start_last_mile_simulator.bat ROUTE-RETAIL-001 1
```

**Stops**:
1. Parkdale Mall
2. Walmart Supercenter
3. Home Depot
4. Target
5. Lowe's

**Timing**: ~1.5 hours  
**Service**: 10-20 min/stop  
**Speeds**: 40-45 mph

---

#### Healthcare & Education Route (Slow zones, 6 stops)
```bash
start_last_mile_simulator.bat ROUTE-HEALTH-001 2
```

**Stops**:
1. CHRISTUS Hospital
2. Baptist Hospital
3. Medical Center
4. Lamar University Campus
5. University Library
6. City Hall

**Timing**: ~2 hours  
**Service**: 8-15 min/stop  
**Speeds**: 20-30 mph (slow zones)

---

#### Industrial & Logistics Route (Long service, 7 stops)
```bash
start_last_mile_simulator.bat ROUTE-IND-001 3
```

**Stops**:
1. Port of Beaumont
2. Logistics Hub
3. ExxonMobil Refinery
4. Industrial Park
5. Restaurant Supply
6. Hotel & Convention
7. Civic Center

**Timing**: ~3 hours  
**Service**: 15-30 min/stop  
**Speeds**: 35-45 mph

---

## 📡 What You'll See

### GPS Updates (Every 30 seconds)
```
🚗 Traveling to: Walmart Supercenter West
📏 Distance: 1.85 miles
🚦 Speed limit: 45 mph
📡 GPS pings: 15 (every 30 seconds)
🎯 Heading: 287.3°
  → 20% complete (38.2 mph)
  🚦 Slowing down: 18.5 mph
  → 40% complete (41.7 mph)
  → 60% complete (39.3 mph)
  → 80% complete (43.1 mph)
```

### Service Time (B2B Realistic)
```
📦 Arrived at: Home Depot Beaumont (Retail)
⏱️ Service time: 15 minutes
🚚 Unloading and processing delivery...
  • 1.0/15 min elapsed...
  • 3.0/15 min elapsed...
  • 5.0/15 min elapsed...
  ...
✓ Delivery complete!
```

---

## 🔍 Key Differences from Old Simulator

| Feature | Old | New (B2B) |
|---------|-----|-----------|
| GPS Interval | 5 sec | 30 sec ⭐ |
| Speed Units | km/h | mph ⭐ |
| Speed Range | 30-50 km/h | 20-60 mph |
| Routes | 4 mixed | 3 B2B only ⭐ |
| Service Time | 8-15 min | 8-30 min (type-based) ⭐ |
| Traffic Delays | Random 20% | Valhalla API only ⭐ |
| Residential | Yes | No (B2B only) ⭐ |

---

## 🎯 Testing Scenarios

### Scenario 1: Speed Limit Compliance
```bash
# Run healthcare route with slow zones (20-25 mph)
start_last_mile_simulator.bat ROUTE-HEALTH-001 2
```

**Watch for**:
- Speeds stay below 25 mph near hospitals
- Speeds stay below 20 mph near schools
- No artificial delays

---

### Scenario 2: Industrial Long Service Times
```bash
# Run industrial route with 15-30 min service
start_last_mile_simulator.bat ROUTE-IND-001 3
```

**Watch for**:
- Service times: 15-30 minutes at warehouses
- GPS updates every 30 seconds while stationary
- Forklift/receiving operations simulated

---

### Scenario 3: Multi-Vehicle B2B Fleet
```bash
# Terminal 1: Retail
start_last_mile_simulator.bat ROUTE-RETAIL-001 1

# Terminal 2: Healthcare
start_last_mile_simulator.bat ROUTE-HEALTH-001 2

# Terminal 3: Industrial
start_last_mile_simulator.bat ROUTE-IND-001 3
```

**Watch for**:
- All 3 routes running simultaneously
- Different service times per route type
- Independent ETA calculations

---

## 📊 Expected GPS Data

### 10-Minute Trip Example

**Old Simulator (5-second intervals)**:
- GPS pings: 120
- Database writes: 120
- Unrealistic frequency

**New B2B Simulator (30-second intervals)**:
- GPS pings: ~20 ⭐
- Database writes: ~20 ⭐
- Industry standard ⭐

---

## ✅ Validation Checklist

Run each route and verify:

### ROUTE-RETAIL-001
- [ ] 5 retail stops visited
- [ ] Service time: 10-20 minutes each
- [ ] Speed: 40-45 mph average
- [ ] GPS: Every 30 seconds
- [ ] No artificial delays

### ROUTE-HEALTH-001
- [ ] 6 stops (3 hospitals, 1 university, 1 government)
- [ ] Service time: 8-15 minutes each
- [ ] Speed: 20-30 mph (slow zones)
- [ ] GPS: Every 30 seconds
- [ ] Compliance with hospital/school zones

### ROUTE-IND-001
- [ ] 7 industrial/commercial stops
- [ ] Service time: 15-30 minutes each
- [ ] Speed: 35-45 mph average
- [ ] GPS: Every 30 seconds
- [ ] Longest total duration (~3 hours)

---

## 🐛 Troubleshooting

### "Shipment ROUTE-XXX not found"
**Solution**: Run `populate_test_data.bat` to create new B2B routes

### GPS updates too fast/slow
**Expected**: Every 30 seconds (not 5)  
**Verify**: Check console for "📡 GPS pings: X (every 30 seconds)"

### Speeds in km/h instead of mph
**Solution**: Updated simulator now uses MPH  
**Verify**: Look for "🚦 Speed limit: XX mph"

### Old routes (ROUTE-DW-001, ROUTE-RES-001) still in database
**Solution**: These are old test data. Use new routes:
- ROUTE-RETAIL-001
- ROUTE-HEALTH-001
- ROUTE-IND-001

---

## 📚 Updated Documentation

- **B2B_UPDATE_SUMMARY.md** - Complete change log
- **QUICKSTART.md** - Updated with new routes
- **TESTING.md** - B2B test scenarios
- **QUICK_REFERENCE.md** - New command reference

---

## 💡 Pro Tips

### Speed Up Testing
```bash
# Skip first 3 stops
start_last_mile_simulator.bat ROUTE-IND-001 3 3
```

### Monitor ETA Accuracy
- Watch for ETA changes with each GPS ping
- Compare estimated vs actual arrival times
- Note speed variations (±5 mph is normal)

### Test Valhalla Integration
- No artificial delays = rerouting is real
- Backend calls Valhalla for actual routes
- Traffic decisions based on real routing engine

---

**Quick Start**: Run `populate_test_data.bat` then `start_last_mile_simulator.bat ROUTE-RETAIL-001 1`

**Dashboard**: http://localhost:5173

**Focus**: B2B commercial logistics, not residential delivery
