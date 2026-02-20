# 📩 AI Inbox Triage Assistant

An intelligent **Streamlit** application that uses **Google Gemini AI** to connect to your Gmail, analyze subject lines, and automatically group them into logical, actionable clusters. Clean your inbox by archiving entire categories with a single click.

---

## ✨ Features
- **AI-Powered Clustering:** Groups emails by context (e.g., Invoices, Social Notifications, Work).
- **Multilingual Support:** Real-time UI and analysis switching between English and Spanish.
- **Direct Action:** Bulk archive emails directly from the app interface.
- **Secure:** Uses `st.secrets` to manage credentials privately.

## 🛠️ Prerequisites

### 1. Google Gemini API Key
Get a free API key at [Google AI Studio](https://aistudio.google.com/).

### 2. Gmail App Password
For security, you cannot use your regular password.
1. Go to your [Google Account](https://myaccount.google.com/).
2. Search for "App Passwords."
3. Create a new one named "Inbox Triage" and copy the 16-character code.

---

## 🚀 Local Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
   cd your-repo-name
Install dependencies:

Bash
pip install -r requirements.txt
Configure Secrets:
Create a folder named .streamlit and inside it, a file named secrets.toml:

Ini, TOML
EMAIL_USER = "your-email@gmail.com"
EMAIL_PASS = "your-16-character-app-password"
GEMINI_API_KEY = "your-gemini-api-key"
Run the App:

Bash
streamlit run triage.py
🔒 Security & Privacy
This project does not store your emails in any external database. The IMAP connection is direct between your environment and Google's servers. Subject lines are sent to the Gemini API solely for the classification process.


---

### 3. Updated `triage.py` (Snippet)
I recommend changing **line 74** of your uploaded file to this to ensure compatibility:

```python
# Change this:
# model = genai.GenerativeModel("models/gemini-2.5-flash")

# To this:
model = genai.GenerativeModel("models/gemini-1.5-flash")
4. File: .gitignore
To prevent accidentally uploading your private passwords to GitHub:

Plaintext
.streamlit/secrets.toml
__pycache__/
.env
