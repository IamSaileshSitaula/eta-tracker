# 🚚 ETA Tracker - Real-Time Logistics Intelligence Platform

> **A production-ready, full-stack shipment tracking system with intelligent route planning, live GPS tracking, and adaptive ETA prediction powered by Valhalla routing engine.**

## 🎯 Overview

ETA Tracker is a comprehensive B2B logistics platform that bridges the gap between logistics managers and customers through real-time shipment visibility. The system intelligently combines GPS tracking, weather data, traffic conditions, and routing optimization to provide accurate, confidence-scored ETAs updated every 30 seconds.

**Built for two distinct user journeys:**

1. **Logistics Managers** - Plan routes, create shipments, monitor live tracking, and optimize deliveries
2. **Customers** - Track their shipments in real-time with confidence-scored ETAs and delay explanations

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![TypeScript](https://img.shields.io/badge/TypeScript-5.8-blue)
![React](https://img.shields.io/badge/React-19.2-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![Valhalla](https://img.shields.io/badge/Valhalla-Routing-orange)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)

## 📚 Table of Contents

- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Feature Deep Dive](#-feature-deep-dive)
- [User Experience Flow](#-user-experience-flow)
- [Data Flow & Interactions](#-data-flow--interactions)
- [Installation & Setup](#-installation--setup)
- [API Reference](#-api-reference)
- [Testing](#-testing)
- [Contributing](#-contributing)

## 📖 Additional Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - 🚀 Get started in 5 minutes with test data
- **[TESTING.md](TESTING.md)** - 🧪 Comprehensive testing guide with scenarios
- **[IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)** - 🔧 Technical implementation details
- **[REMAINING.md](REMAINING.md)** - 📋 Features to be implemented
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - 🤝 How to contribute
- **[CHANGELOG.md](CHANGELOG.md)** - 📝 Version history

## ✨ Key Features

### 🎛️ **Manager Dashboard** - Complete Route Planning & Operations Control

#### **Route Creation & Planning**
- **📍 Structured Address Input** - Professional 6-field address entry system
  - Street number, street name, unit/apt, city, state, ZIP code
  - Real-time validation and autocomplete
  - Facility quick-select for warehouses
  
- **🗺️ Unlimited Intermediate Stops** - Add as many stops as needed
  - Drag-to-reorder stop sequence
  - Delete/edit stops dynamically
  - Geocoding with OpenStreetMap Nominatim
  
- **🧪 Load Test Data** - One-click synthetic route loading
  - Pre-configured Texas routes (Dallas→Houston, San Antonio→El Paso, Austin→Corpus Christi)
  - Instant form population for Phase 1 testing
  - Includes intermediate stops with realistic addresses

- **📦 Load Existing Shipments** - Edit and modify live shipments
  - Load any shipment by tracking number (e.g., PO-98765)
  - Parses all stops from database into editable form
  - Create modified versions of existing routes
  - View historical shipment data

#### **Route Optimization & Intelligence**
- **🚚 Valhalla Routing Engine** - Professional truck routing
  - Height, width, weight constraints
  - Toll avoidance options
  - Hazmat routing
  - Alternative route calculation (fastest, shortest, no-tolls)
  
- **� Real-Time ETA Calculations** - EWMA-based predictions
  - Traffic-aware routing
  - Weather impact analysis
  - Confidence scoring (high/medium/low)
  - Updated every 30 seconds

- **🔄 Reroute Management** - Intelligent reroute suggestions
  - Valhalla-powered alternative routes
  - Time saved calculations
  - One-click reroute acceptance
  - Automatic customer notification

#### **Live Monitoring & Control**
- **📡 GPS Vehicle Tracking** - Real-time fleet monitoring (30-second intervals)
- **🌐 Live Data Fusion** - Weather, traffic, congestion integration
- **📈 Performance Analytics** - ETA confidence trends and accuracy metrics
- **🎯 One-Click Deployment** - Generate tracking numbers and push to customers

### 👁️ **Customer Tracking View** - Real-Time Shipment Visibility

- **📡 Live GPS Tracking** - Vehicle position updates every 30 seconds via WebSocket
- **⏱️ Dynamic ETAs** - Confidence-scored arrival predictions
  - High confidence: ±5 minutes
  - Medium confidence: ±15 minutes
  - Low confidence: ±30 minutes
  
- **🚦 Traffic Awareness** - Visual congestion indicators on route
- **🌦️ Weather Advisories** - Delay explanations with severity levels
- **📱 Responsive Design** - Desktop, tablet, and mobile optimized
- **🔔 Real-Time Notifications** - Reroute alerts and delay updates

## 🏗️ System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FRONTEND LAYER                              │
│  ┌─────────────────┐    ┌──────────────────┐   ┌─────────────────┐│
│  │ Manager Dashboard│    │  Customer Track  │   │  Map Component  ││
│  │  - Route Planner │    │  - Live Tracking │   │  - Leaflet Maps ││
│  │  - Load Existing │    │  - ETA Display   │   │  - Route Viz    ││
│  │  - Test Data     │    │  - Confidence    │   │  - GPS Markers  ││
│  └────────┬─────────┘    └────────┬─────────┘   └────────┬────────┘│
│           │                       │                       │         │
│           └───────────────────────┴───────────────────────┘         │
│                                   │                                 │
│                     React 19 + TypeScript + Vite                    │
└───────────────────────────────────┼─────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │    WebSocket (Socket.io)      │
                    │    REST API (JSON)            │
                    └───────────────┬───────────────┘
                                    │
┌───────────────────────────────────┼─────────────────────────────────┐
│                        BACKEND LAYER                                │
│  ┌─────────────────────────────────────────────────────────────────┤
│  │              Flask Application (app.py)                         │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐   │
│  │  │   API Routes  │  │ Socket.io Hub│  │  Business Logic    │   │
│  │  │ /v1/shipments │  │ - Subscribe  │  │ - ETA Calculation  │   │
│  │  │ /v1/positions │  │ - Broadcast  │  │ - Reroute Engine   │   │
│  │  │ /v1/reroutes  │  │ - GPS Events │  │ - Confidence Score │   │
│  │  └──────────────┘  └──────────────┘  └────────────────────┘   │
│  └────┬─────────────────────┬─────────────────────┬───────────────┘
│       │                     │                     │                 │
│       ▼                     ▼                     ▼                 │
│  ┌──────────┐      ┌───────────────┐     ┌─────────────────┐      │
│  │ Database │      │ Valhalla      │     │ External APIs   │      │
│  │  Layer   │      │ Routing       │     │ - Weather       │      │
│  │ (db.py)  │      │ Client        │     │ - Traffic       │      │
│  └────┬─────┘      └───────┬───────┘     └────────┬────────┘      │
└───────┼────────────────────┼──────────────────────┼────────────────┘
        │                    │                      │
┌───────┴────────────────────┴──────────────────────┴────────────────┐
│                    INFRASTRUCTURE LAYER                             │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐ │
│  │   PostgreSQL     │  │  Valhalla Docker │  │  OpenStreetMap   │ │
│  │   Database       │  │  Routing Engine  │  │  Nominatim API   │ │
│  │  - PostGIS       │  │  - Port 8002     │  │  - Geocoding     │ │
│  │  - Port 5432     │  │  - Texas OSM     │  │  - Free Tier     │ │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### Technology Stack

#### **Frontend Technologies**
- **React 19.2** - Modern UI framework with concurrent features
- **TypeScript 5.8** - Type-safe development
- **Vite** - Lightning-fast build tool and dev server
- **React Router** - Client-side routing
- **Socket.io Client** - Real-time WebSocket communication
- **Leaflet 1.9** - Interactive map visualization
- **Tailwind CSS** - Utility-first styling framework

#### **Backend Technologies**
- **Python 3.8+** - Core backend language
- **Flask** - Lightweight WSGI web framework
- **Flask-SocketIO** - WebSocket support with Socket.io protocol
- **psycopg2** - PostgreSQL database adapter
- **python-dotenv** - Environment variable management
- **requests** - HTTP client for external APIs

#### **Infrastructure & Services**
- **PostgreSQL 15** - Primary database with PostGIS extension
- **Docker** - Containerization for Valhalla and PostgreSQL
- **Valhalla Routing Engine** - Professional truck routing (Docker container)
- **OpenStreetMap Nominatim** - Geocoding service (free tier)

#### **Key Technical Features**
- 📡 **30-Second GPS Intervals** - Industry-standard tracking frequency (83% reduction in database load)
- 🇺🇸 **MPH Speed Limits** - Zone-based speeds (20-60 mph) for realistic simulation
- 📊 **EWMA ETA Prediction** - Exponentially Weighted Moving Average for accurate ETAs
- 🗺️ **Truck Routing Constraints** - Height (4.1m), Width (2.5m), Weight (15t)
- 🌐 **Live Data Fusion** - Weather + Traffic + Congestion = Adaptive ETAs
- 🔄 **Real-Time Synchronization** - WebSocket broadcasting to all connected clients

## � Feature Deep Dive

### **1. Manager Dashboard - Route Planning Workflow**

#### **Creating a New Shipment**

**UX Flow:**
1. Manager opens Dashboard (`/` route)
2. Sees collapsible form sections: Origin → Destination → Intermediate Stops
3. Can fill addresses manually OR use quick-load features
4. System geocodes addresses in real-time
5. Clicks "Generate Tracking & Launch" to create shipment
6. Receives tracking number to share with customer

**Data Flow (Frontend → Backend → Database):**
```
1. User fills Origin Address form
   ├─ Frontend: originComponents state {streetNumber, streetName, city, state, zip}
   ├─ Frontend: Builds full address string "123 Main St, Austin, TX 78701"
   └─ Frontend: Calls geocodeAddress() → OpenStreetMap Nominatim API
       └─ Returns: {lat: 30.2672, lon: -97.7431, label: "full address"}

2. User fills Destination Address (same process as Origin)

3. User adds Intermediate Stops (optional)
   ├─ Frontend: plannerMidStops array state
   ├─ Each stop geocoded independently
   └─ Stops can be reordered with ↑↓ buttons

4. User clicks "Generate Tracking & Launch"
   ├─ Frontend: POST /v1/shipments
   │   └─ Payload: {
   │         ref: "PO-12345" (auto-generated),
   │         stops: [{seq: 1, name: "origin", lat, lon, arrival_time}, ...],
   │         promised_eta: calculated timestamp
   │       }
   │
   ├─ Backend: app.py receives request
   │   ├─ db.create_shipment() inserts into PostgreSQL
   │   │   ├─ Table: shipments (ref, vehicle_id, org_id, promised_eta)
   │   │   └─ Table: stops (shipment_id, seq, name, lat, lon, arrival_time)
   │   │
   │   ├─ Calculates ETAs using Valhalla routing
   │   │   └─ valhalla_client.calculate_route() → Valhalla API (port 8002)
   │   │       └─ Returns: route_geometry, distance_km, duration_min
   │   │
   │   └─ Returns: {id: 1, tracking_number: "PO-12345", stops: [...]}
   │
   └─ Frontend: Displays tracking number with copy button
       └─ Updates lastCreatedTracking state
```

#### **Loading Existing Shipment (NEW Feature)**

**UX Flow:**
1. Manager sees "Load Existing" input at top of form
2. Types tracking number (e.g., "PO-98765") or clicks quick button "📦 Load PO-98765"
3. System fetches shipment from database
4. All form fields populate automatically
5. All address sections expand for visibility
6. Manager can edit addresses, add/remove stops
7. Clicking "Generate Tracking & Launch" creates a NEW shipment (modified copy)

**Data Flow (Load Existing):**
```
1. User enters "PO-98765" and clicks Load
   ├─ Frontend: handleLoadExistingShipment("PO-98765")
   │
   ├─ GET /v1/shipments?ref=PO-98765
   │   └─ Returns: [{id: 1, ref: "PO-98765", vehicle_id: 1, ...}]
   │
   ├─ GET /v1/shipments/1/status
   │   └─ Returns: {
   │         stops: [
   │           {id: 1, name: "123 Main St, Austin, TX", lat: 30.27, lon: -97.74},
   │           {id: 2, name: "456 Elm St, Houston, TX", lat: 29.76, lon: -95.37}
   │         ],
   │         vehicle_position: {lat, lon},
   │         eta_seconds: 3600
   │       }
   │
   ├─ Frontend: Parses addresses
   │   ├─ parseAddressComponents("123 Main St, Austin, TX")
   │   │   └─ Returns: {streetNumber: "123", streetName: "Main St", city: "Austin", state: "TX"}
   │   │
   │   ├─ Sets originComponents state
   │   ├─ Sets destinationComponents state
   │   ├─ Sets plannerMidStops array
   │   └─ Sets plannerPreviewStops for map visualization
   │
   └─ UI: All sections expand, form fully populated
```

#### **Loading Test Data (NEW Feature)**

**UX Flow:**
1. Manager clicks "🧪 Load Test Data" button
2. System randomly selects one of 3 pre-configured Texas routes
3. Form instantly populates with realistic addresses
4. All sections expand automatically
5. Manager can immediately click "Generate Tracking & Launch"

**Data Flow (Test Data):**
```
Frontend only - no backend call
├─ handleLoadTestData()
├─ Selects random route from testRoutes array:
│   ├─ Dallas → Austin → Houston
│   ├─ San Antonio → El Paso
│   └─ Austin → Seguin → Corpus Christi
│
├─ Sets all form states:
│   ├─ setOriginComponents({streetNumber, streetName, city, state, zipCode, unit: ""})
│   ├─ setDestinationComponents({...})
│   └─ setPlannerMidStops([...])
│
└─ Expands all sections for visibility
```

### **2. Valhalla Routing Engine Integration**

**How It Works:**
```
Frontend Request → Backend → Valhalla Docker Container → Response

1. Manager creates route with truck constraints
   └─ Backend: valhalla_client.calculate_route()
       ├─ Builds Valhalla API request:
       │   {
       │     locations: [{lat, lon}, ...],
       │     costing: "truck",
       │     costing_options: {
       │       truck: {
       │         height: 4.1,      // meters (truck height limit)
       │         width: 2.5,       // meters (truck width limit)
       │         weight: 15,       // metric tons
       │         hazmat: false,
       │         use_tolls: 0.5    // toll avoidance factor
       │       }
       │     }
       │   }
       │
       ├─ POST http://localhost:8002/route
       │   └─ Valhalla calculates optimal truck route using Texas OSM data
       │       ├─ Avoids low bridges (height < 4.1m)
       │       ├─ Avoids narrow roads (width < 2.5m)
       │       ├─ Considers weight restrictions
       │       └─ Minimizes toll roads
       │
       └─ Returns: {
             trip: {
               legs: [{distance: 250.3, time: 14580}],
               summary: {length: 250.3, time: 14580}
             },
             route_geometry: "polyline encoded string"
           }

2. Backend calculates ETAs
   ├─ distance_km = 250.3 km
   ├─ duration_min = 14580 / 60 = 243 minutes (4 hours 3 minutes)
   ├─ Applies traffic multiplier (1.1x during peak hours)
   └─ Sets stop arrival times: origin + 243 min = destination ETA
```

### **3. Real-Time GPS Tracking & ETA Updates**

**UX Flow (Customer Tracking Page):**
1. Customer enters tracking number "PO-98765"
2. Map loads showing full route
3. Truck icon appears at current GPS position
4. Every 30 seconds: truck moves, ETAs update, confidence scores recalculate
5. If delays detected: weather/traffic advisory appears
6. If reroute happens: new route draws on map with notification

**Data Flow (Real-Time Updates):**
```
GPS Simulator (simulate_gps.py)
    ↓ Every 30 seconds
    ↓
POST /v1/positions
    └─ {shipment_id: 1, lat: 30.2672, lon: -97.7431, timestamp: "2025-11-04T12:00:00Z"}
    
Backend (app.py)
    ├─ db.update_vehicle_position() → PostgreSQL
    │   └─ UPDATE vehicles SET lat=30.2672, lon=-97.7431, last_seen=now()
    │
    ├─ Calculates remaining distance to destination
    │   └─ Uses haversine formula: distance between current position and destination
    │
    ├─ Recalculates ETA using EWMA (Exponentially Weighted Moving Average)
    │   ├─ Previous ETA: 3600 seconds
    │   ├─ Current speed: 65 mph
    │   ├─ Distance remaining: 50 km
    │   ├─ New ETA: (50 km / 65 mph) * 3600 = 2769 seconds
    │   └─ EWMA: 0.7 * new_eta + 0.3 * previous_eta = 3042 seconds
    │
    ├─ Calculates confidence score
    │   ├─ High: deviation < 5 minutes
    │   ├─ Medium: deviation < 15 minutes
    │   └─ Low: deviation > 15 minutes
    │
    └─ Broadcasts via Socket.io to all subscribed clients
        └─ socketio.emit('position_update', {
              shipment_id: 1,
              lat: 30.2672,
              lon: -97.7431,
              eta_seconds: 3042,
              confidence: "high"
            }, room='shipment_1')

Frontend (TrackingPage.tsx)
    ├─ Socket.io listener receives 'position_update' event
    ├─ Updates vehiclePosition state
    ├─ Updates ETA display
    ├─ Updates confidence badge color
    └─ Map re-renders with new truck marker position
```

### **4. Reroute Suggestion & Acceptance**

**UX Flow:**
1. Backend detects delay or optimization opportunity
2. Calls Valhalla to calculate alternative routes
   - Route 1: Fastest (default truck routing)
   - Route 2: Shortest distance
   - Route 3: No tolls
3. Sends reroute suggestion to Manager Dashboard
4. Manager sees modal with 3 options and time saved
5. Manager clicks "Accept Route 2"
6. Backend updates shipment route
7. Customer's map automatically redraws with new route

**Data Flow (Reroute):**
```
Backend Detects Delay
    ├─ Traffic API reports congestion on current route
    ├─ Calls valhalla_client.calculate_alternatives()
    │   └─ POST http://localhost:8002/route (3 separate requests)
    │       ├─ Request 1: {"costing": "truck"} → fastest route
    │       ├─ Request 2: {"costing": "truck", "shortest": true} → shortest distance
    │       └─ Request 3: {"costing": "truck", "use_tolls": 0.0} → no tolls
    │
    └─ Returns: [
          {id: 1, distance_km: 250, duration_min: 240, time_saved_min: 30},
          {id: 2, distance_km: 235, duration_min: 250, time_saved_min: 20},
          {id: 3, distance_km: 260, duration_min: 255, time_saved_min: 15}
        ]

POST /v1/reroute/suggest
    └─ Stores in database, broadcasts to managers via Socket.io

Manager Dashboard
    ├─ Receives 'reroute_suggested' Socket.io event
    ├─ Opens RerouteModal component
    └─ Shows 3 alternative routes with time saved

Manager Clicks "Accept Route 2"
    ↓
POST /v1/reroutes/2/accept
    ├─ Backend: db.accept_reroute(reroute_id=2, shipment_id=1)
    │   ├─ UPDATE shipments SET route_geometry = new_geometry
    │   └─ UPDATE stops SET eta_timestamp = recalculated ETAs
    │
    └─ Broadcasts 'reroute_accepted' to ALL clients (managers + customers)

Customer Tracking Page
    ├─ Receives 'reroute_accepted' Socket.io event
    ├─ Shows notification: "Route updated - New ETA: 4:30 PM"
    ├─ Map redraws with new route geometry
    └─ ETA badges update with new times
```

## �📦 Installation

## 🎨 User Experience Flow

### **Manager Dashboard Journey**

```
┌─────────────────────────────────────────────────────────────────────┐
│ MANAGER OPENS DASHBOARD                                             │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ 🚚 ETA Tracker - Manager Dashboard                             │ │
│ │ ─────────────────────────────────────────────────────────────── │ │
│ │                                                                 │ │
│ │ ┌─ Load Existing ─────────────────────────────────────────────┐│ │
│ │ │ Enter tracking #: [PO-98765        ] [Load]   📦 PO-98765  ││ │
│ │ └─────────────────────────────────────────────────────────────┘│ │
│ │                                                                 │ │
│ │ ▶ Origin Address                                                │ │
│ │ ▶ Destination Address                                           │ │
│ │ ▶ Intermediate Stops (0)                                        │ │
│ │                                                                 │ │
│ │ [🧪 Test Data]  [📦 Load PO-98765]                             │ │
│ │ [🚀 Generate Tracking & Launch]                                 │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│ USER CLICKS "📦 Load PO-98765"                                       │
│ ↓ ↓ ↓                                                               │
│                                                                      │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ ✅ FORM AUTO-POPULATES                                          │ │
│ │ ─────────────────────────────────────────────────────────────── │ │
│ │                                                                 │ │
│ │ ▼ Origin Address ──────────────────────────                    │ │
│ │   Street #: [123  ] Street Name: [Main St           ]         │ │
│ │   City: [Austin      ] State: [TX] ZIP: [78701]               │ │
│ │   ✓ Resolved: 123 Main St, Austin, TX 78701                   │ │
│ │                                                                 │ │
│ │ ▼ Destination Address ─────────────────────                    │ │
│ │   Street #: [456  ] Street Name: [Elm St            ]         │ │
│ │   City: [Houston     ] State: [TX] ZIP: [77002]               │ │
│ │   ✓ Resolved: 456 Elm St, Houston, TX 77002                   │ │
│ │                                                                 │ │
│ │ ▼ Intermediate Stops (1) ──────────────────                    │ │
│ │   Stop 1: 789 Oak Ave, San Antonio, TX 78205  [↑] [↓] [×]     │ │
│ │                                                                 │ │
│ │ ✅ Route ready with 3 stops                                     │ │
│ │ [🚀 Generate Tracking & Launch]                                 │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│ USER EDITS & CLICKS "GENERATE TRACKING"                             │
│ ↓ ↓ ↓                                                               │
│                                                                      │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ ✅ SHIPMENT CREATED                                             │ │
│ │ ─────────────────────────────────────────────────────────────── │ │
│ │                                                                 │ │
│ │ Latest Tracking Number: PO-12346                                │ │
│ │ [📋 Copy Tracking #]  [🔗 Open Tracking Page]                  │ │
│ │                                                                 │ │
│ │ ┌─ Map Preview ──────────────────────────────────────────────┐ │ │
│ │ │ 🗺️ Route: Austin → San Antonio → Houston                   │ │
│ │ │ 📍 3 stops | 250 km | ETA: 4h 30m                          │ │
│ │ └─────────────────────────────────────────────────────────────┘ │ │
│ └─────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### **Customer Tracking Journey**

```
┌─────────────────────────────────────────────────────────────────────┐
│ CUSTOMER ENTERS TRACKING NUMBER                                     │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ 🚚 Track Your Shipment                                          │ │
│ │ Enter tracking #: [PO-12346        ] [Track]                   │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│ ↓ ↓ ↓ CLICKS "TRACK"                                                │
│                                                                      │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ ✅ LIVE TRACKING VIEW                                           │ │
│ │ ─────────────────────────────────────────────────────────────── │ │
│ │                                                                 │ │
│ │ Tracking: PO-12346  |  Status: IN TRANSIT  |  🟢 High Confidence│ │
│ │                                                                 │ │
│ │ ┌─ Interactive Map ──────────────────────────────────────────┐ │ │
│ │ │                                                             │ │ │
│ │ │  ✓ [Austin] ────────────────────→ 🚚 Current Position      │ │ │
│ │ │        ↓                                                    │ │ │
│ │ │   [ ] San Antonio (ETA: 2:30 PM ±5 min)                    │ │ │
│ │ │        ↓                                                    │ │ │
│ │ │   [ ] Houston (ETA: 5:00 PM ±10 min)                       │ │ │
│ │ │                                                             │ │ │
│ │ │  Legend: ───── Route  🚚 Truck  ✓ Completed  [ ] Upcoming  │ │ │
│ │ └─────────────────────────────────────────────────────────────┘ │ │
│ │                                                                 │ │
│ │ 📊 Stop Details ───────────────────────────────────────────────│ │
│ │ ✅ Austin Distribution Center         | Departed: 10:00 AM     │ │
│ │ 🚚 En Route to San Antonio            | ETA: 2:30 PM ±5 min    │ │
│ │ ⏳ Houston Delivery Center             | ETA: 5:00 PM ±10 min   │ │
│ │                                                                 │ │
│ │ 🌦️ Weather Advisory ────────────────────────────────────────── │ │
│ │ ⚠️ Light rain in San Antonio - 10 min delay expected          │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│ ⏰ 30 SECONDS LATER - AUTO-UPDATE                                   │
│ ↓ ↓ ↓ (No page refresh needed - WebSocket update)                  │
│                                                                      │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ 🚚 TRUCK MOVED ON MAP                                           │ │
│ │ New position: Closer to San Antonio                             │ │
│ │ ETA updated: 2:28 PM ±5 min (2 min improvement)                │ │
│ │ Confidence: Still High 🟢                                       │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│ 🔔 REROUTE NOTIFICATION                                              │
│ ↓ ↓ ↓ (Manager accepted new route)                                  │
│                                                                      │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ 🔄 ROUTE UPDATED NOTIFICATION                                   │ │
│ │ ─────────────────────────────────────────────────────────────── │ │
│ │                                                                 │ │
│ │ Your delivery route has been updated for faster arrival!        │ │
│ │ New ETA: 4:45 PM (15 minutes earlier) ✨                        │ │
│ │ [View New Route]                                                │ │
│ │                                                                 │ │
│ │ Map automatically redraws with new route geometry...            │ │
│ └─────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

## 📦 Installation & Setup

### Prerequisites

**Required Software:**
- **Node.js** 16+ and npm - Frontend development and build
- **Python** 3.8+ - Backend runtime
- **PostgreSQL** 15+ - Database (or Docker container)
- **Docker Desktop** - Valhalla routing engine container
- **Git** - Version control

**Optional but Recommended:**
- **VS Code** - IDE with TypeScript support
- **Postman** - API testing
- **pgAdmin** - Database GUI

### Quick Start Guide

#### **Step 1: Clone Repository**
```bash
git clone https://github.com/IamSaileshSitaula/eta-tracker.git
cd eta_tracker
```

#### **Step 2: Install Frontend Dependencies**
```bash
npm install
```

This installs:
- React, TypeScript, Vite
- Socket.io client
- Leaflet mapping libraries
- Tailwind CSS
- React Router

#### **Step 3: Install Backend Dependencies**
```bash
pip install -r requirements.txt
```

This installs:
- Flask, Flask-SocketIO
- psycopg2 (PostgreSQL adapter)
- python-dotenv
- requests (for external APIs)

#### **Step 4: Set Up Environment Variables**

**Create `.env` file from template:**
```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

**Edit `.env` with your configuration:**
```bash
# Backend Server
SECRET_KEY=your-secret-key-here
FLASK_ENV=development

# Database (PostgreSQL) - Use Docker setup
DB_HOST=localhost
DB_PORT=5432
DB_NAME=eta_tracker
DB_USER=postgres
DB_PASSWORD=your_password_here

# Routing Engines
VALHALLA_URL=http://localhost:8002    # After Step 6
OSRM_URL=https://router.project-osrm.org  # Fallback

# Weather API (Optional)
OPENWEATHER_API_KEY=  # Get free key from openweathermap.org

# Traffic API (Optional)
TOMTOM_API_KEY=  # Get free key from developer.tomtom.com
```

#### **Step 5: Start PostgreSQL Database**

**Using Docker (Recommended):**
```bash
# Start PostgreSQL container
docker compose up -d postgres

# Wait 10 seconds for initialization
# Database automatically creates tables from init_db.sql
```

**Verify database is running:**
```bash
docker ps  # Should show eta-tracker-db container as "healthy"
```

**Database Schema:**
- Tables: `organizations`, `vehicles`, `shipments`, `stops`, `positions`, `reroutes`
- PostGIS extension enabled for geospatial queries
- Sample data: PO-98765 shipment with 3 stops (Beaumont → Houston → Dallas)

#### **Step 6: Set Up Valhalla Routing Engine**

Valhalla provides professional truck routing with height/weight/width constraints. **Highly recommended for Phase 1 testing.**

**First-Time Setup (15-20 minutes):**
```bash
# Windows
docker compose -f docker-compose.valhalla.yml up -d

# Linux/Mac
docker-compose -f docker-compose.valhalla.yml up -d
```

**What happens:**
1. Downloads Valhalla Docker image (~1 GB)
2. Downloads Texas OSM road data (~275 MB)
3. Builds routing tiles (one-time, 10-15 minutes)
4. Starts Valhalla server on port 8002

**Monitor progress:**
```bash
# Watch logs
docker logs eta-tracker-valhalla -f

# You'll see:
# - Downloading texas-latest.osm.pbf...
# - Building tiles...
# - Valhalla service started
```

**Verify Valhalla is working:**
```bash
# Check status endpoint
curl http://localhost:8002/status

# Should return: {"status":"ok"}
```

**Subsequent Starts (instant):**
```bash
# Tiles are cached - starts in seconds
docker start eta-tracker-valhalla
```

**Update `.env` file:**
```bash
VALHALLA_URL=http://localhost:8002
```

#### **Step 7: Start Backend API**

```bash
# Windows
start_backend.bat

# Linux/Mac
python backend/app.py
```

**You should see:**
```
============================================================
Live ETA & Delay Explanation System - Backend v1.0
============================================================

Starting server...
Database: Connected to PostgreSQL
Routing: Valhalla (Truck costing enabled)
  URL: http://localhost:8002

API Endpoints:
  GET/POST /v1/shipments
  POST   /v1/positions
  GET    /v1/shipments/<id>/status
  POST   /v1/reroute/suggest
  POST   /v1/reroutes/<id>/accept
  ...

 * Running on http://127.0.0.1:5000
```

**Keep this terminal open** - backend runs here.

#### **Step 8: Start Frontend Dev Server**

Open a **new terminal**:
```bash
npm run dev
```

**You should see:**
```
  VITE v6.4.1  ready in 394 ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: http://192.168.100.193:3000/
```

#### **Step 9: Open Application**

Navigate to:
```
http://localhost:3000
```

**You should see:**
- Manager Dashboard with route planning form
- "Load Existing" section with PO-98765 quick button
- Test Data button
- Interactive map

#### **Step 10: Test with Existing Data**

**Quick Test:**
1. Click "📦 Load PO-98765" button
2. Form populates with Beaumont → Houston → Dallas route
3. Click "🚀 Generate Tracking & Launch"
4. Copy tracking number
5. Go to "Customer Tracking" page
6. Enter tracking number
7. See live map with route

**Or Test with GPS Simulator:**
```bash
# Open new terminal
python simulate_gps.py PO-98765

# Simulates truck movement every 30 seconds
# Watch customer tracking page update in real-time
```

## 🔄 Data Flow & Interactions

### Complete Data Flow Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│ SHIPMENT CREATION FLOW                                                │
└──────────────────────────────────────────────────────────────────────┘

Manager Dashboard (React)
    │
    │ 1. User fills origin/destination/stops
    │    or clicks "Load PO-98765" or "Test Data"
    │
    ├─→ Frontend State Updates
    │   ├─ originComponents: {streetNumber, streetName, city, state, zip}
    │   ├─ destinationComponents: {...}
    │   └─ plannerMidStops: [...]
    │
    ├─→ 2. Geocoding (OpenStreetMap Nominatim)
    │   ├─ GET https://nominatim.openstreetmap.org/search?q=123+Main+St+Austin+TX
    │   └─ Returns: {lat: 30.2672, lon: -97.7431, display_name: "..."}
    │
    └─→ 3. User clicks "Generate Tracking & Launch"
        │
        ├─→ POST http://localhost:5000/v1/shipments
        │   Body: {
        │     ref: "PO-12346" (auto-generated),
        │     vehicle_id: 1,
        │     stops: [{seq: 1, name, lat, lon, arrival_time}, ...]
        │   }
        │
        └─→ Flask Backend (app.py)
            │
            ├─→ 4. Valhalla Routing Calculation
            │   ├─ valhalla_client.calculate_route()
            │   │   └─→ POST http://localhost:8002/route
            │   │       Body: {
            │   │         locations: [{lat, lon}, ...],
            │   │         costing: "truck",
            │   │         costing_options: {
            │   │           truck: {height: 4.1, width: 2.5, weight: 15}
            │   │         }
            │   │       }
            │   │
            │   └─ Returns: {
            │       distance_km: 250.3,
            │       duration_min: 243,
            │       route_geometry: "polyline_string"
            │     }
            │
            ├─→ 5. Database Operations (PostgreSQL)
            │   ├─ INSERT INTO shipments (ref, vehicle_id, org_id, promised_eta)
            │   │   └─ Returns: shipment_id = 1
            │   │
            │   ├─ INSERT INTO stops (shipment_id, seq, name, lat, lon, arrival_time)
            │   │   ├─ Stop 1: seq=1, arrival_time=now()
            │   │   ├─ Stop 2: seq=2, arrival_time=now() + 243 minutes
            │   │   └─ ...
            │   │
            │   └─ UPDATE vehicles SET shipment_id=1, lat=origin_lat, lon=origin_lon
            │
            └─→ 6. Response to Frontend
                └─ {id: 1, tracking_number: "PO-12346", stops: [...]}

┌──────────────────────────────────────────────────────────────────────┐
│ REAL-TIME TRACKING FLOW (Every 30 seconds)                           │
└──────────────────────────────────────────────────────────────────────┘

GPS Simulator / Real GPS Feed
    │
    │ Every 30 seconds
    │
    └─→ POST http://localhost:5000/v1/positions
        Body: {shipment_id: 1, lat: 30.1234, lon: -94.5678, timestamp: "..."}
        │
        └─→ Flask Backend (app.py)
            │
            ├─→ 1. Database Update
            │   └─ UPDATE vehicles SET lat=30.1234, lon=-94.5678, last_seen=now()
            │
            ├─→ 2. ETA Recalculation
            │   ├─ Calculate distance to next stop (haversine formula)
            │   ├─ Estimate speed based on recent positions
            │   ├─ Apply EWMA smoothing: new_eta = 0.7*calculated + 0.3*previous
            │   └─ Calculate confidence score based on deviation
            │
            ├─→ 3. Traffic & Weather Check (if configured)
            │   ├─ Check traffic API for congestion
            │   ├─ Check weather API for conditions
            │   └─ Adjust ETA multiplier if delays detected
            │
            ├─→ 4. Socket.io Broadcast to ALL subscribed clients
            │   └─ socketio.emit('position_update', {
            │         shipment_id: 1,
            │         lat: 30.1234,
            │         lon: -94.5678,
            │         eta_seconds: 3042,
            │         confidence: "high"
            │       }, room='shipment_1')
            │
            └─→ Customer Tracking Page (React)
                ├─ Socket.io event listener receives update
                ├─ Updates vehiclePosition state → map marker moves
                ├─ Updates eta_seconds state → countdown refreshes
                └─ Updates confidence state → badge color changes

┌──────────────────────────────────────────────────────────────────────┐
│ REROUTE FLOW                                                          │
└──────────────────────────────────────────────────────────────────────┘

Backend Detects Delay (Traffic/Weather)
    │
    └─→ POST http://localhost:5000/v1/reroute/suggest
        Body: {shipment_id: 1, reason: "Traffic congestion"}
        │
        └─→ Flask Backend
            │
            ├─→ 1. Calculate 3 Alternative Routes (Valhalla)
            │   ├─ Route 1: Fastest (default truck)
            │   │   └─→ POST http://localhost:8002/route {costing: "truck"}
            │   │
            │   ├─ Route 2: Shortest distance
            │   │   └─→ POST http://localhost:8002/route {shortest: true}
            │   │
            │   └─ Route 3: No tolls
            │       └─→ POST http://localhost:8002/route {use_tolls: 0.0}
            │
            ├─→ 2. Save to Database
            │   └─ INSERT INTO reroutes (shipment_id, distance_km, duration_min, reason)
            │
            ├─→ 3. Broadcast to Manager Dashboard
            │   └─ socketio.emit('reroute_suggested', {alternatives: [...]})
            │
            └─→ Manager Dashboard
                ├─ Shows RerouteModal component
                ├─ Displays 3 options with time saved
                └─ Manager clicks "Accept Route 2"
                    │
                    └─→ POST /v1/reroutes/2/accept
                        │
                        └─→ Flask Backend
                            ├─→ UPDATE shipments SET route_geometry = new_route
                            ├─→ UPDATE stops SET eta_timestamp = recalculated_etas
                            │
                            └─→ Broadcast to ALL clients (Manager + Customer)
                                └─ socketio.emit('reroute_accepted', {
                                      shipment_id: 1,
                                      new_route: {...},
                                      notification: "Route updated - 15 min faster!"
                                    })
                                │
                                ├─→ Manager: Shows success message, closes modal
                                └─→ Customer: Shows notification, map redraws with new route
```

### Database Schema & Relationships

```sql
-- Organizations (logistics companies)
organizations
├─ id (PK)
├─ name
└─ contact_info

-- Vehicles (trucks, vans)
vehicles
├─ id (PK)
├─ org_id (FK → organizations.id)
├─ name
├─ lat, lon (current GPS position)
└─ last_seen (timestamp)

-- Shipments (delivery routes)
shipments
├─ id (PK)
├─ ref (tracking number, e.g., PO-98765)
├─ vehicle_id (FK → vehicles.id)
├─ org_id (FK → organizations.id)
├─ promised_eta (committed delivery time)
├─ route_geometry (polyline string from Valhalla)
└─ created_at

-- Stops (waypoints in route)
stops
├─ id (PK)
├─ shipment_id (FK → shipments.id)
├─ seq (stop sequence: 1, 2, 3...)
├─ name (address)
├─ lat, lon (coordinates)
├─ arrival_time (actual arrival timestamp, NULL if not arrived)
└─ eta_timestamp (estimated arrival time, updated every 30 sec)

-- Positions (GPS history)
positions
├─ id (PK)
├─ shipment_id (FK → shipments.id)
├─ lat, lon
├─ timestamp
└─ speed (optional)

-- Reroutes (alternative route suggestions)
reroutes
├─ id (PK)
├─ shipment_id (FK → shipments.id)
├─ distance_km
├─ duration_min
├─ time_saved_min
├─ reason (explanation)
├─ accepted (boolean)
└─ created_at
```

### Frontend State Management

```typescript
// Manager Dashboard State
const [originComponents, setOriginComponents] = useState<AddressComponents>({
  streetNumber: '', streetName: '', unit: '', city: '', state: '', zipCode: ''
});
const [destinationComponents, setDestinationComponents] = useState<AddressComponents>({...});
const [plannerMidStops, setPlannerMidStops] = useState<IntermediateStop[]>([]);
const [plannerPreviewStops, setPlannerPreviewStops] = useState<Stop[]>([]);
const [lastCreatedTracking, setLastCreatedTracking] = useState<string | null>(null);

// Customer Tracking State
const [shipmentId, setShipmentId] = useState<number | null>(null);
const [stops, setStops] = useState<Stop[]>([]);
const [vehiclePosition, setVehiclePosition] = useState<{lat: number; lon: number} | null>(null);
const [activeRoute, setActiveRoute] = useState<RouteDetails | null>(null);
const [delayInfo, setDelayInfo] = useState<DelayInfo | null>(null);
const [weatherAdvisory, setWeatherAdvisory] = useState<WeatherAdvisory | null>(null);

// Socket.io Connection
const [socket, setSocket] = useState<Socket | null>(null);

useEffect(() => {
  const newSocket = io('http://localhost:5000');
  newSocket.on('position_update', (data) => {
    setVehiclePosition({lat: data.lat, lon: data.lon});
    // Update ETAs...
  });
  setSocket(newSocket);
}, []);
```

### Test Data & GPS Simulators

**Comprehensive Test Data** (Recommended for development):

```bash
# Populate database with B2B commercial delivery routes in Beaumont, TX
populate_test_data.bat   # Windows
python create_test_data.py   # Linux/Mac

# Creates:
# - 2 Logistics Organizations (ETA Logistics, FastTrack Delivery)
# - 5 Commercial Vehicles (3 trucks, 2 vans)
# - 3 B2B Shipment routes with 19 commercial stops
# - Speed limits and location types for realistic simulation
# - Initial GPS positions at Beaumont Distribution Center
```

**Last-Mile Delivery Simulator** (B2B commercial deliveries with realistic traffic):

```bash
# Simulate realistic B2B last-mile delivery with MPH speeds, 30-second GPS intervals
start_last_mile_simulator.bat ROUTE-RETAIL-001 1   # Windows
python simulate_last_mile.py --route ROUTE-RETAIL-001 --vehicle 1   # Linux/Mac

# Available B2B test routes:
# ROUTE-RETAIL-001  : Retail Express (5 stops: Walmart, Target, Home Depot, etc.)
# ROUTE-HEALTH-001  : Healthcare & Education (6 stops: Hospitals, Universities)
# ROUTE-IND-001     : Industrial & Logistics (7 stops: Port, Warehouses, Refineries)

# Features:
# - 30-second GPS intervals (industry standard)
# - MPH speed limits (20-60 mph by zone)
# - Realistic B2B service times (8-30 minutes)
# - Valhalla API routing (no artificial delays)
```

**Highway GPS Simulator** (Long-haul testing):

```bash
# Simulate Dallas to Beaumont highway route
python simulate_gps.py   # Or: start_gps_simulator.bat
```

**📚 See [QUICKSTART.md](QUICKSTART.md) for complete setup guide and [TESTING.md](TESTING.md) for testing scenarios**

## 🎯 Usage

### Manager Dashboard

1. **Enter Origin Address:**
   - Click "Origin" section to expand
   - Fill in structured address fields (street #, name, unit, city, state, ZIP)
   - Or select from predefined facilities

2. **Enter Destination Address:**
   - Same as origin - structured 6-field input
   - Facility quick-select available

3. **Add Intermediate Stops (Optional):**
   - Click "Intermediate Stops" to expand
   - Add unlimited stops
   - Reorder with ↑↓ buttons
   - Remove with × button

4. **Generate Route:**
   - Click the "🚀 Generate Tracking Number" button
   - System geocodes all addresses
   - Creates shipment with ETAs
   - Displays tracking number

5. **Copy Tracking Number:**
   - Click "Copy Tracking #" button
   - Share with customers

6. **At present, the system uses synthetic GPS data to simulate live tracking. However, it is designed with an optional integration feature that allows connection to a real GPS feed—for example, by linking a driver’s phone live location to capture and update coordinates in real time.** 
 - Option to add gps data(optional)
 - for now just fetch simulated data.

8. View real-time:
   - Vehicle GPS position on map
   - Stop sequence with ETAs
   - Route progress
   - Traffic conditions
   - Weather advisories
   - ETA confidence intervals (high/medium/low)

9. Reroute based on suggestion of Valhalla engine 
   - Suggest Route rerouting to logistics manager
   - Feature to suggest rerouting to logistics manager
   - and also logistics manager can reroute if eta confidence to reduce eta is high enough for logistics manager to do so

10- once logistics manager reroute it should also be automatically be displayed on costumer tracking 

### Customer Tracking

1. Navigate to "Customer Tracking" page
2. Enter tracking number (format: `PO-XXXXXX`)
3. View real-time updates (every 30 seconds):
   - Vehicle GPS position on map
   - Stop sequence with ETAs and confidence levels
   - Route progress with completion percentage
   - Live traffic conditions and congestion
   - Weather advisories and delay predictions
   - ETA confidence intervals (high/medium/low)

## 🔧 Configuration

### Frontend (`vite.config.ts`)

```typescript
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://127.0.0.1:5000',
      '/socket.io': {
        target: 'ws://127.0.0.1:5000',
        ws: true
      }
    }
  }
})
```

### Backend (`backend/app.py`)

```python
# Configure CORS origins
app.config['CORS_ORIGINS'] = ['http://localhost:5173']

# Database connection
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:pass@localhost/eta_db')

# Geocoding rate limits
GEOCODE_RATE_LIMIT = 1.0  # requests per second
```

## 🗂️ Project Structure

```
eta_tracker/
├── 📁 backend/              # Python Flask backend
│   ├── app.py              # Main Flask application with Socket.io
│   ├── traffic_client.py   # Traffic API integration
│   ├── valhalla_client.py  # Routing engine client
│   └── weather_api.py      # Weather service integration
│
├── 📁 components/           # React UI components
│   ├── Map.tsx             # Leaflet map with real-time tracking
│   ├── RerouteModal.tsx    # Reroute suggestion modal
│   └── icons.tsx           # SVG icon library
│
├── 📁 data/                 # Database layer
│   ├── db.py               # Database models and queries
│   ├── init_db.sql         # PostgreSQL schema with PostGIS
│   └── gtfs_ingest.py      # GTFS data import (transit mode)
│
├── 📁 pages/                # Page-level components
│   ├── DashboardPage.tsx   # Manager planning interface (1,900 lines)
│   └── TrackingPage.tsx    # Customer tracking view
│
├── 📁 assets/               # Static assets (images, icons)
│
├── 📄 App.tsx               # Root React component with routing
├── 📄 types.ts              # Shared TypeScript type definitions
├── 📄 index.tsx             # React entry point
├── 📄 index.html            # HTML template
│
├── ⚙️ vite.config.ts        # Vite build configuration
├── ⚙️ tsconfig.json         # TypeScript compiler options
├── ⚙️ package.json          # Node.js dependencies
├── ⚙️ requirements.txt      # Python dependencies
│
├── 🔧 .env.example          # Environment variable template
├── 🔧 .gitignore            # Git ignore rules
│
├── 📚 README.md             # Main documentation (this file)
├── 📚 CONTRIBUTING.md       # Contribution guidelines
├── 📚 CHANGELOG.md          # Version history
├── 📚 LICENSE               # MIT License
│
├── 🧪 test_api.py           # API endpoint tests
├── 🧪 test_backend.py       # Backend unit tests
├── 🧪 test_e2e.py           # End-to-end tests
│
└── 🚀 start_backend.bat     # Quick start script (Windows)
```

## 🌐 API Reference

### REST API Endpoints

#### **Shipments**

**`GET /v1/shipments`**
- **Purpose:** List all shipments or filter by reference number
- **Query Params:** `ref` (optional) - Filter by tracking number
- **Response:** Array of shipment objects
```json
GET /v1/shipments?ref=PO-98765

Response:
[{
  "id": 1,
  "ref": "PO-98765",
  "vehicle_id": 1,
  "org_id": 1,
  "promised_eta": "2025-11-04T17:00:00Z",
  "created_at": "2025-11-04T10:00:00Z"
}]
```

**`POST /v1/shipments`**
- **Purpose:** Create new shipment with stops
- **Body:**
```json
{
  "ref": "PO-12346",
  "vehicle_id": 1,
  "org_id": 1,
  "stops": [
    {
      "seq": 1,
      "name": "123 Main St, Austin, TX 78701",
      "lat": 30.2672,
      "lon": -97.7431,
      "arrival_time": "2025-11-04T12:00:00Z"
    },
    {
      "seq": 2,
      "name": "456 Elm St, Houston, TX 77002",
      "lat": 29.7604,
      "lon": -95.3698,
      "arrival_time": "2025-11-04T16:30:00Z"
    }
  ],
  "promised_eta": "2025-11-04T16:30:00Z"
}
```
- **Response:** Created shipment with ID

**`GET /v1/shipments/{id}/status`**
- **Purpose:** Get real-time shipment status with ETAs
- **Response:**
```json
{
  "id": 1,
  "ref": "PO-98765",
  "status": "in_transit",
  "stops": [
    {
      "id": 1,
      "seq": 1,
      "name": "Beaumont Distribution Center",
      "lat": 30.0802,
      "lon": -94.1266,
      "arrival_time": "2025-11-04T10:00:00Z",
      "eta_timestamp": "2025-11-04T10:00:00Z",
      "eta_seconds": 0,
      "completed": true
    },
    {
      "id": 2,
      "seq": 2,
      "name": "Houston Logistics Hub",
      "lat": 29.7604,
      "lon": -95.3698,
      "arrival_time": null,
      "eta_timestamp": "2025-11-04T14:30:00Z",
      "eta_seconds": 3600,
      "completed": false
    }
  ],
  "vehicle_position": {
    "lat": 30.1234,
    "lon": -94.5678,
    "timestamp": "2025-11-04T13:30:00Z"
  },
  "reason_code": "on_time",
  "confidence": 0.95,
  "explanation": "On schedule, high confidence",
  "weather_advisory": null
}
```

#### **GPS Position Updates**

**`POST /v1/positions`**
- **Purpose:** Update vehicle GPS position (called by GPS simulator or real GPS feed)
- **Body:**
```json
{
  "shipment_id": 1,
  "lat": 30.1234,
  "lon": -94.5678,
  "timestamp": "2025-11-04T13:30:00Z"
}
```
- **Response:** Updated position confirmation
- **Side Effects:** 
  - Updates database
  - Recalculates ETAs
  - Broadcasts to all subscribed clients via Socket.io

#### **Rerouting**

**`POST /v1/reroute/suggest`**
- **Purpose:** Generate reroute suggestions (usually triggered by backend detecting delays)
- **Body:**
```json
{
  "shipment_id": 1,
  "reason": "Traffic congestion detected"
}
```
- **Response:** Array of alternative routes
- **Process:**
  1. Calls Valhalla for 3 alternative routes
  2. Saves to database
  3. Broadcasts to manager dashboard

**`POST /v1/reroutes/{id}/accept`**
- **Purpose:** Accept a suggested reroute
- **Body:**
```json
{
  "shipment_id": 1
}
```
- **Response:** Updated shipment with new route
- **Side Effects:**
  - Updates shipment route_geometry
  - Recalculates all stop ETAs
  - Broadcasts `reroute_accepted` event to ALL clients (manager + customer)

#### **Health Check**

**`GET /health`**
- **Purpose:** Check backend status
- **Response:**
```json
{
  "status": "ok",
  "database": "connected",
  "valhalla": "available",
  "timestamp": "2025-11-04T13:30:00Z"
}
```

### Real-Time Events (Socket.io)

#### **Client → Server Events**

**`connect`**
- **When:** Client connects to WebSocket
- **Response:** Connection acknowledgment

**`subscribe`**
- **Purpose:** Subscribe to shipment updates
- **Payload:**
```javascript
socket.emit('subscribe', { shipment_id: 1 })
```
- **Effect:** Client joins room `shipment_1` and receives all updates

**`unsubscribe`**
- **Purpose:** Unsubscribe from shipment updates
- **Payload:**
```javascript
socket.emit('unsubscribe', { shipment_id: 1 })
```

#### **Server → Client Events**

**`position_update`**
- **When:** Every 30 seconds when GPS position changes
- **Payload:**
```javascript
{
  shipment_id: 1,
  lat: 30.1234,
  lon: -94.5678,
  timestamp: "2025-11-04T13:30:00Z",
  eta_seconds: 3600,
  confidence: "high"
}
```
- **Frontend Action:** Update map marker, refresh ETA displays

**`reroute_suggested`**
- **When:** Backend detects delay and calculates alternatives
- **Payload:**
```javascript
{
  shipment_id: 1,
  alternatives: [
    {
      id: 1,
      distance_km: 250,
      duration_min: 240,
      time_saved_min: 30,
      reason: "Avoids congestion on I-10"
    },
    {
      id: 2,
      distance_km: 235,
      duration_min: 250,
      time_saved_min: 20,
      reason: "Shortest distance route"
    }
  ]
}
```
- **Frontend Action:** Show reroute modal to manager

**`reroute_accepted`**
- **When:** Manager accepts a reroute
- **Payload:**
```javascript
{
  shipment_id: 1,
  new_route: {
    geometry: "encoded_polyline_string",
    distance_km: 235,
    duration_min: 250
  },
  stops: [/* updated stop ETAs */]
}
```
- **Frontend Action:** 
  - Manager: Dismiss modal, show success notification
  - Customer: Show notification, redraw map with new route

**`delay_info`**
- **When:** Delay detected (weather, traffic, etc.)
- **Payload:**
```javascript
{
  shipment_id: 1,
  reason_code: "weather_delay",
  confidence: 0.85,
  explanation: "Heavy rain in Houston area - 15 min delay expected",
  severity: "medium"
}
```
- **Frontend Action:** Show weather advisory banner

**`eta_update`**
- **When:** ETA recalculation (every 30 seconds with GPS update)
- **Payload:**
```javascript
{
  shipment_id: 1,
  stop_id: 2,
  new_eta_timestamp: "2025-11-04T14:45:00Z",
  eta_seconds: 2700,
  confidence: "medium"
}
```
- **Frontend Action:** Update ETA badges and stop timeline

```bash
python data/db.py
```

### 5. Frontend Setup

The frontend is a standard React app. Dependencies are managed via CDN through the `importmap` in `index.html`. No `npm install` is needed for the provided setup.

For local development, it's recommended to run the React app using a development server like Vite, which can proxy API requests to the Flask backend.

Create a `vite.config.js` file:
```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://127.0.0.1:5000',
      '/socket.io': {
        target: 'ws://127.0.0.1:5000',
        ws: true
      }
    }
  }
})
```
Then run `npm install vite @vitejs/plugin-react` and `npx vite`.

## Running the Application

1.  **Start the Backend Server**:
    ```bash
    python backend/app.py
    ```
    The Flask server will start, along with the background tasks for the logistics simulator and the GTFS poller.

2.  **Start the Frontend**:
    Open the `index.html` file in your browser, or run a local dev server as described above.

You should now be able to access the Manager Dashboard and Customer Tracking pages.

## 🧪 Testing

The project includes comprehensive test suites to ensure reliability:

### Test Files

- **`test_api.py`** - API endpoint tests
  - Tests all REST endpoints
  - Validates request/response formats
  - Checks error handling

- **`test_backend.py`** - Backend unit tests
  - Database operations
  - Business logic validation
  - Helper function tests

- **`test_e2e.py`** - End-to-end tests
  - Full workflow validation
  - Real-time update testing
  - Integration testing

- **`test_status_endpoint.py`** - Specific status endpoint tests
  - Shipment status retrieval
  - ETA calculations
  - Error scenarios

### Running Tests

```bash
# Run all API tests
python test_api.py

# Run backend unit tests
python test_backend.py

# Run end-to-end tests
python test_e2e.py

# Run specific test
python test_status_endpoint.py
```

### GPS Simulator

For testing without real GPS hardware:

```bash
# Start GPS simulator
python simulate_gps.py

# Or use Windows batch file
start_gps_simulator.bat
```

The simulator generates realistic GPS positions along the configured route.

## 🎨 Screenshots

*(Add screenshots here of your dashboard and tracking views)*

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on:
- Code of conduct
- Development workflow
- Coding standards
- Pull request process
- Testing guidelines

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

### Technologies Used

- **[React](https://react.dev/)** - UI framework
- **[TypeScript](https://www.typescriptlang.org/)** - Type safety
- **[Vite](https://vitejs.dev/)** - Build tool
- **[Tailwind CSS](https://tailwindcss.com/)** - Utility-first CSS
- **[Leaflet](https://leafletjs.com/)** - Interactive maps
- **[Leaflet Routing Machine](https://www.liedman.net/leaflet-routing-machine/)** - Route visualization
- **[Socket.io](https://socket.io/)** - Real-time communication
- **[Flask](https://flask.palletsprojects.com/)** - Python web framework
- **[PostgreSQL](https://www.postgresql.org/)** - Database
- **[OpenStreetMap Nominatim](https://nominatim.org/)** - Geocoding service

### Special Thanks

- OpenStreetMap contributors for free geocoding API
- Leaflet community for excellent mapping library
- React and TypeScript teams for robust development tools

## 📧 Contact

For questions or support, please:
- Open an [issue](https://github.com/your-username/eta_tracker/issues)
- Contact the maintainers

## 🚀 Roadmap

Future enhancements planned:
- [ ] Mobile app (React Native)
- [ ] Advanced traffic prediction ML model
- [ ] Multi-vehicle fleet management
- [ ] Customer notification system (SMS/Email)
- [ ] Historical route analytics
- [ ] API key authentication
- [ ] Webhook support for third-party integrations
- [ ] Advanced rerouting algorithms

## 💡 Support

If you find this project helpful, please consider:
- ⭐ Starring the repository
- 🐛 Reporting bugs
- 💡 Suggesting features
- 🤝 Contributing code
- 📢 Sharing with others

---

## 📊 Documentation Summary

This README provides comprehensive coverage of the ETA Tracker system:

**What's Covered:**
- ✅ **System Architecture** - 3-layer design (Frontend, Backend, Infrastructure)
- ✅ **Feature Deep Dive** - 6 major features with complete data flows
- ✅ **UX Flow** - ASCII art mockups of Manager & Customer dashboards
- ✅ **Installation & Setup** - 10-step guide with Docker setup
- ✅ **API Reference** - All REST endpoints + Socket.io events with payloads
- ✅ **Data Flow & Interactions** - Complete flow diagrams for shipment creation, tracking, and rerouting
- ✅ **Database Schema** - All tables, relationships, and constraints
- ✅ **Frontend State Management** - TypeScript examples
- ✅ **Usage Guides** - Step-by-step workflows for both dashboards
- ✅ **Configuration** - All environment variables explained
- ✅ **Project Structure** - Directory tree with file purposes
- ✅ **Testing** - How to run API, backend, and E2E tests

**Quick Navigation:**
- 🚀 New to the project? Start with [Overview](#-overview)
- 💻 Want to run it? Go to [Installation & Setup](#-installation--setup)
- 🔧 Need API docs? Check [API Reference](#-api-reference)
- 🐛 Found a bug? See [Contributing](#-contributing)

**Key Features Highlighted:**
1. **Load Existing Shipment** - Input field + quick "📦 Load PO-98765" button
2. **Load Test Data** - "🧪 Test Data" button for random Texas routes
3. **Valhalla Routing** - Truck-specific routing with height/weight/width constraints
4. **Real-Time GPS Tracking** - 30-second update cycles with EWMA confidence scoring
5. **Reroute Management** - Automatic detection, suggestion, and acceptance workflow
6. **Weather & Traffic Integration** - Live advisories and delay explanations

---

**Built with ❤️ by the ETA Tracker Team**

````
