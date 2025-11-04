#!/usr/bin/env python3
"""
System Verification Script

Checks that all components are properly configured and ready for testing.
Run this after setting up the project to verify everything works.
"""

import os
import sys
import subprocess
from dotenv import load_dotenv

load_dotenv()

def print_header(text):
    """Print formatted section header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def check_mark(passed):
    """Return check mark or X"""
    return "✅" if passed else "❌"

def check_python_version():
    """Check Python version"""
    print_header("Python Version")
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    
    required = (3, 8)
    passed = version >= required
    print(f"{check_mark(passed)} Required: Python 3.8+")
    return passed

def check_node_version():
    """Check Node.js version"""
    print_header("Node.js Version")
    try:
        result = subprocess.run(['node', '--version'], 
                              capture_output=True, text=True, timeout=5)
        version = result.stdout.strip()
        print(version)
        
        # Extract major version
        major = int(version.replace('v', '').split('.')[0])
        passed = major >= 16
        print(f"{check_mark(passed)} Required: Node.js 16+")
        return passed
    except Exception as e:
        print(f"❌ Node.js not found: {e}")
        return False

def check_database():
    """Check PostgreSQL connection"""
    print_header("Database Connection")
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not set in .env file")
        return False
    
    print(f"Database URL: {database_url[:30]}...")
    
    try:
        import psycopg2
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Check PostGIS extension
        cursor.execute("SELECT PostGIS_version();")
        version = cursor.fetchone()[0]
        print(f"✅ PostGIS version: {version}")
        
        # Check if schema exists
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_name IN ('shipments', 'vehicles', 'stops', 'positions')
        """)
        table_count = cursor.fetchone()[0]
        
        if table_count == 4:
            print(f"✅ All required tables exist ({table_count}/4)")
        else:
            print(f"⚠️ Only {table_count}/4 tables found")
            print("   Run: psql -U postgres -d eta_tracker -f data/init_db.sql")
        
        conn.close()
        return True
        
    except ImportError:
        print("❌ psycopg2 not installed. Run: pip install psycopg2-binary")
        return False
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def check_python_packages():
    """Check required Python packages"""
    print_header("Python Packages")
    
    required_packages = [
        'flask',
        'flask_socketio',
        'psycopg2',
        'requests',
        'python-dotenv'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} (missing)")
            missing.append(package)
    
    if missing:
        print(f"\nInstall missing packages: pip install {' '.join(missing)}")
        return False
    
    return True

def check_node_packages():
    """Check if node_modules exists"""
    print_header("Node.js Packages")
    
    if os.path.exists('node_modules'):
        print("✅ node_modules directory exists")
        
        # Check for key packages
        key_packages = ['react', 'react-router-dom', 'socket.io-client', 'leaflet']
        for package in key_packages:
            package_path = os.path.join('node_modules', package)
            if os.path.exists(package_path):
                print(f"✅ {package}")
            else:
                print(f"❌ {package} (missing)")
        
        return True
    else:
        print("❌ node_modules not found")
        print("   Run: npm install")
        return False

def check_test_data():
    """Check if test data exists"""
    print_header("Test Data")
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ Cannot check test data (DATABASE_URL not set)")
        return False
    
    try:
        import psycopg2
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Check organizations
        cursor.execute("SELECT COUNT(*) FROM organizations")
        org_count = cursor.fetchone()[0]
        print(f"{check_mark(org_count >= 2)} Organizations: {org_count}/2")
        
        # Check vehicles
        cursor.execute("SELECT COUNT(*) FROM vehicles")
        vehicle_count = cursor.fetchone()[0]
        print(f"{check_mark(vehicle_count >= 5)} Vehicles: {vehicle_count}/5")
        
        # Check shipments
        cursor.execute("SELECT COUNT(*) FROM shipments")
        shipment_count = cursor.fetchone()[0]
        print(f"{check_mark(shipment_count >= 4)} Shipments: {shipment_count}/4")
        
        # Check stops
        cursor.execute("SELECT COUNT(*) FROM stops")
        stop_count = cursor.fetchone()[0]
        print(f"{check_mark(stop_count >= 20)} Stops: {stop_count}/20+")
        
        conn.close()
        
        if org_count < 2 or vehicle_count < 5 or shipment_count < 4:
            print("\n⚠️ Test data incomplete")
            print("   Run: populate_test_data.bat (Windows)")
            print("   Or:  python create_test_data.py (Linux/Mac)")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking test data: {e}")
        return False

def check_files():
    """Check if required files exist"""
    print_header("Required Files")
    
    required_files = [
        'backend/app.py',
        'data/db.py',
        'data/init_db.sql',
        'create_test_data.py',
        'simulate_last_mile.py',
        'package.json',
        'vite.config.ts',
        '.env'
    ]
    
    all_exist = True
    for file_path in required_files:
        exists = os.path.exists(file_path)
        print(f"{check_mark(exists)} {file_path}")
        if not exists:
            all_exist = False
    
    return all_exist

def check_backend():
    """Check if backend can start"""
    print_header("Backend Server")
    
    try:
        import requests
        response = requests.get('http://localhost:5000/health', timeout=2)
        print(f"✅ Backend running on port 5000")
        print(f"   Status: {response.status_code}")
        return True
    except requests.exceptions.ConnectionError:
        print("⚠️ Backend not running")
        print("   Start with: start_backend.bat (Windows)")
        print("   Or:         python backend/app.py (Linux/Mac)")
        return False
    except Exception as e:
        print(f"❌ Error checking backend: {e}")
        return False

def main():
    """Run all checks"""
    print("\n" + "="*70)
    print("  🧪 ETA TRACKER - SYSTEM VERIFICATION")
    print("="*70)
    print("\nChecking system configuration...")
    
    results = {
        'Python Version': check_python_version(),
        'Node.js Version': check_node_version(),
        'Python Packages': check_python_packages(),
        'Node.js Packages': check_node_packages(),
        'Required Files': check_files(),
        'Database Connection': check_database(),
        'Test Data': check_test_data(),
        'Backend Server': check_backend()
    }
    
    # Summary
    print_header("Summary")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        print(f"{check_mark(result)} {name}")
    
    print(f"\n{passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 All systems ready! You can start testing.")
        print("\nNext steps:")
        print("  1. Start backend:  start_backend.bat")
        print("  2. Start frontend: npm run dev")
        print("  3. Run simulator:  start_last_mile_simulator.bat ROUTE-DW-001 1")
        print("  4. Open browser:   http://localhost:5173")
        print("\nSee QUICKSTART.md for detailed instructions.")
        return 0
    else:
        print("\n⚠️ Some checks failed. Please fix the issues above.")
        print("\nQuick fixes:")
        print("  - Install Python packages: pip install -r requirements.txt")
        print("  - Install Node packages:   npm install")
        print("  - Setup database:          psql -U postgres -f data/init_db.sql")
        print("  - Populate test data:      populate_test_data.bat")
        print("  - Create .env file:        Copy from .env.example")
        return 1

if __name__ == '__main__':
    sys.exit(main())
