"""
Simple test script to verify the Flask app can start
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Try importing the app
    from src.app import app
    print("✓ Flask app imported successfully")
    print(f"✓ Static folder: {app.static_folder}")
    print(f"✓ Routes registered:")
    for rule in app.url_map.iter_rules():
        print(f"  - {rule.rule} ({', '.join(rule.methods - {'OPTIONS', 'HEAD'})})")
    print("\n✓ All imports successful!")
    print("\nTo run the server:")
    print("  python src/app.py")
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("\nPlease install dependencies first:")
    print("  pip install -r requirements.txt")
except Exception as e:
    print(f"✗ Error: {e}")
