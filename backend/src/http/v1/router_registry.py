from fastapi import APIRouter

from src.http.v1.livebook_endpoints import router as livebook_router
from src.http.v1.matching_router import router as matching_router
from src.http.v1.analytics_router import router as analytics_router
from src.http.v1.records_router import router as records_router
from src.http.v1.growth_activation_router import router as growth_activation_router
from src.http.v1.product_router import router as product_router
from src.http.v1.campaign_router import router as campaign_router
from src.http.v1.export_router import router as export_router
from src.http.v1.company_research_router import router as company_research_router
from src.http.v1.analytics_export_router import router as analytics_export_router
from src.http.v1.auth_router import router as auth_router
from src.http.v1.discovery_router import router as discovery_router
from src.http.v1.webhooks_router import router as webhooks_router
from src.http.v1.appointment_router import router as appointment_router
from src.http.v1.notification_router import router as notification_router
from src.http.v1.error_log_router import router as error_log_router
from src.http.v1.subscription_router import router as subscription_router
from src.http.v1.usage_router import router as usage_router
from src.http.v1.invoice_router import router as invoice_router
from src.http.v1.sales_page_audit_router import router as sales_page_audit_router
from src.http.v1.industrial_chain_hunter_router import router as industrial_chain_hunter_router
from src.http.v1.sniper_b2b_router import router as sniper_b2b_router
from src.http.v1.persona_signal_router import router as persona_signal_router
from src.http.v1.location_affinity_router import router as location_affinity_router
from src.http.v1.explainer_router import router as explainer_router
from src.http.v1.marketplace_seller_router import router as marketplace_seller_router
from src.http.v1.enrichment_router import router as enrichment_router
from src.http.v1.gpt_companion_router import router as gpt_companion_router
from src.http.v1.usage_billing_router import router as usage_billing_router
from src.http.v1.support_router import router as support_router
from src.http.v1.public_router import router as public_router
from src.http.v1.acquisition_router import router as acquisition_router
from src.http.v1.pricing_router import router as pricing_router
from src.http.v1.company_graph_router import router as company_graph_router
from src.http.v1.market_signals_router import router as market_signals_router
from src.http.v1.opportunities_router import router as opportunities_router

router = APIRouter(prefix="/v1")

router.include_router(livebook_router)
router.include_router(matching_router)
router.include_router(analytics_router)
router.include_router(records_router)
router.include_router(growth_activation_router)
router.include_router(product_router)
router.include_router(campaign_router)
router.include_router(export_router)
router.include_router(company_research_router)
router.include_router(analytics_export_router)
router.include_router(auth_router)
router.include_router(discovery_router)
router.include_router(webhooks_router)
router.include_router(appointment_router)
router.include_router(notification_router)
router.include_router(error_log_router)
router.include_router(subscription_router)
router.include_router(usage_router)
router.include_router(invoice_router)
router.include_router(sales_page_audit_router)
router.include_router(industrial_chain_hunter_router)
router.include_router(sniper_b2b_router)
router.include_router(persona_signal_router)
router.include_router(location_affinity_router)
router.include_router(explainer_router)
router.include_router(marketplace_seller_router)
router.include_router(enrichment_router)
router.include_router(gpt_companion_router)
router.include_router(usage_billing_router)
router.include_router(support_router)
router.include_router(acquisition_router)
router.include_router(pricing_router)
router.include_router(company_graph_router)
router.include_router(market_signals_router)
router.include_router(opportunities_router)