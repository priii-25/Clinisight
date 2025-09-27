import google.generativeai as genai
import cv2
import base64
import json
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class GeminiClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Distress detection prompt template
        self.distress_prompt = """
Analyze this medical/healthcare image for signs of patient distress or emergency situations. 
Look for the following indicators:

1. **Physical Distress Signs:**
   - Unusual body postures (hunched, collapsed, twisted)
   - Signs of pain or discomfort in facial expressions
   - Abnormal positioning (lying on floor, slumped over)
   - Visible injuries or medical emergencies

2. **Behavioral Indicators:**
   - Agitated or erratic movements
   - Signs of confusion or disorientation
   - Attempts to call for help (raised arms, gesturing)
   - Unusual stillness or lack of movement

3. **Emergency Situations:**
   - Falls or accidents
   - Medical device disconnections
   - Choking or breathing difficulties
   - Seizures or convulsions

4. **Environmental Hazards:**
   - Objects that could cause harm
   - Spills or unsafe conditions
   - Equipment malfunctions

Provide your analysis in the following JSON format:
{
  "distress_detected": boolean,
  "severity_level": "none|low|medium|high|critical",
  "primary_concern": "brief description of main issue",
  "indicators": ["list of specific signs observed"],
  "confidence_score": 0.0-1.0,
  "recommended_action": "immediate action needed",
  "description": "detailed analysis of the situation"
}

Be precise and focus on medical/healthcare context. If no distress is detected, still provide the JSON with appropriate values.
"""
        
        logger.info("GeminiClient initialized with distress detection capabilities")
    
    def _encode_frame(self, frame) -> str:
        """Encode OpenCV frame to base64 for Gemini API"""
        try:
            # Convert BGR to RGB (OpenCV uses BGR, Gemini expects RGB)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Encode to JPEG
            success, buffer = cv2.imencode('.jpg', rgb_frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            if not success:
                raise Exception("Failed to encode frame as JPEG")
            
            # Convert to base64
            jpg_as_text = base64.b64encode(buffer).decode('utf-8')
            return jpg_as_text
            
        except Exception as e:
            logger.error(f"Error encoding frame: {str(e)}")
            raise
    
    def analyze_frame(self, frame) -> Dict:
        """Analyze frame for distress indicators using Gemini AI"""
        try:
            # Encode frame for API
            encoded_image = self._encode_frame(frame)
            
            # Create image part for Gemini
            image_part = {
                "mime_type": "image/jpeg",
                "data": encoded_image
            }
            
            # Generate content with image and prompt
            response = self.model.generate_content([
                self.distress_prompt,
                image_part
            ])
            
            # Parse JSON response
            try:
                result = json.loads(response.text)
                
                # Validate required fields
                required_fields = ['distress_detected', 'severity_level', 'description']
                for field in required_fields:
                    if field not in result:
                        logger.warning(f"Missing field '{field}' in Gemini response")
                        result[field] = self._get_default_value(field)
                
                # Add metadata
                result['analysis_timestamp'] = int(__import__('time').time())
                result['model_version'] = 'gemini-1.5-flash'
                
                logger.info(f"Distress analysis completed - Detected: {result.get('distress_detected', False)}, Severity: {result.get('severity_level', 'none')}")
                return result
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Gemini JSON response: {str(e)}")
                logger.error(f"Raw response: {response.text}")
                return self._get_fallback_response("JSON parsing error")
                
        except Exception as e:
            logger.error(f"Error in Gemini frame analysis: {str(e)}")
            return self._get_fallback_response(str(e))
    
    def _get_default_value(self, field: str):
        """Get default values for missing fields"""
        defaults = {
            'distress_detected': False,
            'severity_level': 'none',
            'primary_concern': 'Analysis incomplete',
            'indicators': [],
            'confidence_score': 0.0,
            'recommended_action': 'Monitor situation',
            'description': 'Unable to complete full analysis'
        }
        return defaults.get(field, None)
    
    def _get_fallback_response(self, error_msg: str) -> Dict:
        """Generate fallback response when AI analysis fails"""
        return {
            'distress_detected': False,
            'severity_level': 'unknown',
            'primary_concern': 'Analysis failed',
            'indicators': [],
            'confidence_score': 0.0,
            'recommended_action': 'Manual review required',
            'description': f'AI analysis failed: {error_msg}',
            'analysis_timestamp': int(__import__('time').time()),
            'model_version': 'gemini-1.5-flash',
            'error': True
        }
    
    def batch_analyze(self, frames: List) -> List[Dict]:
        """Analyze multiple frames for distress patterns"""
        results = []
        for i, frame in enumerate(frames):
            try:
                result = self.analyze_frame(frame)
                result['frame_index'] = i
                results.append(result)
            except Exception as e:
                logger.error(f"Error analyzing frame {i}: {str(e)}")
                results.append(self._get_fallback_response(f"Frame {i} analysis failed"))
        
        return results