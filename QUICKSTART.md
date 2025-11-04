# 🚀 Quick Start Guide - ETA Tracker

Get up and running with comprehensive test data in 5 minutes!

---

## 📋 Prerequisites

- ✅ Python 3.8+ installed
- ✅ Node.js 16+ installed  
- ✅ PostgreSQL 12+ installed and running
- ✅ Git installed (for cloning)

---

## ⚡ Quick Setup (5 Minutes)

### Step 1: Clone Repository

```bash
git clone https://github.com/IamSaileshSitaula/eta-tracker.git
cd eta-tracker
```

### Step 2: Database Setup

```bash
# Create database
psql -U postgres -c "CREATE DATABASE eta_tracker;"

# Enable PostGIS extension
psql -U postgres -d eta_tracker -c "CREATE EXTENSION postgis;"

# Initialize schema
psql -U postgres -d eta_tracker -f data/init_db.sql
```

### Step 3: Configure Environment

Create `.env` file in project root:

```env
# Database
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/eta_tracker

# API Settings
API_URL=http://localhost:5000
FLASK_ENV=development

# Optional: External APIs
GEMINI_API_KEY=your_api_key_here
VALHALLA_URL=http://localhost:8002
```

### Step 4: Install Dependencies

**Backend:**
```bash
pip install -r requirements.txt
```

**Frontend:**
```bash
npm install
```

### Step 5: Populate Test Data

```bash
# Windows
populate_test_data.bat

# Linux/Mac  
python create_test_data.py
```

**Creates:**
- 2 Organizations (FastTrack Logistics, QuickShip Express)
- 5 Vehicles (3 trucks, 2 vans)
- 4 Shipment routes with 20+ stops
- Initial GPS positions at Beaumont DC

---

## 🎮 Running the Application

### Option A: Quick Test (Single Terminal)

**Windows:**
```bash
# 1. Start backend (Terminal 1)
start_backend.bat

# 2. Start frontend (Terminal 2)
npm run dev

# 3. Start simulator (Terminal 3)
start_last_mile_simulator.bat ROUTE-DW-001 1
```

**Linux/Mac:**
```bash
# 1. Start backend
python backend/app.py &

# 2. Start frontend
npm run dev &

# 3. Start simulator
python simulate_last_mile.py --route ROUTE-DW-001 --vehicle 1
```

### Option B: Multi-Route Testing

```bash
# Terminal 1: Express Route (Downtown + West End)
start_last_mile_simulator.bat ROUTE-DW-001 1

# Terminal 2: Residential Route (8 stops)
start_last_mile_simulator.bat ROUTE-RES-001 4

# Terminal 3: Full Coverage (10 stops)
start_last_mile_simulator.bat ROUTE-FULL-001 3
```

---

## 🌐 Access Points

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:5173 | React dashboard |
| **Backend API** | http://localhost:5000 | REST API |
| **Health Check** | http://localhost:5000/health | Status endpoint |
| **API Docs** | http://localhost:5000/v1/docs | API documentation |

---

## 📊 Test Routes Overview

### 1. Downtown Express (`ROUTE-DW-001`)
- **Duration**: ~45 min
- **Stops**: 5
- **Distance**: ~8 km
- **Best for**: Quick testing, basic routing

```bash
start_last_mile_simulator.bat ROUTE-DW-001 1
```

### 2. Residential (`ROUTE-RES-001`)
- **Duration**: ~2 hours
- **Stops**: 8  
- **Distance**: ~12 km
- **Best for**: Multi-stop optimization

```bash
start_last_mile_simulator.bat ROUTE-RES-001 4
```

### 3. North-South Corridor (`ROUTE-NS-001`)
- **Duration**: ~1.5 hours
- **Stops**: 6
- **Distance**: ~15 km
- **Best for**: Cross-city routing

```bash
start_last_mile_simulator.bat ROUTE-NS-001 2
```

### 4. Full Coverage (`ROUTE-FULL-001`)
- **Duration**: ~3 hours
- **Stops**: 10
- **Distance**: ~22 km
- **Best for**: Complete system testing

```bash
start_last_mile_simulator.bat ROUTE-FULL-001 3
```

---

## 🎯 First Test Scenario

### Watch a Complete Delivery Cycle

1. **Start Everything**
   ```bash
   # Terminal 1
   start_backend.bat
   
   # Terminal 2  
   npm run dev
   
   # Terminal 3
   start_last_mile_simulator.bat ROUTE-DW-001 1
   ```

2. **Open Dashboard**
   - Navigate to http://localhost:5173
   - Click "Dashboard"
   - Select "Downtown + West End Express"

3. **Watch Real-Time Updates**
   - 🚚 Vehicle moves on map
   - 📍 GPS updates every 5 seconds
   - ⏱️ ETA recalculates automatically
   - 📦 Stops completed in sequence
   - 🚦 Random traffic delays

4. **Observe Features**
   - Stop markers change color (gray → blue → green)
   - Route polyline shows path
   - Current position highlighted
   - Service time delays at each stop
   - Progress bar updates

---

## 🔍 What to Look For

### ✅ Expected Behavior

**GPS Updates:**
- Position updates every 5 seconds
- Speed varies (30-50 km/h in city)
- Occasional slowdowns (traffic lights, turns)
- Stops at delivery locations

**ETA Calculations:**
- Updates automatically on each GPS point
- Accounts for traffic delays
- Adjusts for service time at stops
- Shows realistic arrival times

**Rerouting:**
- Traffic delays detected (20% probability)
- Delays range from 30s to 3 minutes
- Console shows "⚠️ Traffic delay: XXs"
- Backend may suggest alternative routes

**Service Time:**
- 8-15 minutes per stop
- Vehicle stays stationary
- "📦 Delivering packages..." message
- Progress counter during service

---

## 🐛 Common Issues

### Backend Won't Start

**Error**: `Cannot connect to database`

**Solution**:
```bash
# Check PostgreSQL is running
psql -U postgres -c "SELECT version();"

# Verify database exists
psql -U postgres -c "\l" | grep eta_tracker

# Check .env has correct DATABASE_URL
cat .env | grep DATABASE_URL
```

---

### Simulator Says "Shipment Not Found"

**Error**: `Shipment ROUTE-XXX-XXX not found`

**Solution**:
```bash
# Check if test data exists
psql -U postgres -d eta_tracker -c "SELECT ref FROM shipments;"

# If empty, populate test data
populate_test_data.bat
```

---

### Frontend Not Showing Updates

**Error**: Map not updating, no vehicle movement

**Solution**:
1. Check browser console for errors (F12)
2. Verify WebSocket connection in Network tab
3. Ensure simulator is running (check Terminal 3)
4. Refresh page (Ctrl+R)

---

### Port Already in Use

**Error**: `Address already in use: 5000` or `5173`

**Solution**:
```bash
# Find process using port (Windows)
netstat -ano | findstr :5000
taskkill /PID [process_id] /F

# Find process using port (Linux/Mac)
lsof -ti:5000 | xargs kill -9
```

---

## 📚 Next Steps

### 1. Explore Dashboard Features
- Switch between shipments
- Click on stops for details
- Monitor ETA accuracy
- Watch route optimization

### 2. Test Rerouting
- Let simulator run and watch for traffic delays
- Note ETA changes
- Check backend logs for reroute suggestions

### 3. Run Multiple Routes
- Start 2-3 simulators simultaneously
- Compare performance
- Monitor database load

### 4. Read Full Documentation
- [README.md](README.md) - Project overview
- [TESTING.md](TESTING.md) - Comprehensive testing guide
- [CONTRIBUTING.md](CONTRIBUTING.md) - Development guidelines

### 5. Customize Test Data
- Edit `create_test_data.py`
- Add more locations
- Create custom routes
- Adjust timing parameters

---

## 🎓 Learning Path

### Beginner
1. ✅ Run single route test (ROUTE-DW-001)
2. ✅ Watch GPS updates in dashboard
3. ✅ Observe ETA recalculation
4. ✅ See traffic delays happen

### Intermediate
1. Run multiple routes simultaneously
2. Test route restart from mid-point
3. Monitor backend logs for rerouting
4. Analyze ETA accuracy

### Advanced
1. Create custom test routes
2. Implement new rerouting scenarios
3. Add performance monitoring
4. Build automated test suite

---

## 💡 Tips & Tricks

### Speed Up Testing

```bash
# Start from middle of route (skip first 5 stops)
start_last_mile_simulator.bat ROUTE-FULL-001 3 5
```

### Multiple Instances

```bash
# Run different routes on different vehicles
start_last_mile_simulator.bat ROUTE-DW-001 1
start_last_mile_simulator.bat ROUTE-RES-001 4
start_last_mile_simulator.bat ROUTE-NS-001 2
```

### Custom Speeds

Edit `simulate_last_mile.py`:
```python
# Line ~120: Adjust speed range
base_speed = random.uniform(35, 45)  # Default
base_speed = random.uniform(50, 70)  # Faster testing
```

### Traffic Probability

Edit `simulate_last_mile.py`:
```python
# Line ~80: Adjust traffic chance
if random.random() < 0.2:  # 20% default
if random.random() < 0.5:  # 50% more traffic
```

---

## 📞 Getting Help

- 📖 [Documentation](README.md)
- 🐛 [Report Issues](https://github.com/IamSaileshSitaula/eta-tracker/issues)
- 💬 [Discussions](https://github.com/IamSaileshSitaula/eta-tracker/discussions)

---

## ✨ Success Checklist

Before proceeding with development, verify:

- [ ] Backend starts without errors
- [ ] Frontend loads at http://localhost:5173
- [ ] Database has 4 test routes
- [ ] Simulator connects to backend
- [ ] GPS updates appear on map
- [ ] ETA recalculates automatically
- [ ] Traffic delays trigger properly
- [ ] Service time delays work
- [ ] All stops complete successfully

---

**Ready to optimize last-mile delivery! 🚚💨**

For comprehensive testing scenarios, see [TESTING.md](TESTING.md)
