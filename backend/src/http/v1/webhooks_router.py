"""
ROUTER: webhooks_router
PURPOSE: Webhook endpoints for external services (Google Ads Lead Forms, etc.)
ENCODING: UTF-8 WITHOUT BOM
"""

import os
import hmac
import hashlib
import json
import logging
from fastapi import APIRouter, Request, HTTPException, Header, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from src.db.base import get_db
from src.services.lead_service import get_lead_service
from src.models.campaign import Campaign
from src.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


class GoogleAdsLeadFormData(BaseModel):
    """Google Ads Lead Form submission data structure."""
    ***REMOVED*** Required fields
    full_name: str
    email: str
    
    ***REMOVED*** Optional fields
    phone: Optional[str] = None
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    message: Optional[str] = None
    
    ***REMOVED*** Google Ads metadata
    google_ads_lead_id: Optional[str] = None
    google_ads_campaign_id: Optional[str] = None
    google_ads_ad_group_id: Optional[str] = None
    google_ads_keyword: Optional[str] = None
    
    ***REMOVED*** Additional form data
    form_data: Optional[Dict[str, Any]] = None


class GoogleAdsWebhookPayload(BaseModel):
    """Google Ads webhook payload structure."""
    ***REMOVED*** Webhook metadata
    webhook_id: Optional[str] = None
    timestamp: Optional[str] = None
    
    ***REMOVED*** Lead data
    lead_data: GoogleAdsLeadFormData
    
    ***REMOVED*** Campaign information
    campaign_id: Optional[int] = None
    user_id: Optional[int] = None


def verify_google_ads_webhook(
    payload: bytes,
    signature: Optional[str] = None,
    secret: Optional[str] = None
) -> bool:
    """
    Verify Google Ads webhook signature.
    Google Ads can send webhooks with HMAC-SHA256 signatures.
    
    Args:
        payload: Raw request payload
        signature: Signature from X-Google-Ads-Signature header
        secret: Webhook secret from environment
    
    Returns:
        True if signature is valid
    """
    if not signature or not secret:
        ***REMOVED*** If no signature/secret configured, allow (for development)
        logger.warning("Webhook signature verification skipped (not configured)")
        return True
    
    try:
        ***REMOVED*** Calculate expected signature
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        ***REMOVED*** Compare signatures (constant-time comparison)
        return hmac.compare_digest(signature, expected_signature)
    except Exception as e:
        logger.error(f"Error verifying webhook signature: {str(e)}")
        return False


@router.post("/google-ads/lead-form")
async def google_ads_lead_form_webhook(
    request: Request,
    x_google_ads_signature: Optional[str] = Header(None, alias="X-Google-Ads-Signature"),
    db: Session = Depends(get_db)
):
    """
    Webhook endpoint for Google Ads Lead Form submissions.
    Receives lead data from Google Ads and creates a Lead record,
    then automatically converts it to an Appointment (Step 11).
    
    Expected payload structure:
    {
        "webhook_id": "...",
        "timestamp": "...",
        "lead_data": {
            "full_name": "...",
            "email": "...",
            "phone": "...",
            "google_ads_lead_id": "...",
            "google_ads_campaign_id": "...",
            ...
        },
        "campaign_id": 123,  ***REMOVED*** Optional: FinderOS campaign ID
        "user_id": 1  ***REMOVED*** Optional: FinderOS user ID
    }
    """
    try:
        ***REMOVED*** Get raw payload
        payload_bytes = await request.body()
        payload_str = payload_bytes.decode('utf-8')
        
        ***REMOVED*** Verify webhook signature (if configured)
        webhook_secret = os.getenv("GOOGLE_ADS_WEBHOOK_SECRET")
        if not verify_google_ads_webhook(payload_bytes, x_google_ads_signature, webhook_secret):
            logger.warning("Webhook signature verification failed")
            raise HTTPException(status_code=401, detail="Invalid webhook signature")
        
        ***REMOVED*** Parse JSON payload
        try:
            payload_data = json.loads(payload_str)
        except json.JSONDecodeError:
            ***REMOVED*** Try parsing as form data or other formats
            logger.warning(f"Failed to parse JSON payload: {payload_str[:200]}")
            raise HTTPException(status_code=400, detail="Invalid JSON payload")
        
        ***REMOVED*** Extract lead data
        lead_data = payload_data.get("lead_data", payload_data)  ***REMOVED*** Support both nested and flat structures
        
        ***REMOVED*** Get required fields
        full_name = lead_data.get("full_name") or lead_data.get("name") or lead_data.get("fullName")
        email = lead_data.get("email")
        
        if not full_name or not email:
            raise HTTPException(
                status_code=400,
                detail="Missing required fields: full_name and email"
            )
        
        ***REMOVED*** Get optional fields
        phone = lead_data.get("phone") or lead_data.get("phone_number")
        google_ads_lead_id = lead_data.get("google_ads_lead_id") or lead_data.get("lead_id")
        google_ads_campaign_id = lead_data.get("google_ads_campaign_id") or lead_data.get("campaign_id")
        
        ***REMOVED*** Find user_id and campaign_id
        user_id = payload_data.get("user_id")
        campaign_id = payload_data.get("campaign_id")
        
        ***REMOVED*** If not provided, try to find by Google Ads campaign ID
        if not user_id or not campaign_id:
            if google_ads_campaign_id:
                campaign = db.query(Campaign).filter(
                    Campaign.target_data.contains({"google_ads_campaign_id": google_ads_campaign_id})
                ).first()
                
                if campaign:
                    user_id = campaign.user_id
                    campaign_id = campaign.id
                    logger.info(f"Found campaign {campaign_id} for Google Ads campaign {google_ads_campaign_id}")
        
        ***REMOVED*** If still no user_id, use default or raise error
        if not user_id:
            ***REMOVED*** Try to get from environment or use a default
            default_user_id = os.getenv("DEFAULT_WEBHOOK_USER_ID")
            if default_user_id:
                user_id = int(default_user_id)
            else:
                raise HTTPException(
                    status_code=400,
                    detail="user_id not found. Please provide user_id in payload or configure DEFAULT_WEBHOOK_USER_ID"
                )
        
        ***REMOVED*** Create lead using LeadService
        lead_service = get_lead_service(db)
        
        result = lead_service.create_lead_from_google_ads(
            user_id=user_id,
            full_name=full_name,
            email=email,
            phone=phone,
            form_data=lead_data,  ***REMOVED*** Store all form data
            google_ads_lead_id=google_ads_lead_id,
            google_ads_campaign_id=google_ads_campaign_id,
            campaign_id=campaign_id
        )
        
        if not result.get("success"):
            logger.error(f"Failed to create lead: {result.get('error')}")
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Failed to create lead")
            )
        
        logger.info(f"Lead created successfully: {result['lead']['id']} (email: {email})")
        
        ***REMOVED*** Get locale from request (webhook may have Accept-Language header)
        locale = get_locale_from_request(request)
        
        ***REMOVED*** Get language-aware message
        response_message = get_lead_received_message(locale)
        
        ***REMOVED*** Return success response
        return {
            "success": True,
            "message": response_message,
            "lead_id": result["lead"]["id"],
            "appointment_id": result.get("appointment", {}).get("id") if result.get("appointment") else None,
            "is_duplicate": result.get("is_duplicate", False)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing Google Ads webhook: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/google-ads/lead-form/test")
async def test_google_ads_webhook(
    db: Session = Depends(get_db)
):
    """
    Test endpoint for Google Ads Lead Form webhook.
    Returns example payload structure.
    """
    return {
        "message": "Google Ads Lead Form Webhook Test Endpoint",
        "expected_payload": {
            "webhook_id": "webhook_123",
            "timestamp": "2024-01-01T12:00:00Z",
            "lead_data": {
                "full_name": "John Doe",
                "email": "john.doe@example.com",
                "phone": "+1234567890",
                "company_name": "Example Corp",
                "job_title": "Manager",
                "message": "Interested in your product",
                "google_ads_lead_id": "lead_123456",
                "google_ads_campaign_id": "1234567890",
                "google_ads_ad_group_id": "9876543210",
                "google_ads_keyword": "b2b software"
            },
            "campaign_id": 1,
            "user_id": 1
        },
        "endpoint": "/v1/webhooks/google-ads/lead-form",
        "method": "POST",
        "headers": {
            "Content-Type": "application/json",
            "X-Google-Ads-Signature": "optional (for signature verification)"
        }
    }


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Stripe webhook endpoint for subscription events.
    NOTE: Payment APIs are currently disabled.
    Handles: subscription.created, subscription.updated, subscription.deleted,
    invoice.paid, invoice.payment_failed, etc.
    """
    ***REMOVED*** Payment APIs are disabled
    raise HTTPException(
        status_code=503,
        detail="Payment APIs (Stripe/Iyzico) are currently disabled."
    )
    
    stripe.api_key = stripe_secret_key
    
    try:
        payload = await request.body()
        sig_header = request.headers.get("stripe-signature")
        
        ***REMOVED*** Verify webhook signature
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, stripe_webhook_secret
            )
        except ValueError as e:
            logger.error(f"Invalid payload: {str(e)}")
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid signature: {str(e)}")
            raise HTTPException(status_code=400, detail="Invalid signature")
        
        ***REMOVED*** Handle event
        event_type = event["type"]
        event_data = event["data"]["object"]
        
        logger.info(f"Stripe webhook received: {event_type}")
        
        if event_type == "customer.subscription.created":
            ***REMOVED*** New subscription created
            subscription_id = event_data.get("id")
            customer_id = event_data.get("customer")
            
            ***REMOVED*** Find user by customer_id
            from src.models.subscription import Subscription
            subscription = db.query(Subscription).filter(
                Subscription.payment_customer_id == customer_id
            ).first()
            
            if subscription:
                subscription.payment_subscription_id = subscription_id
                subscription.status = event_data.get("status", "active")
                db.commit()
                logger.info(f"Subscription updated: {subscription.id}")
        
        elif event_type == "customer.subscription.updated":
            ***REMOVED*** Subscription updated
            subscription_id = event_data.get("id")
            
            from src.models.subscription import Subscription
            subscription = db.query(Subscription).filter(
                Subscription.payment_subscription_id == subscription_id
            ).first()
            
            if subscription:
                subscription.status = event_data.get("status", "active")
                
                ***REMOVED*** Update period dates
                current_period_start = event_data.get("current_period_start")
                current_period_end = event_data.get("current_period_end")
                
                if current_period_start:
                    from datetime import datetime
                    subscription.current_period_start = datetime.fromtimestamp(current_period_start)
                if current_period_end:
                    from datetime import datetime
                    subscription.current_period_end = datetime.fromtimestamp(current_period_end)
                
                db.commit()
                logger.info(f"Subscription updated: {subscription.id}")
        
        elif event_type == "customer.subscription.deleted":
            ***REMOVED*** Subscription cancelled
            subscription_id = event_data.get("id")
            
            from src.models.subscription import Subscription
            subscription = db.query(Subscription).filter(
                Subscription.payment_subscription_id == subscription_id
            ).first()
            
            if subscription:
                subscription.status = "cancelled"
                from datetime import datetime
                subscription.cancelled_at = datetime.utcnow()
                ***REMOVED*** Downgrade to free
                subscription.plan_type = "free"
                subscription.price = 0
                db.commit()
                logger.info(f"Subscription cancelled: {subscription.id}")
        
        elif event_type == "invoice.paid":
            ***REMOVED*** Invoice paid - create invoice record
            invoice_id = event_data.get("id")
            customer_id = event_data.get("customer")
            amount = event_data.get("amount_paid", 0) / 100  ***REMOVED*** Convert from cents
            currency = event_data.get("currency", "usd").upper()
            
            from src.models.subscription import Subscription
            from src.models.invoice import Invoice
            from datetime import datetime
            
            subscription = db.query(Subscription).filter(
                Subscription.payment_customer_id == customer_id
            ).first()
            
            if subscription:
                invoice = Invoice(
                    user_id=subscription.user_id,
                    subscription_id=subscription.id,
                    invoice_number=f"INV-{invoice_id[:8]}",
                    payment_provider="stripe",
                    payment_provider_invoice_id=invoice_id,
                    amount=amount,
                    currency=currency,
                    total_amount=amount,
                    status="paid",
                    paid_at=datetime.utcnow(),
                    period_start=datetime.fromtimestamp(event_data.get("period_start", 0)) if event_data.get("period_start") else None,
                    period_end=datetime.fromtimestamp(event_data.get("period_end", 0)) if event_data.get("period_end") else None
                )
                db.add(invoice)
                db.commit()
                logger.info(f"Invoice created: {invoice.id}")
        
        elif event_type == "invoice.payment_failed":
            ***REMOVED*** Payment failed
            customer_id = event_data.get("customer")
            
            from src.models.subscription import Subscription
            subscription = db.query(Subscription).filter(
                Subscription.payment_customer_id == customer_id
            ).first()
            
            if subscription:
                subscription.status = "past_due"
                db.commit()
                logger.warning(f"Payment failed for subscription: {subscription.id}")
        
        return {
            "success": True,
            "event_type": event_type,
            "message": "Webhook processed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error processing Stripe webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing webhook: {str(e)}")


@router.get("/health")
async def webhook_health():
    """Health check endpoint for webhooks."""
    return {
        "status": "ok",
        "service": "webhooks",
        "endpoints": [
            "POST /v1/webhooks/google-ads/lead-form",
            "GET /v1/webhooks/google-ads/lead-form/test",
            "POST /v1/webhooks/stripe"
        ]
    }

