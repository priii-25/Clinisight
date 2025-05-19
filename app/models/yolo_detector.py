from ultralytics import YOLO
import numpy as np
import logging

# Set up logging
logger = logging.getLogger(__name__)

class YoloDetector:
    def __init__(self, model_path='app/static/yolov8n.pt', conf_threshold=0.5, iou_threshold=0.45):
        """Initialize YOLO model with configurable thresholds."""
        try:
            self.model = YOLO(model_path)
            self.conf_threshold = conf_threshold
            self.iou_threshold = iou_threshold
            self.model.overrides['conf'] = self.conf_threshold
            self.model.overrides['iou'] = self.iou_threshold
            logger.info(f"YOLO model loaded: {model_path}")
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {str(e)}")
            raise

    def detect(self, frame):
        """Detect objects in a frame and return bounding boxes."""
        try:
            results = self.model(frame, verbose=False)
            boxes = results[0].boxes.data.cpu().numpy()  # [x1, y1, x2, y2, conf, class]
            return boxes
        except Exception as e:
            logger.error(f"Error during detection: {str(e)}")
            return np.array([])

    def segment(self, frame):
        """Perform segmentation and return masks with corresponding labels."""
        try:
            results = self.model(frame, verbose=False)
            if results[0].masks is None:
                return [], []
            masks = results[0].masks.data.cpu().numpy()  # Segmentation masks
            labels = results[0].boxes.cls.cpu().numpy()  # Class labels
            confidences = results[0].boxes.conf.cpu().numpy()  # Confidence scores
            # Filter by confidence
            mask_data = []
            label_data = []
            for i, conf in enumerate(confidences):
                if conf >= self.conf_threshold:
                    mask_data.append(masks[i])
                    label_data.append(int(labels[i]))
            return mask_data, label_data
        except Exception as e:
            logger.error(f"Error during segmentation: {str(e)}")
            return [], []