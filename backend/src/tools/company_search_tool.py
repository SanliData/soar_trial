"""
TOOLS: company_search_tool
PURPOSE: MCP-ready company search — run(input) -> dict; simulates MCP server
"""
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def run(input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Search companies by industry, location. MCP-ready interface.
    Later can delegate to real MCP company search server.
    """
    industry = input.get("industry", "")
    location = input.get("location", "")
    limit = int(input.get("limit", 20))
    companies: List[Dict[str, Any]] = [
        {"name": f"Example {industry} Co", "website": "https://example.com", "location": location},
        {"name": f"{location} {industry} LLC", "website": "https://example-llc.com", "location": location},
    ]
    companies = companies[:limit]
    logger.info("company_search_tool: industry=%s location=%s -> %s", industry, location, len(companies))
    return {"companies": companies, "count": len(companies)}
