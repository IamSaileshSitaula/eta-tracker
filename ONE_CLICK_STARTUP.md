# 🚀 One-Click Startup - Visual Guide

## What Happens When You Run `start_all.bat`

```
C:\Users\saile\OneDrive\Desktop\eta_tracker> .\start_all.bat
```

---

### ⏱️ Timeline (What You'll See)

```
0:00 - Master Script Window Opens
═════════════════════════════════════════════════════════════════
  ETA TRACKER - STARTING ALL COMPONENTS
═════════════════════════════════════════════════════════════════

[✓] Docker Desktop is running

[1/5] Starting PostgreSQL Database...
-----------------------------------------------
Starting PostgreSQL container...
✔ Container eta-tracker-db  Started
Waiting 10 seconds for PostgreSQL to initialize...
[✓] PostgreSQL started on port 5432
```

---

```
0:10 - Valhalla Window Opens (New Terminal)
═════════════════════════════════════════════════════════════════
  VALHALLA ROUTING ENGINE - DOCKER SETUP
═════════════════════════════════════════════════════════════════

[INFO] Docker is installed
[INFO] Using command: docker compose

[INFO] Downloading Texas OSM data...  ← FIRST RUN ONLY (10-15 min)
[INFO] Building Valhalla routing tiles...

✔ Container eta-tracker-valhalla  Started
[✓] Valhalla server running on port 8002
```

---

```
0:15 - Backend Window Opens (New Terminal)
═════════════════════════════════════════════════════════════════
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
═════════════════════════════════════════════════════════════════
```

---

```
0:18 - Frontend Window Opens (New Terminal)
═════════════════════════════════════════════════════════════════
VITE v6.0.1  ready in 1234 ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: http://192.168.1.100:3000/
  
  ➜  press h + enter to show help
═════════════════════════════════════════════════════════════════
```

---

```
0:21 - Back to Master Script (GPS Simulator Choice)
═════════════════════════════════════════════════════════════════
[5/5] GPS Simulator Options
-----------------------------------------------

The GPS Simulator is optional. Would you like to start it?

Available routes:
  1. ROUTE-RETAIL-001   (5 retail stops in Beaumont)
  2. ROUTE-HEALTH-001   (6 healthcare stops)
  3. ROUTE-IND-001      (7 industrial stops)
  4. Skip GPS Simulator

Enter your choice (1-4): _
```

### If You Choose Route 1:

```
0:22 - GPS Simulator Window Opens (New Terminal)
═════════════════════════════════════════════════════════════════
🚛 Unified GPS Simulator - Long Haul + Last Mile Delivery
═════════════════════════════════════════════════════════════════

📍 PHASE 1: Long-Haul Route (Dallas → Houston → Beaumont)
   Distance: 440.2 km
   Waypoints: 19
   Speed: 90 km/h (highway)

[2025-11-10 10:00:00] 📍 Dallas Distribution Center
✅ GPS Update #1 sent - 32.7767°N, 96.7970°W
...
═════════════════════════════════════════════════════════════════
```

---

```
0:25 - Master Script Shows Success Summary
═════════════════════════════════════════════════════════════════
  🎉 ALL COMPONENTS STARTED SUCCESSFULLY!
═════════════════════════════════════════════════════════════════

Running Services:
  ✓ PostgreSQL Database    - Port 5432  (Docker container)
  ✓ Valhalla Routing       - Port 8002  (Docker container)
  ✓ Backend API            - Port 5000  (Python/Flask)
  ✓ Frontend               - Port 3000  (React/Vite)
  ✓ GPS Simulator          - Active    (Sending GPS updates)

Access URLs:
  📊 Manager Dashboard:     http://localhost:3000
  📦 Customer Tracking:     http://localhost:3000/tracking/PO-98765
  🔧 Backend API:           http://localhost:5000
  🗺️  Valhalla Status:       http://localhost:8002/status

Each component is running in its own terminal window.
Close any terminal to stop that specific component.

Press Ctrl+C in this window to view shutdown options...
═════════════════════════════════════════════════════════════════
```

---

## 🖥️ Your Desktop Will Look Like This

```
┌────────────────────────────────────────────────────────────────┐
│ Taskbar:                                                       │
│ [Master Script] [Valhalla] [Backend] [Frontend] [GPS Sim]     │
└────────────────────────────────────────────────────────────────┘

Desktop Windows (5 total):

┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│ ⭐ MASTER SCRIPT    │  │ 🗺️ VALHALLA        │  │ 🔧 BACKEND API      │
│                     │  │                     │  │                     │
│ CONTROL MENU        │  │ Valhalla server     │  │ Flask running on    │
│ 1. Check Status     │  │ running on          │  │ http://0.0.0.0:5000 │
│ 2. Open Dashboard   │  │ port 8002           │  │                     │
│ 3. Open Tracking    │  │                     │  │ * Debug mode: on    │
│ 4. Start GPS Sim    │  │ Ready for routing   │  │                     │
│ 5. Stop All         │  │ requests...         │  │ Waiting for         │
│ 6. Exit             │  │                     │  │ requests...         │
└─────────────────────┘  └─────────────────────┘  └─────────────────────┘

┌─────────────────────┐  ┌─────────────────────┐
│ ⚛️ FRONTEND         │  │ 📍 GPS SIMULATOR    │
│                     │  │                     │
│ VITE v6.0.1         │  │ [10:00:00] Dallas   │
│ ➜ Local:            │  │ ✅ Update #1 sent   │
│   localhost:3000    │  │                     │
│                     │  │ [10:05:00] I-45 S   │
│ ➜ Network:          │  │ ✅ Update #2 sent   │
│   192.168.1.100     │  │                     │
└─────────────────────┘  └─────────────────────┘
```

---

## 🎮 Using the Control Menu

Once everything is running, you see:

```
═════════════════════════════════════════════════════════════════
  CONTROL MENU
═════════════════════════════════════════════════════════════════

  1. Check Status (all services)
  2. Open Manager Dashboard in browser
  3. Open Customer Tracking in browser
  4. Start GPS Simulator (if not running)
  5. Stop All Services
  6. Exit (keep services running)

Enter your choice (1-6): _
```

### Option 1: Check Status

```
Enter your choice (1-6): 1

Checking all services...
-----------------------------------------------

PostgreSQL Database:
  ✓ eta-tracker-db - Up 2 minutes (healthy)

Valhalla Routing Engine:
  ✓ eta-tracker-valhalla - Up 2 minutes

Backend API (Port 5000):
  ✓ Listening on port 5000

Frontend (Port 3000):
  ✓ Listening on port 3000

-----------------------------------------------
```

### Option 2: Open Manager Dashboard

```
Enter your choice (1-6): 2

Opening Manager Dashboard in browser...
```
→ Browser opens at `http://localhost:3000`

### Option 5: Stop All Services

```
Enter your choice (1-6): 5

═════════════════════════════════════════════════════════════════
  STOPPING ALL SERVICES
═════════════════════════════════════════════════════════════════

Stopping Docker containers...
✔ Container eta-tracker-valhalla  Removed
✔ Container eta-tracker-db        Removed
[✓] Docker containers stopped

Stopping Backend and Frontend...
(You may need to close the terminal windows manually)

To forcefully kill all Python and Node processes:
  taskkill /F /IM python.exe
  taskkill /F /IM node.exe

Force kill all Python and Node processes? (y/n): y

SUCCESS: The process "python.exe" with PID 1234 has been terminated.
SUCCESS: The process "python.exe" with PID 5678 has been terminated.
SUCCESS: The process "node.exe" with PID 9012 has been terminated.
[✓] All processes killed

All services stopped.
Press any key to continue . . .
```

---

## ⚡ Quick Commands

### Start Everything
```powershell
.\start_all.bat
```

### Just Check if Running
```powershell
# PostgreSQL
docker ps --filter name=eta-tracker-db

# Valhalla  
docker ps --filter name=eta-tracker-valhalla

# Backend
Test-NetConnection localhost -Port 5000

# Frontend
Test-NetConnection localhost -Port 3000
```

### Stop Everything Manually
```powershell
# Stop Docker containers
docker compose down

# Kill Python processes (Backend + GPS Sim)
taskkill /F /IM python.exe

# Kill Node processes (Frontend)
taskkill /F /IM node.exe
```

---

## 🎯 Recommended Workflow

### First Time Setup:
1. Run `.\start_all.bat`
2. Wait for Valhalla to download Texas OSM data (10-15 min) ☕
3. Choose a GPS route to test
4. Open browser: http://localhost:3000
5. Watch truck move on map!

### Daily Development:
1. Run `.\start_all.bat` (< 30 seconds startup)
2. Skip GPS simulator (option 4)
3. Work on your code
4. GPS simulator runs in cached tile mode (instant)

### When Finished:
1. Press any key in Master Script window
2. Choose "5. Stop All Services"
3. Confirm force kill: `y`
4. All windows close automatically

---

## 🆘 Troubleshooting

### "Docker Desktop is not running!"

**Solution:**
1. Open Docker Desktop from Start Menu
2. Wait for "Docker Desktop is running" status
3. Run `.\start_all.bat` again

---

### Windows Already Open

If you run `.\start_all.bat` when services are already running:

```
[1/5] Starting PostgreSQL Database...
-----------------------------------------------
[✓] PostgreSQL already running

[2/5] Starting Valhalla Routing Engine...
-----------------------------------------------
[✓] Valhalla already running on port 8002

[3/5] Starting Backend API...
-----------------------------------------------
[✓] Backend API already running on port 5000

[4/5] Starting Frontend (React + Vite)...
-----------------------------------------------
[✓] Frontend already running on port 3000
```

The script is **smart** - it won't create duplicate processes!

---

### Port Already in Use

If another app is using required ports:

```
Error: bind: address already in use
```

**Find what's using the port:**
```powershell
# Check port 5432 (PostgreSQL)
netstat -ano | findstr :5432

# Check port 5000 (Backend)
netstat -ano | findstr :5000

# Check port 3000 (Frontend)
netstat -ano | findstr :3000

# Check port 8002 (Valhalla)
netstat -ano | findstr :8002
```

**Kill the process:**
```powershell
# Get PID from netstat output, then:
taskkill /F /PID <PID_NUMBER>
```

---

## 📊 What Each Window Shows

### Master Script Window
- Startup progress
- Service status checks
- Interactive control menu
- Shutdown options

### Valhalla Window
- OSM data download progress (first run)
- Tile building progress
- Server startup messages
- Ready status

### Backend Window
- Database connection status
- Valhalla connection status
- Weather API status
- HTTP request logs
- Error messages (if any)

### Frontend Window
- Vite build output
- Local/Network URLs
- HMR (Hot Module Reload) updates
- Compilation errors (if any)

### GPS Simulator Window
- Current phase (Long-haul or Last-mile)
- GPS coordinates being sent
- Stop completions
- Journey progress

---

## 🎉 Success Indicators

You know everything is working when:

✅ **5 terminal windows are open** (Master + 4 services)  
✅ **Master script shows all green checkmarks**  
✅ **Browser shows map at localhost:3000**  
✅ **Truck icon moves on map** (if GPS simulator running)  
✅ **No red error messages** in any window  

**Now you're ready to develop! 🚀**
