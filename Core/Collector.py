import os
import ssl
import certifi
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from Core.normalizer import normalize_message
from Core.debug_utils import DebugManager


class SlackCollector:
    def __init__(self):
        self.token = os.environ.get("SLACK_BOT_TOKEN")
        if not self.token:
            raise RuntimeError("SLACK_BOT_TOKEN not set.")

        # Create SSL context to avoid certificate errors
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        self.client = WebClient(token=self.token, ssl=ssl_context)
        self.user_cache = {}

    def resolve_user(self, user_id: str) -> str:
        """
        Resolves a Slack User ID to a Real Name using an internal cache.
        """
        if not user_id:
            return "Unknown"
        
        if user_id in self.user_cache:
            return self.user_cache[user_id]

        try:
            response = self.client.users_info(user=user_id)
            user_info = response.get("user", {})
            real_name = user_info.get("real_name") or user_info.get("name") or "Unknown"
            self.user_cache[user_id] = real_name
            return real_name
        except SlackApiError as e:
            print(f"Error resolving user {user_id}: {e}")
            return "Unknown"

    def collect(self, channel_ids: list[str]) -> list[dict]:
        """
        Collects messages from a list of channels, including threads.
        Returns a list of normalized message dictionaries.
        """
        all_messages = []

        for channel_id in channel_ids:
            print(f"Collecting from channel: {channel_id}")
            try:
                channel_msgs = self._collect_channel(channel_id)
                all_messages.extend(channel_msgs)
            except Exception as e:
                print(f"Failed to collect from {channel_id}: {e}")

        # Post-process to resolve user names
        for msg in all_messages:
            if msg.get("user_id"):
                msg["user_name"] = self.resolve_user(msg["user_id"])
        
        return all_messages

    def _collect_channel(self, channel_id: str) -> list[dict]:
        messages = []
        cursor = None

        while True:
            try:
                response = self.client.conversations_history(
                    channel=channel_id,
                    cursor=cursor,
                    limit=100 # Reasonable batch size
                )
            except SlackApiError as e:
                print(f"Error fetching history for {channel_id}: {e}")
                break

            for msg in response.get("messages", []):
                # normalize first to filter out unwanted types
                normalized = normalize_message(msg, channel_id)
                if normalized:
                    messages.append(normalized)

                    # Check for threads
                    if normalized["reply_count"] > 0:
                        thread_messages = self._collect_thread(channel_id, normalized["message_id"])
                        messages.extend(thread_messages)

            cursor = response.get("response_metadata", {}).get("next_cursor")
            if not cursor:
                break
        
        return messages

    def _collect_thread(self, channel_id: str, thread_ts: str) -> list[dict]:
        messages = []
        cursor = None
        
        while True:
            try:
                response = self.client.conversations_replies(
                    channel=channel_id,
                    ts=thread_ts,
                    cursor=cursor,
                    limit=100
                )
            except SlackApiError as e:
                print(f"Error fetching replies for {channel_id}/{thread_ts}: {e}")
                break

            for msg in response.get("messages", []):
                # Skip the parent message if it's returned in replies (Slack usually includes it)
                if msg["ts"] == thread_ts:
                    continue

                normalized = normalize_message(msg, channel_id)
                if normalized:
                    messages.append(normalized)
                DebugManager.log("COLLECTED RAW MESSAGES", messages[:2])

            cursor = response.get("response_metadata", {}).get("next_cursor")
            if not cursor:
                break

        return messages

