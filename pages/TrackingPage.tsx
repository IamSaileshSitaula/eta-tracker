import React, { useState, useEffect, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { io, Socket } from 'socket.io-client';
import { MapComponent } from '../components/Map';
import { CheckCircleIcon, TruckIcon } from '../components/icons';
import { Mode, Stop, TrafficSegment } from '../types';
import { RerouteModal } from '../components/RerouteModalNew';

const API_URL = 'http://localhost:5000';

interface RouteDetails {
    id: number;
    tracking_number: string;
    stops: Stop[];
}

interface ShipmentStatus {
    status: string;
    on_time: boolean;
    confidence: number;
    eta_next_stop_ts: string;
    late_by_min: number;
    current_leg: string;
}

const StopList: React.FC<{ stops: Stop[]; currentStopSeq: number | null }> = ({ stops, currentStopSeq }) => {
    const formatEta = (etaTimestamp: string | null) => {
        if (!etaTimestamp) return 'N/A';
        
        const date = new Date(etaTimestamp);
        const now = new Date();
        const diffMs = date.getTime() - now.getTime();
        const diffMins = Math.floor(diffMs / 60000);
        
        if (diffMins < 60) {
            return `${diffMins} min`;
        } else if (diffMins < 1440) {
            const hours = Math.floor(diffMins / 60);
            const mins = diffMins % 60;
            return `${hours}h ${mins}m`;
        }
        
        return date.toLocaleString('en-US', { 
            month: 'short',
            day: 'numeric',
            hour: 'numeric', 
            minute: '2-digit',
            hour12: true 
        });
    };

    return (
        <div className="space-y-3">
            {stops.map((stop, index) => {
                const isOrigin = stop.is_origin === true;
                const isCompleted = stop.arrival_time || stop.completed;
                const isCurrent = currentStopSeq !== null && stop.seq === currentStopSeq;
                
                return (
                    <div 
                        key={stop.id || index} 
                        className={`relative flex items-start p-3 rounded-xl transition-all duration-300 ${
                            isCurrent 
                                ? 'bg-gradient-to-r from-cyan-500/10 to-blue-500/10 border border-cyan-500/30 shadow-lg shadow-cyan-500/10' 
                                : isCompleted
                                ? 'bg-green-500/5 border border-green-500/20'
                                : 'bg-gray-800/30 border border-gray-700/30 hover:bg-gray-800/50'
                        }`}
                    >
                        <div className="flex flex-col items-center mr-4 z-10">
                            {isCompleted ? (
                                <div className="relative">
                                    <CheckCircleIcon className="w-10 h-10 text-green-500 drop-shadow-[0_0_8px_rgba(34,197,94,0.5)]" />
                                    <div className="absolute inset-0 animate-ping">
                                        <CheckCircleIcon className="w-10 h-10 text-green-500 opacity-20" />
                                    </div>
                                </div>
                            ) : isOrigin ? (
                                <div className="relative w-10 h-10 rounded-full bg-gradient-to-br from-green-500 to-emerald-600 border-2 border-green-400 flex items-center justify-center shadow-lg shadow-green-500/30">
                                    <TruckIcon className="w-6 h-6 text-white drop-shadow-md" />
                                    {isCurrent && (
                                        <div className="absolute inset-0 rounded-full border-2 border-green-400 animate-ping"></div>
                                    )}
                                </div>
                            ) : (
                                <div className={`relative w-10 h-10 rounded-full flex items-center justify-center font-bold text-lg shadow-lg transition-all ${
                                    isCurrent 
                                        ? 'bg-gradient-to-br from-cyan-500 to-blue-600 text-white border-2 border-cyan-400 shadow-cyan-500/50' 
                                        : 'bg-gray-700 border-2 border-gray-600 text-gray-300'
                                }`}>
                                    {stop.seq}
                                    {isCurrent && (
                                        <div className="absolute inset-0 rounded-full border-2 border-cyan-400 animate-ping"></div>
                                    )}
                                </div>
                            )}
                            {index < stops.length - 1 && (
                                <div className={`w-1 h-14 mt-1 rounded-full ${
                                    isCompleted ? 'bg-gradient-to-b from-green-500/50 to-gray-600' : 'bg-gray-600'
                                }`}></div>
                            )}
                        </div>
                        <div className="pt-1 flex-1 min-w-0">
                            <div className="flex items-start justify-between gap-2">
                                <p className={`font-semibold text-base leading-tight ${
                                    isCompleted ? 'text-green-400' : isCurrent ? 'text-white' : 'text-gray-200'
                                }`}>
                                    {stop.name}
                                </p>
                                {isCurrent && (
                                    <span className="px-2 py-0.5 text-xs font-bold bg-cyan-500/20 text-cyan-300 rounded-full border border-cyan-500/30 whitespace-nowrap animate-pulse">
                                        EN ROUTE
                                    </span>
                                )}
                            </div>
                            {isCompleted ? (
                                <div className="flex items-center gap-2 mt-1">
                                    <span className="text-sm text-green-300 font-medium">✓ Completed</span>
                                    <span className="text-xs text-gray-400">
                                        {new Date(stop.arrival_time!).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true })}
                                    </span>
                                </div>
                            ) : isOrigin ? (
                                <p className="text-sm text-green-300 font-medium mt-1">🚀 Origin (Departed)</p>
                            ) : (
                                <div className="mt-1 space-y-1">
                                    <div className="flex items-center gap-2">
                                        <span className="text-xs text-gray-400 uppercase tracking-wide">ETA:</span>
                                        <span className="text-sm font-semibold text-cyan-300">
                                            {formatEta(stop.eta_timestamp || null)}
                                        </span>
                                    </div>
                                    {stop.service_time_min && (
                                        <p className="text-xs text-gray-500">
                                            Service time: {stop.service_time_min} min
                                        </p>
                                    )}
                                </div>
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
    const [shipmentStatus, setShipmentStatus] = useState<ShipmentStatus | null>(null);
    const [currentStopSeq, setCurrentStopSeq] = useState<number | null>(null);
    const [showRerouteModal, setShowRerouteModal] = useState(false);
    const [rerouteReason, setRerouteReason] = useState<string>('');
    const [oldRoute, setOldRoute] = useState<any>(null);
    const [newRoute, setNewRoute] = useState<any>(null);


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
                        setShipmentStatus({
                            status: status.status,
                            on_time: status.on_time,
                            confidence: status.confidence,
                            eta_next_stop_ts: status.eta_next_stop_ts,
                            late_by_min: status.late_by_min || 0,
                            current_leg: status.current_leg || ''
                        });
                        setCurrentStopSeq(status.next_stop?.seq ?? null);
                        
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
                            setShipmentStatus({
                                status: status.status,
                                on_time: status.on_time,
                                confidence: status.confidence,
                                eta_next_stop_ts: status.eta_next_stop_ts,
                                late_by_min: status.late_by_min || 0,
                                current_leg: status.current_leg || ''
                            });
                            setCurrentStopSeq(status.next_stop?.seq ?? null);
                        })
                        .catch(err => console.error('Error fetching updated status:', err));
                }
            }
        });

        newSocket.on('reroute_event', (data: any) => {
            if (data.shipment_id === shipmentId) {
                setRerouteReason(data.reason || 'Route optimized for better ETA');
                setOldRoute(data.old_route);
                setNewRoute(data.new_route);
                setShowRerouteModal(true);
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
                    setShipmentStatus({
                        status: status.status,
                        on_time: status.on_time,
                        confidence: status.confidence,
                        eta_next_stop_ts: status.eta_next_stop_ts,
                        late_by_min: status.late_by_min || 0,
                        current_leg: status.current_leg || ''
                    });
                    setCurrentStopSeq(status.next_stop?.seq ?? null);
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
            <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-900 flex items-center justify-center p-6 relative overflow-hidden">
                {/* Animated background effects */}
                <div className="absolute inset-0 opacity-20">
                    <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-cyan-500 rounded-full mix-blend-multiply filter blur-3xl animate-blob"></div>
                    <div className="absolute top-1/3 right-1/4 w-96 h-96 bg-blue-500 rounded-full mix-blend-multiply filter blur-3xl animate-blob animation-delay-2000"></div>
                    <div className="absolute bottom-1/4 left-1/3 w-96 h-96 bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl animate-blob animation-delay-4000"></div>
                </div>
                
                <div className="max-w-2xl w-full relative z-10">
                    <div className="text-center mb-8">
                        <div className="inline-block p-4 bg-gradient-to-br from-cyan-500/20 to-blue-500/20 rounded-2xl mb-6 backdrop-blur-sm border border-cyan-500/30">
                            <TruckIcon className="w-16 h-16 text-cyan-400 drop-shadow-[0_0_15px_rgba(34,211,238,0.5)]" />
                        </div>
                        <h1 className="text-6xl font-black mb-4 bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-500 bg-clip-text text-transparent drop-shadow-2xl">
                            Track Your Delivery
                        </h1>
                        <p className="text-xl text-gray-300">
                            Real-time tracking with live GPS updates
                        </p>
                    </div>
                    
                    <form onSubmit={handleSubmit} className="relative">
                        <div className="absolute inset-0 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-2xl blur opacity-20"></div>
                        <div className="relative bg-gray-900/80 backdrop-blur-xl border border-gray-700/50 rounded-2xl p-2 shadow-2xl">
                            <div className="flex gap-2">
                                <input
                                    type="text"
                                    value={trackingInput}
                                    onChange={(e) => setTrackingInput(e.target.value)}
                                    placeholder="Enter tracking number (e.g., PO-98765)"
                                    className="flex-1 px-6 py-5 bg-gray-800/50 border border-gray-700/50 rounded-xl text-white text-lg placeholder-gray-500 focus:outline-none focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/30 transition-all"
                                />
                                <button
                                    type="submit"
                                    disabled={isLoading}
                                    className="px-10 py-5 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 disabled:from-gray-600 disabled:to-gray-700 disabled:cursor-not-allowed rounded-xl font-bold text-white text-lg transition-all transform hover:scale-105 active:scale-95 shadow-lg shadow-cyan-500/50 disabled:shadow-none"
                                >
                                    {isLoading ? (
                                        <span className="flex items-center gap-2">
                                            <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
                                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                            </svg>
                                            Tracking...
                                        </span>
                                    ) : 'Track Package'}
                                </button>
                            </div>
                        </div>
                    </form>
                    
                    {error && (
                        <div className="mt-6 p-4 bg-red-500/10 border border-red-500/30 rounded-xl backdrop-blur-sm animate-shake">
                            <p className="text-red-300 text-center font-semibold">⚠️ {error}</p>
                        </div>
                    )}
                    
                    <div className="mt-12 grid grid-cols-3 gap-6 text-center">
                        <div className="p-4 bg-gray-900/40 backdrop-blur-sm border border-gray-700/30 rounded-xl">
                            <div className="text-3xl font-bold text-cyan-400 mb-1">24/7</div>
                            <div className="text-sm text-gray-400">Live Updates</div>
                        </div>
                        <div className="p-4 bg-gray-900/40 backdrop-blur-sm border border-gray-700/30 rounded-xl">
                            <div className="text-3xl font-bold text-blue-400 mb-1">GPS</div>
                            <div className="text-sm text-gray-400">Real-time Tracking</div>
                        </div>
                        <div className="p-4 bg-gray-900/40 backdrop-blur-sm border border-gray-700/30 rounded-xl">
                            <div className="text-3xl font-bold text-purple-400 mb-1">ETA</div>
                            <div className="text-sm text-gray-400">Accurate Estimates</div>
                        </div>
                    </div>
                </div>
                
                <style>{`
                    @keyframes blob {
                        0%, 100% { transform: translate(0, 0) scale(1); }
                        25% { transform: translate(20px, -50px) scale(1.1); }
                        50% { transform: translate(-20px, 20px) scale(0.9); }
                        75% { transform: translate(50px, 50px) scale(1.05); }
                    }
                    .animate-blob {
                        animation: blob 7s infinite;
                    }
                    .animation-delay-2000 {
                        animation-delay: 2s;
                    }
                    .animation-delay-4000 {
                        animation-delay: 4s;
                    }
                    @keyframes shake {
                        0%, 100% { transform: translateX(0); }
                        25% { transform: translateX(-10px); }
                        75% { transform: translateX(10px); }
                    }
                    .animate-shake {
                        animation: shake 0.5s ease-in-out;
                    }
                `}</style>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-900 text-white">
            {/* Reroute Notification Modal */}
            {showRerouteModal && (
                <RerouteModal
                    reason={rerouteReason}
                    oldRoute={oldRoute}
                    newRoute={newRoute}
                    onClose={() => setShowRerouteModal(false)}
                />
            )}

            <div className="h-screen flex">
                {/* Left Panel - Tracking Details */}
                <div className="w-[420px] bg-gray-900/60 backdrop-blur-xl border-r border-gray-700/50 flex flex-col shadow-2xl">
                    {/* Header Section */}
                    <div className="p-6 border-b border-gray-700/50 bg-gradient-to-br from-gray-800/50 to-gray-900/50">
                        <div className="flex items-center justify-between mb-3">
                            <h2 className="text-2xl font-black bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
                                Live Tracking
                            </h2>
                            <div className="flex items-center gap-2 px-3 py-1.5 bg-green-500/10 border border-green-500/30 rounded-full">
                                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                                <span className="text-xs font-semibold text-green-400">LIVE</span>
                            </div>
                        </div>
                        <div className="flex items-center gap-2 mb-4">
                            <span className="text-gray-400 text-sm">Tracking #:</span>
                            <p className="text-cyan-400 font-mono font-bold text-lg">{activeRoute?.tracking_number}</p>
                        </div>

                        {/* Status Card */}
                        {shipmentStatus && (
                            <div className={`relative p-4 rounded-xl border overflow-hidden ${
                                shipmentStatus.on_time 
                                    ? 'bg-gradient-to-br from-green-500/10 to-emerald-500/10 border-green-500/30' 
                                    : 'bg-gradient-to-br from-red-500/10 to-orange-500/10 border-red-500/30'
                            }`}>
                                <div className="absolute top-0 right-0 w-32 h-32 bg-white/5 rounded-full blur-3xl"></div>
                                <div className="relative z-10">
                                    <div className="flex items-center justify-between mb-2">
                                        <span className="text-xs uppercase tracking-wider text-gray-300 font-semibold">Delivery Status</span>
                                        {shipmentStatus.on_time ? (
                                            <span className="px-2.5 py-1 bg-green-500/20 border border-green-500/40 rounded-full text-xs font-bold text-green-300">
                                                ✓ ON TIME
                                            </span>
                                        ) : (
                                            <span className="px-2.5 py-1 bg-red-500/20 border border-red-500/40 rounded-full text-xs font-bold text-red-300">
                                                ⚠ DELAYED {shipmentStatus.late_by_min}m
                                            </span>
                                        )}
                                    </div>
                                    <p className="text-white font-semibold text-sm mb-1">{shipmentStatus.current_leg}</p>
                                    <div className="flex items-center gap-2">
                                        <div className="flex-1 h-1.5 bg-gray-700/50 rounded-full overflow-hidden">
                                            <div 
                                                className="h-full bg-gradient-to-r from-cyan-500 to-blue-600 rounded-full transition-all duration-500"
                                                style={{ width: `${shipmentStatus.confidence * 100}%` }}
                                            ></div>
                                        </div>
                                        <span className="text-xs text-gray-400 font-semibold">{Math.round(shipmentStatus.confidence * 100)}%</span>
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Route Progress */}
                        {remainingInfo && remainingInfo.remainingKm !== null && (
                            <div className="mt-4 p-4 rounded-xl bg-gradient-to-br from-blue-500/10 to-purple-500/10 border border-blue-500/30 shadow-lg shadow-blue-500/10">
                                <div className="flex items-center justify-between mb-3">
                                    <span className="text-xs uppercase tracking-wider text-blue-200 font-semibold">Route Progress</span>
                                    <span className="text-2xl font-black text-white">
                                        {remainingInfo.remainingPercent !== null ? `${100 - remainingInfo.remainingPercent}%` : '—'}
                                    </span>
                                </div>
                                <div className="relative h-2 bg-gray-700/50 rounded-full overflow-hidden mb-2">
                                    <div 
                                        className="absolute top-0 left-0 h-full bg-gradient-to-r from-cyan-500 via-blue-500 to-purple-600 rounded-full transition-all duration-1000"
                                        style={{ width: `${remainingInfo.remainingPercent !== null ? 100 - remainingInfo.remainingPercent : 0}%` }}
                                    >
                                        <div className="absolute inset-0 bg-white/20 animate-pulse"></div>
                                    </div>
                                </div>
                                <p className="text-sm text-blue-200/80">
                                    {remainingInfo.remainingKm !== null ? `${remainingInfo.remainingKm.toFixed(1)} km remaining` : 'Calculating distance…'}
                                </p>
                            </div>
                        )}

                        {/* Traffic Alerts */}
                        {orderedTrafficSegments.length > 0 && (
                            <div className="mt-4">
                                <div className="flex items-center gap-2 mb-3">
                                    <svg className="w-4 h-4 text-orange-400" fill="currentColor" viewBox="0 0 20 20">
                                        <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd"/>
                                    </svg>
                                    <span className="text-sm uppercase tracking-wider text-orange-300 font-semibold">Traffic Alerts</span>
                                </div>
                                <div className="space-y-2 max-h-48 overflow-y-auto custom-scrollbar">
                                    {orderedTrafficSegments.map((segment, index) => {
                                        const severity = segment.traffic_level?.toLowerCase?.() ?? 'traffic';
                                        const severityLabel = severity.replace(/\b\w/g, (char) => char.toUpperCase());
                                        const nearestStopName = findNearestStopName(segment);
                                        const speedFactorPercent = segment.speed_factor != null ? Math.round(segment.speed_factor * 100) : null;

                                        const iconBySeverity: Record<string, string> = {
                                            severe: '🚨',
                                            heavy: '🔴',
                                            high: '🟠',
                                            moderate: '🟡',
                                            medium: '🟡',
                                            light: '🟢',
                                        };

                                        return (
                                            <div
                                                key={`${segment.start.lat}-${segment.start.lon}-${segment.end.lat}-${segment.end.lon}-${index}`}
                                                className="p-3 rounded-lg bg-gray-800/50 border border-gray-700/50 hover:bg-gray-800/70 transition-all"
                                            >
                                                <div className="flex items-start gap-2">
                                                    <span className="text-lg">{iconBySeverity[severity] ?? '🔵'}</span>
                                                    <div className="flex-1 min-w-0">
                                                        <p className="font-semibold text-white text-sm">{severityLabel} Traffic</p>
                                                        <p className="text-gray-400 text-xs truncate">
                                                            {nearestStopName ? `Near ${nearestStopName}` : 'On route'}
                                                        </p>
                                                        <p className="text-gray-500 text-xs mt-0.5">
                                                            Flow: {speedFactorPercent !== null ? `${speedFactorPercent}%` : '—'}
                                                        </p>
                                                    </div>
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            </div>
                        )}
                    </div>
                    
                    {/* Stops List */}
                    <div className="flex-1 overflow-y-auto p-6 custom-scrollbar">
                        <h3 className="text-sm uppercase tracking-wider text-gray-400 font-semibold mb-4 flex items-center gap-2">
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
                            </svg>
                            Delivery Stops ({stops.length})
                        </h3>
                        {isLoading ? (
                            <div className="flex flex-col items-center justify-center h-64 gap-4">
                                <svg className="animate-spin h-12 w-12 text-cyan-500" viewBox="0 0 24 24">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                </svg>
                                <p className="text-gray-400 font-semibold">Loading route details...</p>
                            </div>
                        ) : error ? (
                            <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-xl">
                                <p className="text-red-300 text-center font-semibold">⚠️ {error}</p>
                            </div>
                        ) : stops.length > 0 ? (
                            <StopList stops={stops} currentStopSeq={currentStopSeq} />
                        ) : (
                            <div className="text-gray-400 text-center p-8">
                                <p>No delivery stops found</p>
                            </div>
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
            
            <style>{`
                .custom-scrollbar::-webkit-scrollbar {
                    width: 6px;
                }
                .custom-scrollbar::-webkit-scrollbar-track {
                    background: rgba(31, 41, 55, 0.3);
                    border-radius: 10px;
                }
                .custom-scrollbar::-webkit-scrollbar-thumb {
                    background: rgba(96, 165, 250, 0.3);
                    border-radius: 10px;
                }
                .custom-scrollbar::-webkit-scrollbar-thumb:hover {
                    background: rgba(96, 165, 250, 0.5);
                }
            `}</style>
        </div>
    );
};
