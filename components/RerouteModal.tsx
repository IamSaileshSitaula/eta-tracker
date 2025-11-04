import React, { useState } from 'react';
import { AlertTriangleIcon, CheckCircleIcon, XIcon } from './icons';

interface RerouteOption {
    id: number;
    distance_km: number;
    duration_min: number;
    time_saved_min: number;
    reason: string;
    route_geometry?: any;
}

interface RerouteModalProps {
    isOpen: boolean;
    onClose: () => void;
    currentRoute: {
        distance_km: number;
        duration_min: number;
    };
    alternativeRoute: RerouteOption | null;
    onAccept: (rerouteId: number) => void;
    onReject: () => void;
    isLoading?: boolean;
}

export const RerouteModal: React.FC<RerouteModalProps> = ({
    isOpen,
    onClose,
    currentRoute,
    alternativeRoute,
    onAccept,
    onReject,
    isLoading = false
}) => {
    const [isAccepting, setIsAccepting] = useState(false);

    if (!isOpen || !alternativeRoute) return null;

    const handleAccept = async () => {
        setIsAccepting(true);
        try {
            await onAccept(alternativeRoute.id);
            onClose();
        } catch (error) {
            console.error('Failed to accept reroute:', error);
        } finally {
            setIsAccepting(false);
        }
    };

    const handleReject = () => {
        onReject();
        onClose();
    };

    const formatTime = (minutes: number) => {
        const hours = Math.floor(minutes / 60);
        const mins = Math.round(minutes % 60);
        if (hours > 0) {
            return `${hours}h ${mins}m`;
        }
        return `${mins}m`;
    };

    const formatDistance = (km: number) => {
        return `${km.toFixed(1)} km`;
    };

    const timeSaved = alternativeRoute.time_saved_min;
    const isSignificantSavings = timeSaved >= 10; // Per spec: suggest when ≥10 minutes

    return (
        <>
            {/* Backdrop */}
            <div 
                className="fixed inset-0 bg-black bg-opacity-50 z-40"
                onClick={onClose}
            />
            
            {/* Modal */}
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                <div className="bg-gray-800 rounded-lg shadow-2xl max-w-2xl w-full border border-gray-700">
                    {/* Header */}
                    <div className="flex items-start justify-between p-6 border-b border-gray-700">
                        <div className="flex items-center gap-3">
                            <div className="w-12 h-12 bg-cyan-600 rounded-full flex items-center justify-center">
                                <AlertTriangleIcon className="w-6 h-6 text-white" />
                            </div>
                            <div>
                                <h2 className="text-2xl font-bold text-white">Alternative Route Available</h2>
                                <p className="text-gray-400 text-sm mt-1">
                                    {isSignificantSavings ? 'Significant time savings detected' : 'Minor route optimization available'}
                                </p>
                            </div>
                        </div>
                        <button
                            onClick={onClose}
                            className="text-gray-400 hover:text-white transition-colors"
                        >
                            <XIcon className="w-6 h-6" />
                        </button>
                    </div>

                    {/* Content */}
                    <div className="p-6">
                        {/* Reason */}
                        <div className="mb-6 p-4 bg-yellow-900/30 border border-yellow-600 rounded-lg">
                            <p className="text-yellow-400 font-medium">
                                {alternativeRoute.reason}
                            </p>
                        </div>

                        {/* Route Comparison */}
                        <div className="grid grid-cols-2 gap-4 mb-6">
                            {/* Current Route */}
                            <div className="p-4 bg-gray-700/50 rounded-lg border border-gray-600">
                                <h3 className="text-sm font-semibold text-gray-400 mb-3 uppercase">Current Route</h3>
                                <div className="space-y-2">
                                    <div>
                                        <p className="text-xs text-gray-500">Distance</p>
                                        <p className="text-lg font-bold text-white">{formatDistance(currentRoute.distance_km)}</p>
                                    </div>
                                    <div>
                                        <p className="text-xs text-gray-500">Time</p>
                                        <p className="text-lg font-bold text-white">{formatTime(currentRoute.duration_min)}</p>
                                    </div>
                                </div>
                            </div>

                            {/* Alternative Route */}
                            <div className="p-4 bg-cyan-900/30 rounded-lg border-2 border-cyan-500">
                                <h3 className="text-sm font-semibold text-cyan-400 mb-3 uppercase">Alternative Route</h3>
                                <div className="space-y-2">
                                    <div>
                                        <p className="text-xs text-gray-400">Distance</p>
                                        <p className="text-lg font-bold text-white">{formatDistance(alternativeRoute.distance_km)}</p>
                                    </div>
                                    <div>
                                        <p className="text-xs text-gray-400">Time</p>
                                        <p className="text-lg font-bold text-cyan-300">{formatTime(alternativeRoute.duration_min)}</p>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Time Savings Highlight */}
                        <div className="mb-6 p-4 bg-green-900/30 border border-green-600 rounded-lg flex items-center justify-center">
                            <CheckCircleIcon className="w-6 h-6 text-green-400 mr-3" />
                            <div>
                                <p className="text-green-400 font-bold text-xl">
                                    Save {formatTime(timeSaved)}
                                </p>
                                <p className="text-green-300 text-sm">
                                    Arrive approximately {timeSaved} minutes earlier
                                </p>
                            </div>
                        </div>

                        {/* Warning Note */}
                        <div className="mb-6 p-3 bg-gray-700 rounded text-sm text-gray-300">
                            <p className="font-semibold mb-1">⚠️ Note:</p>
                            <p>The alternative route has been validated for your vehicle's constraints (height, width, weight, hazmat). Traffic and weather conditions are factored into the estimated time.</p>
                        </div>

                        {/* Actions */}
                        <div className="flex gap-3">
                            <button
                                onClick={handleReject}
                                disabled={isAccepting || isLoading}
                                className="flex-1 px-6 py-3 bg-gray-700 hover:bg-gray-600 text-white font-semibold rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                Keep Current Route
                            </button>
                            <button
                                onClick={handleAccept}
                                disabled={isAccepting || isLoading}
                                className="flex-1 px-6 py-3 bg-cyan-600 hover:bg-cyan-500 text-white font-semibold rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                            >
                                {isAccepting ? (
                                    <>
                                        <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                        </svg>
                                        Accepting...
                                    </>
                                ) : (
                                    <>
                                        <CheckCircleIcon className="w-5 h-5" />
                                        Accept Alternative Route
                                    </>
                                )}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </>
    );
};
