# src/models/__init__.py
from .base_model import EmoTTSModel
from .emotion_encoder import EmotionEncoder

__all__ = ["EmoTTSModel", "EmotionEncoder"]
__version__ = "0.1.0"