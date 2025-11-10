import React from 'react';
import { AlertTriangleIcon, CheckCircleIcon, XIcon } from './icons';

interface RerouteModalProps {
    reason: string;
    oldRoute?: {
        distance_km: number;
        duration_min: number;
    };
    newRoute?: {
        distance_km: number;
        duration_min: number;
    };
    onClose: () => void;
}

export const RerouteModal: React.FC<RerouteModalProps> = ({
    reason,
    oldRoute,
    newRoute,
    onClose
}) => {
    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fadeIn">
            <div className="relative max-w-2xl w-full bg-gradient-to-br from-gray-900 to-gray-800 border border-cyan-500/30 rounded-2xl shadow-2xl shadow-cyan-500/20 animate-slideUp">
                {/* Close button */}
                <button
                    onClick={onClose}
                    className="absolute top-4 right-4 p-2 hover:bg-gray-700/50 rounded-lg transition-colors group"
                >
                    <svg className="w-6 h-6 text-gray-400 group-hover:text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12"/>
                    </svg>
                </button>

                {/* Header */}
                <div className="p-6 border-b border-gray-700/50">
                    <div className="flex items-start gap-4">
                        <div className="p-3 bg-gradient-to-br from-cyan-500/20 to-blue-500/20 rounded-xl border border-cyan-500/30">
                            <svg className="w-8 h-8 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                            </svg>
                        </div>
                        <div className="flex-1">
                            <h3 className="text-2xl font-black text-white mb-2">Route Updated</h3>
                            <p className="text-gray-300 text-lg">Your delivery route has been optimized</p>
                        </div>
                    </div>
                </div>

                {/* Content */}
                <div className="p-6">
                    {/* Reason */}
                    <div className="mb-6 p-4 bg-blue-500/10 border border-blue-500/30 rounded-xl">
                        <div className="flex items-start gap-3">
                            <svg className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
                            </svg>
                            <div>
                                <p className="text-sm font-semibold text-blue-300 mb-1">Reason for Reroute</p>
                                <p className="text-gray-200">{reason}</p>
                            </div>
                        </div>
                    </div>

                    {/* Route Comparison */}
                    {oldRoute && newRoute && (
                        <div className="grid grid-cols-2 gap-4 mb-6">
                            {/* Old Route */}
                            <div className="p-4 bg-gray-800/50 border border-gray-700/50 rounded-xl">
                                <p className="text-xs uppercase tracking-wider text-gray-400 mb-3 font-semibold">Previous Route</p>
                                <div className="space-y-2">
                                    <div>
                                        <p className="text-2xl font-bold text-gray-300">{oldRoute.distance_km.toFixed(1)} km</p>
                                        <p className="text-xs text-gray-500">Distance</p>
                                    </div>
                                    <div>
                                        <p className="text-lg font-semibold text-gray-400">{Math.round(oldRoute.duration_min)} min</p>
                                        <p className="text-xs text-gray-500">Duration</p>
                                    </div>
                                </div>
                            </div>

                            {/* New Route */}
                            <div className="p-4 bg-gradient-to-br from-green-500/10 to-emerald-500/10 border border-green-500/30 rounded-xl">
                                <p className="text-xs uppercase tracking-wider text-green-300 mb-3 font-semibold">New Optimized Route</p>
                                <div className="space-y-2">
                                    <div>
                                        <p className="text-2xl font-bold text-green-400">{newRoute.distance_km.toFixed(1)} km</p>
                                        <p className="text-xs text-green-600">Distance</p>
                                    </div>
                                    <div>
                                        <p className="text-lg font-semibold text-green-300">{Math.round(newRoute.duration_min)} min</p>
                                        <p className="text-xs text-green-600">Duration</p>
                                    </div>
                                </div>
                                {oldRoute.duration_min > newRoute.duration_min && (
                                    <div className="mt-3 pt-3 border-t border-green-500/20">
                                        <p className="text-sm text-green-400 font-semibold">
                                            ⚡ Saves {Math.round(oldRoute.duration_min - newRoute.duration_min)} minutes
                                        </p>
                                    </div>
                                )}
                            </div>
                        </div>
                    )}

                    {/* Success Message */}
                    <div className="flex items-start gap-3 p-4 bg-green-500/10 border border-green-500/30 rounded-xl">
                        <svg className="w-6 h-6 text-green-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                        </svg>
                        <div>
                            <p className="font-semibold text-green-300 mb-1">Route Automatically Updated</p>
                            <p className="text-sm text-gray-300">The driver has been notified and your ETAs have been recalculated.</p>
                        </div>
                    </div>
                </div>

                {/* Footer */}
                <div className="p-6 border-t border-gray-700/50 bg-gray-800/30">
                    <button
                        onClick={onClose}
                        className="w-full px-6 py-3 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 rounded-xl font-bold text-white transition-all transform hover:scale-105 active:scale-95 shadow-lg shadow-cyan-500/30"
                    >
                        Got It
                    </button>
                </div>
            </div>

            <style>{`
                @keyframes fadeIn {
                    from { opacity: 0; }
                    to { opacity: 1; }
                }
                @keyframes slideUp {
                    from { 
                        opacity: 0;
                        transform: translateY(20px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }
                .animate-fadeIn {
                    animation: fadeIn 0.3s ease-out;
                }
                .animate-slideUp {
                    animation: slideUp 0.4s ease-out;
                }
            `}</style>
        </div>
    );
};
