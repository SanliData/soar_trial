"""
SERVICE: web_acquisition
PURPOSE: Web acquisition service for async web scraping/enrichment
ENCODING: UTF-8 WITHOUT BOM
"""

from src.services.web_acquisition.interfaces import (
    AcquisitionJobRequest,
    AcquisitionJobResult,
    CoverageReport
)
from src.services.web_acquisition.service import get_acquisition_service

__all__ = [
    "AcquisitionJobRequest",
    "AcquisitionJobResult",
    "CoverageReport",
    "get_acquisition_service",
]
