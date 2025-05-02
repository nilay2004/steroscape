from flask import Flask, jsonify, request, send_from_directory, make_response
from flask_cors import CORS
import os
import platform
import traceback

# Import the app from app.py instead of creating a new one
try:
    from app import app, processing_status, processStoped
    print("Imported app.py successfully")
except ImportError:
    print("Failed to import app.py, using minimal Flask app instead")
    app = Flask(__name__)
    # Configure CORS to allow all origins, methods and headers
    CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"], "allow_headers": "*"}}, supports_credentials=False)

    # Global variables to track processing status
    processing_status = {
        "status": "idle",  # idle, processing, complete, failed
        "percentage": 0,
        "message": "Server is ready"
    }

    # Create global variable for process status
    processStoped = False

    # Create necessary directories
    def ensure_directories():
        dirs_to_create = ['media', 'videos', 'results', 'colmap']
        for d in dirs_to_create:
            dir_path = os.path.join(os.getcwd(), d)
            if not os.path.exists(dir_path):
                print(f"Creating directory: {dir_path}")
                os.makedirs(dir_path)

    # Ensure directories exist
    ensure_directories()

    @app.route('/')
    def index():
        response = jsonify({'message': 'StereoScape API is running. Use the frontend application to interact with the API.', 'status': 'ok'})
        return response

    @app.route('/ping')
    def ping():
        """Simple ping endpoint to test if the server is running"""
        response = jsonify({'status': 'ok', 'message': 'pong'})
        # Add CORS headers explicitly
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        return response

    @app.route('/processing-status', methods=['GET'])
    def get_processing_status():
        """Return the current processing status"""
        response = jsonify(processing_status)
        # Add CORS headers explicitly
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        return response

    @app.route('/results/<path:filename>')
    def sendResultImage(filename):
        return send_from_directory('results', filename)

    @app.route('/videos/<path:filename>')
    def sendFiles(filename):
        return send_from_directory('videos', filename)

    @app.route('/media/<path:filename>')
    def sendMedia(filename):
        return send_from_directory('media', filename)

    @app.route('/stop-process', methods=['POST'])
    def handle_stop():
        global processStoped
        processStoped = True
        response = jsonify({'success': True})
        # Add CORS headers explicitly
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        return response

    @app.errorhandler(500)
    def handle_500_error(e):
        """Handle internal server errors"""
        print("500 Error:", str(e))
        traceback.print_exc()
        response = jsonify({
            'status': 'error',
            'message': 'Internal server error occurred. Please try again later.',
            'error': str(e)
        })
        response.status_code = 500
        # Add CORS headers
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        return response

    @app.errorhandler(404)
    def handle_404_error(e):
        """Handle not found errors"""
        response = jsonify({
            'status': 'error',
            'message': 'The requested resource was not found.',
            'error': str(e)
        })
        response.status_code = 404
        # Add CORS headers
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        return response

    @app.errorhandler(Exception)
    def handle_exception(e):
        """Handle all other exceptions"""
        print("Unhandled exception:", str(e))
        traceback.print_exc()
        response = jsonify({
            'status': 'error',
            'message': 'An unexpected error occurred. Please try again later.',
            'error': str(e)
        })
        response.status_code = 500
        # Add CORS headers
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        return response

    # Add a preflight response for all routes
    @app.route('/', defaults={'path': ''}, methods=['OPTIONS'])
    @app.route('/<path:path>', methods=['OPTIONS'])
    def handle_options(path):
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        return response

if __name__ == "__main__":
    print(f"Running Flask on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True) 