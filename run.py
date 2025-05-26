#!/usr/bin/env python3

import subprocess
import sys
import os

def install_requirements():
    print("Installing requirements...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def main():
    if not os.path.exists("requirements.txt"):
        print("Error: requirements.txt not found. Please run setup.py first.")
        sys.exit(1)
    
    try:
        import flask
    except ImportError:
        print("Flask not found. Installing requirements...")
        install_requirements()
    
    print("Starting Flask application...")
    print("Open your browser and go to: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    
    from app import app
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()
