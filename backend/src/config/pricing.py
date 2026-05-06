"""
CONFIG: pricing
PURPOSE: Single source of truth for usage-based pricing constants
ENCODING: UTF-8 WITHOUT BOM

All pricing values are defined here. UI and API must read from this module.
"""

# Base Costs (USD)
ACCOUNT_ACTIVATION_FEE = 0.98   # Monthly recurring
QUERY_EXECUTION_COST = 1.99     # Per query (max 100 businesses)

# Optional Modules (Per Query, USD)
OPTIONAL_MODULES = {
    "persona_deepening": 0.49,
    "visit_route": 0.99,         # Max 20 stops
    "export": 0.49,              # CSV/PDF/CRM
    "outreach_preparation": 0.99
}

# Query Limits
MAX_RESULTS_PER_QUERY = 100     # Hard limit for standard users
MAX_VISIT_STOPS = 20            # Max stops in visit route

# Quote Token Configuration
QUOTE_TOKEN_EXPIRY_MINUTES = 15   # Quote tokens expire after 15 minutes
QUOTE_SECRET_ENV_VAR = "QUOTE_SECRET"   # Environment variable for quote signing secret

# Pricing Model Dictionary (for API responses)
PRICING_MODEL = {
    "account_activation": {
        "fee": ACCOUNT_ACTIVATION_FEE,
        "period": "monthly",
        "currency": "USD"
    },
    "query_execution": {
        "cost": QUERY_EXECUTION_COST,
        "max_results": MAX_RESULTS_PER_QUERY,
        "currency": "USD"
    },
    "optional_modules": {
        "persona_deepening": {
            "cost": OPTIONAL_MODULES["persona_deepening"],
            "currency": "USD"
        },
        "visit_route": {
            "cost": OPTIONAL_MODULES["visit_route"],
            "max_stops": MAX_VISIT_STOPS,
            "currency": "USD"
        },
        "export": {
            "cost": OPTIONAL_MODULES["export"],
            "currency": "USD"
        },
        "outreach_preparation": {
            "cost": OPTIONAL_MODULES["outreach_preparation"],
            "currency": "USD"
        }
    }
}
