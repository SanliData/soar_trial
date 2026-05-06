***REMOVED*** -*- coding: utf-8 -*-
"""
B2B Products Router - Product definition and management API endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from pydantic import BaseModel
from backend.services.b2b import product_service, industry_research_service, company_discovery_service

router = APIRouter(prefix="/api/v1/b2b/products", tags=["B2B"])


class ProductCreate(BaseModel):
    user_id: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    metadata: Optional[dict] = None


@router.post("/", response_model=dict)
async def create_product(product_data: ProductCreate):
    """Create new product"""
    try:
        product = product_service.create_product(
            user_id=product_data.user_id,
            name=product_data.name,
            description=product_data.description,
            category=product_data.category,
            subcategory=product_data.subcategory,
            metadata=product_data.metadata
        )
        return product.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{product_id}/understand", response_model=dict)
async def understand_product(product_id: int):
    """Analyze product using AI to understand use cases and target industries"""
    try:
        product = product_service.understand_product(product_id)
        return product.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{product_id}/research-industries", response_model=dict)
async def research_industries(product_id: int):
    """Research which industries use the product"""
    try:
        result = industry_research_service.research_industries_for_product(product_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{product_id}/discover-companies", response_model=dict)
async def discover_companies(
    product_id: int,
    location: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000)
):
    """Automatically discover companies that use the product"""
    try:
        companies = company_discovery_service.discover_companies_for_product(
            product_id=product_id,
            location=location,
            limit=limit
        )
        return {
            "product_id": product_id,
            "discovered": len(companies),
            "companies": [c.to_dict() for c in companies]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{product_id}", response_model=dict)
async def get_product(product_id: int):
    """Get product details"""
    product = product_service.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product.to_dict()


@router.get("/", response_model=dict)
async def get_products(user_id: Optional[str] = Query(None)):
    """Get products list"""
    if user_id:
        products = product_service.get_products_by_user(user_id)
    else:
        products = []
    
    return {
        "total": len(products),
        "products": [p.to_dict() for p in products]
    }

