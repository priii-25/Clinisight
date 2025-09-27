from app.models.yolo_detector import YoloDetector
from app.models.gemini_client import GeminiClient
from app.database.models import save_alert
import time
import logging
import os
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class AlertManager:
    def __init__(self, conf_threshold=0.5, enable_ai_analysis=True):
        self.yolo = YoloDetector(conf_threshold=conf_threshold)
        self.last_alert_time = 0
        self.alert_cooldown = 5
        self.enable_ai_analysis = enable_ai_analysis
        
        # Initialize Gemini client if API key is available
        self.gemini_client = None
        if enable_ai_analysis:
            api_key = os.getenv('GEMINI_API_KEY')
            if api_key:
                try:
                    self.gemini_client = GeminiClient(api_key)
                    logger.info("Gemini AI analysis enabled for distress detection")
                except Exception as e:
                    logger.error(f"Failed to initialize Gemini client: {str(e)}")
                    self.gemini_client = None
            else:
                logger.warning("GEMINI_API_KEY not found. AI-powered distress analysis disabled.")
        
        # Analysis frequency control
        self.ai_analysis_interval = 3  # Analyze every 3rd detection to manage API costs
        self.analysis_count = 0

    def process(self, frame) -> List[Dict]:
        """Process frame for alerts using YOLO detection and optional AI analysis"""
        alerts = []
        detections = self.yolo.detect(frame)
        current_time = int(time.time())
        
        # Check if cooldown period has passed
        if current_time - self.last_alert_time < self.alert_cooldown:
            return alerts
        
        # Process YOLO detections
        person_detected = False
        highest_confidence = 0.0
        
        for det in detections:
            if int(det[5]) == 0:  # Person class in COCO dataset
                person_detected = True
                conf = float(det[4])
                if conf > highest_confidence:
                    highest_confidence = conf
        
        if not person_detected:
            return alerts
        
        # Perform AI-powered distress analysis if enabled
        ai_analysis = None
        if self.gemini_client and self._should_perform_ai_analysis():
            try:
                logger.info("Performing AI distress analysis...")
                ai_analysis = self.gemini_client.analyze_frame(frame)
            except Exception as e:
                logger.error(f"AI analysis failed: {str(e)}")
                ai_analysis = None
        
        # Generate alert based on detection and AI analysis
        alert = self._create_alert(
            person_confidence=highest_confidence,
            ai_analysis=ai_analysis,
            timestamp=current_time
        )
        
        # Save alert and update timing
        try:
            save_alert(alert)
            alerts.append(alert)
            self.last_alert_time = current_time
            
            # Log alert details
            severity = alert.get('severity', 'unknown')
            description = alert.get('description', 'No description')
            logger.info(f"Alert generated - Severity: {severity}, Description: {description}")
            
        except Exception as e:
            logger.error(f"Failed to save alert: {str(e)}")
        
        return alerts
    
    def _should_perform_ai_analysis(self) -> bool:
        """Determine if AI analysis should be performed (cost management)"""
        self.analysis_count += 1
        return self.analysis_count % self.ai_analysis_interval == 0
    
    def _create_alert(self, person_confidence: float, ai_analysis: Optional[Dict], timestamp: int) -> Dict:
        """Create alert based on YOLO detection and optional AI analysis"""
        
        # Base alert from YOLO detection
        base_severity = 'high' if person_confidence > 0.8 else 'medium'
        base_description = f"Person detected with confidence {person_confidence:.2f}"
        
        # Enhanced alert with AI analysis
        if ai_analysis and not ai_analysis.get('error', False):
            distress_detected = ai_analysis.get('distress_detected', False)
            ai_severity = ai_analysis.get('severity_level', 'none')
            ai_description = ai_analysis.get('description', '')
            primary_concern = ai_analysis.get('primary_concern', '')
            indicators = ai_analysis.get('indicators', [])
            recommended_action = ai_analysis.get('recommended_action', 'Monitor situation')
            confidence_score = ai_analysis.get('confidence_score', 0.0)
            
            # Determine final severity (prioritize AI analysis if distress detected)
            if distress_detected:
                severity_mapping = {
                    'critical': 'critical',
                    'high': 'high', 
                    'medium': 'medium',
                    'low': 'low',
                    'none': base_severity
                }
                final_severity = severity_mapping.get(ai_severity, base_severity)
            else:
                final_severity = 'low'  # Person present but no distress
            
            # Create comprehensive description
            if distress_detected:
                description = f"DISTRESS DETECTED: {primary_concern}. {ai_description}"
                if indicators:
                    description += f" Indicators: {', '.join(indicators)}"
            else:
                description = f"Person monitoring: {ai_description}"
            
            alert = {
                'room': 'unknown',  # Will be overridden by VideoProcessor
                'severity': final_severity,
                'description': description,
                'timestamp': timestamp,
                'person_confidence': person_confidence,
                'distress_detected': distress_detected,
                'ai_confidence': confidence_score,
                'primary_concern': primary_concern,
                'recommended_action': recommended_action,
                'indicators': indicators,
                'analysis_type': 'ai_enhanced'
            }
        else:
            # Fallback to basic YOLO-only alert
            alert = {
                'room': 'unknown',
                'severity': base_severity,
                'description': base_description,
                'timestamp': timestamp,
                'person_confidence': person_confidence,
                'analysis_type': 'basic_detection'
            }
        
        return alert