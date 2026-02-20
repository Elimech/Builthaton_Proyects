🕸️ Knowledge Weaver AI
Universal Knowledge-Graph Builder | Buildathon 2026

Knowledge Weaver AI is a powerful prototype designed to transform unstructured information into interactive, navigable, and intelligent knowledge maps. By leveraging the Gemini 2.0/2.5 Flash models, this tool bridges the gap between static reading and deep relational understanding.
Features

    Smart Ingestion: Supports .txt files and live URLs. Our engine cleans HTML noise (ads, scripts, menus) to focus only on valuable content.

    Semantic Mapping: Automatically extracts entities and relationships to build a unified Knowledge Graph.

    Dynamic Visualization: A high-performance, force-directed graph with Dark Mode aesthetics, node-importance scaling, and organic physics.

    Natural Language Q&A: Chat directly with your data. The AI reasons over the graph structure to answer complex questions about the mapped concepts.

    Performance-Ready: Built-in support for different Gemini models to manage API quotas and ensure stability.

🛠️ Tech Stack

    Language: Python 3.13

    AI Engine: Google Generative AI (Gemini Flash & Pro)

    Backend: Flask (Web Framework)

    Graph Logic: NetworkX

    Visualization: Pyvis (JavaScript-based dynamic networks)

    Web Scraping: BeautifulSoup4 & Requests

⚙️ Setup & Installation

    Clone the repository:
    Bash

    git clone <your-repo-link>
    cd knowledge-weaver-ai

    Set up your API Key:
    Export your Google AI Studio API Key to your environment:
    Bash

    export GEMINI_API_KEY="your_api_key_here"

    Install dependencies:
    Bash

    pip install -r requirements.txt

    Run the application:
    Bash

    python app.py

    Open http://127.0.0.1:5000 in your browser.

📖 How to Use

    Ingest: Upload a text file or paste a URL (e.g., a Wikipedia article).

    Visualize: Click "Create Graph". Watch the nodes stabilize and organize themselves.

    Explore: Drag nodes to see their connections. Larger nodes represent more connected (important) concepts.

    Query: Use the "Ask AI" box to ask questions like: "How does concept A influence concept B?"
