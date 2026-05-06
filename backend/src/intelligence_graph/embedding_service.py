"""
INTELLIGENCE GRAPH: embedding_service
PURPOSE: OpenAI (or local) embeddings for company similarity search
"""
import logging
import os
from typing import List, Optional

logger = logging.getLogger(__name__)

_OPENAI_AVAILABLE = False
try:
    import openai
    _OPENAI_AVAILABLE = True
except ImportError:
    openai = None


async def get_embedding(text: str) -> Optional[List[float]]:
    """Return embedding vector for text (OpenAI text-embedding-3-small or similar)."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or not _OPENAI_AVAILABLE:
        return None
    try:
        client = openai.OpenAI(api_key=api_key)
        resp = client.embeddings.create(
            model="text-embedding-3-small",
            input=text[:8000],
        )
        return resp.data[0].embedding
    except Exception as e:
        logger.warning("embedding_service get_embedding failed: %s", e)
        return None


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Cosine similarity between two vectors."""
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)
