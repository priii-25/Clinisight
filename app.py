from flask import Flask, Response, request
from flask_cors import CORS
import cv2
from app.services.video_processor import VideoProcessor
from app.api.alerts import alerts_bp
from app.database.models import init_db
from dotenv import load_dotenv
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Enable CORS for the frontend origin
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3001"}})

# Initialize database
try:
    init_db()
    logger.info("Database initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize database: {str(e)}")
    raise

# Register blueprints
app.register_blueprint(alerts_bp, url_prefix='/api')

# Use a local video file for testing
video_path = 'app/static/sample.mp4'
rtsp_urls = {
    '101': video_path,
    '102': video_path
}

# Initialize video processors
try:
    video_processors = {room_id: VideoProcessor(url) for room_id, url in rtsp_urls.items()}
    logger.info("Video processors initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize video processors: {str(e)}")
    raise

@app.route('/api/stream')
def video_feed():
    room_id = request.args.get('room')
    processor = video_processors.get(room_id)
    if not processor:
        logger.warning(f"Invalid room ID: {room_id}")
        return Response("Invalid room ID", status=404)

    def generate():
        while True:
            try:
                frame = processor.queue.get()
                ret, buffer = cv2.imencode('.jpg', frame)
                if not ret:
                    logger.warning("Failed to encode frame")
                    continue
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            except Exception as e:
                logger.error(f"Error in video feed for room {room_id}: {str(e)}")
                break

    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)