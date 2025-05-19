class GeminiClient:
    def __init__(self, api_key):
        self.api_key = api_key

    def analyze_frame(self, frame):
        return {"description": "Patient movement detected"}