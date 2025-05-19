import cv2
from queue import Queue
from threading import Thread
from app.services.alert_manager import AlertManager
import time
import logging

logger = logging.getLogger(__name__)

class VideoProcessor:
    def __init__(self, video_source, max_retries=3):
        self.video_source = video_source
        self.cap = None
        self.queue = Queue(maxsize=10)
        self.alert_manager = AlertManager(conf_threshold=0.5)
        self.running = True
        self.max_retries = max_retries
        self.retry_delay = 5  # Seconds between retries
        self.frame_skip = 2  # Process every 2nd frame to reduce load
        self.frame_count = 0
        self.thread = Thread(target=self._process, daemon=True)
        self.thread.start()
        logger.info(f"VideoProcessor initialized for source: {video_source}")

    def _connect(self):
        retry_count = 0
        while retry_count < self.max_retries:
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
                logger.warning(f"Failed to read frame from {self.video_source}. Reconnecting...")
                self.cap.release()
                self.cap = None
                continue

            self.frame_count += 1
            if self.frame_count % self.frame_skip != 0:
                continue  # Skip frames to reduce processing load

            frame = cv2.resize(frame, (640, 480))
            if not self.queue.full():
                self.queue.put(frame)
                try:
                    self.alert_manager.process(frame)
                except Exception as e:
                    logger.error(f"Error processing frame: {str(e)}")

    def stop(self):
        self.running = False
        self.thread.join()
        if self.cap is not None:
            self.cap.release()
        logger.info(f"VideoProcessor stopped for source: {self.video_source}")