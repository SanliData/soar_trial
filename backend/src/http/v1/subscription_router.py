"""
ROUTER: subscription_router
PURPOSE: Subscription and payment endpoints
ENCODING: UTF-8 WITHOUT BOM
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from src.models.user import User
from src.models.user_account import UserAccount
from src.db.base import get_db
from src.services.auth_service import get_current_user_dependency, get_current_user_impl, is_admin_email
from src.services.payment_service import get_payment_service
from src.services.usage_based_pricing_service import get_usage_based_pricing_service

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


# Helper function to get current user (optional: from Authorization Bearer token)
def get_current_user_from_header(
    authorization: Optional[str] = Header(None, alias="Authorization"),
    db: Session = Depends(get_db)
):
    """Optional user from Authorization: Bearer <jwt>. Returns None if no header or invalid."""
    if authorization and authorization.strip():
        try:
            return get_current_user_impl(authorization=authorization, db=db)
        except Exception:
            return None
    return None


class SubscriptionCreate(BaseModel):
    plan_type: str   # "free", "pro", "enterprise"
    billing_cycle: str = "monthly"   # "monthly", "yearly"
    payment_provider: str = "stripe"   # "stripe", "iyzico"
    payment_token: Optional[str] = None   # Payment token from payment provider


@router.get("/plans")
async def get_plans():
    """
    Get available subscription plans and pricing.
    Public endpoint - no authentication required.
    """
    try:
        from src.db.base import SessionLocal
        db = SessionLocal()
        try:
            payment_service = get_payment_service(db)
            data = payment_service.get_plans()
            return JSONResponse(
                content=data,
                headers={"Cache-Control": "no-store, no-cache, must-revalidate"}
            )
        finally:
            db.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting plans: {str(e)}")


@router.get("/current")
async def get_current_subscription(
    user: Optional[User] = Depends(get_current_user_from_header),
    db: Session = Depends(get_db)
):
    """
    Get current user's account state (usage-based pricing).
    Returns account status, activation fee payment, and query cap.
    """
    try:
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")

        # Admin users: no payment/subscription required (app works without payment setup)
        if is_admin_email(getattr(user, "email", None)):
            return {
                "success": True,
                "account": {
                    "account_status": "active",
                    "activation_fee_paid": True,
                    "query_cap": 99999,
                    "admin_override_active": True,
                },
                "pricing_model": "usage_based",
                "subscription": {
                    "plan_type": "usage_based",
                    "status": "active",
                    "billing_mode": "usage_based",
                },
            }

        # Get user account (usage-based)
        account = db.query(UserAccount).filter(UserAccount.user_id == user.id).first()

        if account:
            return {
                "success": True,
                "account": account.to_dict(),
                "pricing_model": "usage_based",
                "subscription": {
                    "plan_type": "usage_based",   # Legacy compatibility
                    "status": account.account_status,
                    "billing_mode": "usage_based"
                }
            }
        else:
            # Default inactive account
            return {
                "success": True,
                "account": {
                    "account_status": "inactive",
                    "activation_fee_paid": False,
                    "query_cap": 100,
                    "admin_override_active": False
                },
                "pricing_model": "usage_based",
                "subscription": {
                    "plan_type": "usage_based",
                    "status": "inactive",
                    "billing_mode": "usage_based"
                }
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting account: {str(e)}")


@router.post("/create")
async def create_subscription(
    subscription_data: SubscriptionCreate,
    user: Optional[User] = Depends(get_current_user_from_header),
    db: Session = Depends(get_db)
):
    """
    Create or update a subscription for the authenticated user.
    NOTE: Payment APIs (Stripe/Iyzico) are currently disabled. Only free plan is available.
    """
    try:
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Payment APIs are disabled - only free plan is available
        if subscription_data.plan_type != "free":
            raise HTTPException(
                status_code=503,
                detail="Payment APIs (Stripe/Iyzico) are currently disabled. Only free plan is available."
            )
        
        payment_service = get_payment_service(db)
        result = payment_service.create_subscription(
            user_id=user.id,
            plan_type="free",   # Force free plan
            billing_cycle="monthly",   # Ignored for free plan
            payment_provider="none",   # No payment provider
            payment_token=None   # No payment token
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to create subscription"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating subscription: {str(e)}")


@router.post("/cancel")
async def cancel_subscription(
    user: Optional[User] = Depends(get_current_user_from_header),
    db: Session = Depends(get_db)
):
    """
    Cancel the current user's subscription.
    """
    try:
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        payment_service = get_payment_service(db)
        result = payment_service.cancel_subscription(user.id)
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to cancel subscription"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cancelling subscription: {str(e)}")


@router.get("/pricing/calculate")
async def calculate_query_cost(
    include_persona_deepening: bool = False,
    include_visit_route: bool = False,
    include_export: bool = False,
    include_outreach_preparation: bool = False,
    max_results: int = 100,
    db: Session = Depends(get_db)
):
    """
    Calculate cost for a query execution with optional modules.
    Returns signed quote_token required for query execution.
    Public endpoint - no authentication required.
    
    Query Parameters:
    - include_persona_deepening: Include persona deepening module
    - include_visit_route: Include visit route module
    - include_export: Include export module
    - include_outreach_preparation: Include outreach preparation module
    - max_results: Maximum results requested (default: 100, max: 100)
    
    Returns:
    - cost: Cost breakdown
    - quote_token: Signed token required for query execution
    - expires_at: Token expiration timestamp
    """
    try:
        from src.core.query_limits import MAX_RESULTS_PER_QUERY
        
        # Enforce max_results cap
        if max_results > MAX_RESULTS_PER_QUERY:
            raise HTTPException(
                status_code=400,
                detail=f"max_results ({max_results}) exceeds maximum allowed ({MAX_RESULTS_PER_QUERY})"
            )
        
        pricing_service = get_usage_based_pricing_service(db)
        result = pricing_service.calculate_query_cost_with_quote(
            include_persona_deepening=include_persona_deepening,
            include_visit_route=include_visit_route,
            include_export=include_export,
            include_outreach_preparation=include_outreach_preparation,
            max_results=max_results
        )
        
        return {
            "success": True,
            "cost": {
                "base_query": result["base_query"],
                "optional_modules": result["optional_modules"],
                "total_optional": result["total_optional"],
                "total_cost": result["total_cost"],
                "currency": result["currency"],
                "max_results": result["max_results"],
                "breakdown": result["breakdown"]
            },
            "quote_token": result["quote_token"],
            "expires_at": result["expires_at"],
            "request_fingerprint": result["request_fingerprint"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating cost: {str(e)}")


@router.get("/pricing/model")
async def get_pricing_model(db: Session = Depends(get_db)):
    """
    Get complete usage-based pricing model.
    Public endpoint - no authentication required.
    """
    try:
        pricing_service = get_usage_based_pricing_service(db)
        return {
            "success": True,
            "pricing": pricing_service.get_pricing_model()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting pricing model: {str(e)}")


@router.get("/pricing/estimate")
async def estimate_monthly_cost(
    estimated_queries: int,
    avg_optional_modules: Optional[str] = None,   # Comma-separated list
    db: Session = Depends(get_db)
):
    """
    Estimate monthly cost based on expected usage.
    Public endpoint - no authentication required.
    """
    try:
        pricing_service = get_usage_based_pricing_service(db)
        modules_list = []
        if avg_optional_modules:
            modules_list = [m.strip() for m in avg_optional_modules.split(",")]
        
        estimate = pricing_service.estimate_monthly_cost(
            estimated_queries_per_month=estimated_queries,
            avg_optional_modules=modules_list
        )
        return {
            "success": True,
            "estimate": estimate
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error estimating cost: {str(e)}")


@router.get("/health")
def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "domain": "subscriptions"
    }


