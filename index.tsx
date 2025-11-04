
/**
 * Application Entry Point
 * 
 * Initializes the React application and mounts it to the DOM.
 * Uses React 19's StrictMode for development checks.
 * 
 * @author ETA Tracker Team
 * @version 1.0.0
 */

import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

// Get the root DOM element
const rootElement = document.getElementById('root');
if (!rootElement) {
  throw new Error('Failed to find root element. Check that index.html has a div with id="root"');
}

// Create React root and render the application
const root = ReactDOM.createRoot(rootElement);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
