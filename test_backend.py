#!/usr/bin/env python
"""
Backend Database Test
Tests database connectivity and basic shipment queries
"""
import sys
sys.path.insert(0, 'backend')
sys.path.insert(0, 'data')

from flask import Flask, jsonify
from flask_cors import CORS
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

# Test database connection
conn = psycopg2.connect(
    dbname=os.getenv('DB_NAME', 'postgres'),
    user=os.getenv('DB_USER', 'postgres'),
    password=os.getenv('DB_PASSWORD', ''),
    host=os.getenv('DB_HOST', 'localhost'),
    port=os.getenv('DB_PORT', '5432')
)

@app.route('/test/shipments', methods=['GET'])
def test_shipments():
    try:
        ref = 'PO-98765'
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, ref, vehicle_id, organization_id, status, 
                       created_at::text, updated_at::text
                FROM shipments
                WHERE ref = %s
            """, (ref,))
            
            rows = cur.fetchall()
            
            if not rows:
                return jsonify([]), 200
            
            shipments = []
            for row in rows:
                shipments.append({
                    'id': row[0],
                    'ref': row[1],
                    'vehicle_id': row[2],
                    'organization_id': row[3],
                    'status': row[4],
                    'created_at': row[5],
                    'updated_at': row[6]
                })
            
            return jsonify(shipments), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Test server starting on http://localhost:5001")
    print("Test URL: http://localhost:5001/test/shipments")
    app.run(host='0.0.0.0', port=5001, debug=False)
