# 🚧 Remaining Features - ETA Tracker

This document lists all features mentioned in the README and codebase that are **not yet implemented** but are planned or documented as future work.

**Last Updated**: November 4, 2025  
**Version**: 1.1.0 (B2B Realism Update)

---

## 📋 Table of Contents

1. [Manager Dashboard Features](#manager-dashboard-features)
2. [Customer Tracking Features](#customer-tracking-features)
3. [Backend & API Features](#backend--api-features)
4. [Routing & Optimization](#routing--optimization)
5. [Real-time GPS Integration](#real-time-gps-integration)
6. [Analytics & Reporting](#analytics--reporting)
7. [Driver Management](#driver-management)
8. [Advanced Features](#advanced-features)

---

## 🎛️ Manager Dashboard Features

### ✅ Implemented
- ✅ Structured address input (6-field)
- ✅ Interactive route planning with unlimited stops
- ✅ Facility quick select
- ✅ Real-time geocoding (OpenStreetMap Nominatim)
- ✅ Route overview with live ETA calculations
- ✅ One-click deployment with tracking numbers
- ✅ GPS-based driver tracking (30-second intervals)
- ✅ Live data integration (weather, traffic, congestion)
- ✅ ETA confidence analytics

### 🚧 Not Yet Implemented

#### 1. **Automatic Rerouting Display for Customer**
- **Status**: Mentioned in README (item 10), not implemented
- **Description**: "once logistics manager reroute it should also be automatically be displayed on customer tracking"
- **Current State**: 
  - Backend has `accept_reroute()` endpoint
  - Frontend RerouteModal component exists
  - Missing: Real-time Socket.io event to push reroute updates to customer tracking page
- **Implementation Needed**:
  - Add `reroute_accepted` Socket.io event
  - Update TrackingPage.tsx to listen for reroute events
  - Automatically update customer map with new route
  - Display notification to customer about route change

#### 2. **Drag-to-Reorder Stops**
- **Status**: Mentioned in README, not implemented
- **Description**: "Unlimited intermediate stops with drag-to-reorder"
- **Current State**: Up/down arrow buttons work, but no drag-and-drop
- **Implementation Needed**:
  - Add React DnD library or use native HTML5 drag-and-drop
  - Update DashboardPage.tsx with drag handlers
  - Visual feedback during drag operation

#### 3. **Historical Performance Visualization**
- **Status**: Mentioned in README feature list
- **Description**: "Route and historical performance visualization powered by the Valhalla API"
- **Current State**: No historical data tracking or visualization
- **Implementation Needed**:
  - Track completed route metrics (actual vs planned times)
  - Store historical ETA accuracy per route/stop
  - Create visualization dashboard showing:
    - Average delay by route
    - ETA accuracy trends
    - Common delay causes
    - Performance over time

#### 4. **Reroute Suggestion Based on ETA Confidence**
- **Status**: Partially implemented
- **Description**: "logistics manager can reroute if eta confidence to reduce eta is high enough"
- **Current State**: 
  - Basic reroute suggestion exists (`/v1/reroute/suggest`)
  - Uses placeholder logic (TODO comment: "Implement Valhalla routing comparison")
  - No confidence-based triggering
- **Implementation Needed**:
  - Integrate real Valhalla API for alternative routes
  - Add confidence threshold logic
  - Suggest reroutes only when:
    - Current ETA confidence is low (<60%)
    - Alternative route has high confidence (>80%)
    - Time savings >= 10 minutes
  - Display confidence comparison in RerouteModal

---

## 📱 Customer Tracking Features

### ✅ Implemented
- ✅ Live GPS tracking (30-second intervals)
- ✅ Dynamic ETAs with confidence levels
- ✅ Traffic awareness indicators
- ✅ Weather advisories
- ✅ Responsive design
- ✅ ETA confidence display

### 🚧 Not Yet Implemented

#### 1. **Real-time Reroute Notifications**
- **Status**: Not implemented
- **Description**: Customer should see route changes pushed by manager
- **Current State**: Customer page shows static route
- **Implementation Needed**:
  - Socket.io listener for `reroute_accepted` event
  - Update map with new route geometry
  - Show toast notification: "Route updated - new ETA: XX:XX"
  - Animate transition from old to new route

#### 2. **ETA Confidence Intervals Visualization**
- **Status**: Mentioned but not fully visualized
- **Description**: "View real-time updates (every 30 seconds): ETA confidence intervals (high/medium/low)"
- **Current State**: Confidence shown as text (High/Medium/Low)
- **Implementation Needed**:
  - Visual confidence meter/gauge
  - Color-coded confidence bands
  - Trend chart showing confidence over time
  - Explanation of factors affecting confidence

#### 3. **Delay Prediction Timeline**
- **Status**: Not implemented
- **Description**: Show predicted delays before they happen
- **Current State**: Delays shown after they occur
- **Implementation Needed**:
  - Predictive model for traffic-based delays
  - Weather forecast integration for future stops
  - Timeline view showing potential delays ahead
  - Proactive notifications (e.g., "Heavy traffic expected in 15 minutes")

---

## 🔧 Backend & API Features

### ✅ Implemented
- ✅ Flask REST API with Socket.io
- ✅ PostgreSQL with PostGIS
- ✅ GPS position ingestion
- ✅ ETA calculation with weather/traffic
- ✅ Delay reason scoring
- ✅ Basic reroute suggestion

### 🚧 Not Yet Implemented

#### 1. **Full Valhalla Routing Engine Integration**
- **Status**: Placeholder implementation
- **Description**: Real Valhalla API instead of OSRM
- **Current State**: 
  - `valhalla_client.py` has `_valhalla_route()` method
  - Currently uses OSRM as fallback
  - `valhalla_url` is None by default
- **Implementation Needed**:
  - Set up Valhalla server (Docker or hosted)
  - Configure `VALHALLA_URL` environment variable
  - Implement truck costing with real constraints
  - Use Valhalla alternatives API for rerouting
  - Support avoid tolls, height/weight restrictions

**Code Location**: `backend/valhalla_client.py`, line 202
```python
# TODO: Request alternatives from OSRM/Valhalla
```

#### 2. **Driver Hours of Service (HOS) Tracking**
- **Status**: Defined but not implemented
- **Description**: Track driver hours and predict HOS violations
- **Current State**: 
  - Reason code exists: `DRIVER_HOS_RISK`
  - Score function mentions "approaching 11-hour drive limit"
  - No actual tracking logic
- **Implementation Needed**:
  - Track cumulative drive time per driver
  - Store driver shift start time
  - Calculate remaining hours before HOS limit
  - Add reason: "Driver approaching 11-hour limit, rest break needed"
  - Suggest stops for mandatory breaks

**Code Location**: `backend/app.py`, line 200

#### 3. **Road Incident Detection**
- **Status**: Defined but not implemented
- **Description**: Detect road closures, accidents via traffic API
- **Current State**: 
  - Reason code exists: `ROAD_INCIDENT`
  - Score function has placeholder
  - No integration with traffic incident APIs
- **Implementation Needed**:
  - Integrate HERE Traffic API incidents endpoint
  - Parse accident, closure, construction events
  - Match incidents to route path
  - Calculate delay impact
  - Trigger automatic reroute suggestions

#### 4. **Manual Event Reporting**
- **Status**: Mentioned but not implemented
- **Description**: "VEHICLE_ISSUE: reported via manual event"
- **Current State**: No endpoint or UI for manual event submission
- **Implementation Needed**:
  - New endpoint: `POST /v1/events/manual`
  - Driver/manager can report:
    - Vehicle breakdown
    - Flat tire
    - Mechanical issue
    - Customer unavailable
    - Loading delay
  - Events trigger ETA recalculation
  - Events stored in database for analysis

**Code Location**: `backend/app.py`, line 197

#### 5. **Real Active Shipment Detection**
- **Status**: Hardcoded placeholder
- **Description**: Get actual active shipment instead of hardcoded PO-98765
- **Current State**: 
```python
shipment = db.get_shipment_by_ref('PO-98765')  # TODO: Get actual active shipment
```
- **Implementation Needed**:
  - Query shipments by vehicle_id with status='in_transit'
  - Handle multiple active shipments per vehicle
  - Route GPS updates to correct shipment

**Code Location**: `backend/app.py`, line 409

---

## 🗺️ Routing & Optimization

### ✅ Implemented
- ✅ OSRM routing with truck profile
- ✅ Route visualization on map
- ✅ Traffic-aware ETA calculation
- ✅ Weather impact on ETAs

### 🚧 Not Yet Implemented

#### 1. **Alternative Route Comparison**
- **Status**: TODO comment in code
- **Description**: Compare multiple route alternatives
- **Current State**: Only single route calculated
- **Implementation Needed**:
  - Request 2-3 alternatives from Valhalla
  - Compare by:
    - Total time
    - Distance
    - Toll costs
    - Traffic severity
  - Display alternatives in RerouteModal with pros/cons
  - Let manager choose best option

**Code Location**: `backend/app.py`, line 781-782

#### 2. **Dynamic Stop Reordering**
- **Status**: Endpoint mentioned in docs, not implemented
- **Description**: Optimize stop sequence mid-route
- **Implementation Needed**:
  - Traveling Salesman Problem (TSP) solver
  - Reorder remaining stops for optimal time
  - Endpoint: `POST /v1/shipments/{id}/reorder`
  - Consider time windows and priorities
  - Manager approval required before applying

**Code Location**: Referenced in `TESTING.md`, line 306

#### 3. **Road Closure Simulation**
- **Status**: Endpoint mentioned in docs, not implemented
- **Description**: Test system behavior with road closures
- **Implementation Needed**:
  - Endpoint: `POST /v1/simulate/road-closure`
  - Block specific road segments
  - Force rerouting through Valhalla
  - Useful for disaster planning and testing

**Code Location**: Referenced in `TESTING.md`, line 295

#### 4. **Transit Mode (GTFS Integration)**
- **Status**: Database schema exists, not implemented
- **Description**: Support public transit routing
- **Current State**: 
  - `gtfs_ingest.py` exists but unused
  - Database has GTFS schema
  - No integration with routing
- **Implementation Needed**:
  - Ingest GTFS data for Beaumont, TX
  - Multi-modal routing (truck + transit)
  - Schedule-based ETAs
  - Transfer optimization

---

## 📡 Real-time GPS Integration

### ✅ Implemented
- ✅ Simulated GPS with 30-second intervals
- ✅ GPS position ingestion API
- ✅ Road network snapping
- ✅ Socket.io broadcasting

### 🚧 Not Yet Implemented

#### 1. **Real Driver Phone GPS Integration**
- **Status**: Mentioned in README (item 6)
- **Description**: "At present, the system uses synthetic GPS data to simulate live tracking. However, it is designed with an optional integration feature that allows connection to a real GPS feed—for example, by linking a driver's phone live location to capture and update coordinates in real time."
- **Current State**: Only simulator supported
- **Implementation Needed**:
  - Mobile app or web interface for drivers
  - POST GPS from phone to `/v1/positions`
  - Authentication and vehicle assignment
  - Battery optimization (30-second minimum)
  - Offline queueing and retry logic
  - Options:
    - Progressive Web App (PWA)
    - React Native mobile app
    - Third-party GPS device API integration

#### 2. **GPS Data Quality Monitoring**
- **Status**: Not implemented
- **Description**: Detect and handle poor GPS quality
- **Implementation Needed**:
  - Track GPS accuracy (HDOP, satellite count)
  - Detect stale data (no update in 2+ minutes)
  - Flag erratic position jumps
  - Smooth GPS jitter with Kalman filter
  - Alert manager when GPS quality drops

#### 3. **Multi-Vehicle Dashboard**
- **Status**: Not implemented
- **Description**: Track multiple vehicles simultaneously
- **Current State**: Manager can only view one shipment at a time
- **Implementation Needed**:
  - Fleet overview map with all active vehicles
  - List of vehicles with status indicators
  - Click vehicle to see route details
  - Filter by organization, status, delay severity
  - Real-time updates for all vehicles via Socket.io

---

## 📊 Analytics & Reporting

### ✅ Implemented
- ✅ Basic ETA confidence scoring
- ✅ Delay reason classification
- ✅ Real-time traffic and weather data

### 🚧 Not Yet Implemented

#### 1. **Historical Performance Analytics Dashboard**
- **Status**: Mentioned in README
- **Description**: "Route and historical performance visualization"
- **Implementation Needed**:
  - Track completed routes with metrics:
    - Planned vs actual arrival times
    - ETA accuracy (MAPE - Mean Absolute Percentage Error)
    - Total delays by reason code
    - Service time accuracy
  - Visualizations:
    - Charts showing performance trends
    - Heatmap of delay hotspots
    - Route comparison (which routes are most reliable)
  - Export reports to CSV/PDF

#### 2. **Predictive ETA Models**
- **Status**: Not implemented
- **Description**: Machine learning for better ETA predictions
- **Current State**: ETAs use simple speed-based calculations
- **Implementation Needed**:
  - Collect historical data:
    - Actual travel times
    - Weather conditions
    - Traffic patterns
    - Day of week, time of day
    - Driver behavior
  - Train ML model (e.g., XGBoost, Random Forest)
  - Use model to predict travel time per segment
  - Confidence intervals based on model uncertainty
  - Retrain model monthly with new data

#### 3. **Driver Performance Metrics**
- **Status**: Not implemented
- **Description**: Track driver efficiency and behavior
- **Implementation Needed**:
  - Metrics per driver:
    - Average speed vs speed limit
    - On-time delivery rate
    - Service time variance
    - Fuel efficiency (if data available)
    - Customer satisfaction scores
  - Leaderboard for gamification
  - Identify training opportunities

#### 4. **Customer Satisfaction Tracking**
- **Status**: Not implemented
- **Description**: Collect feedback after delivery
- **Implementation Needed**:
  - Post-delivery survey on tracking page
  - Rating: 1-5 stars
  - Questions:
    - "Was the ETA accurate?"
    - "Was the driver professional?"
    - "Was the package in good condition?"
  - Store feedback in database
  - Link to shipment and driver
  - Dashboard for managers to review feedback

---

## 👤 Driver Management

### ✅ Implemented
- ✅ Vehicle assignment to shipments
- ✅ Basic vehicle tracking

### 🚧 Not Yet Implemented

#### 1. **Driver Profiles**
- **Status**: No driver table in database
- **Implementation Needed**:
  - Database table: `drivers`
    - id, name, phone, email
    - license_number, license_expiry
    - vehicle_id (current assignment)
    - status (active, on_break, off_duty)
  - Link GPS positions to driver (not just vehicle)
  - Driver login for mobile app

#### 2. **Driver Hours of Service (HOS) Compliance**
- **Status**: Reason code exists, tracking not implemented
- **Description**: Enforce 11-hour drive limit (US regulations)
- **Implementation Needed**:
  - Track driver shift start time
  - Accumulate drive time from GPS data
  - Calculate remaining hours
  - Warn at 10.5 hours: "30 minutes of drive time remaining"
  - Prevent route assignment when HOS exceeded
  - Mandatory 10-hour rest period

#### 3. **Driver Communication**
- **Status**: Not implemented
- **Description**: Two-way messaging between manager and driver
- **Implementation Needed**:
  - In-app messaging
  - Push notifications to driver app
  - Driver can report issues (vehicle, traffic, customer)
  - Manager can send instructions or updates
  - Message history stored per shipment

#### 4. **Driver Task Management**
- **Status**: Not implemented
- **Description**: Assign tasks and track completion
- **Implementation Needed**:
  - Task types:
    - Pickup at origin
    - Delivery to stop
    - Fuel stop
    - Maintenance check
    - Rest break
  - Driver sees task list in mobile app
  - Check off tasks when complete
  - Photos for proof of delivery (POD)

---

## 🚀 Advanced Features

### 🚧 Not Yet Implemented

#### 1. **Predictive Rerouting**
- **Status**: Not implemented
- **Description**: Automatically reroute before delays happen
- **Implementation Needed**:
  - Monitor traffic forecasts (not just current)
  - Weather predictions (next 2 hours)
  - Predict delays before they occur
  - Automatically calculate alternative routes
  - Present to manager: "Traffic jam forming ahead, reroute now to save 15 minutes?"
  - Option for auto-accept based on savings threshold

#### 2. **Multi-Tenancy for Organizations**
- **Status**: Database supports organizations, not enforced
- **Description**: Isolate data per logistics company
- **Current State**: org_id field exists but no isolation
- **Implementation Needed**:
  - User authentication with organization assignment
  - API requests filtered by organization
  - Prevent cross-organization data access
  - Organization admin can invite users
  - Billing per organization

#### 3. **API Rate Limiting and Caching**
- **Status**: No rate limiting
- **Description**: Protect against abuse and reduce API costs
- **Implementation Needed**:
  - Rate limit geocoding (currently 1 req/sec)
  - Cache geocoding results (address → coordinates)
  - Cache traffic data (2 minutes)
  - Cache weather data (10 minutes)
  - Redis for distributed caching

#### 4. **Mobile Progressive Web App (PWA)**
- **Status**: Desktop-only web interface
- **Description**: Mobile-optimized experience
- **Implementation Needed**:
  - Service worker for offline capability
  - Install prompts on mobile browsers
  - Push notifications for status updates
  - Mobile-optimized map controls
  - Touch-friendly UI
  - GPS integration for driver app

#### 5. **Webhook Notifications**
- **Status**: Not implemented
- **Description**: Push updates to external systems
- **Implementation Needed**:
  - Configuration: customer provides webhook URL
  - Events to send:
    - Shipment created
    - GPS position update (configurable frequency)
    - ETA updated
    - Delay detected
    - Stop completed
    - Shipment completed
  - Retry logic with exponential backoff
  - Webhook logs and monitoring

#### 6. **Geofencing and Auto-Arrival**
- **Status**: Not implemented
- **Description**: Automatically mark stops as complete
- **Implementation Needed**:
  - Define geofence radius per stop (e.g., 100 meters)
  - When vehicle enters geofence:
    - Mark "arrived" timestamp
    - Start dwell timer
  - When vehicle exits geofence:
    - Mark "departed" timestamp
    - Calculate actual service time
  - Reduce manual input from drivers

#### 7. **Load Optimization**
- **Status**: Not implemented
- **Description**: Optimize vehicle loading order
- **Implementation Needed**:
  - Last-In-First-Out (LIFO) loading strategy
  - 3D bin packing for cargo space
  - Weight distribution for safety
  - Loading instructions for warehouse staff
  - Integration with warehouse management systems (WMS)

#### 8. **Customer Self-Service Portal**
- **Status**: Basic tracking only
- **Description**: Full-featured customer portal
- **Implementation Needed**:
  - Request pickup/delivery
  - Upload shipping documents
  - Schedule delivery time windows
  - Reroute request (redirect to alternate address)
  - Delivery preferences (leave at door, signature required)
  - Shipment history and invoices

#### 9. **Carbon Footprint Tracking**
- **Status**: Not implemented
- **Description**: Calculate and report emissions
- **Implementation Needed**:
  - Track distance per route
  - Vehicle type and fuel efficiency
  - Calculate CO2 emissions
  - Display on dashboard: "This route emitted X kg CO2"
  - Monthly reports for sustainability goals
  - Suggest eco-friendly routing options

#### 10. **Integration with Fleet Management Systems**
- **Status**: Not implemented
- **Description**: Connect with telematics providers
- **Implementation Needed**:
  - APIs for:
    - Geotab
    - Verizon Connect
    - Samsara
    - KeepTruckin
  - Import GPS data automatically
  - Import vehicle diagnostics (fuel, odometer, engine health)
  - Two-way sync of shipment data

---

## 🎯 Priority Recommendations

Based on impact and user needs, here's a suggested implementation order:

### High Priority (MVP Completion)
1. ✅ **Automatic Reroute Display for Customer** - Critical for feature completeness
2. ✅ **Full Valhalla Integration** - Replace OSRM placeholders
3. ✅ **Real Driver GPS Integration** - Move beyond simulation
4. ✅ **Driver HOS Tracking** - Regulatory compliance

### Medium Priority (Enhanced UX)
5. ✅ **Historical Performance Dashboard** - Valuable insights for managers
6. ✅ **Drag-to-Reorder Stops** - Better UX for route planning
7. ✅ **ETA Confidence Visualization** - Build trust with customers
8. ✅ **Alternative Route Comparison** - Better rerouting decisions

### Low Priority (Nice-to-Have)
9. ⏳ **Predictive ETA Models** - Requires significant data collection
10. ⏳ **Multi-Vehicle Fleet Dashboard** - Scale to enterprise
11. ⏳ **Mobile PWA** - Expand reach
12. ⏳ **Webhook Notifications** - API ecosystem

---

## 📝 Contributing

Want to implement one of these features? See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

When you complete a feature:
1. Move it from "🚧 Not Yet Implemented" to "✅ Implemented"
2. Update this document with the implementation date
3. Update [CHANGELOG.md](CHANGELOG.md) with version bump
4. Add tests and documentation

---

## 📞 Questions?

If you have questions about any planned feature or want to discuss implementation approaches, please:
- Open a GitHub issue
- Tag with `feature-request` or `implementation-question`
- Reference this document

---

**Repository**: https://github.com/IamSaileshSitaula/eta-tracker  
**Maintained by**: ETA Tracker Team  
**License**: MIT
