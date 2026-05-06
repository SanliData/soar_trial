"""
DATA GRAPH: company_graph
PURPOSE: Company intelligence graph — industry, location, technologies, projects, contacts.
         Embedding + similarity search ile benzer şirket ve hedef pazar keşfi.
"""
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


async def find_similar_companies(
    company_id: Optional[str] = None,
    industry: Optional[str] = None,
    location: Optional[str] = None,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    """
    Benzer şirketleri döndür (embedding/similarity veya filtre).
    Şu an stub; gerçek impl: vektör DB veya graf sorgusu.
    """
    logger.info("company_graph: find_similar_companies industry=%s location=%s", industry, location)
    return []


async def get_company_context(company_id: str) -> Optional[Dict[str, Any]]:
    """
    Şirket bağlamı: industry, location, technologies, projects.
    Stub; gerçek impl: graf/DB’den okuma.
    """
    return None
