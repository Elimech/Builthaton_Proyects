

🪄 Transcription & Slide Creator
This project is an AI-powered web application that transforms audio files or real-time recordings into fully structured PowerPoint presentations and PDF documents.

It leverages OpenAI Whisper for high-accuracy transcription and Google Gemini 2.0 Flash for intelligent content generation and speaker notes.

🚀 Features

Live Recording: Capture audio directly from your browser using a built-in recorder.


File Uploads: Supports mp3, mp4, wav, m4a, and opus formats.


Automatic Transcription: Audio processing powered by the Whisper base model.


Generative AI Slides: Automatically creates titles, bullet points, and detailed speaker notes.


Language Enforcement: The AI identifies the source language and generates all content in that same language.


Multi-Format Export: Download your results as .pptx (PowerPoint) or .pdf files.

🛠️ Technologies Used

Frontend: Streamlit 


AI Models: * OpenAI Whisper: For speech-to-text transcription.


Google Gemini 2.0 Flash: For slide structuring and content synthesis.

Document Processing:


python-pptx: For PowerPoint generation.


reportlab: For PDF creation.


Audio Engine: ffmpeg (system-level).

📦 Local Installation
To run this project locally, follow these steps:

Clone the repository:

Bash
git clone https://github.com/your-username/transcription-slide-creator.git
cd transcription-slide-creator
Install System Dependencies: You must have ffmpeg installed to process audio.

Ubuntu/Debian: sudo apt update && sudo apt install ffmpeg

MacOS: brew install ffmpeg

Install Python Libraries:

Bash
pip install -r requirements.txt
Set Up API Keys: Create a .streamlit/secrets.toml file in the root directory:

Ini, TOML
API_KEY = "YOUR_GEMINI_API_KEY_HERE"
Run the App:

Bash
streamlit run Main.py
☁️ Deployment on Streamlit Cloud
This application is ready to be hosted on Streamlit Cloud. Follow these steps:

Push your code to a GitHub repository.

Log in to Streamlit Cloud.

Click "New app" and select your repository and the Main.py file.

Important - Secrets Configuration:

In the Advanced settings menu, find the Secrets field.

Paste your Google API Key there:

Ini, TOML
API_KEY = "your_actual_gemini_api_key"

System Dependencies: Streamlit will automatically detect the packages.txt file and install ffmpeg for you.

Click Deploy and your AI tool will be live!

📝 Structure & Logic
The app uses a strict prompt engineering approach to ensure that:

The output language matches the audio transcript exactly.

Slide content and speaker notes are clearly separated using custom regex patterns.

A minimum of 5 slides are generated if clear instructions are detected in the audio.
