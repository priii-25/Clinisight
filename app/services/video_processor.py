import cv2
from confluent_kafka import Producer
import json
import time
import logging
import os

logger = logging.getLogger(__name__)

class VideoProcessor:
    def __init__(self, video_source, room_id, max_retries=3):
        self.video_source = video_source
        self.room_id = room_id
        self.cap = None
        self.running = True
        self.max_retries = max_retries
        self.retry_delay = 5
        self.frame_skip = 5
        self.frame_count = 0
        self.is_local_file = os.path.isfile(video_source)
        
        # Kafka producer configuration
        self.producer = Producer({
            'bootstrap.servers': 'localhost:9092',
            'client.id': f'video-processor-{room_id}'
        })
        self.frame_topic = 'video-frames'
        self.alert_topic = 'alerts'
        
        # Initialize YOLO detection
        from app.services.alert_manager import AlertManager
        self.alert_manager = AlertManager(conf_threshold=0.5)
        
        # Start processing thread
        from threading import Thread
        self.thread = Thread(target=self._process, daemon=True)
        self.thread.start()
        logger.info(f"VideoProcessor initialized for source: {video_source}, room: {room_id}")

    def _connect(self):
        retry_count = 0
        while retry_count < self.max_retries:
            if not os.path.exists(self.video_source) and self.is_local_file:
                logger.error(f"Video file does not exist: {self.video_source}")
                return False
            self.cap = cv2.VideoCapture(self.video_source)
            if self.cap.isOpened():
                logger.info(f"Successfully connected to video source: {self.video_source}")
                return True
            logger.warning(f"Failed to connect to {self.video_source}. Retrying ({retry_count+1}/{self.max_retries})...")
            retry_count += 1
            time.sleep(self.retry_delay)
        logger.error(f"Failed to connect to video source after {self.max_retries} retries: {self.video_source}")
        return False

    def _process(self):
        while self.running:
            if self.cap is None or not self.cap.isOpened():
                if not self._connect():
                    time.sleep(self.retry_delay)
                    continue

            ret, frame = self.cap.read()
            if not ret:
                if self.is_local_file:
                    logger.info(f"End of video reached for {self.video_source}. Looping back to start.")
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                else:
                    logger.warning(f"Failed to read frame from {self.video_source}. Reconnecting...")
                    self.cap.release()
                    self.cap = None
                    continue

            self.frame_count += 1
            frame = cv2.resize(frame, (640, 480))

            # Encode frame as JPEG and send to Kafka
            ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
            if ret:
                frame_data = buffer.tobytes()
                self.producer.produce(
                    self.frame_topic,
                    key=self.room_id.encode('utf-8'),
                    value=frame_data,
                    callback=lambda err, msg: logger.error(f"Frame delivery failed: {err}") if err else None
                )
                self.producer.poll(0)

            # Process for detection less frequently
            if self.frame_count % self.frame_skip == 0:
                try:
                    alerts = self.alert_manager.process(frame)
                    for alert in alerts:
                        alert['room'] = self.room_id
                        self.producer.produce(
                            self.alert_topic,
                            key=self.room_id.encode('utf-8'),
                            value=json.dumps(alert).encode('utf-8'),
                            callback=lambda err, msg: logger.error(f"Alert delivery failed: {err}") if err else None
                        )
                        self.producer.poll(0)
                except Exception as e:
                    logger.error(f"Error processing frame: {str(e)}")

    def stop(self):
        self.running = False
        self.thread.join()
        if self.cap is not None:
            self.cap.release()
        self.producer.flush()
        logger.info(f"VideoProcessor stopped for source: {self.video_source}")