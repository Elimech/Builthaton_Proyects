import logging
from sentence_transformers import SentenceTransformer
from .managers import DeviceManager

logger = logging.getLogger(__name__)

class EmbeddingManager:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None

    @property
    def model(self):
        if self._model is None:
            logger.info(f"EmbeddingManager: Loading SentenceTransformer '{self.model_name}'...")
            device = DeviceManager.get_device()
            # SentenceTransformer handles 'mps', 'cuda', 'cpu' strings correctly usually
            self._model = SentenceTransformer(self.model_name, device=device)
            logger.info("EmbeddingManager: Loaded.")
        return self._model

    def encode(self, text: str):
        try:
            # normalize_embeddings=True for cosine similarity
            return self.model.encode(text, normalize_embeddings=True)
        except Exception as e:
            logger.error(f"EmbeddingManager: Error encoding text: {e}")
            return None
