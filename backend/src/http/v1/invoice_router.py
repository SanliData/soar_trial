"""
ROUTER: invoice_router
PURPOSE: Invoice and payment history endpoints
ENCODING: UTF-8 WITHOUT BOM
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from src.models.user import User
from src.models.invoice import Invoice
from src.db.base import get_db
from src.services.auth_service import get_current_user_dependency, get_current_user_impl

router = APIRouter(prefix="/invoices", tags=["invoices"])


# Helper function to get current user
def get_current_user_from_header(
    authorization: str = Depends(lambda: None),
    db: Session = Depends(get_db)
):
    """Helper to inject authorization header into get_current_user_dependency"""
    if authorization:
        return get_current_user_impl(authorization=authorization, db=db)
    return None


class InvoiceListResponse(BaseModel):
    success: bool
    invoices: List[Dict[str, Any]]
    total: int


@router.get("/list", response_model=InvoiceListResponse)
async def get_invoices(
    limit: int = Query(50, description="Maximum number of invoices"),
    user: Optional[User] = Depends(get_current_user_from_header),
    db: Session = Depends(get_db)
):
    """
    Get invoices for the authenticated user.
    """
    try:
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        invoices = db.query(Invoice).filter(
            Invoice.user_id == user.id
        ).order_by(Invoice.created_at.desc()).limit(limit).all()
        
        return InvoiceListResponse(
            success=True,
            invoices=[invoice.to_dict() for invoice in invoices],
            total=len(invoices)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting invoices: {str(e)}")


@router.get("/{invoice_id}")
async def get_invoice(
    invoice_id: int,
    user: Optional[User] = Depends(get_current_user_from_header),
    db: Session = Depends(get_db)
):
    """
    Get a specific invoice by ID.
    """
    try:
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        invoice = db.query(Invoice).filter(
            Invoice.id == invoice_id,
            Invoice.user_id == user.id
        ).first()
        
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        return {
            "success": True,
            "invoice": invoice.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting invoice: {str(e)}")


@router.get("/health")
def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "domain": "invoices"
    }


