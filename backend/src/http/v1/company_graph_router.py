import logging
from fastapi import APIRouter, HTTPException
from src.company_graph.graph_query_engine import get_company_node, get_company_contacts
from src.company_graph.similarity_engine import find_similar_companies
from src.company_graph.graph_store import refresh_graph

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/graph", tags=["company-graph"])


@router.get("/company/{id}")
async def get_company(id: int):
    node = get_company_node(id)
    if not node:
        raise HTTPException(status_code=404, detail="Company not found")
    contacts = get_company_contacts(id)
    return {"company": node, "contacts": contacts}


@router.get("/similar/{id}")
async def get_similar(id: int, limit: int = 10):
    return find_similar_companies(company_id=id, limit=limit)


@router.post("/refresh")
async def refresh():
    try:
        g = refresh_graph()
        return {"ok": True, "nodes": len(g.get("nodes", [])), "edges": len(g.get("edges", []))}
    except Exception as e:
        logger.exception("graph refresh: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
