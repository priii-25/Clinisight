from app.models.yolo_detector import YoloDetector
from app.database.models import save_alert
import time
import logging

logger = logging.getLogger(__name__)

class AlertManager:
    def __init__(self, conf_threshold=0.5):
        self.yolo = YoloDetector(conf_threshold=conf_threshold)
        self.last_alert_time = 0
        self.alert_cooldown = 5  # Seconds between alerts for the same detection

    def process(self, frame):
        """Process a frame for detection and segmentation, generating alerts."""
        alerts = []

        # Object detection
        detections = self.yolo.detect(frame)
        for det in detections:
            if int(det[5]) == 0:  # Person class in COCO dataset
                conf = det[4]
                severity = 'high' if conf > 0.8 else 'medium'
                current_time = int(time.time())
                if current_time - self.last_alert_time < self.alert_cooldown:
                    continue
                alert = {
                    'room': 'unknown',
                    'severity': severity,
                    'description': f"Person detected with confidence {conf:.2f}",
                    'timestamp': current_time
                }
                try:
                    save_alert(alert)
                    alerts.append(alert)
                    self.last_alert_time = current_time
                    logger.info(f"Alert generated: {alert['description']}")
                except Exception as e:
                    logger.error(f"Failed to save alert: {str(e)}")

        # Segmentation for additional context
        masks, labels = self.yolo.segment(frame)
        for mask, label in zip(masks, labels):
            if label == 0:  # Person class
                current_time = int(time.time())
                if current_time - self.last_alert_time < self.alert_cooldown:
                    continue
                # Analyze mask for additional context (e.g., person size or position)
                mask_area = mask.sum()  # Approximate area of the segmented person
                alert = {
                    'room': 'unknown',
                    'severity': 'high' if mask_area > 5000 else 'medium',
                    'description': f"Segmented person detected with area {mask_area}",
                    'timestamp': current_time
                }
                try:
                    save_alert(alert)
                    alerts.append(alert)
                    self.last_alert_time = current_time
                    logger.info(f"Segmentation alert: {alert['description']}")
                except Exception as e:
                    logger.error(f"Failed to save segmentation alert: {str(e)}")

        return alerts