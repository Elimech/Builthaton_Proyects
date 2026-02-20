import os
import json
from dotenv import load_dotenv
from google import genai

# Find .env in the parent directory of 'Core'
lib_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(lib_dir)
env_path = os.path.join(project_root, '.env')
load_dotenv(env_path)

class GeminiAnalyzer:

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")

        self.api_key = api_key
        self.client = genai.Client(api_key=api_key)
        self.model_id = 'gemini-1.5-pro' # More stable model ID for analysis

    def analyze(self, context: dict):

        prompt = f"""
You are an organizational psychologist AI.

Analyze the following Slack team data and produce:

1. Emotional climate summary
2. Stress level interpretation
3. Burnout risk assessment
4. Communication pattern insights
5. Recommendations for leadership

DATA:
{json.dumps(context, indent=2)}
"""

        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt
        )
        return response.text
