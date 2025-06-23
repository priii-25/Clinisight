from ultralytics import YOLO
import numpy as np
import logging
import torch

logger = logging.getLogger(__name__)

class YoloDetector:
    def __init__(self, model_path='app/static/yolov8n.pt', conf_threshold=0.5, iou_threshold=0.45):
        try:
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            self.model = YOLO(model_path).to(device)
            self.conf_threshold = conf_threshold
            self.iou_threshold = iou_threshold
            self.model.overrides['conf'] = self.conf_threshold
            self.model.overrides['iou'] = self.iou_threshold
            logger.info(f"YOLO model loaded on {device}: {model_path}")
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {str(e)}")
            raise

    def detect(self, frame):
        try:
            results = self.model(frame, verbose=False)
            boxes = results[0].boxes.data.cpu().numpy()
            return boxes
        except Exception as e:
            logger.error(f"Error during detection: {str(e)}")
            return np.array([])

    def segment(self, frame):
        logger.warning("Segmentation not supported with current model")
        return [], []