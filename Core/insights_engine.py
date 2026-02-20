class InsightsEngine:

    def __init__(self, metrics, messages):
        self.metrics = metrics
        self.messages = messages

    def build_context(self):
        return {
            "total_messages": self.metrics.total_messages(),
            "unique_users": self.metrics.unique_users(),
            "stress_ratio": self.metrics.stress_ratio(),
            "after_hours_ratio": self.metrics.after_hours_ratio(),
            "burnout_score": self.metrics.burnout_score(),
            "recent_messages": self.messages[-5:]
        }
