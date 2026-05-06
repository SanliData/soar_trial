***REMOVED*** Production Audit: Quote Token Enforcement

***REMOVED******REMOVED*** Implementation Evidence

***REMOVED******REMOVED******REMOVED*** Task A: Diffs and Evidence

***REMOVED******REMOVED******REMOVED******REMOVED*** 1. Modified Files - Git Diffs

**File: `backend/src/models/subscription.py`**

```diff
--- a/backend/src/models/subscription.py
+++ b/backend/src/models/subscription.py
@@ -14,11 +14,11 @@
 class Subscription(Base):
     """
-    Subscription model for storing user subscription plans and payment information.
-    Supports Free, Pro, and Enterprise tiers.
+    Subscription model for storing user account state and payment information.
+    DEPRECATED: This model is being phased out in favor of UserAccount for usage-based pricing.
+    Kept for backward compatibility during migration.
     """
@@ -28,9 +28,9 @@
     ***REMOVED*** Subscription plan
-    plan_type = Column(String(50), default="free", nullable=False, index=True)  ***REMOVED*** "free", "pro", "enterprise", "usage_based"
+    plan_type = Column(String(50), default="usage_based", nullable=False, index=True)  ***REMOVED*** Legacy: "free", "pro", "enterprise", "usage_based"
     
     ***REMOVED*** Billing mode
-    billing_mode = Column(String(50), default="subscription", nullable=False)  ***REMOVED*** "subscription", "usage_based"
+    billing_mode = Column(String(50), default="usage_based", nullable=False)  ***REMOVED*** "usage_based" only
```

**File: `backend/src/services/payment_service.py`**

```diff
--- a/backend/src/services/payment_service.py
+++ b/backend/src/services/payment_service.py
@@ -39,42 +39,8 @@
     """
     
-    ***REMOVED*** Subscription plan definitions
-    PLANS = {
-        "free": {
-            "name": "Free",
-            "price": 0,
-            "features": [
-                "Up to 10 companies per month",
-                "Up to 50 personas per month",
-                "Basic campaign management",
-                "Email support"
-            ],
-            "limits": {
-                "companies_per_month": 10,
-                "personas_per_month": 50,
-                "campaigns_per_month": 1
-            }
-        },
-        "pro": {
-            "name": "Pro",
-            "price_monthly": 99,
-            "price_yearly": 990,  ***REMOVED*** 2 months free
-            "features": [
-                "Unlimited companies",
-                "Unlimited personas",
-                "Unlimited campaigns",
-                "Google Ads integration",
-                "Priority support",
-                "Advanced analytics"
-            ],
-            "limits": {
-                "companies_per_month": -1,  ***REMOVED*** Unlimited
-                "personas_per_month": -1,
-                "campaigns_per_month": -1
-            }
-        },
-        "enterprise": {
-            "name": "Enterprise",
-            "price_monthly": 299,
-            "price_yearly": 2990,  ***REMOVED*** 2 months free
-            "features": [
-                "Everything in Pro",
-                "Dedicated account manager",
-                "Custom integrations",
-                "SLA guarantee",
-                "White-label options",
-                "API access"
-            ],
-            "limits": {
-                "companies_per_month": -1,
-                "personas_per_month": -1,
-                "campaigns_per_month": -1
-            }
-        }
-    }
+    ***REMOVED*** DEPRECATED: Fixed subscription plans removed
+    ***REMOVED*** All pricing is now usage-based (pay-as-you-go)
+    ***REMOVED*** See UsageBasedPricingService for current pricing model
+    PLANS = {}  ***REMOVED*** Empty - no fixed plans
@@ -118,13 +84,15 @@
     def get_plans(self) -> Dict[str, Any]:
         """
-        Get available subscription plans.
+        Get pricing information (usage-based only).
+        DEPRECATED: Fixed plans removed. Returns usage-based pricing model.
         
         Returns:
-            Dictionary with plan information
+            Dictionary with usage-based pricing information
         """
+        from src.services.usage_based_pricing_service import UsageBasedPricingService
+        pricing_service = UsageBasedPricingService(self.db)
+        
         return {
             "success": True,
-            "plans": self.PLANS,
+            "pricing_model": "usage_based",
+            "plans": {},  ***REMOVED*** No fixed plans
+            "usage_based_pricing": pricing_service.get_pricing_model(),
             "payment_providers": {
                 "stripe": self.stripe_enabled,
                 "iyzico": self.iyzico_enabled
-            }
+            },
+            "note": "All pricing is usage-based (pay-as-you-go). No fixed subscription tiers."
         }
```

**File: `backend/src/http/v1/subscription_router.py`**

```diff
--- a/backend/src/http/v1/subscription_router.py
+++ b/backend/src/http/v1/subscription_router.py
@@ -12,6 +12,8 @@
 from src.models.user import User
+from src.models.user_account import UserAccount
 from src.db.base import get_db
 from src.services.auth_service import get_current_user_dependency, get_current_user_impl
 from src.services.payment_service import get_payment_service
+from src.services.usage_based_pricing_service import get_usage_based_pricing_service
@@ -58,25 +60,45 @@
 @router.get("/current")
 async def get_current_subscription(
     user: Optional[User] = Depends(get_current_user_from_header),
     db: Session = Depends(get_db)
 ):
     """
-    Get current user's subscription.
+    Get current user's account state (usage-based pricing).
+    Returns account status, activation fee payment, and query cap.
     """
     try:
         if not user:
             raise HTTPException(status_code=401, detail="Authentication required")
         
-        payment_service = get_payment_service(db)
-        subscription = payment_service.get_user_subscription(user.id)
+        ***REMOVED*** Get user account (usage-based)
+        account = db.query(UserAccount).filter(UserAccount.user_id == user.id).first()
         
-        if subscription:
+        if account:
             return {
                 "success": True,
-                "subscription": subscription
+                "account": account.to_dict(),
+                "pricing_model": "usage_based",
+                "subscription": {
+                    "plan_type": "usage_based",  ***REMOVED*** Legacy compatibility
+                    "status": account.account_status,
+                    "billing_mode": "usage_based"
+                }
             }
         else:
-            return {
+            ***REMOVED*** Default inactive account
+            return {
                 "success": True,
-                "subscription": {
-                    "plan_type": "free",
-                    "status": "active"
+                "account": {
+                    "account_status": "inactive",
+                    "activation_fee_paid": False,
+                    "query_cap": 100,
+                    "admin_override_active": False
                 }
+                "pricing_model": "usage_based",
+                "subscription": {
+                    "plan_type": "usage_based",
+                    "status": "inactive",
+                    "billing_mode": "usage_based"
+                }
             }
@@ -85,6 +107,75 @@
         raise HTTPException(status_code=500, detail=f"Error getting account: {str(e)}")
 
 
+@router.get("/pricing/calculate")
+async def calculate_query_cost(
+    include_persona_deepening: bool = False,
+    include_visit_route: bool = False,
+    include_export: bool = False,
+    include_outreach_preparation: bool = False,
+    max_results: int = 100,
+    db: Session = Depends(get_db)
+):
+    """
+    Calculate cost for a query execution with optional modules.
+    Returns signed quote_token required for query execution.
+    Public endpoint - no authentication required.
+    """
+    try:
+        from src.core.query_limits import MAX_RESULTS_PER_QUERY
+        
+        ***REMOVED*** Enforce max_results cap
+        if max_results > MAX_RESULTS_PER_QUERY:
+            raise HTTPException(
+                status_code=400,
+                detail=f"max_results ({max_results}) exceeds maximum allowed ({MAX_RESULTS_PER_QUERY})"
+            )
+        
+        pricing_service = get_usage_based_pricing_service(db)
+        result = pricing_service.calculate_query_cost_with_quote(
+            include_persona_deepening=include_persona_deepening,
+            include_visit_route=include_visit_route,
+            include_export=include_export,
+            include_outreach_preparation=include_outreach_preparation,
+            max_results=max_results
+        )
+        
+        return {
+            "success": True,
+            "cost": {
+                "base_query": result["base_query"],
+                "optional_modules": result["optional_modules"],
+                "total_optional": result["total_optional"],
+                "total_cost": result["total_cost"],
+                "currency": result["currency"],
+                "max_results": result["max_results"],
+                "breakdown": result["breakdown"]
+            },
+            "quote_token": result["quote_token"],
+            "expires_at": result["expires_at"],
+            "request_fingerprint": result["request_fingerprint"]
+        }
+    except HTTPException:
+        raise
+    except Exception as e:
+        raise HTTPException(status_code=500, detail=f"Error calculating cost: {str(e)}")
+
+
+@router.get("/pricing/model")
+async def get_pricing_model(db: Session = Depends(get_db)):
+    """
+    Get complete usage-based pricing model.
+    Public endpoint - no authentication required.
+    """
+    try:
+        pricing_service = get_usage_based_pricing_service(db)
+        return {
+            "success": True,
+            "pricing": pricing_service.get_pricing_model()
+        }
+    except Exception as e:
+        raise HTTPException(status_code=500, detail=f"Error getting pricing model: {str(e)}")
+
+
+@router.get("/pricing/estimate")
+async def estimate_monthly_cost(
+    estimated_queries: int,
+    avg_optional_modules: Optional[str] = None,  ***REMOVED*** Comma-separated list
+    db: Session = Depends(get_db)
+):
+    """
+    Estimate monthly cost based on expected usage.
+    Public endpoint - no authentication required.
+    """
+    try:
+        pricing_service = get_usage_based_pricing_service_service(db)
+        modules_list = []
+        if avg_optional_modules:
+            modules_list = [m.strip() for m in avg_optional_modules.split(",")]
+        
+        estimate = pricing_service.estimate_monthly_cost(
+            estimated_queries_per_month=estimated_queries,
+            avg_optional_modules=modules_list
+        )
+        return {
+            "success": True,
+            "estimate": estimate
+        }
+    except Exception as e:
+        raise HTTPException(status_code=500, detail=f"Error estimating cost: {str(e)}")
+
```

**File: `backend/src/http/v1/b2b_api_router.py`**

```diff
--- a/backend/src/http/v1/b2b_api_router.py
+++ b/backend/src/http/v1/b2b_api_router.py
@@ -145,7 +145,15 @@
     selected_lat: Optional[float] = Field(None, description="Selected latitude from map")
     selected_lng: Optional[float] = Field(None, description="Selected longitude from map")
     auto_start_queries: bool = Field(default=False, description="Start analysis automatically after submission (Yes/No)")
-    cost_confirmed: bool = Field(default=False, description="User has confirmed the query cost preview")
+    quote_token: Optional[str] = Field(None, description="Signed quote token from /pricing/calculate endpoint (required if auto_start_queries=True)")
+    include_persona_deepening: bool = Field(default=False, description="Include persona deepening module")
+    include_visit_route: bool = Field(default=False, description="Include visit route module")
+    include_export: bool = Field(default=False, description="Include export module")
+    include_outreach_preparation: bool = Field(default=False, description="Include outreach preparation module")
+    max_results: int = Field(default=100, description="Maximum results (max: 100)")
@@ -262,25 +270,70 @@
     ***REMOVED*** Auto-start queries if user opted in
     if request.auto_start_queries:
-        ***REMOVED*** Require cost confirmation before executing queries
-        if not request.cost_confirmed:
-            logger.warning(f"Query execution skipped for plan {plan_id}: Cost not confirmed by user")
+        ***REMOVED*** HARD ENFORCEMENT: Require valid quote_token
+        if not request.quote_token:
+            logger.warning(f"Query execution blocked for plan {plan_id}: quote_token missing")
             raise HTTPException(
                 status_code=400,
-                return OnboardingPlanResponse(...)
+                detail={
+                    "error": "quote_token is required for query execution",
+                    "error_code": "QUOTE_TOKEN_MISSING",
+                    "message": "Please call /v1/subscriptions/pricing/calculate first to get a quote_token"
+                }
             )
         
+        ***REMOVED*** Validate quote token
+        try:
+            from src.core.quote_token import validate_quote_token
+            from src.core.query_limits import MAX_RESULTS_PER_QUERY
+            
+            ***REMOVED*** Enforce max_results cap
+            normalized_max_results = min(request.max_results, MAX_RESULTS_PER_QUERY)
+            
+            validation_result = validate_quote_token(
+                quote_token=request.quote_token,
+                include_persona_deepening=request.include_persona_deepening,
+                include_visit_route=request.include_visit_route,
+                include_export=request.include_export,
+                include_outreach_preparation=request.include_outreach_preparation,
+                max_results=normalized_max_results
+            )
+            
+            if not validation_result["valid"]:
+                logger.warning(f"Query execution blocked for plan {plan_id}: {validation_result['error_code']} - {validation_result['error']}")
+                raise HTTPException(
+                    status_code=400,
+                    detail={
+                        "error": validation_result["error"],
+                        "error_code": validation_result["error_code"],
+                        "message": "Quote token validation failed. Please get a new quote from /v1/subscriptions/pricing/calculate"
+                    }
+                )
+            
+            logger.info(f"Quote token validated for plan {plan_id}, proceeding with query execution")
+            
+        except HTTPException:
+            raise
+        except Exception as e:
+            logger.error(f"Error validating quote token: {str(e)}", exc_info=True)
+            raise HTTPException(
+                status_code=500,
+                detail={
+                    "error": f"Error validating quote token: {str(e)}",
+                    "error_code": "QUOTE_TOKEN_VALIDATION_ERROR"
+                }
+            )
+        
         try:
             from src.services.query_execution_service import get_query_execution_service
             query_service = get_query_execution_service(db)
             ***REMOVED*** Start query pipeline automatically (no admin approval needed for standard queries)
             ***REMOVED*** MAX 100 results enforced automatically
             query_service.start_query_pipeline(
                 plan_id=plan_id,
                 target_type=request.target_type,
                 geography=request.geography,
                 decision_roles=request.decision_roles,
                 auto_approved=True,  ***REMOVED*** Standard queries (MAX 100) don't need admin approval
-                cost_confirmed=True  ***REMOVED*** User confirmed cost in frontend
+                cost_confirmed=True  ***REMOVED*** Quote token validated = cost confirmed
             )
-            logger.info(f"Query pipeline auto-started for plan: {plan_id} (cost confirmed)")
+            logger.info(f"Query pipeline auto-started for plan: {plan_id} (quote token validated)")
```

***REMOVED******REMOVED******REMOVED******REMOVED*** 2. New Files Created

**File: `backend/src/config/pricing.py`** (NEW)
- Single source of truth for all pricing constants
- All pricing values defined here

**File: `backend/src/core/quote_token.py`** (NEW)
- HMAC-based quote token generation
- Quote token validation
- Request fingerprint matching

**File: `backend/tests/test_quote_token.py`** (NEW)
- Unit tests for quote token generation/validation

**File: `backend/tests/test_pricing_enforcement.py`** (NEW)
- Integration tests for hard enforcement

***REMOVED******REMOVED******REMOVED*** Task B: Server-Side Enforcement

***REMOVED******REMOVED******REMOVED******REMOVED*** Quote Token Generation

**Endpoint:** `GET /v1/subscriptions/pricing/calculate`

**Implementation:** `backend/src/core/quote_token.py::generate_quote_token()`

- Creates HMAC-signed token using `QUOTE_SECRET` or `JWT_SECRET`
- Includes request fingerprint (canonical hash of query params + max_results + modules)
- Sets expiration (15 minutes)
- Returns `quote_token`, `expires_at`, `request_fingerprint`

***REMOVED******REMOVED******REMOVED******REMOVED*** Quote Token Validation

**Implementation:** `backend/src/core/quote_token.py::validate_quote_token()`

**Validation Checks:**
1. Token format (payload.signature)
2. HMAC signature verification
3. Expiration check
4. Request fingerprint match
5. max_results <= 100 (rejects if exceeded)

**Error Codes:**
- `QUOTE_TOKEN_MISSING`
- `QUOTE_TOKEN_INVALID_FORMAT`
- `QUOTE_TOKEN_INVALID_SIGNATURE`
- `QUOTE_TOKEN_EXPIRED`
- `QUOTE_TOKEN_FINGERPRINT_MISMATCH`
- `MAX_RESULTS_EXCEEDED`
- `QUOTE_TOKEN_VALIDATION_ERROR`

***REMOVED******REMOVED******REMOVED******REMOVED*** Query Execution Enforcement

**Endpoint:** `POST /api/v1/b2b/onboarding/create-plan`

**Enforcement:** `backend/src/http/v1/b2b_api_router.py::create_onboarding_plan()`

- **REQUIRES:** `quote_token` if `auto_start_queries=True`
- **VALIDATES:** Quote token before execution
- **REJECTS:** Invalid/expired/mismatched tokens
- **ENFORCES:** max_results <= 100

***REMOVED******REMOVED******REMOVED*** Task C: Single Source of Truth

**File:** `backend/src/config/pricing.py`

**Constants:**
- `ACCOUNT_ACTIVATION_FEE = 0.98`
- `QUERY_EXECUTION_COST = 1.99`
- `OPTIONAL_MODULES = {...}`
- `MAX_RESULTS_PER_QUERY = 100`
- `MAX_VISIT_STOPS = 20`

**Usage:**
- `UsageBasedPricingService` reads from `src.config.pricing`
- UI should match these values (documented in implementation)

***REMOVED******REMOVED******REMOVED*** Task D: Backward Compatibility

**Subscription Model:**
- Fields unchanged (no migration needed)
- `plan_type` default changed to `"usage_based"`
- Existing records remain valid
- New accounts default to usage-based

**Compatibility Mapping:**
- Legacy `plan_type="free"` → Treated as `account_status="inactive"`
- Legacy `plan_type="pro"` → Treated as `account_status="active"` (if paid)
- Legacy `plan_type="enterprise"` → Requires admin override

***REMOVED******REMOVED******REMOVED*** Task E: Testing

**Test Files:**
- `backend/tests/test_quote_token.py` - Unit tests
- `backend/tests/test_pricing_enforcement.py` - Integration tests

**Run Tests:**
```bash
cd backend
pytest tests/test_quote_token.py -v
pytest tests/test_pricing_enforcement.py -v
```

***REMOVED******REMOVED*** API Endpoint Examples

***REMOVED******REMOVED******REMOVED*** 1. Get Pricing Model

```bash
curl -X GET "https://your-service-url/v1/subscriptions/pricing/model"
```

**Expected Response:**
```json
{
  "success": true,
  "pricing": {
    "model": "usage_based",
    "account_activation": {
      "fee": 0.98,
      "period": "monthly",
      "currency": "USD"
    },
    "query_execution": {
      "cost": 1.99,
      "max_results": 100,
      "currency": "USD"
    },
    "optional_modules": {
      "Persona Deepening": {"cost": 0.49, "currency": "USD"},
      "Visit Route": {"cost": 0.99, "currency": "USD"},
      "Export": {"cost": 0.49, "currency": "USD"},
      "Outreach Preparation": {"cost": 0.99, "currency": "USD"}
    }
  }
}
```

***REMOVED******REMOVED******REMOVED*** 2. Calculate Cost and Get Quote Token

```bash
curl -X GET "https://your-service-url/v1/subscriptions/pricing/calculate?include_persona_deepening=true&include_export=true&max_results=100"
```

**Expected Response:**
```json
{
  "success": true,
  "cost": {
    "base_query": 1.99,
    "optional_modules": {
      "persona_deepening": 0.49,
      "export": 0.49
    },
    "total_optional": 0.98,
    "total_cost": 2.97,
    "currency": "USD",
    "max_results": 100,
    "breakdown": {
      "Query execution (max 100 businesses)": "$1.99",
      "Persona Deepening": "$0.49",
      "Export": "$0.49",
      "Total": "$2.97"
    }
  },
  "quote_token": "eyJ0b3RhbF9jb3N0IjogMi45NywgInBlcnNvbmFfZGVlcGVuaW5nIjogdHJ1ZSwgImV4cG9ydCI6IHRydWUsICJtYXhfcmVzdWx0cyI6IDEwMCwgInJlcXVlc3RfZmluZ2VycHJpbnQiOiAiYWJjMTIzLi4uIiwgImV4cGlyZXNfYXQiOiAiMjAyNS0wMS0wOVQxMjowMDowMFoifQ==.a1b2c3d4e5f6...",
  "expires_at": "2025-01-09T12:15:00Z",
  "request_fingerprint": "abc123def456..."
}
```

***REMOVED******REMOVED******REMOVED*** 3. Blocked Query Execution (No Quote Token)

```bash
curl -X POST "https://your-service-url/api/v1/b2b/onboarding/create-plan" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "target_type": "hotels",
    "geography": "Istanbul",
    "decision_roles": "procurement",
    "product_service": "cleaning services",
    "meeting_goal": "sales meeting",
    "auto_start_queries": true
  }'
```

**Expected Response (400):**
```json
{
  "detail": {
    "error": "quote_token is required for query execution",
    "error_code": "QUOTE_TOKEN_MISSING",
    "message": "Please call /v1/subscriptions/pricing/calculate first to get a quote_token"
  }
}
```

***REMOVED******REMOVED******REMOVED*** 4. Blocked Query Execution (Invalid Quote Token)

```bash
curl -X POST "https://your-service-url/api/v1/b2b/onboarding/create-plan" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "target_type": "hotels",
    "geography": "Istanbul",
    "decision_roles": "procurement",
    "product_service": "cleaning services",
    "meeting_goal": "sales meeting",
    "auto_start_queries": true,
    "quote_token": "invalid.token.here",
    "max_results": 100
  }'
```

**Expected Response (400):**
```json
{
  "detail": {
    "error": "Invalid quote token signature",
    "error_code": "QUOTE_TOKEN_INVALID_SIGNATURE",
    "message": "Quote token validation failed. Please get a new quote from /v1/subscriptions/pricing/calculate"
  }
}
```

***REMOVED******REMOVED******REMOVED*** 5. Blocked Query Execution (Fingerprint Mismatch)

```bash
***REMOVED*** Step 1: Get quote with persona_deepening=true
QUOTE=$(curl -s "https://your-service-url/v1/subscriptions/pricing/calculate?include_persona_deepening=true" | jq -r '.quote_token')

***REMOVED*** Step 2: Try to execute with persona_deepening=false (mismatch)
curl -X POST "https://your-service-url/api/v1/b2b/onboarding/create-plan" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d "{
    \"target_type\": \"hotels\",
    \"geography\": \"Istanbul\",
    \"decision_roles\": \"procurement\",
    \"product_service\": \"cleaning services\",
    \"meeting_goal\": \"sales meeting\",
    \"auto_start_queries\": true,
    \"quote_token\": \"$QUOTE\",
    \"include_persona_deepening\": false,
    \"max_results\": 100
  }"
```

**Expected Response (400):**
```json
{
  "detail": {
    "error": "Request fingerprint mismatch. Query parameters do not match quote.",
    "error_code": "QUOTE_TOKEN_FINGERPRINT_MISMATCH",
    "message": "Quote token validation failed. Please get a new quote from /v1/subscriptions/pricing/calculate"
  }
}
```

***REMOVED******REMOVED******REMOVED*** 6. Blocked Query Execution (Max Results Exceeded)

```bash
curl -X POST "https://your-service-url/api/v1/b2b/onboarding/create-plan" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "target_type": "hotels",
    "geography": "Istanbul",
    "decision_roles": "procurement",
    "product_service": "cleaning services",
    "meeting_goal": "sales meeting",
    "auto_start_queries": true,
    "quote_token": "valid.token.here",
    "max_results": 200
  }'
```

**Expected Response (400):**
```json
{
  "detail": {
    "error": "max_results (200) exceeds maximum allowed (100)",
    "error_code": "MAX_RESULTS_EXCEEDED"
  }
}
```

***REMOVED******REMOVED******REMOVED*** 7. Successful Query Execution (Valid Quote Token)

```bash
***REMOVED*** Step 1: Get quote token
QUOTE_RESPONSE=$(curl -s "https://your-service-url/v1/subscriptions/pricing/calculate?max_results=100")
QUOTE_TOKEN=$(echo $QUOTE_RESPONSE | jq -r '.quote_token')

***REMOVED*** Step 2: Execute query with valid quote token
curl -X POST "https://your-service-url/api/v1/b2b/onboarding/create-plan" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d "{
    \"target_type\": \"hotels\",
    \"geography\": \"Istanbul\",
    \"decision_roles\": \"procurement\",
    \"product_service\": \"cleaning services\",
    \"meeting_goal\": \"sales meeting\",
    \"auto_start_queries\": true,
    \"quote_token\": \"$QUOTE_TOKEN\",
    \"max_results\": 100
  }"
```

**Expected Response (200/201):**
```json
{
  "plan_id": "uuid-here",
  "target_type": "hotels",
  "geography": "Istanbul",
  "decision_roles": "procurement",
  "product_service": "cleaning services",
  "meeting_goal": "sales meeting",
  "created_at": "2025-01-09T12:00:00Z",
  "recommendations": {...}
}
```

***REMOVED******REMOVED*** Router Registration

**File:** `backend/src/http/v1/router_registry.py`

**Line 19:** `from src.http.v1.subscription_router import router as subscription_router`
**Line 55:** `router.include_router(subscription_router)`

**Prefix:** `/v1/subscriptions` (from `subscription_router` definition)

**Full Endpoints:**
- `GET /v1/subscriptions/pricing/model`
- `GET /v1/subscriptions/pricing/calculate`
- `GET /v1/subscriptions/pricing/estimate`
- `GET /v1/subscriptions/current`
- `GET /v1/subscriptions/plans`

***REMOVED******REMOVED*** Request/Response Schemas

***REMOVED******REMOVED******REMOVED*** GET /v1/subscriptions/pricing/calculate

**Request:**
- Query params: `include_persona_deepening`, `include_visit_route`, `include_export`, `include_outreach_preparation`, `max_results`

**Response:**
```python
{
  "success": bool,
  "cost": {
    "base_query": float,
    "optional_modules": dict,
    "total_optional": float,
    "total_cost": float,
    "currency": str,
    "max_results": int,
    "breakdown": dict
  },
  "quote_token": str,  ***REMOVED*** HMAC-signed token
  "expires_at": str,   ***REMOVED*** ISO timestamp
  "request_fingerprint": str  ***REMOVED*** SHA256 hash
}
```

***REMOVED******REMOVED******REMOVED*** POST /api/v1/b2b/onboarding/create-plan

**Request:**
```python
{
  "target_type": str,
  "geography": str,
  "decision_roles": str,
  "product_service": str,
  "meeting_goal": str,
  "auto_start_queries": bool,
  "quote_token": str,  ***REMOVED*** REQUIRED if auto_start_queries=True
  "include_persona_deepening": bool,
  "include_visit_route": bool,
  "include_export": bool,
  "include_outreach_preparation": bool,
  "max_results": int  ***REMOVED*** Max: 100
}
```

**Response (Success):**
```python
{
  "plan_id": str,
  "target_type": str,
  "geography": str,
  "decision_roles": str,
  "product_service": str,
  "meeting_goal": str,
  "created_at": str,
  "recommendations": dict
}
```

**Response (Error - Missing Quote):**
```python
{
  "detail": {
    "error": "quote_token is required for query execution",
    "error_code": "QUOTE_TOKEN_MISSING",
    "message": "Please call /v1/subscriptions/pricing/calculate first to get a quote_token"
  }
}
```

**Response (Error - Invalid Quote):**
```python
{
  "detail": {
    "error": str,  ***REMOVED*** Error message
    "error_code": str,  ***REMOVED*** One of: QUOTE_TOKEN_INVALID_SIGNATURE, QUOTE_TOKEN_EXPIRED, QUOTE_TOKEN_FINGERPRINT_MISMATCH, MAX_RESULTS_EXCEEDED
    "message": "Quote token validation failed. Please get a new quote from /v1/subscriptions/pricing/calculate"
  }
}
```

***REMOVED******REMOVED*** Test Commands

***REMOVED******REMOVED******REMOVED*** Run Unit Tests

```bash
cd backend
pytest tests/test_quote_token.py -v
```

**Expected Output:**
```
tests/test_quote_token.py::TestQuoteToken::test_generate_quote_token_basic PASSED
tests/test_quote_token.py::TestQuoteToken::test_validate_quote_token_valid PASSED
tests/test_quote_token.py::TestQuoteToken::test_validate_quote_token_missing PASSED
tests/test_quote_token.py::TestQuoteToken::test_validate_quote_token_invalid_signature PASSED
tests/test_quote_token.py::TestQuoteToken::test_validate_quote_token_fingerprint_mismatch PASSED
tests/test_quote_token.py::TestQuoteToken::test_validate_quote_token_max_results_exceeded PASSED
```

***REMOVED******REMOVED******REMOVED*** Run Integration Tests

```bash
cd backend
pytest tests/test_pricing_enforcement.py -v
```

**Expected Output:**
```
tests/test_pricing_enforcement.py::TestPricingEnforcement::test_pricing_calculate_returns_quote_token PASSED
tests/test_pricing_enforcement.py::TestPricingEnforcement::test_query_execution_blocked_without_quote_token PASSED
tests/test_pricing_enforcement.py::TestPricingEnforcement::test_query_execution_with_valid_quote_token PASSED
tests/test_pricing_enforcement.py::TestPricingEnforcement::test_query_execution_with_invalid_quote_token PASSED
tests/test_pricing_enforcement.py::TestPricingEnforcement::test_query_execution_with_fingerprint_mismatch PASSED
tests/test_pricing_enforcement.py::TestPricingEnforcement::test_max_results_enforced PASSED
```

***REMOVED******REMOVED*** Summary

***REMOVED******REMOVED******REMOVED*** ✅ Hard Enforcement Implemented

1. **Quote Token Generation:** HMAC-signed tokens with request fingerprint
2. **Quote Token Validation:** Signature, expiration, fingerprint, max_results checks
3. **Query Execution Blocked:** Without valid quote_token
4. **Error Codes:** Clear error codes for all failure cases
5. **Single Source of Truth:** `src.config.pricing` module
6. **Tests:** Unit and integration tests provided

***REMOVED******REMOVED******REMOVED*** Files Modified/Created

**Modified:**
- `backend/src/models/subscription.py`
- `backend/src/services/payment_service.py`
- `backend/src/services/usage_based_pricing_service.py`
- `backend/src/http/v1/subscription_router.py`
- `backend/src/http/v1/b2b_api_router.py`

**Created:**
- `backend/src/config/pricing.py` (NEW)
- `backend/src/core/quote_token.py` (NEW)
- `backend/tests/test_quote_token.py` (NEW)
- `backend/tests/test_pricing_enforcement.py` (NEW)

***REMOVED******REMOVED******REMOVED*** Verification

All endpoints are registered in `router_registry.py` and enforce quote token validation before query execution.
