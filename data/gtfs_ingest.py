#!/usr/bin/env python3
"""
GTFS Static Data Ingestion Script

This script downloads a GTFS static data zip file and loads it into the PostgreSQL database.
"""

import os
import sys
import csv
import zipfile
import requests
from io import BytesIO
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_batch

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()


def get_db_connection():
    """Get database connection"""
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        return psycopg2.connect(database_url)
    else:
        return psycopg2.connect(
            dbname=os.getenv('DB_NAME', 'postgres'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', ''),
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432')
        )


def download_gtfs_zip(url):
    """Download GTFS zip file from URL"""
    print(f"Downloading GTFS data from {url}...")
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return BytesIO(response.content)


def ingest_routes(conn, zip_file):
    """Ingest routes.txt"""
    print("Ingesting routes...")
    with zip_file.open('routes.txt') as f:
        reader = csv.DictReader(f.read().decode('utf-8').splitlines())
        rows = []
        for row in reader:
            rows.append((
                row['route_id'],
                row.get('route_short_name', ''),
                row.get('route_long_name', ''),
                int(row.get('route_type', 0))
            ))
        
        with conn.cursor() as cur:
            execute_batch(cur, """
                INSERT INTO gtfs.routes (route_id, route_short_name, route_long_name, route_type)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (route_id) DO UPDATE SET
                    route_short_name = EXCLUDED.route_short_name,
                    route_long_name = EXCLUDED.route_long_name,
                    route_type = EXCLUDED.route_type
            """, rows)
        
        conn.commit()
        print(f"Inserted {len(rows)} routes")


def ingest_stops(conn, zip_file):
    """Ingest stops.txt"""
    print("Ingesting stops...")
    with zip_file.open('stops.txt') as f:
        reader = csv.DictReader(f.read().decode('utf-8').splitlines())
        rows = []
        for row in reader:
            rows.append((
                row['stop_id'],
                row.get('stop_name', ''),
                float(row.get('stop_lat', 0)),
                float(row.get('stop_lon', 0))
            ))
        
        with conn.cursor() as cur:
            execute_batch(cur, """
                INSERT INTO gtfs.stops (stop_id, stop_name, stop_lat, stop_lon)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (stop_id) DO UPDATE SET
                    stop_name = EXCLUDED.stop_name,
                    stop_lat = EXCLUDED.stop_lat,
                    stop_lon = EXCLUDED.stop_lon
            """, rows)
        
        conn.commit()
        print(f"Inserted {len(rows)} stops")


def ingest_trips(conn, zip_file):
    """Ingest trips.txt"""
    print("Ingesting trips...")
    with zip_file.open('trips.txt') as f:
        reader = csv.DictReader(f.read().decode('utf-8').splitlines())
        rows = []
        for row in reader:
            rows.append((
                row['trip_id'],
                row['route_id'],
                row.get('trip_headsign', ''),
                int(row.get('direction_id', 0))
            ))
        
        with conn.cursor() as cur:
            execute_batch(cur, """
                INSERT INTO gtfs.trips (trip_id, route_id, trip_headsign, direction_id)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (trip_id) DO UPDATE SET
                    route_id = EXCLUDED.route_id,
                    trip_headsign = EXCLUDED.trip_headsign,
                    direction_id = EXCLUDED.direction_id
            """, rows, page_size=1000)
        
        conn.commit()
        print(f"Inserted {len(rows)} trips")


def ingest_stop_times(conn, zip_file):
    """Ingest stop_times.txt"""
    print("Ingesting stop times...")
    with zip_file.open('stop_times.txt') as f:
        reader = csv.DictReader(f.read().decode('utf-8').splitlines())
        rows = []
        for row in reader:
            rows.append((
                row['trip_id'],
                row['stop_id'],
                int(row.get('stop_sequence', 0)),
                row.get('arrival_time', ''),
                row.get('departure_time', '')
            ))
            
            # Process in batches to avoid memory issues
            if len(rows) >= 10000:
                with conn.cursor() as cur:
                    execute_batch(cur, """
                        INSERT INTO gtfs.stop_times (trip_id, stop_id, stop_sequence, arrival_time, departure_time)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (trip_id, stop_sequence) DO UPDATE SET
                            stop_id = EXCLUDED.stop_id,
                            arrival_time = EXCLUDED.arrival_time,
                            departure_time = EXCLUDED.departure_time
                    """, rows, page_size=1000)
                conn.commit()
                print(f"Processed {len(rows)} stop times...")
                rows = []
        
        # Process remaining rows
        if rows:
            with conn.cursor() as cur:
                execute_batch(cur, """
                    INSERT INTO gtfs.stop_times (trip_id, stop_id, stop_sequence, arrival_time, departure_time)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (trip_id, stop_sequence) DO UPDATE SET
                        stop_id = EXCLUDED.stop_id,
                        arrival_time = EXCLUDED.arrival_time,
                        departure_time = EXCLUDED.departure_time
                """, rows, page_size=1000)
            conn.commit()
            print(f"Processed final {len(rows)} stop times")


def main():
    """Main ingestion function"""
    gtfs_url = os.getenv('GTFS_STATIC_ZIP_URL')
    if not gtfs_url:
        print("Error: GTFS_STATIC_ZIP_URL not configured in .env file")
        sys.exit(1)
    
    try:
        # Download GTFS data
        zip_data = download_gtfs_zip(gtfs_url)
        
        # Open zip file
        with zipfile.ZipFile(zip_data) as zip_file:
            # Connect to database
            conn = get_db_connection()
            
            try:
                # Ingest data in order (respecting foreign keys)
                ingest_routes(conn, zip_file)
                ingest_stops(conn, zip_file)
                ingest_trips(conn, zip_file)
                ingest_stop_times(conn, zip_file)
                
                print("\nGTFS data ingestion completed successfully!")
                
            finally:
                conn.close()
    
    except Exception as e:
        print(f"Error during ingestion: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
