#!/usr/bin/env python
"""
WSGI entry point for the Pickleball application.
Supports deployment on multiple platforms:
- Heroku
- Vercel
- Local development
"""
import os
import sys
import logging
import traceback
from app import create_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('pickleball-app')

# Determine the environment
flask_env = os.environ.get('FLASK_ENV', 'production')
logger.info(f"Starting application in {flask_env} environment")

try:
    # Create the Flask application
    application = create_app(flask_env)
    
    # For compatibility with WSGI servers that expect 'app'
    app = application
    
    logger.info(f"Application initialized successfully")
    
    # For Vercel deployment
    # This is the handler that Vercel calls when processing a request
    def handler(request, **kwargs):
        try:
            return app(request.environ, lambda s, h, b: [s, h, [b if isinstance(b, bytes) else b.encode('utf-8')]])
        except Exception as e:
            # Log the error for debugging
            error_msg = f"ERROR: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            
            # Return a custom error response
            status = '500 Internal Server Error'
            headers = [('Content-type', 'application/json')]
            error_response = '{"error": "Internal Server Error", "message": "An unexpected error occurred"}'
            
            return [status, headers, [error_response.encode('utf-8')]]
    
except Exception as e:
    # Log initialization error
    error_msg = f"INITIALIZATION ERROR: {str(e)}\n{traceback.format_exc()}"
    logger.critical(error_msg)
    
    # Define a fallback handler that returns the error
    def handler(request, **kwargs):
        status = '500 Internal Server Error'
        headers = [('Content-type', 'application/json')]
        error_response = '{"error": "Initialization Error", "message": "Application failed to initialize"}'
        return [status, headers, [error_response.encode('utf-8')]]

# For Heroku and local development
if __name__ == "__main__":
    try:
        port = int(os.environ.get('PORT', 8000))
        
        # Auto-detect available servers
        server_type = os.environ.get('SERVER_TYPE', '').lower()
        
        if not server_type:
            # Auto-detect the best server to use
            if os.name == 'nt':  # Windows
                server_type = 'waitress'  # Default for Windows
            else:
                # Try to detect available servers
                try:
                    import gunicorn
                    server_type = 'gunicorn'  # Prefer Gunicorn if available
                except ImportError:
                    try:
                        from waitress import serve
                        server_type = 'waitress'  # Fallback to Waitress
                    except ImportError:
                        server_type = 'flask'  # Last resort
        
        # Start the appropriate server
        if server_type == 'waitress':
            try:
                from waitress import serve
                logger.info(f"Starting Waitress server on port {port}...")
                serve(application, host="0.0.0.0", port=port)
            except ImportError:
                logger.error("Waitress server requested but not installed. Falling back to Flask.")
                server_type = 'flask'
                
        elif server_type == 'gunicorn':
            try:
                # We don't directly import or use gunicorn here - it's used externally
                logger.info(f"Application ready for Gunicorn on port {port}")
                # Gunicorn should be started externally with:
                # gunicorn wsgi:app -b 0.0.0.0:$PORT
                app.run(host="0.0.0.0", port=port)
            except Exception:
                logger.error("Error with Gunicorn setup. Falling back to Flask.")
                server_type = 'flask'
                
        if server_type == 'flask':
            # Basic Flask development server - not recommended for production
            logger.info(f"Starting Flask development server on port {port}...")
            app.run(host="0.0.0.0", port=port, debug=(flask_env == 'development'))
            
    except NameError as ne:
        logger.critical(f"Application failed to initialize: {str(ne)}")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"Error starting server: {str(e)}")
        traceback.print_exc()
        sys.exit(1) 