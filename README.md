**Employee Engagement** is an analytics dashboard that connects to your Slack workspace, collects messages, and analyzes the **emotional climate** of your team in real time. It calculates stress scores, detects emotions, and uses **Google Gemini AI** to generate organizational psychology insights.

### Key Questions It Answers:
- 🔴 **Is my team burning out?** — Burnout score based on stress + after-hours activity
- 😊 **What's the emotional mood?** — Sentiment breakdown (positive/neutral/negative)
- 📊 **When is stress highest?** — Weekly stress trends by day
- 🗣️ **What are people saying?** — Read actual messages with stress indicators
- 🤖 **What should leadership do?** — AI-generated recommendations

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📡 **Slack Integration** | Connects to your workspace, lists channels, collects messages + threads |
| 🎯 **Stress Scoring** | Heuristic NLP detects stress keywords in English and Spanish |
| 🍩 **Sentiment Donut** | Visual breakdown of positive, neutral, and negative messages |
| 📈 **Trend Charts** | Sentiment over time + weekly stress trend with gradient fills |
| 😤 **Emotion Detection** | Tracks Anger, Joy, Love, Sadness, Fear, and Stress across messages |
| 🤖 **Gemini AI Analysis** | Deep organizational psychology report with actionable insights |
| 💬 **Message Reader** | Browse real messages with user avatars, timestamps, and stress badges |
| 🌙 **Dark Theme UI** | Premium dark dashboard inspired by Hootsuite Listening |
| ⚡ **Animated KPIs** | Count-up animations on key metrics |

---

## 🏗️ Architecture

```
Employee_Engagement/
├── Core/                      # Backend logic
│   ├── Collector.py           # Slack API — message collection + threads
│   ├── normalizer.py          # Text cleaning + stress score calculation
│   ├── metrics_engine.py      # KPIs, sentiment, emotions, trends
│   ├── insights_engine.py     # Context builder for Gemini
│   ├── gemini_analyzer.py     # Google Gemini AI integration
│   ├── debug_utils.py         # Debug logging utility
│   └── test_connection.py     # CLI pipeline test
│
├── UI/                        # Frontend
│   ├── app.py                 # FastAPI server + API endpoints
│   ├── templates/
│   │   └── dashboard.html     # Main dashboard template
│   └── static/
│       ├── style.css          # Dark theme design system (900+ lines)
│       └── dashboard.js       # Charts, data loading, view management
│
├── .env                       # API keys (not committed)
└── requirements.txt           # Python dependencies
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Dashboard UI |
| `GET` | `/api/channels` | List all Slack channels |
| `GET` | `/api/channel/{id}/analyze` | Full analysis of a channel (metrics + AI) |
| `GET` | `/api/channel/{id}/messages` | Raw messages from a channel |
| `GET` | `/api/data` | Legacy — analyzes first available channel |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- A [Slack Bot Token](https://api.slack.com/apps) with scopes: `channels:history`, `channels:read`, `groups:read`, `groups:history`, `users:read`
- A [Google Gemini API Key](https://ai.google.dev) (optional, for AI insights)

### 1. Clone the repo

```bash
git clone https://github.com/your-username/Employee_Engagement.git
cd Employee_Engagement/Employee_Engagement
```

### 2. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install fastapi uvicorn jinja2 python-dotenv slack_sdk google-genai
```

### 4. Configure environment variables

Create a `.env` file in the `Employee_Engagement/` directory:

```env
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
GEMINI_API_KEY=your-gemini-api-key
```

### 5. Test the pipeline (optional)

```bash
python -m Core.test_connection
```

### 6. Launch the dashboard

```bash
uvicorn UI.app:app --reload
```

Open **http://localhost:8000** in your browser.

---

## 🖥️ Dashboard Views

### 📊 Sentiment View
> KPI metrics, sentiment donut chart, sentiment over time, emotion bar chart, stress trend line, and high-stress comments.

### 💬 Messages View
> Browse all messages in a channel with user names, stress scores (color-coded), timestamps, thread indicators, and reactions.

### 🤖 AI Insights View
> Gemini-generated organizational psychology report covering emotional climate, burnout risk, communication patterns, and leadership recommendations.

---

## 🧮 How Stress Scoring Works

The system uses a **keyword-based heuristic** that supports **English and Spanish**:

```python
# Example stress keywords
"urgent", "deadline", "asap", "error", "fail", "broken",
"cansado", "mamado", "estrés", "urgente", "agotado", "no puedo más"
```

- Each keyword match adds `+0.25` to the score
- Score is capped at `1.0`
- **Burnout Score** = `0.6 × stress_ratio + 0.4 × after_hours_ratio` (scale 0–100)

### Sentiment Classification
| Stress Score | Sentiment |
|-------------|-----------|
| `0.0` | ✅ Positive |
| `0.01 – 0.49` | ⚠️ Neutral |
| `≥ 0.50` | 🔴 Negative |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.11, FastAPI, Uvicorn |
| **Slack API** | `slack_sdk` — messages, threads, user resolution |
| **AI** | Google Gemini 1.5 Pro (`google-genai`) |
| **Frontend** | HTML5, CSS3, JavaScript (vanilla) |
| **Charts** | Chart.js 4.4 |
| **Typography** | Inter (Google Fonts) |
| **Design** | Dark theme, glassmorphism, CSS animations |

---

## 📄 License

This project is for educational and organizational research purposes.

---

## 👤 Author

**Julian Ramirez**
