import os
import sys
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Request
from pathlib import Path
from dotenv import load_dotenv

# Ensure Core package is importable
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
env_path = project_root / ".env"
load_dotenv(env_path)

from Core.Collector import SlackCollector
from Core.metrics_engine import MetricsEngine
from Core.insights_engine import InsightsEngine
from Core.gemini_analyzer import GeminiAnalyzer

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# --- Shared collector instance ---
_collector = None

def get_collector():
    global _collector
    if _collector is None:
        _collector = SlackCollector()
    return _collector


@app.get("/")
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/api/channels")
async def list_channels():
    """Lists all Slack channels the bot has access to."""
    try:
        collector = get_collector()
        response = collector.client.conversations_list(
            types="public_channel,private_channel",
            limit=200
        )
        channels = []
        for ch in response.get("channels", []):
            channels.append({
                "id": ch["id"],
                "name": ch["name"],
                "num_members": ch.get("num_members", 0),
                "is_private": ch.get("is_private", False),
            })
        # Sort by name
        channels.sort(key=lambda c: c["name"])
        return JSONResponse(content={"channels": channels})
    except Exception as e:
        print(f"Error listing channels: {e}")
        return JSONResponse(
            content={"error": str(e), "channels": []},
            status_code=500
        )


@app.get("/api/channel/{channel_id}/messages")
async def get_channel_messages(channel_id: str):
    """Returns raw normalized messages from a specific channel."""
    try:
        collector = get_collector()
        messages = collector.collect([channel_id])

        # Build a clean response with the messages
        msg_list = []
        for m in messages:
            msg_list.append({
                "user": m.get("user_name", "Unknown"),
                "text": m.get("text_clean", ""),
                "stress_score": m.get("stress_score", 0),
                "timestamp": m.get("timestamp", ""),
                "reactions": m.get("reactions", []),
                "is_thread": m.get("is_thread", False),
            })

        return JSONResponse(content={
            "channel_id": channel_id,
            "count": len(msg_list),
            "messages": msg_list,
        })
    except Exception as e:
        print(f"Error fetching messages for {channel_id}: {e}")
        return JSONResponse(
            content={"error": str(e), "messages": []},
            status_code=500
        )


@app.get("/api/channel/{channel_id}/analyze")
async def analyze_channel(channel_id: str):
    """Full analysis of a specific channel — metrics + Gemini insights."""
    try:
        collector = get_collector()
        messages = collector.collect([channel_id])

        if not messages:
            return JSONResponse(content={
                "total_messages": 0,
                "unique_users": 0,
                "burnout_score": 0,
                "stress_ratio": 0,
                "after_hours_ratio": 0,
                "sentiment_share": {"positive": 0, "neutral": 0, "negative": 0,
                                     "positive_pct": 0, "neutral_pct": 0, "negative_pct": 0},
                "emotion_counts": {"Anger": 0, "Joy": 0, "Love": 0, "Sadness": 0, "Fear": 0, "Stress": 0},
                "weekly_stress": {"labels": [], "values": []},
                "sentiment_over_time": {"labels": [], "positive": [], "neutral": [], "negative": []},
                "similar_comments": [],
                "gemini_analysis": None,
                "messages": [],
            })

        engine = MetricsEngine(messages)

        # Try Gemini analysis
        gemini_text = None
        try:
            insights_engine = InsightsEngine(engine, messages)
            context = insights_engine.build_context()
            gemini = GeminiAnalyzer()
            gemini_text = gemini.analyze(context)
        except Exception as ge:
            print(f"Gemini analysis skipped: {ge}")

        # Build message list for the UI
        msg_list = []
        for m in messages:
            msg_list.append({
                "user": m.get("user_name", "Unknown"),
                "text": m.get("text_clean", ""),
                "stress_score": m.get("stress_score", 0),
                "timestamp": m.get("timestamp", ""),
                "reactions": m.get("reactions", []),
                "is_thread": m.get("is_thread", False),
            })

        return JSONResponse(content={
            "total_messages": engine.total_messages(),
            "unique_users": engine.unique_users(),
            "burnout_score": engine.burnout_score(),
            "stress_ratio": round(engine.stress_ratio(), 4),
            "after_hours_ratio": round(engine.after_hours_ratio(), 4),
            "sentiment_share": engine.sentiment_share(),
            "emotion_counts": engine.emotion_counts(),
            "weekly_stress": engine.weekly_stress_trend(),
            "sentiment_over_time": engine.sentiment_over_time(),
            "similar_comments": engine.similar_comments(),
            "gemini_analysis": gemini_text,
            "messages": msg_list,
        })
    except Exception as e:
        print(f"Error analyzing channel {channel_id}: {e}")
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )


# Keep legacy endpoint for backward compat
@app.get("/api/data")
async def get_data():
    """Legacy endpoint — analyzes first available channel."""
    try:
        collector = get_collector()
        response = collector.client.conversations_list(
            types="public_channel,private_channel"
        )
        channels = response.get("channels", [])
        if not channels:
            return JSONResponse(content={"error": "No channels found"}, status_code=404)

        # Redirect to channel-specific analysis
        first_channel = channels[0]["id"]
        return await analyze_channel(first_channel)
    except Exception as e:
        print(f"Error in /api/data: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)