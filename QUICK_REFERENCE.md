# 🚀 Quick Reference - ETA Tracker Test Infrastructure

**One-page reference for test data and simulation**

---

## ⚡ Quick Commands

### Setup (One-Time)
```bash
verify_setup.bat              # Check system configuration
populate_test_data.bat        # Create test data (2 orgs, 5 vehicles, 4 routes, 20+ stops)
```

### Running Tests
```bash
# Terminal 1: Backend
start_backend.bat

# Terminal 2: Frontend  
npm run dev

# Terminal 3: Simulator (choose one)
start_last_mile_simulator.bat ROUTE-DW-001 1     # Express (5 stops, 45 min)
start_last_mile_simulator.bat ROUTE-RES-001 4    # Residential (8 stops, 2 hrs)
start_last_mile_simulator.bat ROUTE-NS-001 2     # North-South (6 stops, 1.5 hrs)
start_last_mile_simulator.bat ROUTE-FULL-001 3   # Full Coverage (10 stops, 3 hrs)
```

### Dashboard
```
http://localhost:5173
```

---

## 🗺️ Test Routes

| Route | Stops | Time | Distance | Use Case |
|-------|-------|------|----------|----------|
| **ROUTE-DW-001** | 5 | 45 min | ~8 km | Quick testing |
| **ROUTE-RES-001** | 8 | 2 hrs | ~12 km | Multi-stop optimization |
| **ROUTE-NS-001** | 6 | 1.5 hrs | ~15 km | Cross-city routing |
| **ROUTE-FULL-001** | 10 | 3 hrs | ~22 km | Complete system test |

---

## 📍 Beaumont Locations (20 Total)

| Neighborhood | Count | Example Locations |
|-------------|-------|-------------------|
| **Downtown** | 3 | City Hall, Convention Center, Civic Center |
| **West End** | 3 | Community Center, Hospital, Plaza |
| **South End** | 3 | Library, Memorial Park, Shopping Center |
| **North End** | 3 | High School, Sports Complex, North Mall |
| **East End** | 3 | Medical Plaza, Senior Center, Recreation Center |
| **Residential** | 2 | Oak Drive, Maple Street |
| **Industrial** | 3 | Industrial Park, Distribution Center, Warehouse |

---

## 🎮 Simulator Features

- **GPS Updates**: Every 5 seconds
- **Speed**: 30-50 km/h (city driving)
- **Traffic Delays**: 20% probability, 30-180s duration
- **Service Time**: 8-15 minutes per stop
- **Mid-Route Restart**: Use `--start` parameter

**Example**: Resume from stop 5
```bash
start_last_mile_simulator.bat ROUTE-FULL-001 3 5
```

---

## 🧪 Common Test Scenarios

### 1. Basic Tracking Test
```bash
start_backend.bat
npm run dev
start_last_mile_simulator.bat ROUTE-DW-001 1
# Open: http://localhost:5173
```

### 2. Multi-Vehicle Test
```bash
# Terminal 1
start_last_mile_simulator.bat ROUTE-DW-001 1

# Terminal 2
start_last_mile_simulator.bat ROUTE-RES-001 4

# Terminal 3
start_last_mile_simulator.bat ROUTE-FULL-001 3
```

### 3. Traffic Delay Test
```bash
# Run any route and watch for "⚠️ Traffic delay" messages
start_last_mile_simulator.bat ROUTE-NS-001 2
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| **Backend not responding** | Run `start_backend.bat` |
| **Shipment not found** | Run `populate_test_data.bat` |
| **GPS not updating** | Check browser console (F12) |
| **Port in use** | Kill process: `taskkill /PID [pid] /F` |

---

## 📚 Documentation

| File | Purpose |
|------|---------|
| **QUICKSTART.md** | 5-minute setup guide |
| **TESTING.md** | Comprehensive testing guide |
| **TEST_DATA_SUMMARY.md** | Infrastructure details |
| **COMPLETION_SUMMARY.md** | Full project summary |

---

## ✅ Success Checklist

Before testing:
- [ ] Backend running (port 5000)
- [ ] Frontend running (port 5173)
- [ ] Test data populated (4 routes)
- [ ] Simulator connected
- [ ] Dashboard showing updates

---

## 🎯 Expected Behavior

When simulator runs:
- ✅ GPS position updates every 5 seconds
- ✅ Vehicle moves stop-by-stop on map
- ✅ ETA recalculates automatically
- ✅ Traffic delays appear randomly
- ✅ Service time delays at each stop
- ✅ Stops marked complete (gray → blue → green)

---

## 💡 Tips

**Speed up testing**:
```bash
# Skip first 5 stops
start_last_mile_simulator.bat ROUTE-FULL-001 3 5
```

**Increase traffic**:
Edit `simulate_last_mile.py` line 80:
```python
if random.random() < 0.5:  # 50% instead of 20%
```

**Faster speeds**:
Edit `simulate_last_mile.py` line 120:
```python
base_speed = random.uniform(50, 70)  # Faster
```

---

## 📞 Help

- 📖 Full docs: [README.md](README.md)
- 🐛 Issues: https://github.com/IamSaileshSitaula/eta-tracker/issues
- 💬 Discussions: https://github.com/IamSaileshSitaula/eta-tracker/discussions

---

**Quick Reference v1.0 | Last Updated: 2025**
