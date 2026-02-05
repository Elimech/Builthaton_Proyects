import logging
import time
from pathlib import Path
from typing import List, Dict, Any, Callable
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from .managers import CacheManager
from .ocr import OCRManager
from .vision import VisionManager
from .embedding import EmbeddingManager

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self):
        self.ocr_manager = OCRManager()
        self.vision_manager = VisionManager()
        self.embedding_manager = EmbeddingManager()
        self.cache_manager = None
        self.current_results = []

    def process_folder(self, folder_path: Path, progress_callback: Callable[[int, int], None] = None) -> List[Dict[str, Any]]:
        self.cache_manager = CacheManager(folder_path)
        cached_data = self.cache_manager.load_cache()
        
        # Index cached files
        cached_map = {item["file"]: item for item in cached_data}
        
        image_extensions = {".png", ".jpg", ".jpeg", ".bmp", ".tiff"}
        image_paths = [
            p for p in folder_path.iterdir()
            if p.suffix.lower() in image_extensions
        ]
        
        results = []
        total = len(image_paths)
        
        for i, image_path in enumerate(image_paths, start=1):
            file_str = str(image_path.resolve())
            
            # Check cache
            cached_item = cached_map.get(file_str)
            is_valid_cache = (
                cached_item and 
                cached_item.get("type") != "error" and 
                cached_item.get("description") not in [None, "", "Error generating description."]
            )
            
            if is_valid_cache:
                logger.info(f"Using cached result for {image_path.name}")
                results.append(cached_item)
            else:
                # Process new
                try:
                    logger.info(f"Processing {image_path.name}...")
                    text = self.ocr_manager.extract_text(file_str)
                    description = self.vision_manager.describe_image(file_str)
                    
                    full_text = f"{text}\n{description}".strip()
                    embedding = self.embedding_manager.encode(full_text)
                    
                    # Convert numpy array to list for JSON serialization if necessary, 
                    # but we keep it as list in memory usually for compatibility
                    if hasattr(embedding, "tolist"):
                        embedding = embedding.tolist()
                        
                    item = {
                        "file": file_str,
                        "text": text,
                        "description": description,
                        "embedding": embedding,
                        "type": "image"
                    }
                    results.append(item)
                    
                except Exception as e:
                    logger.error(f"Error processing {image_path.name}: {e}")
                    results.append({
                        "file": file_str,
                        "type": "error",
                        "error": str(e)
                    })
            
            if progress_callback:
                progress_callback(i, total)
        
        self.current_results = results
        self.cache_manager.save_cache(results)
        return results

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if not self.current_results:
            return []
            
        try:
            query_embedding = self.embedding_manager.encode(query)
            if query_embedding is None:
                return []
                
            # Filter valid embeddings
            valid_items = [item for item in self.current_results if item.get("embedding")]
            if not valid_items:
                return []
                
            embeddings = [item["embedding"] for item in valid_items]
            
            scores = cosine_similarity([query_embedding], embeddings)[0]
            
            scored_results = []
            for item, score in zip(valid_items, scores):
                # Create a copy to not mutate original with temporary score
                res = item.copy()
                res["score"] = float(score)
                scored_results.append(res)
                
            scored_results.sort(key=lambda x: x["score"], reverse=True)
            return scored_results[:top_k]
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
