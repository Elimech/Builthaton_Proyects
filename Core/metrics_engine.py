class MetricsEngine:
    def __init__(self, messages):
        self.messages = messages

    def total_messages(self):
        return len(self.messages)

    def unique_users(self):
        return len(set(m["user_name"] for m in self.messages))
    
    def stress_ratio(self):
        if not self.messages:
            return 0

        stressed = sum(m["stress_score"] for m in self.messages)
        return stressed / len(self.messages)

    def after_hours_ratio(self):
        if not self.messages:
            return 0

        after_hours = sum(
            1 for m in self.messages
            if m["time_data"]["hour"] < 8 or m["time_data"]["hour"] > 19
        )

        return after_hours / len(self.messages)
    
    def burnout_score(self):
        stress = self.stress_ratio()
        after_hours = self.after_hours_ratio()

        score = (
            0.6 * stress +
            0.4 * after_hours
        )

        return round(score * 100, 2)

    def debug_summary(self):
        return {
            "total_messages": self.total_messages(),
            "unique_users": self.unique_users(),
            "stress_ratio": self.stress_ratio(),
            "after_hours_ratio": self.after_hours_ratio(),
            "burnout_score": self.burnout_score()
        }

    def weekly_stress_trend(self):
        """Groups messages by day and calculates average stress per day."""
        if not self.messages:
            return {"labels": [], "values": []}

        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        stress_by_day = {day: [] for day in days}

        for m in self.messages:
            day_idx = m["time_data"].get("day")
            if day_idx is not None and 0 <= day_idx < 7:
                stress_by_day[days[day_idx]].append(m["stress_score"])

        labels = []
        values = []
        for day in days:
            scores = stress_by_day[day]
            if scores:
                labels.append(day)
                values.append(sum(scores) / len(scores))

        return {"labels": labels, "values": values}

    def similar_comments(self):
        """Returns actual messages that have a high stress score."""
        # Sort by stress score and return top stressed comments
        stressed_messages = sorted(
            [m for m in self.messages if m["stress_score"] > 0],
            key=lambda x: x["stress_score"],
            reverse=True
        )
        return [m["text_clean"] for m in stressed_messages[:5]]

    def sentiment_share(self):
        """Categorizes messages into positive/neutral/negative by stress score."""
        if not self.messages:
            return {"positive": 0, "neutral": 0, "negative": 0}

        positive = sum(1 for m in self.messages if m["stress_score"] == 0)
        negative = sum(1 for m in self.messages if m["stress_score"] >= 0.5)
        neutral = len(self.messages) - positive - negative

        total = len(self.messages)
        return {
            "positive": positive,
            "neutral": neutral,
            "negative": negative,
            "positive_pct": round(positive / total * 100, 1) if total else 0,
            "neutral_pct": round(neutral / total * 100, 1) if total else 0,
            "negative_pct": round(negative / total * 100, 1) if total else 0,
        }

    def emotion_counts(self):
        """Scans messages for emotion keyword groups and returns counts."""
        emotion_keywords = {
            "Anger": ["angry", "furious", "rage", "hate", "puto", "matar", "escopetazo"],
            "Joy": ["happy", "great", "awesome", "love", "animos", "listos", "genial", "feliz", "bien"],
            "Love": ["love", "care", "appreciate", "gracias", "abrazo", "cariño"],
            "Sadness": ["sad", "depressed", "lonely", "llore", "triste", "mal", "terrible"],
            "Fear": ["fear", "afraid", "scared", "worried", "miedo", "preocupado"],
            "Stress": ["stress", "estrés", "estres", "cansado", "mamado", "agotado", "urgent", "deadline"],
        }

        counts = {emotion: 0 for emotion in emotion_keywords}
        for m in self.messages:
            text_lower = m.get("text_clean", "").lower()
            for emotion, keywords in emotion_keywords.items():
                for keyword in keywords:
                    if keyword in text_lower:
                        counts[emotion] += 1
                        break  # Count each message only once per emotion

        return counts

    def sentiment_over_time(self):
        """Groups sentiment by day of week for multi-line chart."""
        if not self.messages:
            return {"labels": [], "positive": [], "neutral": [], "negative": []}

        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        sentiment_by_day = {day: {"positive": 0, "neutral": 0, "negative": 0} for day in days}

        for m in self.messages:
            day_idx = m["time_data"].get("day")
            if day_idx is not None and 0 <= day_idx < 7:
                day = days[day_idx]
                if m["stress_score"] == 0:
                    sentiment_by_day[day]["positive"] += 1
                elif m["stress_score"] >= 0.5:
                    sentiment_by_day[day]["negative"] += 1
                else:
                    sentiment_by_day[day]["neutral"] += 1

        active_days = [d for d in days if any(sentiment_by_day[d].values())]
        return {
            "labels": active_days,
            "positive": [sentiment_by_day[d]["positive"] for d in active_days],
            "neutral": [sentiment_by_day[d]["neutral"] for d in active_days],
            "negative": [sentiment_by_day[d]["negative"] for d in active_days],
        }
