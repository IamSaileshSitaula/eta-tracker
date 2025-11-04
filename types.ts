/**
 * Type Definitions for ETA Tracker Application
 * 
 * This file contains all shared TypeScript interfaces and types
 * used across the frontend components for type safety and consistency.
 * 
 * @author ETA Tracker Team
 * @version 1.0.0
 */

/**
 * Application mode enum
 */
export enum Mode {
  /** Logistics shipment tracking mode */
  Logistics = 'logistics',
  /** Public transit GTFS tracking mode */
  Transit = 'transit',
}

/**
 * Route stop with location and timing information
 */
export interface Stop {
  /** Unique stop identifier */
  id: number | string;
  /** Stop name/address */
  name: string;
  /** Latitude coordinate */
  lat: number;
  /** Longitude coordinate */
  lon: number;
  /** Actual arrival timestamp (ISO 8601) */
  arrival_time: string | null;
  /** Estimated time to arrival in seconds */
  eta_seconds: number | null;
  /** Estimated arrival timestamp (ISO 8601) */
  eta_timestamp?: string;
  /** Stop order in route sequence */
  stop_sequence?: number;
  /** Legacy sequence number */
  seq?: number;
  /** Whether stop is completed */
  completed?: boolean;
  /** Whether stop is origin */
  is_origin?: boolean;
  /** Stop status */
  status?: string;
}

/**
 * Weather advisory notification
 */
export interface WeatherAdvisory {
  /** Advisory message text */
  message: string;
  /** Severity level for UI display */
  severity: 'low' | 'medium' | 'high';
}

/**
 * Real-time ETA update payload from backend
 */
export interface EtaUpdatePayload {
  /** Update source identifier */
  source: string;
  /** Unique tracking key */
  key: string;
  /** Current vehicle latitude */
  lat: number;
  /** Current vehicle longitude */
  lon: number;
  /** Updated ETA calculations for all stops */
  per_stop_etas: Stop[];
  /** Current weather advisory if any */
  advisory: WeatherAdvisory | null;
  /** Last update timestamp (ISO 8601) */
  last_timestamp: string;
}

/**
 * GTFS trip information for transit mode
 */
export interface GtfsTrip {
  /** Unique GTFS trip identifier */
  trip_id: string;
  /** Route short name (e.g., "101") */
  route_short_name: string;
  /** Trip destination headsign */
  trip_headsign: string;
}

/**
 * Complete route details for active shipment
 */
export interface RouteDetails {
  /** Shipment database ID */
  id: number;
  /** Customer-facing tracking number */
  tracking_number: string;
  /** Ordered list of route stops */
  stops: Stop[];
}

/**
 * Traffic segment with congestion information
 */
export interface TrafficSegment {
  /** Segment start coordinate */
  start: { lat: number; lon: number };
  /** Segment end coordinate */
  end: { lat: number; lon: number };
  /** Traffic level description (e.g., "heavy", "moderate") */
  traffic_level: string;
  /** Hex color code for map visualization */
  color: string;
  /** Speed reduction factor (0-1) */
  speed_factor: number;
  /** Current actual speed in km/h */
  current_speed_kph: number;
  /** Free-flow speed limit in km/h */
  freeflow_speed_kph: number;
}
