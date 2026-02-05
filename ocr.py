import logging
import easyocr
from .managers import DeviceManager

logger = logging.getLogger(__name__)

class OCRManager:
    def __init__(self, lang_list=["es"]):
        self.lang_list = lang_list
        self._reader = None

    @property
    def reader(self):
        if self._reader is None:
            logger.info("OCRManager: Initializing EasyOCR...")
            device = DeviceManager.get_device()
            # EasyOCR expects gpu=True/False, generally doesn't support MPS natively as easily as PyTorch,
            # but we pass gpu=True if cuda. For MPS we might need to rely on CPU fallback or test support.
            # EasyOCR logic: gpu=True uses CUDA.
            use_gpu = (device == "cuda")
            self._reader = easyocr.Reader(self.lang_list, gpu=use_gpu)
            logger.info("OCRManager: Initialized.")
        return self._reader

    def extract_text(self, image_path: str) -> str:
        try:
            results = self.reader.readtext(image_path, detail=1, paragraph=False)
            if not results:
                return ""
            
            # results is list of (bbox, text, prob)
            texts = [item[1] for item in results]
            return "\n".join(texts).strip()
        except Exception as e:
            logger.error(f"OCRManager: Error extracting text from {image_path}: {e}")
            return ""
