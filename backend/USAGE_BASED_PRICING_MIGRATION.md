***REMOVED*** Usage-Based Pricing Migration - Implementation Guide

***REMOVED******REMOVED*** Overview

SOAR B2B has been migrated from fixed subscription tiers (Free/Pro/Enterprise) to a fully usage-based (pay-as-you-go) pricing model.

***REMOVED******REMOVED*** What Changed

***REMOVED******REMOVED******REMOVED*** 1. Pricing Model ✅

**Old Model (Removed):**
- Free Plan: $0/month
- Pro Plan: $99/month or $990/year
- Enterprise Plan: $299/month or $2990/year
- "Unlimited" claims removed

**New Model (Implemented):**
- **Account activation**: $0.98/month
- **Query execution**: $1.99 per query (max 100 businesses)
- **Optional modules**:
  - Persona deepening: $0.49
  - Visit Route (max 20 stops): $0.99
  - Export (CSV/PDF/CRM): $0.49
  - Outreach preparation: $0.99

***REMOVED******REMOVED******REMOVED*** 2. Backend Changes ✅

**New Service:**
- `UsageBasedPricingService` - Handles all pricing calculations
- Endpoints:
  - `GET /api/v1/pricing/model` - Get pricing model
  - `GET /api/v1/pricing/calculate` - Calculate query cost
  - `GET /api/v1/pricing/estimate` - Estimate monthly cost
  - `GET /api/v1/pricing/activation` - Get activation fee info

**New Model:**
- `UserAccount` - Tracks account status, activation fee, query cap, usage
- Fields:
  - `account_status`: "inactive", "active", "suspended"
  - `activation_fee_paid`: Boolean
  - `query_cap`: Default 100 (MAX_RESULTS_PER_QUERY)
  - `admin_override_active`: Boolean for admin override
  - `queries_this_month`: Usage tracking

**Updated Service:**
- `QueryExecutionService` - Now requires cost confirmation before execution
- Method: `calculate_query_cost_preview()` - Shows cost before execution

***REMOVED******REMOVED******REMOVED*** 3. UI Changes ✅

**Onboarding Form:**
- Removed fixed pricing tiers section
- Added simple usage-based pricing info
- Links to cost calculator and Enterprise contact

**Results Hub:**
- Each result set is individually downloadable
- Each query is individually tracked and billed

***REMOVED******REMOVED******REMOVED*** 4. Cost Preview ✅

Before query execution, users must:
1. See cost breakdown
2. Confirm to proceed
3. Query executes only after confirmation

***REMOVED******REMOVED*** Implementation Details

***REMOVED******REMOVED******REMOVED*** Pricing Calculation

```python
from src.services.usage_based_pricing_service import get_usage_based_pricing_service

pricing_service = get_usage_based_pricing_service(db)
cost = pricing_service.calculate_query_cost(
    include_persona_deepening=True,
    include_visit_route=False,
    include_export=True,
    include_outreach_preparation=False
)
***REMOVED*** Returns: {
***REMOVED***   "base_query": 1.99,
***REMOVED***   "optional_modules": {"persona_deepening": 0.49, "export": 0.49},
***REMOVED***   "total_cost": 2.97,
***REMOVED***   "max_results": 100
***REMOVED*** }
```

***REMOVED******REMOVED******REMOVED*** Query Execution Flow

1. User selects objectives
2. System calculates cost preview
3. User confirms cost
4. Query executes
5. Usage tracked and billed

***REMOVED******REMOVED******REMOVED*** Account Activation

1. User pays $0.98/month activation fee
2. Account status set to "active"
3. Query cap enforced (MAX 100 unless admin override)
4. Usage tracked per query

***REMOVED******REMOVED*** Enforcement

***REMOVED******REMOVED******REMOVED*** MAX 100 Cap
- Non-negotiable unless admin override
- Enforced in `query_limits.py`
- Admin override: up to 1000 results (via admin API key)

***REMOVED******REMOVED******REMOVED*** Cost Confirmation
- Required before query execution
- Prevents unexpected charges
- User must explicitly confirm

***REMOVED******REMOVED*** Enterprise/Agency

For custom requirements:
- Custom caps (above 100)
- API access
- White-label options
- Admin override

**Contact**: Single "Contact us" section for Enterprise inquiries

***REMOVED******REMOVED*** Migration Checklist

- [x] Remove fixed subscription tiers from UI
- [x] Create usage-based pricing service
- [x] Create UserAccount model
- [x] Add pricing API endpoints
- [x] Add cost preview to query execution
- [x] Update onboarding form pricing section
- [ ] Update pricing page with cost calculator (TODO)
- [ ] Update Results Hub to show per-query billing (TODO)
- [ ] Update payment service to remove fixed plans (TODO)

***REMOVED******REMOVED*** API Endpoints

***REMOVED******REMOVED******REMOVED*** Get Pricing Model
```bash
GET /api/v1/pricing/model
```

***REMOVED******REMOVED******REMOVED*** Calculate Query Cost
```bash
GET /api/v1/pricing/calculate?include_persona_deepening=true&include_export=true
```

***REMOVED******REMOVED******REMOVED*** Estimate Monthly Cost
```bash
GET /api/v1/pricing/estimate?queries_per_month=10&avg_modules=persona_deepening,export
```

***REMOVED******REMOVED*** Testing

***REMOVED******REMOVED******REMOVED*** Manual Test

1. Start server:
```bash
cd backend
python -m uvicorn src.app:app --reload --host 127.0.0.1 --port 8000
```

2. Test pricing API:
```bash
curl "http://127.0.0.1:8000/api/v1/pricing/model"
curl "http://127.0.0.1:8000/api/v1/pricing/calculate?include_persona_deepening=true"
```

3. Test onboarding form:
- Open: `http://127.0.0.1:8000/ui/en/soarb2b_onboarding_5q.html`
- Verify pricing section shows usage-based info
- No fixed plans visible

***REMOVED******REMOVED*** Next Steps

1. Add cost calculator to pricing page
2. Implement cost confirmation UI in objective selection
3. Update payment service to handle usage-based billing
4. Add usage tracking per query
5. Update Results Hub to show per-query costs
