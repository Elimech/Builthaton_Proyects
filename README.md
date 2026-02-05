# Visual Memory 2.0

A modern, AI-powered image search application.
Extracts text (OCR) and descriptions (BLIP) from images to allow semantic search.

## Features
- **Smart Search**: Search by content ("invoice from June", "photo of a dog") not just filename.
- **Modern UI**: Dark-themed, responsive interface built with CustomTkinter.
- **Lazy Loading**: Efficient resource usage; models load only when needed.
- **Caching**: Results are saved to disk (`visual_memory_cache.json`) for instant subsequent loads.
- **Device Auto-detect**: Automatically uses CUDA (NVIDIA), MPS (Mac), or CPU.

## Installation

1.  **Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run**:
    ```bash
    python main.py
    ```

## Structure
- `core/`: modular AI logic (OCR, Vision, Embeddings).
- `ui/`: Interface code.
- `main.py`: Entry point.

## First Run
The first time you process a folder, it will download necessary AI models (~1GB total). This may take a few minutes. Subsequent runs will be faster.
