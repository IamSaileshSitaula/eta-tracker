/**
 * ETA Tracker Application
 * 
 * Main application component with routing for:
 * - Manager Dashboard: Plan shipments and monitor routes
 * - Customer Tracking: Real-time shipment tracking view
 * 
 * @author ETA Tracker Team
 * @version 1.0.0
 */

import React from 'react';
import { HashRouter, Routes, Route, Link } from 'react-router-dom';
import { DashboardPage } from './pages/DashboardPage';
import { TrackingPage } from './pages/TrackingPage';

/**
 * Root App Component
 * Provides navigation and routing for the entire application
 * 
 * Routes:
 * - / - Manager Dashboard for creating and monitoring shipments
 * - /track - Customer tracking page with tracking number input
 * - /track/:trackingNumber - Customer tracking page with pre-filled tracking number
 */
const App: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-900 text-gray-200">
      <HashRouter>
        {/* Navigation Bar */}
        <nav className="bg-gray-800 p-4 shadow-lg">
          <div className="container mx-auto flex justify-between items-center">
            <Link 
              to="/" 
              className="text-2xl font-bold text-cyan-400 hover:text-cyan-300 transition-colors"
            >
              🚚 ETA Tracker
            </Link>
            <div className="flex gap-2">
              <Link 
                to="/" 
                className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors"
              >
                Manager Dashboard
              </Link>
              <Link 
                to="/track" 
                className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors"
              >
                Customer Tracking
              </Link>
            </div>
          </div>
        </nav>

        {/* Main Content Area */}
        <main>
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/track" element={<TrackingPage />} />
            <Route path="/track/:trackingNumber" element={<TrackingPage />} />
          </Routes>
        </main>
      </HashRouter>
    </div>
  );
};

export default App;
