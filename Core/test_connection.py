import os
import sys
from dotenv import load_dotenv

# Find .env in the parent directory of 'Core'
lib_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(lib_dir)
env_path = os.path.join(project_root, '.env')
load_dotenv(env_path)
from Core.metrics_engine import MetricsEngine  
from Core.Collector import SlackCollector
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from Core.debug_utils import DebugManager
from Core.insights_engine import InsightsEngine
from Core.gemini_analyzer import GeminiAnalyzer

# Ensure SLACK_BOT_TOKEN is available
if not os.environ.get("SLACK_BOT_TOKEN"):
    print("Error: SLACK_BOT_TOKEN not found in environment variables.")
    # Attempt to load from file if present (ad-hoc fix for local testing if needed)
    # But better to rely on env vars.
    pass

def test_pipeline():
    print("\n=== INITIALIZING PIPELINE ===")
    try:
        collector = SlackCollector()
    except Exception as e:
        print(f"Failed to initialize Collector: {e}")
        return

    # 1. Test Auth
    print("\n--- Testing Auth ---")
    try:
        auth = collector.client.auth_test()
        print(f"Bot User: {auth['user']}")
        print(f"Team: {auth['team']}")
    except SlackApiError as e:
        print(f"Auth failed: {e}")
        return

    # 2. List Channels to find a target
    print("\n--- Finding Channels ---")
    channels = []
    try:
        response = collector.client.conversations_list(types="public_channel,private_channel")
        channels = response["channels"]
        print(f"Found {len(channels)} channels.")
        for ch in channels[:5]: # Show first 5
            print(f" - {ch['name']} ({ch['id']})")
    except SlackApiError as e:
        print(f"Failed to list channels: {e}")
        return

    if not channels:
        print("No channels found. Exiting.")
        return

    target_channel_id = channels[0]["id"]
    print(f"\n--- Collecting from {target_channel_id} ---")

    # 3. Collect & Normalize
    messages = collector.collect([target_channel_id])
    print(f"Collected {len(messages)} normalized messages.")

    if not messages:
        print("No messages to analyze.")
        return

    # 4. Analyze
    print("\n--- Running Metrics Engine ---")
    engine = MetricsEngine(messages)
    insights_engine = InsightsEngine(engine, messages)

    context = insights_engine.build_context()
    print("\n--- Running Gemini Analysis ---")

    gemini = GeminiAnalyzer()

    try:
        analysis = gemini.analyze(context)
        print("\n--- Gemini Report ---")
        print(analysis)
    except Exception as e:
        print(f"Gemini Analysis Failed: {e}")
    DebugManager.log("INSIGHTS CONTEXT", context)
    print(f"Total Messages: {engine.total_messages()}")
    print(f"Unique Users: {engine.unique_users()}")
    print(f"Stress Ratio: {engine.stress_ratio():.2f}")
    print(f"After Hours Ratio: {engine.after_hours_ratio():.2f}")
    print(f"Burnout Score: {engine.burnout_score()}")
    DebugManager.log("METRICS SUMMARY", engine.debug_summary())
    print("\n--- Insights Context ---")
    print(context)

    # 5. Show sample data
    print("\n--- Sample Message Data ---")
    sample = messages[0]
    print(f"User: {sample['user_name']}")
    print(f"Text: {sample['text_clean'][:50]}...")
    print(f"Stress: {sample['stress_score']}")
    print(f"Time: {sample['timestamp']}")
    return {
        "total_messages": engine.total_messages(),
        "unique_users": engine.unique_users(),
        "burnout_score": engine.burnout_score(),
        "weekly_stress": engine.weekly_stress_trend(),
        "similar_comments": engine.similar_comments()
    }


if __name__ == "__main__":
    print("\n=== TESTING PIPELINE ===")
    test_pipeline()
