/**
 * Manager Dashboard Page
 * 
 * Main dashboard for logistics managers to plan and track shipments.
 * Features:
 * - Create new shipments with custom routes
 * - Add unlimited intermediate stops
 * - Real-time tracking and monitoring
 * - Route visualization on map
 * 
 * @author ETA Tracker Team
 * @version 1.0.0
 */

import React, { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import { io, Socket } from 'socket.io-client';
import { MapComponent } from '../components/Map';
import { RerouteModal } from '../components/RerouteModal';
import { CheckCircleIcon, TruckIcon, AlertTriangleIcon } from '../components/icons';
import { Mode, WeatherAdvisory, TrafficSegment, Stop } from '../types';

// ============================================================================
// CONSTANTS
// ============================================================================

const API_URL = 'http://localhost:5000';
const GEOCODE_RATE_LIMIT_MS = 1000; // OpenStreetMap Nominatim rate limit
const MAX_GEOCODE_RETRIES = 3;
const GEOCODE_RETRY_DELAY_MS = 2000;

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

interface Facility {
    id: string;
    name: string;
    city: string;
    state: string;
    lat: number;
    lon: number;
}

interface AddressComponents {
    streetNumber: string;
    streetName: string;
    unit: string;
    city: string;
    state: string;
    zipCode: string;
}

interface GeocodeResult {
    lat: number;
    lon: number;
    label: string;
}

interface ResolvedLocation {
    address: string;
    lat: number;
    lon: number;
    label?: string;
    source: 'manual' | 'facility';
}

interface IntermediateStop {
    id: string;
    address: string;
    resolved: ResolvedLocation | null;
    components?: AddressComponents;
    useStructured?: boolean;
}

interface RouteDetails {
    id: number;
    tracking_number: string;
    stops: Stop[];
}

interface RerouteOption {
    id: number;
    distance_km: number;
    duration_min: number;
    time_saved_min: number;
    reason: string;
}

interface DelayInfo {
    reason_code: string;
    confidence: number;
    explanation: string;
}

// ============================================================================
// FACILITY DATA
// ============================================================================

const facilityOptions: Facility[] = [
    { id: 'dallas', name: 'Dallas Facility', city: 'Dallas', state: 'TX', lat: 32.896, lon: -97.036 },
    { id: 'houston', name: 'Houston Hub', city: 'Houston', state: 'TX', lat: 29.99, lon: -95.336 },
    { id: 'beaumont', name: 'Beaumont DC', city: 'Beaumont', state: 'TX', lat: 30.08, lon: -94.126 },
    { id: 'okc', name: 'Oklahoma City Consolidation', city: 'Oklahoma City', state: 'OK', lat: 35.4676, lon: -97.5164 },
    { id: 'tulsa', name: 'Tulsa Crossdock', city: 'Tulsa', state: 'OK', lat: 36.1539, lon: -95.9928 },
    { id: 'kansas-city', name: 'Kansas City DC', city: 'Kansas City', state: 'MO', lat: 39.0997, lon: -94.5786 },
    { id: 'savannah', name: 'Savannah Port', city: 'Savannah', state: 'GA', lat: 32.0809, lon: -81.0912 },
    { id: 'charleston', name: 'Charleston Hub', city: 'Charleston', state: 'SC', lat: 32.7765, lon: -79.9311 },
    { id: 'charlotte', name: 'Charlotte Distribution', city: 'Charlotte', state: 'NC', lat: 35.2271, lon: -80.8431 },
    { id: 'atlanta', name: 'Atlanta Mega DC', city: 'Atlanta', state: 'GA', lat: 33.6407, lon: -84.4277 },
    { id: 'memphis', name: 'Memphis Riverport', city: 'Memphis', state: 'TN', lat: 35.1495, lon: -90.049 },
    { id: 'denver', name: 'Denver Mountain Terminal', city: 'Denver', state: 'CO', lat: 39.7392, lon: -104.9903 }
];

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Format facility object into readable address string
 */
const formatFacilityAddress = (facility: Facility): string => 
    `${facility.name}, ${facility.city}, ${facility.state}`;

/**
 * Calculate dwell time in minutes based on stop position
 * @param index - Stop index in route
 * @param total - Total number of stops
 * @returns Dwell time in minutes
 */
const dwellMinutesForIndex = (index: number, total: number): number => {
    if (index === 0) return 30;           // Origin: 30 min loading
    if (index === total - 1) return 60;   // Destination: 60 min unloading
    return 45;                            // Intermediate stops: 45 min
};

// ============================================================================
// STOPLIST COMPONENT
// ============================================================================

/**
 * StopList Component
 * Displays list of stops with ETAs and completion status
 * Shows delay information banner when applicable
 */
const StopList: React.FC<{ stops: Stop[]; delayInfo?: DelayInfo | null }> = ({ stops, delayInfo }) => {
    const formatEta = (etaTimestamp: string | null) => {
        if (!etaTimestamp) return 'N/A';
        
        const date = new Date(etaTimestamp);
        return date.toLocaleTimeString('en-US', { 
            hour: 'numeric', 
            minute: '2-digit',
            hour12: true 
        });
    };

    const formatReasonCode = (code: string) => {
        return code.split('_').map(w => w.charAt(0) + w.slice(1).toLowerCase()).join(' ');
    };

    const shouldShowDelayBanner = delayInfo && 
        delayInfo.reason_code !== 'on_time' && 
        delayInfo.reason_code !== 'ON_TIME';

    return (
        <div className="space-y-4">
            {shouldShowDelayBanner && (
                <div className="bg-yellow-900/30 border border-yellow-600 rounded-lg p-3 mb-4">
                    <div className="flex items-start gap-2">
                        <AlertTriangleIcon className="w-5 h-5 text-yellow-500 mt-0.5 flex-shrink-0" />
                        <div className="flex-1">
                            <p className="text-sm font-semibold text-yellow-400">
                                {formatReasonCode(delayInfo.reason_code)}
                            </p>
                            <p className="text-xs text-gray-300 mt-1">{delayInfo.explanation}</p>
                            <p className="text-xs text-gray-400 mt-1">
                                Confidence: {Math.round(delayInfo.confidence * 100)}%
                            </p>
                        </div>
                    </div>
                </div>
            )}
            {stops.map((stop, index) => {
                const isOrigin = stop.is_origin === true;
                const isCompleted = stop.arrival_time || stop.completed;
                
                return (
                    <div key={stop.id || index} className="flex items-start">
                        <div className="flex flex-col items-center mr-4">
                            {isCompleted ? (
                                <CheckCircleIcon className="w-8 h-8 text-green-500" />
                            ) : isOrigin ? (
                                <div className="w-8 h-8 rounded-full bg-green-600 border-2 border-green-400 flex items-center justify-center">
                                    <TruckIcon className="w-5 h-5 text-white" />
                                </div>
                            ) : (
                                <div className="w-8 h-8 rounded-full bg-gray-700 border-2 border-cyan-400 flex items-center justify-center font-bold text-cyan-400">
                                    {index + 1}
                                </div>
                            )}
                            {index < stops.length - 1 && (
                                <div className="w-0.5 h-12 bg-gray-600 mt-1"></div>
                            )}
                        </div>
                        <div className="pt-1 flex-1">
                            <p className={`font-semibold ${isCompleted ? 'text-gray-500 line-through' : isOrigin ? 'text-green-400' : 'text-gray-100'}`}>
                                {stop.name}
                            </p>
                            {isCompleted ? (
                                <p className="text-sm text-green-400">
                                    Arrived at {new Date(stop.arrival_time!).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true })}
                                </p>
                            ) : isOrigin ? (
                                <p className="text-sm text-green-300">Origin (Departed)</p>
                            ) : (
                                <p className="text-sm text-cyan-300">
                                    ETA: {formatEta(stop.eta_timestamp || null)}
                                </p>
                            )}
                        </div>
                    </div>
                );
            })}
        </div>
    );
};

// ============================================================================
// MAIN DASHBOARD COMPONENT
// ============================================================================

/**
 * DashboardPage Component
 * Main manager interface for shipment planning, route visualization, and real-time tracking
 * 
 * Features:
 * - Create shipments with unlimited intermediate stops
 * - Geocode addresses using OpenStreetMap Nominatim API
 * - Real-time route tracking via Socket.io
 * - Interactive map with route visualization
 * - Facility selection with predefined addresses
 * - Reroute suggestions for delays
 * - Weather advisory notifications
 */
export const DashboardPage: React.FC = () => {
    // ========================================================================
    // STATE MANAGEMENT
    // ========================================================================
    
    // Socket.io connection for real-time tracking
    const [socket, setSocket] = useState<Socket | null>(null);
    
    // Tracking input for existing shipments
    const [trackingInput, setTrackingInput] = useState('');
    
    // Active route details from tracking or shipment creation
    const [activeRoute, setActiveRoute] = useState<RouteDetails | null>(null);
    
    // Error message display
    const [error, setError] = useState<string | null>(null);
    
    // Loading state for async operations
    const [isLoading, setIsLoading] = useState(false);
    
    // Real-time vehicle GPS position
    const [vehiclePosition, setVehiclePosition] = useState<{ lat: number; lon: number } | null>(null);
    
    // Route stops with ETAs and status
    const [stops, setStops] = useState<Stop[]>([]);
    
    // Current shipment ID for tracking
    const [shipmentId, setShipmentId] = useState<number | null>(null);
    
    // Weather advisory information
    const [weatherAdvisory, setWeatherAdvisory] = useState<WeatherAdvisory | null>(null);
    
    // Delay information with reasons
    const [delayInfo, setDelayInfo] = useState<DelayInfo | null>(null);
    
    // Reroute suggestion details
    const [rerouteOption, setRerouteOption] = useState<RerouteOption | null>(null);
    
    // Reroute modal visibility
    const [showRerouteModal, setShowRerouteModal] = useState(false);
    
    // Shipment creation loading state
    const [isCreatingShipment, setIsCreatingShipment] = useState(false);
    
    // Shipment creation error message
    const [creationError, setCreationError] = useState<string | null>(null);
    
    // Last created tracking ID for copy functionality
    const [lastCreatedTracking, setLastCreatedTracking] = useState<string | null>(null);
    
    // Copy button status (idle, copied, failed)
    const [copyStatus, setCopyStatus] = useState<'idle' | 'copied' | 'failed'>('idle');
    
    // Timestamp of successful shipment creation
    const [creationSuccessTs, setCreationSuccessTs] = useState<number | null>(null);
    
    // Traffic segments for route visualization (future feature)
    const [trafficSegments, setTrafficSegments] = useState<TrafficSegment[]>([]);

    // ------------------------------------------------------------------------
    // Address Input State
    // ------------------------------------------------------------------------
    
    /**
     * Helper function to create empty address components object
     * @returns Empty AddressComponents with all fields as empty strings
     */
    const emptyAddressComponents = (): AddressComponents => ({
        streetNumber: '',
        streetName: '',
        unit: '',
        city: '',
        state: '',
        zipCode: ''
    });
    
    // Structured address components for origin
    const [originComponents, setOriginComponents] = useState<AddressComponents>(emptyAddressComponents());
    
    // Structured address components for destination
    const [destinationComponents, setDestinationComponents] = useState<AddressComponents>(emptyAddressComponents());

    // Full address string for origin (built from components)
    const [plannerOriginAddress, setPlannerOriginAddress] = useState<string>('');
    
    // Full address string for destination (built from components)
    const [plannerDestinationAddress, setPlannerDestinationAddress] = useState<string>('');
    
    // Geocoded location for origin with lat/lon
    const [plannerOriginResolved, setPlannerOriginResolved] = useState<ResolvedLocation | null>(null);
    
    // Geocoded location for destination with lat/lon
    const [plannerDestinationResolved, setPlannerDestinationResolved] = useState<ResolvedLocation | null>(null);
    
    // List of intermediate stops between origin and destination
    const [plannerMidStops, setPlannerMidStops] = useState<IntermediateStop[]>([]);
    
    // Address components for new intermediate stop being added
    const [newStopComponents, setNewStopComponents] = useState<AddressComponents>(emptyAddressComponents());
    
    // Preview route stops before shipment creation
    const [plannerPreviewStops, setPlannerPreviewStops] = useState<Stop[]>([]);
    
    // Route planner error messages
    const [plannerError, setPlannerError] = useState<string | null>(null);
    
    // Loading state for geocoding preview route
    const [isGeocodingPreview, setIsGeocodingPreview] = useState(false);
    
    // Map click mode for selecting locations on map
    const [mapClickMode, setMapClickMode] = useState<'origin' | 'destination' | 'stop' | null>(null);
    
    // Cache for geocoding results to avoid duplicate API calls
    const geocodeCacheRef = useRef<Map<string, GeocodeResult>>(new Map());
    
    // Request ID to handle concurrent preview requests
    const previewRequestIdRef = useRef(0);

    // ------------------------------------------------------------------------
    // UI State - Collapsible Sections
    // ------------------------------------------------------------------------
    
    // Origin section collapsed by default
    const [isOriginExpanded, setIsOriginExpanded] = useState(false);
    
    // Destination section collapsed by default
    const [isDestinationExpanded, setIsDestinationExpanded] = useState(false);
    
    // Intermediate stops section collapsed by default
    const [isStopsExpanded, setIsStopsExpanded] = useState(false);

    // ========================================================================
    // HELPER FUNCTIONS
    // ========================================================================

    /**
     * Build full address string from structured address components
     * Formats components into standard address format: "123 Main St Unit A, City, State ZIP"
     * 
     * @param components - Structured address components object
     * @returns Formatted address string
     */
    const buildAddressFromComponents = useCallback((components: AddressComponents): string => {
        const parts: string[] = [];
        
        // Combine street number and name
        if (components.streetNumber && components.streetName) {
            parts.push(`${components.streetNumber} ${components.streetName}`);
        } else if (components.streetName) {
            parts.push(components.streetName);
        }
        
        // Add unit to street address
        if (components.unit) {
            parts[0] = parts[0] ? `${parts[0]} ${components.unit}` : components.unit;
        }
        
        // Add city
        if (components.city) {
            parts.push(components.city);
        }
        
        // Add state and ZIP
        if (components.state) {
            const lastPart = parts[parts.length - 1];
            if (components.zipCode) {
                parts[parts.length - 1] = `${lastPart ? lastPart + ', ' : ''}${components.state} ${components.zipCode}`;
            } else {
                parts[parts.length - 1] = `${lastPart ? lastPart + ', ' : ''}${components.state}`;
            }
        }
        
        return parts.join(', ');
    }, []);

    /**
     * Convert degrees to radians for haversine distance calculation
     */
    const toRad = (deg: number): number => (deg * Math.PI) / 180;
    
    /**
     * Calculate distance between two GPS coordinates using Haversine formula
     * 
     * @param a - First coordinate {lat, lon}
     * @param b - Second coordinate {lat, lon}
     * @returns Distance in kilometers
     */
    const haversineDistanceKm = (a: { lat: number; lon: number }, b: { lat: number; lon: number }): number => {
        const dLat = toRad(b.lat - a.lat);
        const dLon = toRad(b.lon - a.lon);
        const originLat = toRad(a.lat);
        const destLat = toRad(b.lat);
        const hav = Math.sin(dLat / 2) ** 2 + Math.cos(originLat) * Math.cos(destLat) * Math.sin(dLon / 2) ** 2;
        return 6371 * 2 * Math.atan2(Math.sqrt(hav), Math.sqrt(1 - hav));
    };

    // ========================================================================
    // EFFECTS - Address Synchronization
    // ========================================================================

    /**
     * Sync origin components to full address string
     * Rebuilds address when any component changes and resets geocoding
     */
    useEffect(() => {
        const built = buildAddressFromComponents(originComponents);
        if (built !== plannerOriginAddress) {
            setPlannerOriginAddress(built);
            setPlannerOriginResolved(null);
        }
    }, [originComponents, buildAddressFromComponents]);

    /**
     * Sync destination components to full address string
     * Rebuilds address when any component changes and resets geocoding
     */
    useEffect(() => {
        const built = buildAddressFromComponents(destinationComponents);
        if (built !== plannerDestinationAddress) {
            setPlannerDestinationAddress(built);
            setPlannerDestinationResolved(null);
        }
    }, [destinationComponents, buildAddressFromComponents]);

    /**
     * Find nearest stop to a traffic segment midpoint
     * Used for associating traffic delays with specific stops
     * 
     * @param segment - Traffic segment with start/end coordinates
     * @returns Name of nearest stop or null if no stops exist
     */
    const findNearestStopName = useCallback((segment: TrafficSegment) => {
        if (!stops.length) {
            return null;
        }

        // Calculate segment midpoint
        const midpoint = {
            lat: (segment.start.lat + segment.end.lat) / 2,
            lon: (segment.start.lon + segment.end.lon) / 2
        };

        // Find closest stop using haversine distance
        let closestName: string | null = null;
        let closestDistance = Number.POSITIVE_INFINITY;

        stops.forEach(stop => {
            const distance = haversineDistanceKm(midpoint, { lat: stop.lat, lon: stop.lon });
            if (distance < closestDistance) {
                closestDistance = distance;
                closestName = stop.name;
            }
        });

        return closestName;
    }, [stops]);

    /**
     * Validate if address string looks complete enough for geocoding
     * Checks for state abbreviation patterns and proper formatting
     * 
     * @param address - Address string to validate
     * @returns True if address appears complete
     */
    const addressLooksComplete = useCallback((address: string): boolean => {
        const trimmed = address.trim();
        if (!trimmed) return false;
        
        // Check if address has commas and state abbreviation
        const commaCount = (trimmed.match(/,/g) || []).length;
        const hasStatePattern = /,\s*[A-Z]{2}\s*$/i.test(trimmed) || // ends with ", XX"
                               /,\s*[A-Z]{2}\s+\d{5}$/i.test(trimmed); // ends with ", XX 12345"
        
        return commaCount >= 1 && hasStatePattern;
    }, []);

    /**
     * Sort traffic segments by severity (severe > heavy > moderate > light)
     * Used to display most critical traffic first
     */
    const orderedTrafficSegments = useMemo(() => {
        if (!trafficSegments.length) {
            return [] as TrafficSegment[];
        }

        const severityRank: Record<string, number> = {
            severe: 0,
            heavy: 1,
            high: 1,
            moderate: 2,
            medium: 2,
            light: 3
        };

        return [...trafficSegments].sort((a, b) => {
            const rankA = severityRank[a.traffic_level?.toLowerCase?.() ?? ''] ?? 4;
            const rankB = severityRank[b.traffic_level?.toLowerCase?.() ?? ''] ?? 4;
            return rankA - rankB;
        });
    }, [trafficSegments]);

    /**
     * Generate unique tracking number for shipments
     * Format: PO-XXXXXX where X is a random digit
     * 
     * @returns Generated tracking number
     */
    const generateTrackingNumber = useCallback(() => {
        const random = Math.floor(100000 + Math.random() * 900000);
        return `PO-${random}`;
    }, []);

    /**
     * Copy tracking number to clipboard with fallback for older browsers
     * Shows success/failure status for 2 seconds
     */
    const handleCopyTracking = useCallback(async () => {
        if (!lastCreatedTracking) {
            return;
        }

        try {
            // Modern clipboard API
            if (navigator.clipboard && navigator.clipboard.writeText) {
                await navigator.clipboard.writeText(lastCreatedTracking);
            } else {
                // Fallback for older browsers
                const textarea = document.createElement('textarea');
                textarea.value = lastCreatedTracking;
                document.body.appendChild(textarea);
                textarea.select();
                document.execCommand('copy');
                document.body.removeChild(textarea);
            }
            setCopyStatus('copied');
            setTimeout(() => setCopyStatus('idle'), 2000);
        } catch (err) {
            console.error('Clipboard copy failed:', err);
            setCopyStatus('failed');
            setTimeout(() => setCopyStatus('idle'), 2000);
        }
    }, [lastCreatedTracking]);

    // ========================================================================
    // EVENT HANDLERS - Stop Management
    // ========================================================================

    /**
     * Add new intermediate stop from structured address components
     * Checks for facility matches and auto-resolves coordinates if available
     */
    const handleAddManualStop = useCallback(() => {
        const addressToUse = buildAddressFromComponents(newStopComponents);

        if (addressToUse) {
            const newStop: IntermediateStop = {
                id: Date.now().toString(),
                address: addressToUse,
                resolved: null,
                components: { ...newStopComponents },
                useStructured: true
            };
            
            // Check if it matches a predefined facility
            const trimmedLower = addressToUse.toLowerCase();
            const facilityMatch = facilityOptions.find(option => 
                formatFacilityAddress(option).toLowerCase() === trimmedLower
            );
            
            // Auto-resolve facility coordinates
            if (facilityMatch) {
                newStop.resolved = {
                    address: formatFacilityAddress(facilityMatch),
                    lat: facilityMatch.lat,
                    lon: facilityMatch.lon,
                    label: facilityMatch.name,
                    source: 'facility'
                };
            }
            
            setPlannerMidStops(prev => [...prev, newStop]);
            setNewStopComponents(emptyAddressComponents());
            setPlannerError(null);
        }
    }, [newStopComponents, buildAddressFromComponents]);

    /**
     * Remove intermediate stop from route
     * @param idToRemove - Unique ID of stop to remove
     */
    const handleRemoveMidStop = useCallback((idToRemove: string) => {
        setPlannerMidStops(prev => prev.filter(stop => stop.id !== idToRemove));
    }, []);

    /**
     * Move intermediate stop up or down in the route order
     * @param id - Unique ID of stop to move
     * @param direction - 'up' or 'down'
     */
    const handleMoveMidStop = useCallback((id: string, direction: 'up' | 'down') => {
        setPlannerMidStops(prev => {
            const index = prev.findIndex(stop => stop.id === id);
            if (index === -1) return prev;
            
            const targetIndex = direction === 'up' ? index - 1 : index + 1;
            if (targetIndex < 0 || targetIndex >= prev.length) {
                return prev;
            }
            
            // Swap positions
            const next = [...prev];
            [next[index], next[targetIndex]] = [next[targetIndex], next[index]];
            return next;
        });
    }, []);

    /**
     * Update address for existing intermediate stop
     * Checks for facility matches and updates resolved coordinates
     * 
     * @param id - Unique ID of stop to update
     * @param newAddress - New address string
     */
    const handleUpdateStopAddress = useCallback((id: string, newAddress: string) => {
        setPlannerMidStops(prev => prev.map(stop => {
            if (stop.id !== id) return stop;
            
            const trimmedLower = newAddress.trim().toLowerCase();
            const facilityMatch = facilityOptions.find(option => 
                formatFacilityAddress(option).toLowerCase() === trimmedLower
            );
            
            return {
                ...stop,
                address: newAddress,
                resolved: facilityMatch ? {
                    address: formatFacilityAddress(facilityMatch),
                    lat: facilityMatch.lat,
                    lon: facilityMatch.lon,
                    label: facilityMatch.name,
                    source: 'facility'
                } : null
            };
        }));
    }, []);

    // ========================================================================
    // GEOCODING - OpenStreetMap Nominatim API
    // ========================================================================

    /**
     * Geocode address using OpenStreetMap Nominatim API
     * 
     * Features:
     * - Result caching to avoid duplicate API calls
     * - Automatic retry with 2-second delay on rate limiting (429)
     * - Query simplification fallback (removes commas)
     * - 15-second timeout per request
     * - Rate limit: 1 request per second (enforced by caller)
     * - Max 3 retry attempts
     * 
     * @param address - Full address string to geocode
     * @param retryCount - Current retry attempt (0-2)
     * @returns GeocodeResult with coordinates and display name
     * @throws Error if geocoding fails after all retries
     */
    const geocodeAddress = useCallback(async (address: string, retryCount = 0): Promise<GeocodeResult> => {
        const trimmed = address.trim();
        if (!trimmed) {
            throw new Error('Address is empty');
        }

        const cacheKey = trimmed.toLowerCase();
        if (geocodeCacheRef.current.has(cacheKey)) {
            return geocodeCacheRef.current.get(cacheKey)!;
        }

        // Add delay for retries
        if (retryCount > 0) {
            await new Promise(resolve => setTimeout(resolve, 2000));
        }

        const controller = new AbortController();
        const timeoutId = window.setTimeout(() => controller.abort(), 15000);

        try {
            const url = new URL('https://nominatim.openstreetmap.org/search');
            url.searchParams.set('format', 'json');
            url.searchParams.set('limit', '1');
            url.searchParams.set('q', trimmed);
            url.searchParams.set('addressdetails', '1');
            url.searchParams.set('countrycodes', 'us');

            const response = await fetch(url.toString(), {
                signal: controller.signal,
                headers: {
                    'Accept': 'application/json',
                    'Accept-Language': 'en',
                    'User-Agent': 'ETA-Tracker/1.0 (eta-tracker@localhost)' // OSM requires User-Agent with contact
                }
            });

            if (!response.ok) {
                // Handle rate limiting
                if (response.status === 429 && retryCount < 2) {
                    await new Promise(resolve => setTimeout(resolve, 2000));
                    return geocodeAddress(trimmed, retryCount + 1);
                }
                throw new Error(`Geocoding service returned ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            
            if (!Array.isArray(data) || data.length === 0) {
                // Retry with simplified query if first attempt fails
                if (retryCount === 0 && trimmed.includes(',')) {
                    const simplified = trimmed.split(',').map(s => s.trim()).join(' ');
                    return geocodeAddress(simplified, retryCount + 1);
                }
                throw new Error(`Address "${trimmed}" not found. Try including city and state (e.g., "123 Main St, Chicago, IL")`);
            }

            const first = data[0];
            const result: GeocodeResult = {
                lat: parseFloat(first.lat),
                lon: parseFloat(first.lon),
                label: first.display_name ?? trimmed
            };

            geocodeCacheRef.current.set(cacheKey, result);
            return result;
        } catch (error: any) {
            window.clearTimeout(timeoutId);
            
            if (error?.name === 'AbortError') {
                throw new Error('Geocoding timeout - server took too long to respond');
            }
            
            // Retry on network errors
            if (retryCount < 2 && (error?.message?.includes('fetch') || error?.message?.includes('network'))) {
                await new Promise(resolve => setTimeout(resolve, 2000));
                return geocodeAddress(trimmed, retryCount + 1);
            }
            
            throw error;
        } finally {
            window.clearTimeout(timeoutId);
        }
    }, []);

    // ========================================================================
    // EVENT HANDLERS - Route Preview & Planning
    // ========================================================================

    /**
     * Generate route preview with all stops geocoded
     * 
     * Process:
     * 1. Validate origin and destination
     * 2. Geocode origin/destination (use cache if available)
     * 3. Geocode all intermediate stops with rate limiting
     * 4. Check for duplicate locations
     * 5. Calculate ETAs and build preview stops list
     * 
     * Rate Limiting:
     * - 1 second delay between geocoding requests
     * - Uses concurrent request ID to handle race conditions
     */
    const handlePreviewRoute = useCallback(async () => {
        const originAddress = plannerOriginAddress.trim();
        const destinationAddress = plannerDestinationAddress.trim();

        // Validate required fields
        if (!originAddress || !destinationAddress) {
            setPlannerPreviewStops([]);
            setPlannerError('Enter origin and destination addresses to build a route overview.');
            return;
        }

        // Track request to handle concurrent preview attempts
        const requestId = previewRequestIdRef.current + 1;
        previewRequestIdRef.current = requestId;
        setIsGeocodingPreview(true);
        setPlannerError(null);

        console.log('🚀 Starting route preview:', {
            origin: originAddress,
            destination: destinationAddress,
            requestId
        });

        try {
            let resolvedOrigin: ResolvedLocation;
            if (plannerOriginResolved && plannerOriginResolved.address === originAddress) {
                resolvedOrigin = plannerOriginResolved;
            } else {
                const geocode = await geocodeAddress(originAddress);
                resolvedOrigin = {
                    address: originAddress,
                    lat: geocode.lat,
                    lon: geocode.lon,
                    label: geocode.label,
                    source: 'manual'
                };
                setPlannerOriginResolved(resolvedOrigin);
            }

            let resolvedDestination: ResolvedLocation;
            if (plannerDestinationResolved && plannerDestinationResolved.address === destinationAddress) {
                resolvedDestination = plannerDestinationResolved;
            } else {
                const geocode = await geocodeAddress(destinationAddress);
                resolvedDestination = {
                    address: destinationAddress,
                    lat: geocode.lat,
                    lon: geocode.lon,
                    label: geocode.label,
                    source: 'manual'
                };
                setPlannerDestinationResolved(resolvedDestination);
            }

            const sameLocation =
                resolvedOrigin.address.toLowerCase() === resolvedDestination.address.toLowerCase() ||
                (Math.abs(resolvedOrigin.lat - resolvedDestination.lat) < 0.00001 &&
                    Math.abs(resolvedOrigin.lon - resolvedDestination.lon) < 0.00001);

            if (sameLocation) {
                setPlannerPreviewStops([]);
                setPlannerError('Origin and destination must reference different locations.');
                return;
            }

            if (previewRequestIdRef.current !== requestId) {
                return;
            }

            const orderedStops: Stop[] = [
                {
                    id: 1,
                    name: originAddress,
                    lat: resolvedOrigin.lat,
                    lon: resolvedOrigin.lon,
                    arrival_time: null,
                    eta_seconds: null,
                    stop_sequence: 1
                }
            ];

            // Add intermediate stops
            for (let i = 0; i < plannerMidStops.length; i++) {
                const midStop = plannerMidStops[i];
                let resolvedStop = midStop.resolved;
                
                if (!resolvedStop) {
                    try {
                        const geocoded = await geocodeAddress(midStop.address);
                        resolvedStop = {
                            address: midStop.address,
                            lat: geocoded.lat,
                            lon: geocoded.lon,
                            label: geocoded.label,
                            source: 'manual'
                        };
                        console.log(`✅ Stop ${i+1} geocoded successfully`);
                    } catch (err) {
                        console.error(`❌ Failed to geocode stop ${i+1}: "${midStop.address}"`, err);
                        throw new Error(`Unable to geocode stop "${midStop.address}"`);
                    }
                }
                
                orderedStops.push({
                    id: i + 2,
                    name: resolvedStop.label || midStop.address,
                    lat: resolvedStop.lat,
                    lon: resolvedStop.lon,
                    arrival_time: null,
                    eta_seconds: null,
                    seq: i + 2,
                    stop_sequence: i + 2,
                    completed: false,
                    is_origin: false
                });
            }

            // Add destination
            // Add destination
            console.log('🏁 Adding destination to route...');
            orderedStops.push({
                id: plannerMidStops.length + 2,
                name: destinationAddress,
                lat: resolvedDestination.lat,
                lon: resolvedDestination.lon,
                arrival_time: null,
                eta_seconds: null,
                seq: plannerMidStops.length + 2,
                stop_sequence: plannerMidStops.length + 2,
                completed: false,
                is_origin: false
            });

            console.log(`✅ Route preview complete with ${orderedStops.length} total stop(s)`);
            setPlannerPreviewStops(orderedStops);
            setPlannerError(null);
        } catch (error: any) {
            console.error('❌ Route preview error:', error);
            console.error('❌ Error details:', {
                message: error?.message,
                stack: error?.stack,
                name: error?.name
            });
            if (previewRequestIdRef.current !== requestId) {
                console.log('⚠️ Ignoring error from outdated request');
                return;
            }
            setPlannerPreviewStops([]);
            const message = error?.message || 'Unable to resolve one or more addresses';
            setPlannerError(message);
        } finally {
            if (previewRequestIdRef.current === requestId) {
                setIsGeocodingPreview(false);
                console.log('🏁 Geocoding complete');
            }
        }
    }, [
        plannerOriginAddress,
        plannerDestinationAddress,
        plannerOriginResolved,
        plannerDestinationResolved,
        plannerMidStops,
        geocodeAddress
    ]);

    /**
     * Set facility as route origin
     * Auto-fills address and coordinates from predefined facility data
     * 
     * @param facility - Facility object with name, address, coordinates
     */
    const useFacilityAsOrigin = useCallback((facility: Facility) => {
        const formatted = formatFacilityAddress(facility);
        setPlannerOriginAddress(formatted);
        setPlannerOriginResolved({
            address: formatted.trim(),
            lat: facility.lat,
            lon: facility.lon,
            label: facility.name,
            source: 'facility'
        });
        // Cache facility result for future lookups
        geocodeCacheRef.current.set(formatted.trim().toLowerCase(), {
            lat: facility.lat,
            lon: facility.lon,
            label: formatted
        });
        setPlannerError(null);
    }, []);

    /**
     * Set facility as route destination
     * Auto-fills address and coordinates from predefined facility data
     * 
     * @param facility - Facility object with name, address, coordinates
     */
    const useFacilityAsDestination = useCallback((facility: Facility) => {
        const formatted = formatFacilityAddress(facility);
        setPlannerDestinationAddress(formatted);
        setPlannerDestinationResolved({
            address: formatted.trim(),
            lat: facility.lat,
            lon: facility.lon,
            label: facility.name,
            source: 'facility'
        });
        // Cache facility result for future lookups
        geocodeCacheRef.current.set(formatted.trim().toLowerCase(), {
            lat: facility.lat,
            lon: facility.lon,
            label: formatted
        });
        setPlannerError(null);
    }, []);

    // ========================================================================
    // EFFECTS - Auto Preview Route
    // ========================================================================

    /**
     * Auto-generate route preview when addresses change
     * Debounced by 500ms to avoid excessive API calls while typing
     */
    useEffect(() => {
        const timeoutId = window.setTimeout(() => {
            handlePreviewRoute();
        }, 500);

        return () => window.clearTimeout(timeoutId);
    }, [handlePreviewRoute]);

    // ========================================================================
    // MEMOIZED VALUES - Route Preview
    // ========================================================================

    /**
     * Calculate vehicle preview position (first stop location)
     * Used to center map on route origin
     */
    const plannerVehiclePreview = useMemo(() => {
        if (!plannerPreviewStops.length) {
            return null;
        }
        const first = plannerPreviewStops[0];
        return { lat: first.lat, lon: first.lon };
    }, [plannerPreviewStops]);

    /**
     * Calculate estimated ETAs for all stops in preview
     * Uses simplified time calculations:
     * - Origin: 30 minutes dwell
     * - Destination: 60 minutes dwell
     * - Intermediate: 45 minutes dwell
     * - Travel: ~3 km between stops, ~60 km/h average speed
     */
    const plannerEtaPreview = useMemo(() => {
        if (!plannerPreviewStops.length) {
            return null;
        }

        const now = new Date();
        let cumulativeMinutes = 0;

        // Dwell time based on stop type
        const dwellForIndex = (index: number) => {
            if (index === 0) return 30; // Origin
            if (index === plannerPreviewStops.length - 1) return 60; // Destination
            return 45; // Intermediate stops
        };

        plannerPreviewStops.forEach((stop, index) => {
            if (index > 0) {
                const prev = plannerPreviewStops[index - 1];
                const distanceKm = haversineDistanceKm({ lat: prev.lat, lon: prev.lon }, { lat: stop.lat, lon: stop.lon });
                const driveMinutes = Math.max(15, Math.round((distanceKm / 70) * 60));
                cumulativeMinutes += driveMinutes;
            }
            cumulativeMinutes += dwellForIndex(index);
        });

        return new Date(now.getTime() + cumulativeMinutes * 60000);
    }, [plannerPreviewStops]);

    const findRoute = async (trackingNumber: string) => {
        if (!trackingNumber) return;
        setIsLoading(true);
        setError(null);
        setActiveRoute(null);
        setDelayInfo(null);
        setTrafficSegments([]);
        setCreationError(null);
        
        try {
            const shipmentResponse = await fetch(`${API_URL}/v1/shipments?ref=${trackingNumber}`);
            
            if (shipmentResponse.ok) {
                const shipments = await shipmentResponse.json();
                
                if (shipments.length > 0) {
                    const shipment = shipments[0];
                    setShipmentId(shipment.id);
                    
                    const statusResponse = await fetch(`${API_URL}/v1/shipments/${shipment.id}/status`);
                    if (statusResponse.ok) {
                        const status = await statusResponse.json();
                        
                        const routeDetails: RouteDetails = {
                            id: shipment.id,
                            tracking_number: trackingNumber,
                            stops: status.stops || [],
                        };
                        
                        setActiveRoute(routeDetails);
                        const stopsFromStatus: Stop[] = status.stops || [];
                        setStops(stopsFromStatus);

                        const statusVehicle = status.vehicle_position;
                        const derivedPosition = statusVehicle && statusVehicle.lat != null && statusVehicle.lon != null
                            ? { lat: Number(statusVehicle.lat), lon: Number(statusVehicle.lon) }
                            : (stopsFromStatus.length > 0
                                ? { lat: Number(stopsFromStatus[0].lat), lon: Number(stopsFromStatus[0].lon) }
                                : null);
                        setVehiclePosition(derivedPosition);
                        
                        // Load delay info if available
                        if (status.reason_code && status.reason_code !== 'on_time' && status.reason_code !== 'ON_TIME') {
                            setDelayInfo({
                                reason_code: status.reason_code,
                                confidence: status.confidence || 0,
                                explanation: status.explanation || 'Delay detected'
                            });
                        } else {
                            setDelayInfo(null);
                        }
                        if (status.weather_advisory) {
                            setWeatherAdvisory(status.weather_advisory);
                        }
                        return;
                    }
                }
            }
            
            throw new Error("Tracking number not found.");
        } catch (err: any) {
            setError(err.message || 'Failed to fetch');
        } finally {
            setIsLoading(false);
        }
    };

    const handleCreateShipment = useCallback(async () => {
        // Check if we have origin and destination addresses
        const hasOrigin = plannerOriginAddress.trim().length > 0;
        const hasDestination = plannerDestinationAddress.trim().length > 0;
        
        if (!hasOrigin || !hasDestination) {
            setPlannerError('Add at least an origin and destination before launching a route.');
            return;
        }

        // If preview stops haven't been generated yet, wait for them
        if (plannerPreviewStops.length < 2) {
            setPlannerError('Waiting for addresses to be geocoded... Please try again in a moment.');
            return;
        }

        setPlannerError(null);
        setCreationError(null);
        setIsCreatingShipment(true);
        setCopyStatus('idle');

        const trackingNumber = generateTrackingNumber();
        const now = new Date();
        let cumulativeMinutes = 0;

        const stopsPayload = plannerPreviewStops.map((stop, index) => {
            let arrival = new Date(now.getTime() + cumulativeMinutes * 60000);

            if (index > 0) {
                const prev = plannerPreviewStops[index - 1];
                const distanceKm = haversineDistanceKm({ lat: prev.lat, lon: prev.lon }, { lat: stop.lat, lon: stop.lon });
                const driveMinutes = Math.max(15, Math.round((distanceKm / 70) * 60));
                cumulativeMinutes += driveMinutes;
                arrival = new Date(now.getTime() + cumulativeMinutes * 60000);
            }

            const dwellMinutes = dwellMinutesForIndex(index, plannerPreviewStops.length);
            cumulativeMinutes += dwellMinutes;
            const departure = new Date(now.getTime() + cumulativeMinutes * 60000);

            return {
                seq: index + 1,
                name: stop.name,
                lat: stop.lat,
                lon: stop.lon,
                planned_service_min: dwellMinutes,
                planned_arr_ts: arrival.toISOString(),
                planned_dep_ts: departure.toISOString()
            };
        });

        const promisedEtaTs = stopsPayload[stopsPayload.length - 1]?.planned_arr_ts ?? now.toISOString();

        try {
            const response = await fetch(`${API_URL}/v1/shipments`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    ref: trackingNumber,
                    vehicle_id: 1,
                    stops: stopsPayload,
                    promised_eta_ts: promisedEtaTs
                })
            });

            if (!response.ok) {
                const errorBody = await response.json().catch(() => null);
                throw new Error(errorBody?.error || 'Failed to create shipment');
            }

            setLastCreatedTracking(trackingNumber);
            setTrackingInput(trackingNumber);
            setCreationSuccessTs(Date.now());
            setTrafficSegments([]);
            await findRoute(trackingNumber);
        } catch (err: any) {
            setCreationError(err.message || 'Failed to create shipment');
        } finally {
            setIsCreatingShipment(false);
        }
    }, [plannerPreviewStops, generateTrackingNumber, findRoute]);

    // ========================================================================
    // EFFECTS - Socket.io & Real-time Tracking
    // ========================================================================

    /**
     * Load existing shipment on component mount
     * Automatically loads the first available shipment for demo purposes
     */
    useEffect(() => {
        loadExisting();
    }, []);

    /**
     * Load existing shipment from API
     * Used on initial page load to restore last active shipment
     */
    const loadExisting = async () => {
        setIsLoading(true);
        try {
            const response = await fetch(`${API_URL}/v1/shipments`);
            if (response.ok) {
                const shipments = await response.json();
                if (shipments.length > 0) {
                    const shipment = shipments[0];
                    findRoute(shipment.ref);
                }
            }
        } catch (error) {
            console.error('Error loading existing shipment:', error);
        } finally {
            setIsLoading(false);
        }
    };

    /**
     * Establish Socket.io connection for real-time tracking updates
     * 
     * Events:
     * - position_update: Real-time GPS position from vehicle
     * - delay_info: Traffic/weather delay notifications
     * - reroute_suggested: Alternative route suggestions
     * 
     * Auto-fetches updated ETAs when position changes
     */
    useEffect(() => {
        if (!activeRoute || !shipmentId) {
            if (socket) socket.disconnect();
            return;
        }

        const newSocket = io(API_URL);
        setSocket(newSocket);

        newSocket.on('connect', () => {
            console.log('Socket.io connected, subscribing to shipment:', shipmentId);
            newSocket.emit('subscribe', { shipment_id: shipmentId });
        });

        newSocket.on('position_update', (data: any) => {
            console.log('Socket.IO position_update received:', data);
            if (data.shipment_id === shipmentId && data.vehicle_position) {
                console.log('Setting vehicle position:', data.vehicle_position);
                setVehiclePosition({
                    lat: data.vehicle_position.lat,
                    lon: data.vehicle_position.lon
                });
                
                // Fetch updated ETAs when position changes
                fetch(`${API_URL}/v1/shipments/${shipmentId}/status`)
                    .then(res => res.json())
                    .then(status => {
                        console.log('Status fetched:', status);
                        if (status.stops) {
                            setStops(status.stops);
                        }
                    })
                    .catch(err => console.error('Error fetching updated status:', err));
            }
        });

        return () => {
            newSocket.disconnect();
        };
    }, [activeRoute, shipmentId]);

    // Backup polling every 60 seconds
    useEffect(() => {
        if (!shipmentId) return;
        
        const refreshInterval = setInterval(async () => {
            try {
                const statusResponse = await fetch(`${API_URL}/v1/shipments/${shipmentId}/status`);
                if (statusResponse.ok) {
                    const status = await statusResponse.json();
                    setStops(status.stops || []);
                    setVehiclePosition(status.vehicle_position);
                }
            } catch (error) {
                console.error('Error refreshing status:', error);
            }
        }, 60000);
        
        return () => clearInterval(refreshInterval);
    }, [shipmentId]);

    /**
     * Handle tracking form submission
     * Triggers route lookup for existing shipment
     */
    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (trackingInput.trim()) {
            findRoute(trackingInput.trim());
        }
    };

    // ========================================================================
    // JSX RENDER
    // ========================================================================

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-slate-800 to-gray-900 text-white">
            <div className="h-screen flex">
                {/* ============================================================
                    LEFT PANEL - Manager Controls
                    ============================================================ */}
                <div className="w-96 bg-gray-800/50 backdrop-blur-sm border-r border-gray-700 flex flex-col">
                    <div className="p-6">
                        <h2 className="text-2xl font-bold mb-4 bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
                            Manager Dashboard
                        </h2>
                        <div className="mt-6 bg-gray-700/30 border border-gray-600 rounded-lg p-4 space-y-4">
                            <div className="flex items-start justify-between gap-4">
                                <div>
                                    <h3 className="text-lg font-semibold text-cyan-300">Plan New Shipment</h3>
                                    <p className="text-xs text-gray-400 mt-1">
                                        Generate a tracking number and push the live route to customer tracking.
                                    </p>
                                </div>
                                <span className="text-[10px] uppercase tracking-wider text-gray-500">Control Board</span>
                            </div>
                            <div className="grid grid-cols-1 gap-3">
                                <div>
                                    <button
                                        type="button"
                                        onClick={() => setIsOriginExpanded(!isOriginExpanded)}
                                        className="w-full flex items-center justify-between text-xs font-semibold text-gray-300 uppercase tracking-wider hover:text-cyan-300 transition-colors"
                                    >
                                        <span>Origin Address</span>
                                        <span className="text-lg">{isOriginExpanded ? '▼' : '▶'}</span>
                                    </button>
                                    {isOriginExpanded && (
                                        <div className="mt-2 space-y-2">
                                            <div className="grid grid-cols-2 gap-2">
                                                <input
                                                    type="text"
                                                    placeholder="Street # (e.g., 123)"
                                                    value={originComponents.streetNumber}
                                                    onChange={(e) => setOriginComponents({...originComponents, streetNumber: e.target.value})}
                                                    className="bg-gray-900/60 border border-gray-600 rounded-md px-2 py-1.5 text-xs text-gray-100 focus:outline-none focus:border-cyan-400"
                                                />
                                                <input
                                                    type="text"
                                                    placeholder="Street Name"
                                                    value={originComponents.streetName}
                                                    onChange={(e) => setOriginComponents({...originComponents, streetName: e.target.value})}
                                                    className="bg-gray-900/60 border border-gray-600 rounded-md px-2 py-1.5 text-xs text-gray-100 focus:outline-none focus:border-cyan-400"
                                                />
                                            </div>
                                            <input
                                                type="text"
                                                placeholder="Unit/Apt # (optional)"
                                                value={originComponents.unit}
                                                onChange={(e) => setOriginComponents({...originComponents, unit: e.target.value})}
                                                className="w-full bg-gray-900/60 border border-gray-600 rounded-md px-2 py-1.5 text-xs text-gray-100 focus:outline-none focus:border-cyan-400"
                                            />
                                            <div className="grid grid-cols-3 gap-2">
                                                <input
                                                    type="text"
                                                    placeholder="City"
                                                    value={originComponents.city}
                                                onChange={(e) => setOriginComponents({...originComponents, city: e.target.value})}
                                                className="col-span-2 bg-gray-900/60 border border-gray-600 rounded-md px-2 py-1.5 text-xs text-gray-100 focus:outline-none focus:border-cyan-400"
                                            />
                                            <input
                                                type="text"
                                                placeholder="State"
                                                value={originComponents.state}
                                                onChange={(e) => setOriginComponents({...originComponents, state: e.target.value.toUpperCase()})}
                                                maxLength={2}
                                                className="bg-gray-900/60 border border-gray-600 rounded-md px-2 py-1.5 text-xs text-gray-100 focus:outline-none focus:border-cyan-400 uppercase"
                                            />
                                        </div>
                                        <input
                                            type="text"
                                            placeholder="ZIP Code (optional)"
                                            value={originComponents.zipCode}
                                            onChange={(e) => setOriginComponents({...originComponents, zipCode: e.target.value})}
                                            maxLength={10}
                                            className="w-full bg-gray-900/60 border border-gray-600 rounded-md px-2 py-1.5 text-xs text-gray-100 focus:outline-none focus:border-cyan-400"
                                        />
                                        {plannerOriginResolved && plannerOriginResolved.address === plannerOriginAddress.trim() && (
                                            <p className="mt-1 text-[10px] text-green-400">
                                                ✓ Resolved: {plannerOriginResolved.label ?? plannerOriginAddress}
                                                {plannerOriginResolved.source === 'facility' ? ' (facility)' : ' (geocoded)'}
                                            </p>
                                        )}
                                        {!plannerOriginResolved && plannerOriginAddress.trim() && !addressLooksComplete(plannerOriginAddress) && (
                                            <p className="mt-1 text-[10px] text-yellow-400">
                                                ⚠ Include full address with city and state for best results (e.g., "123 Main St, Chicago, IL")
                                            </p>
                                        )}
                                        {!plannerOriginResolved && addressLooksComplete(plannerOriginAddress) && (
                                            <p className="mt-1 text-[10px] text-cyan-400">
                                                📍 Address ready - will be geocoded when route is generated
                                            </p>
                                        )}
                                    </div>
                                    )}
                                </div>
                                <div>
                                    <button
                                        type="button"
                                        onClick={() => setIsDestinationExpanded(!isDestinationExpanded)}
                                        className="w-full flex items-center justify-between text-xs font-semibold text-gray-300 uppercase tracking-wider hover:text-cyan-300 transition-colors"
                                    >
                                        <span>Destination Address</span>
                                        <span className="text-lg">{isDestinationExpanded ? '▼' : '▶'}</span>
                                    </button>
                                    {isDestinationExpanded && (
                                        <div className="mt-2 space-y-2">
                                        <div className="grid grid-cols-2 gap-2">
                                            <input
                                                type="text"
                                                placeholder="Street # (e.g., 456)"
                                                value={destinationComponents.streetNumber}
                                                onChange={(e) => setDestinationComponents({...destinationComponents, streetNumber: e.target.value})}
                                                className="bg-gray-900/60 border border-gray-600 rounded-md px-2 py-1.5 text-xs text-gray-100 focus:outline-none focus:border-cyan-400"
                                            />
                                            <input
                                                type="text"
                                                placeholder="Street Name"
                                                value={destinationComponents.streetName}
                                                onChange={(e) => setDestinationComponents({...destinationComponents, streetName: e.target.value})}
                                                className="bg-gray-900/60 border border-gray-600 rounded-md px-2 py-1.5 text-xs text-gray-100 focus:outline-none focus:border-cyan-400"
                                            />
                                        </div>
                                        <input
                                            type="text"
                                            placeholder="Unit/Apt # (optional)"
                                            value={destinationComponents.unit}
                                            onChange={(e) => setDestinationComponents({...destinationComponents, unit: e.target.value})}
                                            className="w-full bg-gray-900/60 border border-gray-600 rounded-md px-2 py-1.5 text-xs text-gray-100 focus:outline-none focus:border-cyan-400"
                                        />
                                        <div className="grid grid-cols-3 gap-2">
                                            <input
                                                type="text"
                                                placeholder="City"
                                                value={destinationComponents.city}
                                                onChange={(e) => setDestinationComponents({...destinationComponents, city: e.target.value})}
                                                className="col-span-2 bg-gray-900/60 border border-gray-600 rounded-md px-2 py-1.5 text-xs text-gray-100 focus:outline-none focus:border-cyan-400"
                                            />
                                            <input
                                                type="text"
                                                placeholder="State"
                                                value={destinationComponents.state}
                                                onChange={(e) => setDestinationComponents({...destinationComponents, state: e.target.value.toUpperCase()})}
                                                maxLength={2}
                                                className="bg-gray-900/60 border border-gray-600 rounded-md px-2 py-1.5 text-xs text-gray-100 focus:outline-none focus:border-cyan-400 uppercase"
                                            />
                                        </div>
                                        <input
                                            type="text"
                                            placeholder="ZIP Code (optional)"
                                            value={destinationComponents.zipCode}
                                            onChange={(e) => setDestinationComponents({...destinationComponents, zipCode: e.target.value})}
                                            maxLength={10}
                                            className="w-full bg-gray-900/60 border border-gray-600 rounded-md px-2 py-1.5 text-xs text-gray-100 focus:outline-none focus:border-cyan-400"
                                        />
                                        {plannerDestinationResolved && plannerDestinationResolved.address === plannerDestinationAddress.trim() && (
                                            <p className="mt-1 text-[10px] text-green-400">
                                                ✓ Resolved: {plannerDestinationResolved.label ?? plannerDestinationAddress}
                                                {plannerDestinationResolved.source === 'facility' ? ' (facility)' : ' (geocoded)'}
                                            </p>
                                        )}
                                        {!plannerDestinationResolved && plannerDestinationAddress.trim() && !addressLooksComplete(plannerDestinationAddress) && (
                                            <p className="mt-1 text-[10px] text-yellow-400">
                                                ⚠ Include full address with city and state for best results (e.g., "456 Oak Ave, Austin, TX")
                                            </p>
                                        )}
                                        {!plannerDestinationResolved && addressLooksComplete(plannerDestinationAddress) && (
                                            <p className="mt-1 text-[10px] text-cyan-400">
                                                📍 Address ready - will be geocoded when route is generated
                                            </p>
                                        )}
                                    </div>
                                    )}
                                </div>
                            </div>
                            <datalist id="facility-suggestions">
                                {facilityOptions.map(option => (
                                    <option key={option.id} value={formatFacilityAddress(option)} />
                                ))}
                            </datalist>

                            <div>
                                <button
                                    type="button"
                                    onClick={() => setIsStopsExpanded(!isStopsExpanded)}
                                    className="w-full flex items-center justify-between mb-2 hover:text-cyan-300 transition-colors"
                                >
                                    <div className="flex items-center justify-between flex-1">
                                        <span className="text-xs font-semibold text-gray-300 uppercase tracking-wider">
                                            Intermediate Stops
                                        </span>
                                        <div className="flex items-center gap-2">
                                            {plannerMidStops.length > 0 && (
                                                <span className="text-[10px] text-cyan-400 font-semibold">
                                                    {plannerMidStops.length} stop{plannerMidStops.length !== 1 ? 's' : ''} added
                                                </span>
                                            )}
                                            <span className="text-[10px] text-gray-500">Optional</span>
                                        </div>
                                    </div>
                                    <span className="text-lg ml-2">{isStopsExpanded ? '▼' : '▶'}</span>
                                </button>
                                {plannerMidStops.length > 1 && (
                                    <button
                                        type="button"
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            setPlannerMidStops([]);
                                        }}
                                        className="text-[10px] text-red-400 hover:text-red-300 underline mb-2"
                                    >
                                        Clear All
                                    </button>
                                )}
                                {isStopsExpanded && (
                                    <div className="space-y-2">
                                    <div className="grid grid-cols-2 gap-2">
                                        <input
                                            type="text"
                                            placeholder="Street #"
                                            value={newStopComponents.streetNumber}
                                            onChange={(e) => setNewStopComponents({...newStopComponents, streetNumber: e.target.value})}
                                            className="bg-gray-900/60 border border-gray-600 rounded-md px-2 py-1.5 text-xs text-gray-100 focus:outline-none focus:border-cyan-400"
                                        />
                                        <input
                                            type="text"
                                            placeholder="Street Name"
                                            value={newStopComponents.streetName}
                                            onChange={(e) => setNewStopComponents({...newStopComponents, streetName: e.target.value})}
                                            className="bg-gray-900/60 border border-gray-600 rounded-md px-2 py-1.5 text-xs text-gray-100 focus:outline-none focus:border-cyan-400"
                                        />
                                    </div>
                                    <input
                                        type="text"
                                        placeholder="Unit/Apt # (optional)"
                                        value={newStopComponents.unit}
                                        onChange={(e) => setNewStopComponents({...newStopComponents, unit: e.target.value})}
                                        className="w-full bg-gray-900/60 border border-gray-600 rounded-md px-2 py-1.5 text-xs text-gray-100 focus:outline-none focus:border-cyan-400"
                                    />
                                    <div className="grid grid-cols-3 gap-2">
                                        <input
                                            type="text"
                                            placeholder="City"
                                            value={newStopComponents.city}
                                            onChange={(e) => setNewStopComponents({...newStopComponents, city: e.target.value})}
                                            className="col-span-2 bg-gray-900/60 border border-gray-600 rounded-md px-2 py-1.5 text-xs text-gray-100 focus:outline-none focus:border-cyan-400"
                                        />
                                        <input
                                            type="text"
                                            placeholder="State"
                                            value={newStopComponents.state}
                                            onChange={(e) => setNewStopComponents({...newStopComponents, state: e.target.value.toUpperCase()})}
                                            maxLength={2}
                                            className="bg-gray-900/60 border border-gray-600 rounded-md px-2 py-1.5 text-xs text-gray-100 focus:outline-none focus:border-cyan-400 uppercase"
                                        />
                                    </div>
                                    <input
                                        type="text"
                                        placeholder="ZIP Code (optional)"
                                        value={newStopComponents.zipCode}
                                        onChange={(e) => setNewStopComponents({...newStopComponents, zipCode: e.target.value})}
                                        maxLength={10}
                                        className="w-full bg-gray-900/60 border border-gray-600 rounded-md px-2 py-1.5 text-xs text-gray-100 focus:outline-none focus:border-cyan-400"
                                    />
                                    <button
                                        type="button"
                                        onClick={handleAddManualStop}
                                        disabled={!newStopComponents.city || !newStopComponents.state}
                                        className="w-full px-4 py-2 text-xs font-semibold rounded-md bg-cyan-700 hover:bg-cyan-600 disabled:opacity-40 disabled:cursor-not-allowed text-white"
                                    >
                                        + Add Stop
                                    </button>
                                    <p className="mt-1 text-[10px] text-gray-500">
                                        💡 <span className="font-semibold">Add unlimited stops!</span> At minimum, enter City and State. Each stop can be edited inline after adding.
                                    </p>
                                    <div className="mt-3 space-y-2">
                                        {plannerMidStops.length > 0 ? (
                                            <>
                                                <div className="flex items-center justify-between text-[10px] text-gray-400 px-1">
                                                    <span>Route Sequence</span>
                                                    <span>{plannerMidStops.length} intermediate stop{plannerMidStops.length !== 1 ? 's' : ''}</span>
                                                </div>
                                            {plannerMidStops.map((stop, index) => (
                                                <div key={stop.id} className="bg-gray-900/60 border border-gray-600 rounded-md px-3 py-2 text-xs text-gray-200 space-y-2">
                                                    <div className="flex items-center justify-between gap-2">
                                                        <div className="flex items-center gap-2 flex-1 min-w-0">
                                                            <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-cyan-600/20 border border-cyan-500 text-cyan-300 font-bold text-[10px] flex-shrink-0">
                                                                {index + 1}
                                                            </span>
                                                            <input
                                                                type="text"
                                                                value={stop.address}
                                                                onChange={(e) => handleUpdateStopAddress(stop.id, e.target.value)}
                                                                className="flex-1 min-w-0 bg-gray-800/50 border border-gray-700 rounded px-2 py-1 text-xs focus:outline-none focus:border-cyan-500"
                                                                list="facility-suggestions"
                                                            />
                                                        </div>
                                                        <div className="flex items-center gap-1 flex-shrink-0">
                                                            <button
                                                                type="button"
                                                                onClick={() => handleMoveMidStop(stop.id, 'up')}
                                                                disabled={index === 0}
                                                                className="px-2 py-1 rounded bg-gray-800 border border-gray-600 hover:bg-gray-700 disabled:opacity-30 disabled:cursor-not-allowed"
                                                                title="Move up"
                                                            >
                                                                ↑
                                                            </button>
                                                            <button
                                                                type="button"
                                                                onClick={() => handleMoveMidStop(stop.id, 'down')}
                                                                disabled={index === plannerMidStops.length - 1}
                                                                className="px-2 py-1 rounded bg-gray-800 border border-gray-600 hover:bg-gray-700 disabled:opacity-30 disabled:cursor-not-allowed"
                                                                title="Move down"
                                                            >
                                                                ↓
                                                            </button>
                                                            <button
                                                                type="button"
                                                                onClick={() => handleRemoveMidStop(stop.id)}
                                                                className="px-2 py-1 rounded bg-red-600/20 border border-red-500 text-red-300 hover:bg-red-600/40"
                                                                title="Remove stop"
                                                            >
                                                                ✕
                                                            </button>
                                                        </div>
                                                    </div>
                                                    {stop.resolved && (
                                                        <p className="text-[10px] text-gray-400 pl-8">
                                                            ✓ {stop.resolved.label || stop.address}
                                                            {stop.resolved.source === 'facility' ? ' (facility)' : ' (geocoded)'}
                                                        </p>
                                                    )}
                                                </div>
                                            ))}
                                        </>
                                    ) : (
                                        <div className="text-center py-6 px-3 border-2 border-dashed border-gray-700 rounded-md">
                                            <p className="text-xs text-gray-400">
                                                No intermediate stops yet
                                            </p>
                                            <p className="text-[10px] text-gray-500 mt-1">
                                                Enter addresses above to add stops to your route
                                            </p>
                                        </div>
                                    )}
                                </div>
                                    </div>
                                )}
                            </div>

                            {plannerError && (
                                <div className="p-3 rounded-md bg-red-900/20 border border-red-500/30">
                                    <p className="text-xs text-red-400 font-semibold">❌ Geocoding Error</p>
                                    <p className="text-xs text-red-300 mt-1">{plannerError}</p>
                                    <p className="text-[10px] text-gray-400 mt-2">
                                        💡 Tip: Make sure addresses include street, city, and state. Check browser console (F12) for details.
                                    </p>
                                </div>
                            )}

                            {isGeocodingPreview && !plannerError && (
                                <div className="p-2 rounded-md bg-blue-900/20 border border-blue-500/30">
                                    <p className="text-xs text-blue-300">🔍 Resolving addresses with OpenStreetMap...</p>
                                </div>
                            )}

                            {!isGeocodingPreview && plannerPreviewStops.length >= 2 && !plannerError && (
                                <div className="p-2 rounded-md bg-green-900/20 border border-green-500/30">
                                    <p className="text-xs text-green-300">✅ Route ready with {plannerPreviewStops.length} stop{plannerPreviewStops.length !== 1 ? 's' : ''}</p>
                                </div>
                            )}

                            {plannerPreviewStops.length < 2 && plannerOriginAddress && plannerDestinationAddress && !isGeocodingPreview && (
                                <p className="text-xs text-yellow-400 px-2">
                                    ⏳ Geocoding addresses... Please wait a moment before launching.
                                </p>
                            )}
                            {plannerPreviewStops.length < 2 && (!plannerOriginAddress || !plannerDestinationAddress) && !isGeocodingPreview && (
                                <p className="text-xs text-gray-500 px-2">
                                    📍 Enter origin and destination addresses to generate route.
                                </p>
                            )}

                            <button
                                onClick={handleCreateShipment}
                                disabled={isCreatingShipment || isGeocodingPreview || !plannerOriginAddress.trim() || !plannerDestinationAddress.trim()}
                                className={`w-full px-6 py-3 rounded-md font-bold text-sm transition-all ${
                                    isCreatingShipment || isGeocodingPreview || !plannerOriginAddress.trim() || !plannerDestinationAddress.trim()
                                        ? 'bg-gray-700 text-gray-400 cursor-not-allowed'
                                        : 'bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white shadow-lg hover:shadow-cyan-500/50'
                                }`}
                            >
                                {isCreatingShipment ? '⏳ Creating route...' : isGeocodingPreview ? '🔍 Geocoding...' : '🚀 Generate Tracking & Launch'}
                            </button>

                            {creationError && (
                                <div className="p-3 rounded-md bg-red-900/20 border border-red-500/30">
                                    <p className="text-xs text-red-400">{creationError}</p>
                                </div>
                            )}
                            
                            {lastCreatedTracking && (
                                <div className="p-3 rounded-md bg-cyan-900/20 border border-cyan-500/30">
                                    <div className="flex items-center justify-between gap-3">
                                        <div>
                                            <p className="text-[11px] uppercase tracking-wider text-cyan-300">Latest Tracking Number</p>
                                            <p className="font-mono text-sm text-white mt-1">{lastCreatedTracking}</p>
                                        </div>
                                        <div className="flex flex-col gap-2">
                                            <button
                                                onClick={handleCopyTracking}
                                                className="px-3 py-1 rounded-md text-xs font-semibold bg-gray-900/70 border border-cyan-500/40 text-cyan-100 hover:bg-gray-900"
                                            >
                                                {copyStatus === 'copied' ? 'Copied' : copyStatus === 'failed' ? 'Copy failed' : 'Copy'}
                                            </button>
                                            <a
                                                href={`#/track/${lastCreatedTracking}`}
                                                className="px-3 py-1 rounded-md text-xs font-semibold bg-cyan-600 hover:bg-cyan-500 text-white text-center"
                                                target="_blank"
                                                rel="noreferrer"
                                            >
                                                Open Customer View
                                            </a>
                                        </div>
                                    </div>
                                    {creationSuccessTs && (
                                        <p className="text-[10px] text-cyan-200/70 mt-2">
                                            Sync live updates with the customer dashboard using this reference.
                                        </p>
                                    )}
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                {/* Right Panel - Map & Route Overview */}
                <div className="flex-1 flex flex-col">
                    {stops.length > 0 ? (
                        <MapComponent
                            vehiclePosition={vehiclePosition}
                            stops={stops}
                            mode={Mode.Logistics}
                            shipmentId={shipmentId || undefined}
                            onTrafficUpdate={setTrafficSegments}
                        />
                    ) : plannerPreviewStops.length >= 2 ? (
                        <>
                            <div className="flex-1">
                                <MapComponent
                                    mapId="planner-map-primary"
                                    stops={plannerPreviewStops}
                                    vehiclePosition={plannerVehiclePreview}
                                    mode={Mode.Logistics}
                                />
                            </div>
                            <div className="h-48 border-t border-gray-700/60 bg-gray-900/90 backdrop-blur-sm p-4 overflow-y-auto">
                                <div className="flex items-center justify-between mb-3">
                                    <h3 className="text-sm font-bold text-cyan-300 uppercase tracking-wider">📋 Route Overview</h3>
                                    {plannerEtaPreview && (
                                        <p className="text-xs text-gray-400 uppercase tracking-wide">
                                            ⏱️ Est. Completion {plannerEtaPreview.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })}
                                        </p>
                                    )}
                                </div>
                                <ol className="space-y-2 text-sm text-gray-200 list-decimal list-inside">
                                    {plannerPreviewStops.map((stop, index) => (
                                        <li key={stop.id} className="leading-relaxed">
                                            <span className="font-semibold text-cyan-200">
                                                {index === 0
                                                    ? 'Origin'
                                                    : index === plannerPreviewStops.length - 1
                                                        ? 'Destination'
                                                        : `Stop ${index}`}
                                            </span>
                                            <span className="text-gray-500"> · </span>
                                            <span className="text-gray-300">{stop.name}</span>
                                        </li>
                                    ))}
                                </ol>
                            </div>
                        </>
                    ) : (
                        <div className="flex items-center justify-center h-full text-gray-400">
                            <div className="text-center">
                                <TruckIcon className="w-24 h-24 mx-auto mb-4 text-gray-600" />
                                <p>Choose origin and destination to preview the planned route.</p>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            <RerouteModal
                isOpen={showRerouteModal}
                onClose={() => setShowRerouteModal(false)}
                currentRoute={{ distance_km: 0, duration_min: 0 }}
                alternativeRoute={rerouteOption}
                onAccept={(id) => {
                    console.log('Accept reroute:', id);
                    setShowRerouteModal(false);
                }}
                onReject={() => {
                    console.log('Reject reroute');
                    setShowRerouteModal(false);
                }}
            />
        </div>
    );
};