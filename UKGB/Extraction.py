import time
import re
import os
from google import genai
from google.genai import errors

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def extract_relationships(text):
    MODEL_ID = "gemini-flash-lite-latest"
    prompt = f"""
    Extract relationships from the text and return them as triples: (entity1, relationship, entity2).
    
    CRITICAL RULES:
    1. Unify entities: Use simple and consistent names (e.g., use "trees" instead of "trees of the forest").
    2. Connect everything: Try to find how each phrase relates to the previous one to form a single graph.
    3. Format: Only return the triples, one per line.
    
    Text: {text}
    """

    try:
        response = client.models.generate_content(model=MODEL_ID, contents=prompt)
        if not response.text: return []
        
        matches = re.findall(r"\((.*?)\)", response.text)
        return [tuple(p.strip() for p in m.split(",")) for m in matches if len(m.split(",")) == 3]
    except Exception as e:
        print(f"Error in extraction: {e}")
        return None