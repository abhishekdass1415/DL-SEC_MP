#!/usr/bin/env python
"""
Simple script to run the Flask backend server
"""
from app import app, socketio

if __name__ == '__main__':
    print("Starting Threat Detection Backend Server...")
    print("Backend API: http://localhost:5000")
    print("WebSocket: ws://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)

