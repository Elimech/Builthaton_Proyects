from datetime import datetime
from Core.debug_utils import DebugManager
import re

def clean_text(text: str) -> str:
    """Removes Slack formatting (e.g., <@U12345>, commands) from text."""
    if not text:
        return ""
    # Remove user mentions <@U...>
    text = re.sub(r"<@[A-Z0-9]+>", "", text)
    # Remove channel mentions <#C...>
    text = re.sub(r"<#[A-Z0-9]+\|?.*?>", "", text)
    # Remove URLs
    text = re.sub(r"<http.*?>", "", text)
    return text.strip()

def calculate_stress_score(text: str) -> float:
    """
    Heuristic for stress score, supporting English and Spanish keywords.
    """
    stress_keywords = [
        "urgent", "deadline", "asap", "error", "fail", "broken", "critical",
        "cansado", "mamado", "matar", "estrés", "estres", "urgente", "deadline", 
        "terminar", "pesado", "agotado", "no puedo más", "ayuda", "error", 
        "falló", "fallo", "mordió", "perro", "mal", "terrible", "peor",
        "hacer nada", "mamado de trabajar", "señor stark", "stark", "llore",
        "no funciona", "puto", "escopetazo", "kurt cobain"
    ]
    text_lower = text.lower()
    score = 0.0
    for word in stress_keywords:
        if word in text_lower:
            score += 0.25 # Increased impact per keyword
    return min(score, 1.0)

def normalize_message(raw_message: dict, channel_id: str = None) -> dict:
    """
    Transforms a raw Slack message into a clean structured dictionary.
    """
    # Ignore non-user messages (like bot join messages)
    if raw_message.get("type") != "message":
        return None
    
    # Skip subtypes like 'channel_join', 'channel_leave' unless you want them
    if raw_message.get("subtype"):
        return None

    # Extract basic fields
    message_id = raw_message.get("ts")
    user_id = raw_message.get("user", "unknown")
    text = raw_message.get("text", "")
    reply_count = raw_message.get("reply_count", 0)

    # Convert timestamp
    ts = raw_message.get("ts")
    timestamp_iso = None
    time_data = {"hour": 0, "day": 0}
    
    if ts:
        dt = datetime.fromtimestamp(float(ts.split(".")[0]))
        timestamp_iso = dt.isoformat()
        time_data = {
            "hour": dt.hour,
            "day": dt.weekday(), # 0=Monday, 6=Sunday
            "iso": timestamp_iso
        }

    # Extract reactions
    reactions = []
    if "reactions" in raw_message:
        for reaction in raw_message["reactions"]:
            reactions.append(reaction["name"])

    # Calculate derived metrics
    cleaned_text = clean_text(text)
    stress = calculate_stress_score(cleaned_text)

    normalized = {
        "message_id": message_id,
        "channel_id": channel_id,
        "user_id": user_id,
        "user_name": "Unknown", # Collector should populate this if possible, or we resolve later
        # Note: 'user_name' is often not in the raw message event, need user profile lookup
        "text": text,
        "text_clean": cleaned_text,
        "stress_score": stress,
        "timestamp": timestamp_iso,
        "time_data": time_data,
        "is_thread": raw_message.get("thread_ts") is not None and raw_message.get("thread_ts") != raw_message.get("ts"),
        "reply_count": reply_count,
        "reactions": reactions,
    }
    DebugManager.log("NORMALIZED MESSAGE SAMPLE", normalized)

    return normalized




