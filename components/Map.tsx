/**
 * Interactive Map Component
 * 
 * Features:
 * - Real-time vehicle position tracking with custom truck icon
 * - Route visualization with Leaflet Routing Machine
 * - Multiple stop markers with sequence numbers
 * - Route progress tracking (completed vs remaining)
 * - Traffic segment overlays with color-coded severity
 * - Automatic map centering and bounds fitting
 * 
 * @author ETA Tracker Team
 * @version 1.0.0
 */

import React, { useRef, useEffect, useState, useMemo } from 'react';
import { Stop, Mode, TrafficSegment } from '../types';

declare const L: any;

/**
 * Remaining route information
 */
interface RemainingInfo {
  remainingPercent: number | null;
  remainingKm: number | null;
}

/**
 * MapComponent Props
 */
interface MapProps {
  /** Current vehicle GPS position */
  vehiclePosition: { lat: number; lon: number } | null;
  /** Array of route stops with coordinates and status */
  stops: Stop[];
  /** Display mode: 'manager' or 'customer' */
  mode: Mode;
  /** Active shipment ID for tracking */
  shipmentId?: number;
  /** Callback for route progress updates */
  onRemainingChange?: (info: RemainingInfo | null) => void;
  /** Callback for traffic segment updates */
  onTrafficUpdate?: (segments: TrafficSegment[]) => void;
  /** Unique map container ID for multiple instances */
  mapId?: string;
}

const truckLogoUrl = new URL('../assets/truck-logo.png', import.meta.url).href;

/**
 * MapComponent
 * Renders interactive Leaflet map with real-time tracking
 */
export const MapComponent: React.FC<MapProps> = ({ vehiclePosition, stops, mode, shipmentId, onRemainingChange, onTrafficUpdate, mapId }) => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<any>(null);
  const vehicleMarker = useRef<any>(null);
  const routingControl = useRef<any>(null);
  const stopMarkers = useRef<any[]>([]);
  const trafficLayers = useRef<any[]>([]);
  const progressLine = useRef<any>(null);
  const routeLatLngs = useRef<Array<{ lat: number; lng: number }>>([]);
  const [mapReady, setMapReady] = useState(false);
  const [routePath, setRoutePath] = useState<any>(null);
  const [routeLengthKm, setRouteLengthKm] = useState<number>(0);
  const stopsRef = useRef<Stop[]>(stops);

  useEffect(() => {
    stopsRef.current = stops;
  }, [stops]);

  const routeSignature = useMemo(() => {
    if (stops.length < 2) {
      return '';
    }

    return stops
      .map((stop) => {
        const identifier = stop.id ?? stop.stop_sequence ?? stop.seq ?? stop.name ?? 'stop';
        return `${identifier}:${stop.lat.toFixed(5)}:${stop.lon.toFixed(5)}`;
      })
      .join('|');
  }, [stops]);

  const toRad = (deg: number) => (deg * Math.PI) / 180;

  const haversineDistanceKm = (a: { lat: number; lon?: number; lng?: number }, b: { lat: number; lon?: number; lng?: number }) => {
    const lonA = a.lon ?? a.lng ?? 0;
    const lonB = b.lon ?? b.lng ?? 0;
    const dLat = toRad(b.lat - a.lat);
    const dLon = toRad(lonB - lonA);
    const originLat = toRad(a.lat);
    const destLat = toRad(b.lat);

    const hav = Math.sin(dLat / 2) ** 2 + Math.cos(originLat) * Math.cos(destLat) * Math.sin(dLon / 2) ** 2;
    return 6371 * 2 * Math.atan2(Math.sqrt(hav), Math.sqrt(1 - hav));
  };

  const projectOntoSegment = (
    point: { lat: number; lon: number },
    start: { lat: number; lng: number },
    end: { lat: number; lng: number }
  ) => {
    const ax = start.lng;
    const ay = start.lat;
    const bx = end.lng;
    const by = end.lat;
    const px = point.lon;
    const py = point.lat;

    const dx = bx - ax;
    const dy = by - ay;
    const segmentLengthSq = dx * dx + dy * dy;

    let t = 0;
    if (segmentLengthSq > 0) {
      t = ((px - ax) * dx + (py - ay) * dy) / segmentLengthSq;
      t = Math.max(0, Math.min(1, t));
    }

    return {
      lat: ay + t * dy,
      lng: ax + t * dx,
      t,
    };
  };

  useEffect(() => {
    if (map.current || !mapContainer.current) return;
    
    map.current = L.map(mapContainer.current).setView([39.8283, -98.5795], 4);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: ' OpenStreetMap contributors',
      maxZoom: 19,
    }).addTo(map.current);

    if (!map.current.getPane('vehiclePane')) {
      map.current.createPane('vehiclePane');
    }
    const vehiclePane = map.current.getPane('vehiclePane');
    if (vehiclePane) {
      vehiclePane.style.zIndex = '650';
      vehiclePane.style.pointerEvents = 'none';
    }

    setMapReady(true);

    return () => {
      if (map.current) {
        map.current.remove();
        map.current = null;
      }
      setMapReady(false);
    };
  }, []);

  useEffect(() => {
    if (!map.current) {
      return;
    }

    const clearRouteArtifacts = () => {
      if (routingControl.current) {
        map.current.removeControl(routingControl.current);
        routingControl.current = null;
      }

      trafficLayers.current.forEach(layer => layer.remove());
      trafficLayers.current = [];

      if (progressLine.current) {
        map.current.removeLayer(progressLine.current);
        progressLine.current = null;
      }

      routeLatLngs.current = [];
      setRouteLengthKm(0);
      setRoutePath(null);

      if (onTrafficUpdate) {
        onTrafficUpdate([]);
      }
    };

    if (!routeSignature) {
      clearRouteArtifacts();
      return;
    }

    const currentStops = stopsRef.current;
    if (!currentStops || currentStops.length < 2) {
      clearRouteArtifacts();
      return;
    }

    clearRouteArtifacts();

    const waypoints = currentStops.map(stop => L.latLng(stop.lat, stop.lon));

    routingControl.current = (L as any).Routing.control({
      waypoints,
      routeWhileDragging: false,
      addWaypoints: false,
      draggableWaypoints: false,
      fitSelectedRoutes: true,
      showAlternatives: false,
      show: false,
      lineOptions: {
        styles: [{ color: '#000000', opacity: 0, weight: 0 }],
        extendToWaypoints: true,
        missingRouteTolerance: 0
      },
      createMarker: () => null,
      router: (L as any).Routing.osrmv1({
        serviceUrl: 'https://router.project-osrm.org/route/v1',
        profile: 'driving'
      })
    }).on('routesfound', (e: any) => {
      const routes = e.routes;
      if (routes && routes.length > 0) {
        const primaryRoute = routes[0];
        setRoutePath(primaryRoute);

        const coords = primaryRoute.coordinates.map((coord: any) => ({ lat: coord.lat, lng: coord.lng }));
        routeLatLngs.current = coords;

        let total = 0;
        for (let i = 0; i < coords.length - 1; i++) {
          total += haversineDistanceKm(coords[i], coords[i + 1]);
        }
        setRouteLengthKm(total);
      }
    }).addTo(map.current);

    const signatureAtFetch = routeSignature;

    if (shipmentId) {
      fetch(`http://localhost:5000/v1/shipments/${shipmentId}/traffic`)
        .then(res => res.json())
        .then(data => {
          if (routeSignature !== signatureAtFetch) {
            return;
          }

          let activeSegments: TrafficSegment[] = [];
          if (data.success && data.segments) {
            data.segments.forEach((segment: TrafficSegment) => {
              if (!segment || segment.traffic_level === 'none') {
                return;
              }

              activeSegments.push(segment);

              const latlngs = [
                [segment.start.lat, segment.start.lon],
                [segment.end.lat, segment.end.lon]
              ];

              const trafficLine = L.polyline(latlngs, {
                color: segment.color,
                weight: 8,
                opacity: 0.7,
                zIndex: 1000
              }).addTo(map.current);

              trafficLine.bindTooltip(
                `<strong>${segment.traffic_level.toUpperCase()} TRAFFIC</strong><br/>` +
                `Current: ${segment.current_speed_kph} km/h<br/>` +
                `Normal: ${segment.freeflow_speed_kph} km/h`,
                { sticky: true }
              );

              trafficLayers.current.push(trafficLine);
            });
          }

          if (onTrafficUpdate) {
            onTrafficUpdate(activeSegments);
          }
        })
        .catch(err => {
          console.error('Error fetching traffic:', err);
          if (onTrafficUpdate) {
            onTrafficUpdate([]);
          }
        });
    } else if (onTrafficUpdate) {
      onTrafficUpdate([]);
    }

    setTimeout(() => {
      const container = document.querySelector('.leaflet-routing-container');
      if (container) {
        (container as HTMLElement).style.display = 'none';
      }
    }, 100);

    map.current.fitBounds(L.latLngBounds(waypoints), { padding: [50, 50] });
  }, [routeSignature, shipmentId, onTrafficUpdate]);

  useEffect(() => {
    if (!map.current) {
      return;
    }

    stopMarkers.current.forEach(marker => marker.remove());
    stopMarkers.current = [];

    if (stops.length === 0) {
      return;
    }

    stops.forEach((stop, index) => {
      const isCompleted = !!stop.arrival_time;

      const iconHtml = isCompleted
        ? '<div style="background: #10b981; color: white; width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; border: 3px solid white; box-shadow: 0 3px 10px rgba(0,0,0,0.4); font-size: 16px;">✓</div>'
        : '<div style="background: #eab308; color: white; width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; border: 3px solid white; box-shadow: 0 3px 10px rgba(0,0,0,0.4); font-size: 16px;">' + (index + 1) + '</div>';

      const icon = L.divIcon({
        html: iconHtml,
        className: 'custom-marker',
        iconSize: [36, 36],
        iconAnchor: [18, 18]
      });

      const etaText = stop.eta_seconds ? Math.round(stop.eta_seconds / 60) + ' min' : 'N/A';
      const arrivalText = stop.arrival_time ? new Date(stop.arrival_time).toLocaleTimeString() : '';

      const popupContent = stop.arrival_time
        ? '<div style="color: #1f2937; min-width: 150px;"><strong style="font-size: 14px; color: #111827;">' + stop.name + '</strong><br/><span style="color: #10b981; font-size: 12px; font-weight: 600;">✓ Arrived at ' + arrivalText + '</span></div>'
        : '<div style="color: #1f2937; min-width: 150px;"><strong style="font-size: 14px; color: #111827;">' + stop.name + '</strong><br/><span style="color: #3b82f6; font-size: 12px; font-weight: 600;">🚚 ETA: ' + etaText + '</span></div>';

      const marker = L.marker([stop.lat, stop.lon], { icon })
        .addTo(map.current)
        .bindPopup(popupContent);

      stopMarkers.current.push(marker);
    });
  }, [stops]);

  useEffect(() => {
    if (!mapReady || !vehiclePosition || !routeLatLngs.current.length) {
      if (onRemainingChange) {
        onRemainingChange(null);
      }
      console.log('Vehicle marker not ready:', { mapReady, vehiclePosition, hasRoute: routeLatLngs.current.length > 0 });
      return;
    }

    console.log('Updating vehicle marker:', vehiclePosition, 'Mode:', mode);

    const latlngs = routeLatLngs.current;
    let closestPoint = { lat: vehiclePosition.lat, lon: vehiclePosition.lon };
  let closestDistance = Infinity;
  let segmentIndex = -1;
    let distanceAlong = 0;
    let accumulated = 0;

    for (let i = 0; i < latlngs.length - 1; i++) {
      const start = latlngs[i];
      const end = latlngs[i + 1];
      const projection = projectOntoSegment(vehiclePosition, start, end);
      const projectedPoint = { lat: projection.lat, lon: projection.lng };
      const distanceToSegment = haversineDistanceKm(vehiclePosition, { lat: projection.lat, lon: projection.lng });

      if (distanceToSegment < closestDistance) {
        closestDistance = distanceToSegment;
        closestPoint = projectedPoint;
        segmentIndex = i;
        const segmentLength = haversineDistanceKm(start, end);
        distanceAlong = accumulated + segmentLength * projection.t;
      }

      accumulated += haversineDistanceKm(start, end);
    }

    const snappedPosition = closestPoint;

    if (vehicleMarker.current) {
      console.log('Moving existing vehicle marker to:', snappedPosition);
      vehicleMarker.current.setLatLng([snappedPosition.lat, snappedPosition.lon]);
    } else {
      console.log('Creating new vehicle marker at:', snappedPosition);
      const vehicleIconHtml = mode === Mode.Transit
        ? '<div style="font-size: 48px; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.5)); line-height: 1;">🚌</div>'
        : `<div style="width: 60px; height: 68px; background-image: url('${truckLogoUrl}'); background-size: contain; background-repeat: no-repeat; background-position: center bottom; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.35));"></div>`;
      
      console.log('Vehicle icon HTML:', vehicleIconHtml);
      
      const vehicleIcon = L.divIcon({
        html: vehicleIconHtml,
        className: 'vehicle-marker',
        iconSize: [60, 68],
        iconAnchor: [30, 64]
      });

      vehicleMarker.current = L.marker([snappedPosition.lat, snappedPosition.lon], { 
        icon: vehicleIcon,
        zIndexOffset: 2000,
        pane: 'vehiclePane'
      }).addTo(map.current);
      
      console.log('Vehicle marker added to map');
    }

    if (segmentIndex >= 0) {
      const forwardLatLngs = [[snappedPosition.lat, snappedPosition.lon]].concat(
        latlngs.slice(segmentIndex + 1).map(point => [point.lat, point.lng])
      );

      if (progressLine.current) {
        progressLine.current.setLatLngs(forwardLatLngs);
        progressLine.current.setStyle({ color: '#1d4ed8' });
      } else {
        progressLine.current = L.polyline(forwardLatLngs, {
          color: '#1d4ed8',
          weight: 6,
          opacity: 0.9,
          dashArray: '12 6',
          zIndex: 900
        }).addTo(map.current);
      }

      const remainingKm = Math.max(0, routeLengthKm - distanceAlong);
      const remainingPercent = routeLengthKm > 0 ? Math.max(0, Math.round((remainingKm / routeLengthKm) * 100)) : null;

      if (onRemainingChange) {
        onRemainingChange({ remainingPercent, remainingKm });
      }
    } else if (onRemainingChange) {
      onRemainingChange(null);
    }
  }, [vehiclePosition, mode, mapReady, routePath, routeLengthKm]);

  return <div ref={mapContainer} id={mapId ?? 'map'} className="w-full h-full" />;
};
