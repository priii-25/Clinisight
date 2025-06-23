from flask import Flask, Response, request
from flask_cors import CORS
import signal
import sys
from confluent_kafka import Consumer, KafkaException
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
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

# Initialize database
try:
    init_db()
    logger.info("Database initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize database: {str(e)}")
    sys.exit(1)

# Use a local video file for testing
video_path = 'app/static/sample.mp4'
rtsp_urls = {
    '101': video_path,
    '102': video_path
}

# Initialize video processors
try:
    video_processors = {room_id: VideoProcessor(url, room_id) for room_id, url in rtsp_urls.items()}
    logger.info("Video processors initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize video processors: {str(e)}")
    sys.exit(1)

# Kafka consumer configuration
consumer_conf = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'video-stream-consumer',
    'auto.offset.reset': 'latest'
}

@app.route('/api/stream')
def video_feed():
    room_id = request.args.get('room')
    if room_id not in video_processors:
        logger.warning(f"Invalid room ID: {room_id}")
        return Response("Invalid room ID", status=404)

    consumer = Consumer(consumer_conf)
    consumer.subscribe(['video-frames'])

    def generate():
        try:
            while True:
                msg = consumer.poll(timeout=1.0)
                if msg is None:
                    continue
                if msg.error():
                    raise KafkaException(msg.error())
                
                # Check if the message is for the requested room
                if msg.key().decode('utf-8') != room_id:
                    continue

                frame = msg.value()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        except Exception as e:
            logger.error(f"Error in video feed for room {room_id}: {str(e)}")
        finally:
            consumer.close()

    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Graceful shutdown
def shutdown_handler(signum, frame):
    logger.info("Shutting down server...")
    for processor in video_processors.values():
        processor.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        shutdown_handler(None, None)