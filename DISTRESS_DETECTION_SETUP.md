# AI-Powered Distress Detection Setup

This guide explains how to set up the advanced AI-powered distress detection system using Google's Gemini AI.

## Prerequisites

1. Google AI Studio API key (free tier available)
2. Python environment with updated requirements
3. Kafka setup (see KAFKA_SETUP.md)

## Setup Instructions

### 1. Get Gemini API Key

1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Create a new API key
4. Copy the API key for configuration

### 2. Environment Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your Gemini API key:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

### 3. Install Updated Requirements

```bash
pip install -r requirements.txt
```

This will install the new `google-generativeai` library needed for AI analysis.

### 4. How It Works

The system now provides **advanced distress detection** with the following capabilities:

#### Detection Features:
- **Physical Distress**: Unusual postures, pain indicators, injuries
- **Behavioral Analysis**: Agitation, confusion, calls for help
- **Emergency Situations**: Falls, medical device issues, breathing difficulties
- **Environmental Hazards**: Unsafe conditions, equipment malfunctions

#### Severity Levels:
- **Critical**: Immediate medical intervention required
- **High**: Urgent attention needed
- **Medium**: Monitor closely
- **Low**: Normal monitoring
- **None**: No distress detected

#### Alert Information:
- Detailed description of detected issues
- Specific indicators observed
- Recommended actions
- Confidence scores
- Analysis timestamps

### 5. System Architecture

```
[Video Frame] → [YOLO Detection] → [Person Detected?] 
                       ↓
              [Gemini AI Analysis] → [Distress Assessment] → [Enhanced Alert]
                       ↓
              [Kafka: alerts topic] → [Database] → [Frontend Dashboard]
```

### 6. Cost Management

- AI analysis runs every 3rd person detection (configurable)
- Uses Gemini Flash model for cost efficiency
- Gemini free tier includes 15 requests/minute

### 7. Configuration Options

In your `.env` file, you can adjust:

```env
# How often to run AI analysis (every Nth detection)
AI_ANALYSIS_INTERVAL=3

# Cooldown between alerts (seconds)
ALERT_COOLDOWN_SECONDS=5
```

### 8. Testing the System

1. Start Kafka (see KAFKA_SETUP.md)
2. Start the application:
   ```bash
   python app.py
   ```
3. Check logs for AI initialization:
   ```
   INFO - Gemini AI analysis enabled for distress detection
   ```

### 9. Expected Alert Format

With AI enhancement, alerts now include:

```json
{
  "room": "101",
  "severity": "high",
  "description": "DISTRESS DETECTED: Patient appears to be in pain. Person showing signs of physical discomfort with defensive posturing and facial expressions indicating distress. Indicators: unusual body posture, facial pain indicators",
  "timestamp": 1695820800,
  "person_confidence": 0.92,
  "distress_detected": true,
  "ai_confidence": 0.85,
  "primary_concern": "Patient appears to be in pain",
  "recommended_action": "Check patient immediately",
  "indicators": ["unusual body posture", "facial pain indicators"],
  "analysis_type": "ai_enhanced"
}
```

### 10. Fallback Behavior

If AI analysis fails or API key is missing:
- System falls back to basic person detection
- Continues normal operation with YOLO-only alerts
- Logs warnings but doesn't crash

### 11. Privacy and Security

- Frames are processed in real-time (not stored)
- API calls use secure HTTPS
- Consider using Google Cloud for HIPAA compliance in production

## Troubleshooting

### Common Issues:

1. **"Import google.generativeai could not be resolved"**
   - Run: `pip install google-generativeai`

2. **"GEMINI_API_KEY not found"**
   - Check your `.env` file has the correct API key
   - Ensure `.env` is in the project root

3. **"AI analysis failed"**
   - Check internet connection
   - Verify API key is valid
   - Check Google AI Studio quotas

4. **High API costs**
   - Increase `AI_ANALYSIS_INTERVAL` value
   - Monitor usage in Google AI Studio

### Logs to Monitor:

```
INFO - Gemini AI analysis enabled for distress detection
INFO - Performing AI distress analysis...
INFO - Alert generated - Severity: high, Description: DISTRESS DETECTED...
```

This advanced system provides much more accurate and detailed distress detection compared to the previous hardcoded approach.