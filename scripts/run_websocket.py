#!/usr/bin/env python
"""
Script to run the WebSocket server for real-time chat.
This should be run as a separate process from the main Flask application.
"""

import os
import sys
import asyncio
import logging
from dotenv import load_dotenv

# Add parent directory to path so we can import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.websocket import start_websocket_server

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Get WebSocket host and port from environment variables
    host = os.getenv('WEBSOCKET_HOST', 'localhost')
    port = int(os.getenv('WEBSOCKET_PORT', 8765))
    
    logger.info(f"Starting WebSocket server on {host}:{port}")
    
    # Start WebSocket server
    loop = asyncio.get_event_loop()
    start_server = start_websocket_server(host, port)
    server = loop.run_until_complete(start_server)
    
    try:
        logger.info("WebSocket server running. Press Ctrl+C to stop.")
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info("Stopping WebSocket server...")
    finally:
        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()
        logger.info("WebSocket server stopped.") 