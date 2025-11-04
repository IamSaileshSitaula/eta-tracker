# 🚚 ETA Tracker

A full-stack, real-time shipment tracking system that supports unlimited stops, intelligent route planning, and live GPS tracking.

Built for customers to monitor deliveries with precision and understand the confidence level of each ETA, and for logistics managers to manage operations through:

- **Live ETA and confidence analytics**
- **Rerouting control interface**
- **Route and historical performance visualization** powered by the Valhalla API
- **GPS-based driver tracking** with multi-stop management
- **Integration of live weather, traffic, and congestion data** for smarter and adaptive ETA recalibration

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![TypeScript](https://img.shields.io/badge/TypeScript-5.8-blue)
![React](https://img.shields.io/badge/React-19.2-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)

## 📚 Documentation

- **[README.md](README.md)** - Complete project documentation (you are here)
- **[QUICKSTART.md](QUICKSTART.md)** - 🚀 Get started in 5 minutes with test data
- **[TESTING.md](TESTING.md)** - 🧪 Comprehensive testing guide with scenarios
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - How to contribute to this project
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and release notes
- **[LICENSE](LICENSE)** - MIT License terms

## ✨ Features

### Manager Dashboard
- 📍 **Structured Address Input** - 6-field address entry (street #, name, unit, city, state, ZIP)
- 🗺️ **Interactive Route Planning** - Unlimited intermediate stops with drag-to-reorder
- 🏢 **Facility Quick Select** - Predefined warehouse/facility addresses
- 🔄 **Real-time Geocoding** - OpenStreetMap Nominatim API with caching
- 📊 **Route Overview** - Live ETA calculations with traffic considerations
- 🎯 **One-Click Deployment** - Generate tracking numbers and push to customer view
- 🔀 **Rerouting Control Interface** - Manual reroute triggers and optimization controls
- 📍 **GPS-Based Driver Tracking** - Multi-stop management with real-time position updates (30-second intervals)
- 🌐 **Live Data Integration** - Weather, traffic, and congestion data for adaptive ETA recalibration
- 📊 **ETA Confidence Analytics** - Understand confidence level of each ETA provided every 30 seconds

### Customer Tracking View
- 📡 **Live GPS Tracking** - Real-time vehicle position updates via Socket.io (30-second intervals)
- ⏱️ **Dynamic ETAs** - EWMA-based arrival time predictions with confidence levels
- 🚦 **Traffic Awareness** - Visual traffic congestion indicators
- 🌦️ **Weather Advisories** - Delay notifications with severity levels
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile
- 📈 **ETA Confidence Display** - Real-time confidence scoring for each delivery estimate

## 🏗️ Architecture

```
┌─────────────────┐      WebSocket      ┌──────────────────┐
│  React Frontend │ ←─────────────────→ │  Flask Backend   │
│  (TypeScript)   │      REST API       │  (Python)        │
└─────────────────┘                     └──────────────────┘
        │                                        │
        │ Leaflet Maps                           │ SQLAlchemy
        ▼                                        ▼
┌─────────────────┐                     ┌──────────────────┐
│ OpenStreetMap   │                     │   PostgreSQL     │
│ Nominatim API   │                     │   Database       │
└─────────────────┘                     └──────────────────┘
```

### Technology Stack

**Frontend:**
- React 19.2 with TypeScript
- React Router for navigation
- Socket.io Client for real-time updates
- Leaflet + Leaflet Routing Machine for maps
- Tailwind CSS for styling
- Vite for build tooling

**Backend:**
- Python 3.8+ with Flask
- Flask-SocketIO for WebSocket communication
- PostgreSQL database
- Valhalla routing engine
- Weather API integration
- GTFS support for transit mode

**Real-time Updates & Intelligence:**
- Socket.io bidirectional communication (30-second GPS intervals)
- GPS position broadcasting with confidence scoring
- Live ETA recalibration with EWMA-based predictions
- Traffic and weather event notifications
- Valhalla API integration for optimal route calculations
- Adaptive rerouting based on live conditions

**Key Technical Features:**
- 📡 **30-Second GPS Intervals** - Industry-standard tracking frequency (83% reduction in database load)
- 🇺🇸 **MPH Speed Limits** - Zone-based speeds (20-60 mph) for realistic simulation
- 📊 **ETA Confidence Scoring** - Real-time confidence levels (high/medium/low) updated every 30 seconds
- 🗺️ **Valhalla Routing Engine** - Professional-grade routing with traffic integration
- 🌐 **Live Data Fusion** - Weather, traffic, and congestion data for adaptive ETAs
- 🏢 **B2B Focus** - Commercial delivery optimization (retail, healthcare, industrial, hopspitillity)

## 📦 Installation

### Prerequisites

Ensure you have the following installed:
- **Node.js** 16+ and npm
- **Python** 3.8+
- **PostgreSQL** 12+
- **Docker Desktop** (for Valhalla routing engine)
- **Git**

### Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/eta_tracker.git
   cd eta_tracker
   ```

2. **Install frontend dependencies:**
   ```bash
   npm install
   ```

3. **Install backend dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   # Copy example env file
   cp .env.example .env
   
   # Edit .env with your configuration
   ```

   Required environment variables:
   - `DATABASE_URL` - PostgreSQL connection string
   - `SECRET_KEY` - Flask session security key
   - `VALHALLA_API_URL` (optional) - Routing engine URL
   - `WEATHER_API_KEY` (optional) - Weather service API key

5. **Initialize database:**
   ```bash
   python data/db.py
   ```

6. **Set up Valhalla Routing Engine (Optional but Recommended):**
   
   Valhalla provides professional truck routing with height/weight constraints. Without it, the system falls back to OSRM (limited features).
   
   **First-time setup (takes 15-20 minutes):**
   ```bash
   # Windows
   start_valhalla.bat
   
   # Linux/Mac
   docker-compose -f docker-compose.valhalla.yml up -d
   ```
   
   This will:
   - Download Valhalla Docker image
   - Download Texas OSM road data (~150 MB)
   - Build routing tiles (one-time, 10-15 minutes)
   - Start Valhalla server on port 8002
   
   **Update your `.env` file:**
   ```bash
   VALHALLA_URL=http://localhost:8002
   ```
   
   **Subsequent starts (takes seconds):**
   ```bash
   docker start eta-tracker-valhalla
   ```
   
   **Verify Valhalla is working:**
   ```bash
   curl http://localhost:8002/status
   ```

7. **Start the backend server:**
   ```bash
   python backend/app.py
   # Or use the batch file on Windows:
   start_backend.bat
   ```

8. **Start the frontend dev server:**
   ```bash
   npm run dev
   ```

9. **Open your browser:**
   ```
   http://localhost:5173
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
   - confidence interval

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

## 🌐 API Endpoints

### Shipments

- `GET /v1/shipments` - List all shipments
- `POST /v1/shipments` - Create new shipment
- `GET /v1/shipments/{id}` - Get shipment details
- `GET /v1/shipments/{id}/status` - Get real-time status

### Tracking

- `GET /api/track/{tracking_number}` - Track by number

### Real-time Events (Socket.io)

- `subscribe` - Subscribe to shipment updates
- `position_update` - Vehicle GPS position event
- `eta_update` - Updated ETA calculations
- `delay_info` - Delay notification event
- `reroute_suggested` - Alternative route event

```bash
python data/db.py
```

### 5. Ingest GTFS Data (For Transit Mode)

To populate the database with the GTFS schedule data, run the ingestion script. This will download the zip file specified in your `.env` and load it into the `gtfs` schema.

```bash
python data/gtfs_ingest.py
```

### 6. Frontend Setup

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

**Built with ❤️ by the ETA Tracker Team**

````
