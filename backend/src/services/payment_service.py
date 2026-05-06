"""
SERVICE: payment_service
PURPOSE: Payment processing service for Stripe and Iyzico integration
ENCODING: UTF-8 WITHOUT BOM
"""

import os
import logging
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from src.models.subscription import Subscription
from src.models.user import User

logger = logging.getLogger(__name__)

try:
    import stripe
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False
    stripe = None

try:
    from iyzipay import Iyzipay, Options, CreatePaymentRequest
    IYZICO_AVAILABLE = True
except ImportError:
    IYZICO_AVAILABLE = False
    Iyzipay = None


class PaymentService:
    """
    Service for processing payments and managing subscriptions.
    Supports Stripe and Iyzico payment providers.
    """
    
    # DEPRECATED: Fixed subscription plans removed
    # All pricing is now usage-based (pay-as-you-go)
    # See UsageBasedPricingService for current pricing model
    PLANS = {}   # Empty - no fixed plans
    
    def __init__(self, db: Session):
        """Initialize Payment Service with database session."""
        self.db = db
        
        # Stripe configuration
        self.stripe_secret_key = os.getenv("STRIPE_SECRET_KEY")
        self.stripe_publishable_key = os.getenv("STRIPE_PUBLISHABLE_KEY")
        
        if STRIPE_AVAILABLE and self.stripe_secret_key:
            stripe.api_key = self.stripe_secret_key
            self.stripe_enabled = True
        else:
            self.stripe_enabled = False
        
        # Iyzico configuration
        self.iyzico_api_key = os.getenv("IYZICO_API_KEY")
        self.iyzico_secret_key = os.getenv("IYZICO_SECRET_KEY")
        self.iyzico_base_url = os.getenv("IYZICO_BASE_URL", "https://api.iyzipay.com")
        
        if IYZICO_AVAILABLE and self.iyzico_api_key and self.iyzico_secret_key:
            self.iyzico_enabled = True
        else:
            self.iyzico_enabled = False
    
    def get_plans(self) -> Dict[str, Any]:
        """
        Get subscription plans for display (Free, Premium, Ajans) and usage-based pricing.
        Plans are used by the pricing section on the homepage.
        """
        from src.services.usage_based_pricing_service import UsageBasedPricingService
        pricing_service = UsageBasedPricingService(self.db)
        
        # Commercial Pay-As-You-Go: Bireysel + Ajanslar (enterprise-friendly, compliant)
        plans = {
            "free": {
                "name": "Free Trial",
                "name_tr": "Ücretsiz Deneme",
                "price": 0,
                "price_monthly": 0,
                "price_yearly": 0,
                "features": [
                    "First use: Free trial",
                    "No long-term commitment",
                    "Basic campaign management",
                    "Email support"
                ],
                "features_tr": [
                    "İlk kullanım: Ücretsiz deneme",
                    "Uzun vadeli taahhüt yok",
                    "Temel kampanya yönetimi",
                    "E-posta destek"
                ]
            },
            "premium": {
                "name": "Individual & Small Teams",
                "name_tr": "Bireysel Kullanıcılar",
                "subtitle": "Pay-as-you-go. Flexible. Scalable. Transparent.",
                "subtitle_tr": "Kullandıkça öde. Esnek. Ölçeklenebilir. Şeffaf.",
                "price": 0.49,
                "price_monthly": 0,
                "price_yearly": 0,
                "registration_fee": 0.98,
                "features": [
                    "First use: Free trial",
                    "Activation: $0.98 (monthly)",
                    "Estimated query cost $4–9 (per query: 100 companies with full contact info, target persona criteria, persona list, ad targeting & location)",
                    "No long-term commitment"
                ],
                "features_tr": [
                    "İlk kullanım: Ücretsiz deneme",
                    "Aktivasyon: $0.98 (aylık)",
                    "Sorgulama tahmini maliyet 4–9 dolar (her sorgu: 100 firma tam iletişim bilgisi / hedef persona kriteri / persona listesi / reklam hedefleme ve lokasyon bilgisi)",
                    "Uzun vadeli taahhüt yok"
                ]
            },
            "agency": {
                "name": "Agencies & Professional Teams",
                "name_tr": "Ajanslar & Profesyonel Ekipler",
                "subtitle": "High volume, multi-client, scalable.",
                "subtitle_tr": "Yüksek hacim, çoklu müşteri, ölçeklenebilir.",
                "price": 0.29,
                "price_monthly": 0,
                "price_yearly": 0,
                "registration_fee": 0.98,
                "features": [
                    "Activation: $0.98 (monthly)",
                    "Estimated $4–9 per query; decreasing cost as volume increases",
                    "Multi-client / campaign support",
                    "Priority infrastructure & faster processing"
                ],
                "features_tr": [
                    "Hesap aktivasyonu: $0.98 (aylık)",
                    "Sorgulama tahmini 4–9 USD; hacim arttıkça azalan maliyet",
                    "Çoklu müşteri / kampanya desteği",
                    "Öncelikli altyapı & hızlandırılmış işleme"
                ]
            }
        }
        
        return {
            "success": True,
            "pricing_model": "usage_based",
            "plans": plans,
            "usage_based_pricing": pricing_service.get_pricing_model(),
            "payment_providers": {
                "stripe": self.stripe_enabled,
                "iyzico": self.iyzico_enabled
            },
        }
    
    def create_subscription(
        self,
        user_id: int,
        plan_type: str,
        billing_cycle: str = "monthly",
        payment_provider: str = "stripe",
        payment_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a subscription for a user.
        
        Args:
            user_id: User ID
            plan_type: Plan type (free, pro, enterprise)
            billing_cycle: Billing cycle (monthly, yearly)
            payment_provider: Payment provider (stripe, iyzico)
            payment_token: Payment token from payment provider
        
        Returns:
            Dictionary with subscription creation result
        """
        try:
            if plan_type not in self.PLANS:
                return {
                    "success": False,
                    "error": f"Invalid plan type: {plan_type}"
                }
            
            plan = self.PLANS[plan_type]
            
            # Get user
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return {
                    "success": False,
                    "error": "User not found"
                }
            
            # Check if user already has a subscription
            existing_subscription = self.db.query(Subscription).filter(
                Subscription.user_id == user_id
            ).first()
            
            # Calculate price
            if plan_type == "free":
                price = 0
            else:
                price_key = f"price_{billing_cycle}"
                price = plan.get(price_key, plan.get("price_monthly", 0))
            
            # Process payment if not free plan
            # NOTE: Payment APIs (Stripe/Iyzico) are currently disabled
            payment_customer_id = None
            payment_subscription_id = None
            
            if plan_type != "free":
                # Payment APIs are disabled - only free plan is available
                return {
                    "success": False,
                    "error": "Payment APIs (Stripe/Iyzico) are currently disabled. Only free plan is available."
                }
            
            # Calculate period dates
            now = datetime.utcnow()
            if billing_cycle == "yearly":
                period_end = now + timedelta(days=365)
            else:
                period_end = now + timedelta(days=30)
            
            # Create or update subscription
            if existing_subscription:
                subscription = existing_subscription
                subscription.plan_type = plan_type
                subscription.payment_provider = payment_provider
                subscription.payment_customer_id = payment_customer_id
                subscription.payment_subscription_id = payment_subscription_id
                subscription.status = "active"
                subscription.billing_cycle = billing_cycle
                subscription.price = price
                subscription.current_period_start = now
                subscription.current_period_end = period_end
                subscription.cancelled_at = None
            else:
                subscription = Subscription(
                    user_id=user_id,
                    plan_type=plan_type,
                    payment_provider=payment_provider,
                    payment_customer_id=payment_customer_id,
                    payment_subscription_id=payment_subscription_id,
                    status="active",
                    billing_cycle=billing_cycle,
                    price=price,
                    started_at=now,
                    current_period_start=now,
                    current_period_end=period_end
                )
                self.db.add(subscription)
            
            self.db.commit()
            self.db.refresh(subscription)
            
            logger.info(f"Subscription created: {subscription.id} for user {user_id}, plan: {plan_type}")
            
            return {
                "success": True,
                "subscription": subscription.to_dict(),
                "message": "Subscription created successfully"
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating subscription: {str(e)}")
            return {
                "success": False,
                "error": f"Error creating subscription: {str(e)}"
            }
    
    def _create_stripe_subscription(
        self,
        user: User,
        plan_type: str,
        billing_cycle: str,
        price: float,
        payment_token: str
    ) -> Dict[str, Any]:
        """
        Create Stripe subscription.
        NOTE: Payment APIs are currently disabled.
        
        Args:
            user: User object
            plan_type: Plan type
            billing_cycle: Billing cycle
            price: Subscription price
            payment_token: Stripe payment token
        
        Returns:
            Dictionary with Stripe subscription result
        """
        # Payment APIs are disabled
        return {
            "success": False,
            "error": "Payment APIs (Stripe/Iyzico) are currently disabled."
        }
    
    def _create_iyzico_subscription(
        self,
        user: User,
        plan_type: str,
        billing_cycle: str,
        price: float,
        payment_token: str
    ) -> Dict[str, Any]:
        """
        Create Iyzico subscription.
        NOTE: Payment APIs are currently disabled.
        
        Args:
            user: User object
            plan_type: Plan type
            billing_cycle: Billing cycle
            price: Subscription price
            payment_token: Iyzico payment token
        
        Returns:
            Dictionary with Iyzico subscription result
        """
        # Payment APIs are disabled
        return {
            "success": False,
            "error": "Payment APIs (Stripe/Iyzico) are currently disabled."
        }
    
    def cancel_subscription(
        self,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Cancel a user's subscription.
        
        Args:
            user_id: User ID
        
        Returns:
            Dictionary with cancellation result
        """
        try:
            subscription = self.db.query(Subscription).filter(
                Subscription.user_id == user_id
            ).first()
            
            if not subscription:
                return {
                    "success": False,
                    "error": "Subscription not found"
                }
            
            # Cancel with payment provider
            # NOTE: Payment APIs (Stripe/Iyzico) are currently disabled
            # Stripe cancellation is disabled
            if subscription.payment_provider == "stripe" and subscription.payment_subscription_id:
                logger.info(f"Skipping Stripe cancellation - Payment APIs are disabled (subscription_id: {subscription.payment_subscription_id})")
            
            # Update subscription status
            subscription.status = "cancelled"
            subscription.cancelled_at = datetime.utcnow()
            
            # Downgrade to free plan
            subscription.plan_type = "free"
            subscription.price = 0
            subscription.payment_provider = None
            subscription.payment_customer_id = None
            subscription.payment_subscription_id = None
            
            self.db.commit()
            
            return {
                "success": True,
                "message": "Subscription cancelled successfully",
                "subscription": subscription.to_dict()
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error cancelling subscription: {str(e)}")
            return {
                "success": False,
                "error": f"Error cancelling subscription: {str(e)}"
            }
    
    def get_user_subscription(
        self,
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get user's subscription.
        
        Args:
            user_id: User ID
        
        Returns:
            Subscription dictionary or None
        """
        try:
            subscription = self.db.query(Subscription).filter(
                Subscription.user_id == user_id
            ).first()
            
            if subscription:
                return subscription.to_dict()
            else:
                # Return free plan by default
                return {
                    "user_id": user_id,
                    "plan_type": "free",
                    "status": "active",
                    "price": 0,
                    "features": self.PLANS["free"]["features"]
                }
                
        except Exception as e:
            logger.error(f"Error getting subscription: {str(e)}")
            return None


def get_payment_service(db: Session) -> PaymentService:
    """
    Get PaymentService instance with database session.
    """
    return PaymentService(db)


