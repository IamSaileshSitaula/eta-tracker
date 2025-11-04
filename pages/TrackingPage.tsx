import React, { useState, useEffect, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { io, Socket } from 'socket.io-client';
import { MapComponent } from '../components/Map';
import { CheckCircleIcon, TruckIcon } from '../components/icons';
import { Mode, Stop, TrafficSegment } from '../types';

const API_URL = 'http://localhost:5000';

interface RouteDetails {
    id: number;
    tracking_number: string;
    stops: Stop[];
}

const StopList: React.FC<{ stops: Stop[] }> = ({ stops }) => {
    const formatEta = (etaTimestamp: string | null) => {
        if (!etaTimestamp) return 'N/A';
        
        const date = new Date(etaTimestamp);
        return date.toLocaleTimeString('en-US', { 
            hour: 'numeric', 
            minute: '2-digit',
            hour12: true 
        });
    };

    return (
        <div className="space-y-4">
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

export const TrackingPage: React.FC = () => {
    const { trackingNumber: urlTrackingNumber } = useParams<{ trackingNumber: string }>();
    const navigate = useNavigate();
    
    const [socket, setSocket] = useState<Socket | null>(null);
    const [trackingInput, setTrackingInput] = useState(urlTrackingNumber || '');
    const [activeRoute, setActiveRoute] = useState<RouteDetails | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [vehiclePosition, setVehiclePosition] = useState<{ lat: number; lon: number } | null>(null);
    const [stops, setStops] = useState<Stop[]>([]);
    const [shipmentId, setShipmentId] = useState<number | null>(null);
    const [remainingInfo, setRemainingInfo] = useState<{ remainingPercent: number | null; remainingKm: number | null } | null>(null);
    const [trafficSegments, setTrafficSegments] = useState<TrafficSegment[]>([]);

    const toRad = (deg: number) => (deg * Math.PI) / 180;
    const haversineDistanceKm = (a: { lat: number; lon: number }, b: { lat: number; lon: number }) => {
        const dLat = toRad(b.lat - a.lat);
        const dLon = toRad(b.lon - a.lon);
        const originLat = toRad(a.lat);
        const destLat = toRad(b.lat);
        const hav = Math.sin(dLat / 2) ** 2 + Math.cos(originLat) * Math.cos(destLat) * Math.sin(dLon / 2) ** 2;
        return 6371 * 2 * Math.atan2(Math.sqrt(hav), Math.sqrt(1 - hav));
    };

    const findNearestStopName = (segment: TrafficSegment): string | null => {
        if (!stops.length) {
            return null;
        }

        const midpoint = {
            lat: (segment.start.lat + segment.end.lat) / 2,
            lon: (segment.start.lon + segment.end.lon) / 2,
        };

        let closestName: string | null = null;
        let closestDistance = Infinity;

        stops.forEach((stop) => {
            const distance = haversineDistanceKm(midpoint, { lat: stop.lat, lon: stop.lon });
            if (distance < closestDistance) {
                closestDistance = distance;
                closestName = stop.name;
            }
        });

        return closestName;
    };

    const orderedTrafficSegments = useMemo(() => {
        if (!trafficSegments.length) {
            return [];
        }

        const severityRank: Record<string, number> = {
            severe: 0,
            heavy: 1,
            high: 1,
            moderate: 2,
            medium: 2,
            light: 3,
        };

        return [...trafficSegments].sort((a, b) => {
            const rankA = severityRank[a.traffic_level?.toLowerCase?.() ?? ''] ?? 4;
            const rankB = severityRank[b.traffic_level?.toLowerCase?.() ?? ''] ?? 4;
            return rankA - rankB;
        });
    }, [trafficSegments]);

    const findRoute = async (trackingNumber: string) => {
        if (!trackingNumber) return;
        setIsLoading(true);
        setError(null);
        setActiveRoute(null);
        
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
                        setStops(status.stops || []);
                        setVehiclePosition(status.vehicle_position);
                        
                        if (urlTrackingNumber !== trackingNumber) {
                            navigate(`/track/${trackingNumber}`);
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
    
    useEffect(() => {
        if (urlTrackingNumber) {
            findRoute(urlTrackingNumber);
        }
    }, [urlTrackingNumber]);

    // Real-time updates via Socket.IO
    useEffect(() => {
        if (!activeRoute || !shipmentId) {
            if (socket) socket.disconnect();
            return;
        }

        const newSocket = io(API_URL);
        setSocket(newSocket);

        newSocket.on('connect', () => {
            newSocket.emit('subscribe', { shipment_id: shipmentId });
        });

        newSocket.on('position_update', (data: any) => {
            if (data.shipment_id === shipmentId && data.vehicle_position) {
                setVehiclePosition(data.vehicle_position);

                if (data.per_stop_etas) {
                    const updatedStops = data.per_stop_etas;
                    setStops(updatedStops);
                    
                    fetch(`${API_URL}/v1/shipments/${shipmentId}/status`)
                        .then(res => res.json())
                        .then(status => {
                            if (status.remaining_percent != null) {
                                setRemainingInfo({ remainingPercent: status.remaining_percent, remainingKm: status.remaining_km });
                            }
                            if (status.traffic_segments) {
                                setTrafficSegments(status.traffic_segments);
                            }
                        })
                        .catch(err => console.error('Error fetching updated status:', err));
                }
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
                // Silently fail - socket.io is primary update mechanism
            }
        }, 60000);
        
        return () => clearInterval(refreshInterval);
    }, [shipmentId]);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (trackingInput.trim()) {
            findRoute(trackingInput.trim());
        }
    };

    if (!urlTrackingNumber) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-gray-900 via-slate-800 to-gray-900 flex items-center justify-center p-6">
                <div className="max-w-2xl w-full">
                    <h1 className="text-5xl font-bold text-center mb-4 bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
                        Track Your Delivery
                    </h1>
                    <p className="text-gray-400 text-center mb-8">
                        Enter your tracking number below to see live updates.
                    </p>
                    <form onSubmit={handleSubmit} className="flex gap-3">
                        <input
                            type="text"
                            value={trackingInput}
                            onChange={(e) => setTrackingInput(e.target.value)}
                            placeholder="Enter tracking number (e.g., PO-98765)"
                            className="flex-1 px-6 py-4 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20"
                        />
                        <button
                            type="submit"
                            disabled={isLoading}
                            className="px-8 py-4 bg-cyan-500 hover:bg-cyan-600 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg font-semibold text-white transition-colors"
                        >
                            {isLoading ? 'Tracking...' : 'Track'}
                        </button>
                    </form>
                    {error && (
                        <p className="mt-4 text-center text-red-400">{error}</p>
                    )}
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-slate-800 to-gray-900 text-white">
            <div className="h-screen flex">
                {/* Left Panel - Tracking Details */}
                <div className="w-96 bg-gray-800/50 backdrop-blur-sm border-r border-gray-700 flex flex-col">
                    <div className="p-6 border-b border-gray-700">
                        <h2 className="text-2xl font-bold mb-2">Tracking Details</h2>
                        <p className="text-cyan-400 font-mono">{activeRoute?.tracking_number}</p>
                        {remainingInfo && remainingInfo.remainingKm !== null && (
                            <div className="mt-4 p-4 rounded-lg bg-blue-900/20 border border-blue-500/30">
                                <p className="text-sm uppercase tracking-wide text-blue-200/80 font-semibold">Remaining Route</p>
                                <p className="text-2xl font-bold text-white mt-1">
                                    {remainingInfo.remainingPercent !== null ? `${remainingInfo.remainingPercent}%` : '—'}
                                </p>
                                <p className="text-sm text-blue-200/70">
                                    {remainingInfo.remainingKm !== null ? `${remainingInfo.remainingKm.toFixed(1)} km left` : 'Calculating…'}
                                </p>
                            </div>
                        )}
                        {orderedTrafficSegments.length > 0 && (
                            <div className="mt-4">
                                <p className="text-sm uppercase tracking-wide text-orange-200/80 font-semibold">Route Traffic Alerts</p>
                                <div className="mt-3 space-y-3">
                                    {orderedTrafficSegments.map((segment, index) => {
                                        const severity = segment.traffic_level?.toLowerCase?.() ?? 'traffic';
                                        const severityLabel = severity.replace(/\b\w/g, (char) => char.toUpperCase());
                                        const nearestStopName = findNearestStopName(segment);
                                        const speedFactorPercent = segment.speed_factor != null ? Math.round(segment.speed_factor * 100) : null;
                                        const currentSpeedDisplay = segment.current_speed_kph != null ? `${Math.round(segment.current_speed_kph)} km/h` : '—';
                                        const normalSpeedDisplay = segment.freeflow_speed_kph != null ? `${Math.round(segment.freeflow_speed_kph)} km/h` : null;

                                        const styleBySeverity: Record<string, string> = {
                                            severe: 'border-red-500/50 bg-red-500/10',
                                            heavy: 'border-orange-500/50 bg-orange-500/10',
                                            high: 'border-orange-500/50 bg-orange-500/10',
                                            moderate: 'border-yellow-500/40 bg-yellow-500/10',
                                            medium: 'border-yellow-500/40 bg-yellow-500/10',
                                            light: 'border-emerald-500/30 bg-emerald-500/10',
                                        };

                                        const containerStyle = styleBySeverity[severity] ?? 'border-blue-500/30 bg-blue-500/10';

                                        return (
                                            <div
                                                key={`${segment.start.lat}-${segment.start.lon}-${segment.end.lat}-${segment.end.lon}-${index}`}
                                                className={`p-3 rounded-lg border flex gap-3 items-start ${containerStyle}`}
                                            >
                                                <span
                                                    className="mt-1 h-3 w-3 rounded-full flex-shrink-0"
                                                    style={{ backgroundColor: segment.color || '#f97316' }}
                                                    aria-hidden="true"
                                                ></span>
                                                <div className="text-sm leading-relaxed">
                                                    <p className="font-semibold text-white">{severityLabel} Traffic</p>
                                                    <p className="text-gray-200/80">
                                                        {nearestStopName ? `Near ${nearestStopName}` : 'On current route'} · {currentSpeedDisplay}
                                                        {normalSpeedDisplay ? ` vs ${normalSpeedDisplay} normal` : ''}
                                                    </p>
                                                    <p className="text-gray-300/70 text-xs mt-1">
                                                        Flow at {speedFactorPercent !== null ? `${speedFactorPercent}%` : '—'} of normal
                                                    </p>
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            </div>
                        )}
                    </div>
                    
                    <div className="flex-1 overflow-y-auto p-6">
                        {isLoading ? (
                            <div className="flex items-center justify-center h-full">
                                <div className="text-gray-400">Loading...</div>
                            </div>
                        ) : error ? (
                            <div className="text-red-400 text-center">{error}</div>
                        ) : stops.length > 0 ? (
                            <StopList stops={stops} />
                        ) : (
                            <div className="text-gray-400 text-center">No stops found</div>
                        )}
                    </div>
                </div>

                {/* Right Panel - Map */}
                <div className="flex-1 relative">
                    {activeRoute && stops.length > 0 && (
                        <MapComponent
                            stops={stops}
                            vehiclePosition={vehiclePosition}
                            mode={Mode.Logistics}
                            shipmentId={shipmentId || undefined}
                            onRemainingChange={setRemainingInfo}
                            onTrafficUpdate={setTrafficSegments}
                        />
                    )}
                </div>
            </div>
        </div>
    );
};
