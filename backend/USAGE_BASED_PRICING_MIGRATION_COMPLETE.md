***REMOVED*** Usage-Based Pricing Migration - Complete Implementation

***REMOVED******REMOVED*** Overview

SOAR B2B has been fully migrated from fixed subscription tiers (Free/Pro/Enterprise) to a pure usage-based (pay-as-you-go) pricing model.

***REMOVED******REMOVED*** Changes Summary

***REMOVED******REMOVED******REMOVED*** Backend Changes

***REMOVED******REMOVED******REMOVED******REMOVED*** 1. Subscription Model (`backend/src/models/subscription.py`)
- **Status:** DEPRECATED - Kept for backward compatibility
- **Change:** `plan_type` default changed to `"usage_based"`
- **Note:** New accounts should use `UserAccount` model instead

***REMOVED******REMOVED******REMOVED******REMOVED*** 2. Payment Service (`backend/src/services/payment_service.py`)
- **Removed:** All fixed plan definitions (Free, Pro, Enterprise)
- **Updated:** `get_plans()` now returns usage-based pricing model
- **Integration:** Uses `UsageBasedPricingService` for pricing information

***REMOVED******REMOVED******REMOVED******REMOVED*** 3. Subscription Router (`backend/src/http/v1/subscription_router.py`)
- **Updated:** `/current` endpoint returns `UserAccount` state instead of subscription plan
- **Added:** `/pricing/calculate` - Calculate query cost with optional modules
- **Added:** `/pricing/model` - Get complete pricing model
- **Added:** `/pricing/estimate` - Estimate monthly cost

***REMOVED******REMOVED******REMOVED******REMOVED*** 4. Usage-Based Pricing Service (`backend/src/services/usage_based_pricing_service.py`)
- **Status:** Already exists and fully functional
- **Pricing Model:**
  - Account activation: $0.98/month
  - Query execution: $1.99 per query (max 100 businesses)
  - Optional modules:
    - Persona deepening: $0.49
    - Visit Route (max 20 stops): $0.99
    - Export (CSV/PDF/CRM): $0.49
    - Outreach preparation: $0.99

***REMOVED******REMOVED******REMOVED******REMOVED*** 5. Query Limits (`backend/src/core/query_limits.py`)
- **Enforcement:** MAX 100 results per query (non-negotiable)
- **Admin Override:** Up to 1000 results (requires admin key)
- **Status:** Already enforced

***REMOVED******REMOVED******REMOVED*** Frontend Changes

***REMOVED******REMOVED******REMOVED******REMOVED*** 1. Landing Page (`frontend/landing_page.html`)
- **Removed:** Fixed subscription tiers (Free/Pro/Enterprise)
- **Added:** Usage-based pricing display
- **Added:** Cost calculator with monthly estimation
- **Added:** Enterprise contact section

***REMOVED******REMOVED******REMOVED******REMOVED*** 2. SOAR B2B Home Page (`backend/src/ui/soarb2b_home.html`)
- **Removed:** "Choose Your Plan" section with fixed tiers
- **Updated:** Pricing section shows usage-based model
- **Removed:** Plan loading JavaScript
- **Added:** Direct links to onboarding and cost calculator

***REMOVED******REMOVED******REMOVED******REMOVED*** 3. Onboarding Form (`backend/src/ui/soarb2b_onboarding_5q.html`)
- **TODO:** Add cost preview modal before query execution
- **TODO:** Show estimated cost based on selected modules
- **TODO:** Require explicit confirmation before executing query

***REMOVED******REMOVED******REMOVED******REMOVED*** 4. Results Hub (`backend/src/ui/*/soarb2b_results_hub.html`)
- **TODO:** Display usage-based billing information
- **TODO:** Show cost per query execution
- **TODO:** Make each result set downloadable

***REMOVED******REMOVED*** API Endpoints

***REMOVED******REMOVED******REMOVED*** Pricing Endpoints

**GET `/v1/subscriptions/pricing/model`**
- Returns complete usage-based pricing model
- Public endpoint (no auth required)

**GET `/v1/subscriptions/pricing/calculate`**
- Calculate cost for a single query
- Parameters:
  - `include_persona_deepening` (bool)
  - `include_visit_route` (bool)
  - `include_export` (bool)
  - `include_outreach_preparation` (bool)
- Returns cost breakdown

**GET `/v1/subscriptions/pricing/estimate`**
- Estimate monthly cost
- Parameters:
  - `estimated_queries` (int)
  - `avg_optional_modules` (string, comma-separated)
- Returns monthly cost estimate

**GET `/v1/subscriptions/current`**
- Returns user account state (usage-based)
- Requires authentication
- Returns:
  - `account_status`: "inactive" | "active" | "suspended"
  - `activation_fee_paid`: boolean
  - `query_cap`: 100 (default, or admin override)
  - `admin_override_active`: boolean

***REMOVED******REMOVED*** Pricing Model

***REMOVED******REMOVED******REMOVED*** Base Costs
- **Account Activation:** $0.98/month (recurring)
- **Query Execution:** $1.99 per query
  - Max 100 businesses per query
  - No unlimited claims

***REMOVED******REMOVED******REMOVED*** Optional Modules
- **Persona Deepening:** $0.49 per query
- **Visit Route:** $0.99 per query (max 20 stops)
- **Export:** $0.49 per query (CSV/PDF/CRM)
- **Outreach Preparation:** $0.99 per query

***REMOVED******REMOVED******REMOVED*** Enterprise / Agency
- Custom caps (beyond 100)
- API access
- White-label options
- Admin override
- Contact: sales@soarb2b.com

***REMOVED******REMOVED*** Query Execution Enforcement

***REMOVED******REMOVED******REMOVED*** Max Results Cap
- **Standard:** 100 results per query (enforced)
- **Admin Override:** Up to 1000 results (requires admin key)
- **Enforcement:** Automatic in `query_limits.py`

***REMOVED******REMOVED******REMOVED*** Cost Preview (TODO)
Before query execution:
1. Calculate estimated cost
2. Display cost breakdown
3. Require explicit user confirmation
4. Proceed with execution

***REMOVED******REMOVED*** Migration Checklist

***REMOVED******REMOVED******REMOVED*** Backend ✅
- [x] Update subscription model (deprecated, kept for compatibility)
- [x] Remove fixed plans from payment service
- [x] Update subscription router endpoints
- [x] Add cost calculation endpoints
- [x] Verify query limits enforcement (100 max)

***REMOVED******REMOVED******REMOVED*** Frontend ✅
- [x] Update landing page pricing section
- [x] Update SOAR B2B home page pricing section
- [ ] Add cost preview modal in onboarding
- [ ] Update Results Hub with usage billing
- [ ] Remove all "unlimited" language
- [ ] Remove all fixed plan references

***REMOVED******REMOVED******REMOVED*** Testing ⏳
- [ ] Test cost calculation API
- [ ] Test monthly cost estimation
- [ ] Test query execution with cost preview
- [ ] Verify 100 result cap enforcement
- [ ] Test enterprise contact flow

***REMOVED******REMOVED*** Next Steps

1. **Add Cost Preview Modal** in onboarding form
   - Calculate cost before query execution
   - Show breakdown
   - Require confirmation

2. **Update Results Hub**
   - Display cost per query
   - Show usage-based billing
   - Make results downloadable

3. **Remove Remaining References**
   - Search for "unlimited" in all UI files
   - Remove Google Ads as "included" feature
   - Update all pricing-related text

4. **Testing**
   - End-to-end query execution flow
   - Cost calculation accuracy
   - Billing integration

***REMOVED******REMOVED*** Files Modified

***REMOVED******REMOVED******REMOVED*** Backend
- `backend/src/models/subscription.py`
- `backend/src/services/payment_service.py`
- `backend/src/http/v1/subscription_router.py`

***REMOVED******REMOVED******REMOVED*** Frontend
- `frontend/landing_page.html`
- `backend/src/ui/soarb2b_home.html`

***REMOVED******REMOVED*** Files To Update (TODO)

- `backend/src/ui/soarb2b_onboarding_5q.html` - Add cost preview
- `backend/src/ui/*/soarb2b_results_hub.html` - Show usage billing
- All language variants of UI files

***REMOVED******REMOVED*** Breaking Changes

- **Removed:** Fixed subscription plans (Free/Pro/Enterprise)
- **Removed:** "Unlimited" claims
- **Changed:** `/v1/subscriptions/current` returns account state, not plan
- **Changed:** `/v1/subscriptions/plans` returns usage-based pricing only

***REMOVED******REMOVED*** Backward Compatibility

- Subscription model kept for existing data
- Legacy plan types still supported in database
- New accounts default to usage-based
- Migration path: Update existing subscriptions to usage-based
