"""
ROUTER: marketplace_seller_router
PURPOSE: API endpoints for online seller discovery (Amazon, eBay, etc.)
ENCODING: UTF-8 WITHOUT BOM
"""

from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Path, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.models.user import User
from src.db.base import get_db
from src.services.auth_service import get_current_user_dependency
from src.services.marketplace_seller_service import MarketplaceSellerService

router = APIRouter(prefix="/marketplace-sellers", tags=["marketplace-sellers"])


***REMOVED*** ============================================================================
***REMOVED*** REQUEST/RESPONSE MODELS
***REMOVED*** ============================================================================

class DiscoverSellersRequest(BaseModel):
    marketplace: str = Field(..., description="Marketplace name: 'amazon', 'ebay', 'etsy', 'ali express', 'trendyol', 'hepsiburada'")
    query: str = Field(..., description="Search query (product category, keywords, etc.)")
    max_results: int = Field(50, ge=1, le=200, description="Maximum number of results")


class MarketplaceSellerResponse(BaseModel):
    id: int
    user_id: int
    marketplace: str
    seller_id: str
    seller_name: str
    seller_profile_url: Optional[str]
    business_name: Optional[str]
    business_registration_number: Optional[str]
    business_address: Optional[str]
    business_location: Optional[dict]
    owner_inference: Optional[dict]
    location_inference_confidence: Optional[float]
    location_signals: Optional[List[str]]
    seller_metadata: Optional[dict]
    status: str
    verification_status: Optional[str]
    created_at: str
    updated_at: str


***REMOVED*** ============================================================================
***REMOVED*** MARKETPLACE SELLER ENDPOINTS
***REMOVED*** ============================================================================

@router.post("/discover", response_model=List[MarketplaceSellerResponse])
async def discover_marketplace_sellers(
    request: DiscoverSellersRequest,
    user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Discover sellers from online marketplaces.
    
    Supported marketplaces:
    - Amazon (seller profiles)
    - eBay (seller profiles)
    - Etsy (shop profiles)
    - AliExpress (store profiles)
    - Trendyol (Turkish marketplace)
    - Hepsiburada (Turkish marketplace)
    """
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    valid_marketplaces = ["amazon", "ebay", "etsy", "ali express", "trendyol", "hepsiburada"]
    if request.marketplace.lower() not in valid_marketplaces:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid marketplace. Must be one of: {', '.join(valid_marketplaces)}"
        )
    
    service = MarketplaceSellerService(db)
    
    try:
        sellers = service.discover_sellers(
            user_id=user.id,
            marketplace=request.marketplace.lower(),
            query=request.query,
            max_results=request.max_results
        )
        
        return [MarketplaceSellerResponse(**seller.to_dict()) for seller in sellers]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error discovering sellers: {str(e)}")


@router.get("/{seller_id}", response_model=MarketplaceSellerResponse)
async def get_marketplace_seller(
    seller_id: int = Path(..., description="Seller ID"),
    user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """Get a specific marketplace seller"""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    service = MarketplaceSellerService(db)
    seller = service.get_seller(user.id, seller_id)
    
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    
    return MarketplaceSellerResponse(**seller.to_dict())


@router.get("", response_model=List[MarketplaceSellerResponse])
async def list_marketplace_sellers(
    marketplace: Optional[str] = Query(None, description="Filter by marketplace"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """List marketplace sellers for the authenticated user"""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    service = MarketplaceSellerService(db)
    sellers = service.list_sellers(user.id, marketplace=marketplace, limit=limit, offset=offset)
    
    return [MarketplaceSellerResponse(**seller.to_dict()) for seller in sellers]


@router.post("/{seller_id}/infer-business", response_model=MarketplaceSellerResponse)
async def infer_business_entity(
    seller_id: int = Path(..., description="Seller ID"),
    user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Infer business entity information from seller data.
    
    Uses:
    - Seller profile information
    - Public records
    - Website scraping
    - Social media profiles
    """
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    service = MarketplaceSellerService(db)
    
    ***REMOVED*** Verify seller belongs to user
    seller = service.get_seller(user.id, seller_id)
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    
    try:
        updated_seller = service.infer_business_entity(seller_id)
        return MarketplaceSellerResponse(**updated_seller.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inferring business entity: {str(e)}")


@router.post("/{seller_id}/infer-owner", response_model=MarketplaceSellerResponse)
async def infer_owner(
    seller_id: int = Path(..., description="Seller ID"),
    user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Infer owner information from seller data.
    
    Uses:
    - Business registration records
    - Website contact information
    - LinkedIn profiles
    - Social media profiles
    """
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    service = MarketplaceSellerService(db)
    
    ***REMOVED*** Verify seller belongs to user
    seller = service.get_seller(user.id, seller_id)
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    
    try:
        updated_seller = service.infer_owner(seller_id)
        return MarketplaceSellerResponse(**updated_seller.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inferring owner: {str(e)}")


@router.post("/{seller_id}/extract-location", response_model=MarketplaceSellerResponse)
async def extract_location_signals(
    seller_id: int = Path(..., description="Seller ID"),
    user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """Extract location signals from seller data"""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    service = MarketplaceSellerService(db)
    
    ***REMOVED*** Verify seller belongs to user
    seller = service.get_seller(user.id, seller_id)
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    
    try:
        updated_seller = service.extract_location_signals(seller_id)
        return MarketplaceSellerResponse(**updated_seller.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting location signals: {str(e)}")
