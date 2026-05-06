***REMOVED*** SOAR B2B Case Library - Schema Documentation

***REMOVED******REMOVED*** Overview

The Case Library stores structured case study data in JSON format. Each case represents a real-world implementation of SOAR B2B for a specific customer scenario, with results and metrics.

***REMOVED******REMOVED*** Schema Structure

***REMOVED******REMOVED******REMOVED*** Top-Level Fields

```json
{
  "meta": { ... },
  "objective": { ... },
  "target_profile": { ... },
  "sequence": { ... },
  "outputs": { ... },
  "analysis_result": { ... },
  "usage_flags": { ... }
}
```

***REMOVED******REMOVED******REMOVED*** 1. Meta Section

**Purpose:** Case identification and metadata

```json
{
  "meta": {
    "case_id": "HOTEL_CLEANING_TR_NATIONWIDE",
    "title": "Case Title",
    "sector": "Hospitality",
    "region": "TR",
    "access_level": "public|sales|internal",
    "created_at": "2025-01-15T10:00:00Z",
    "updated_at": "2025-01-15T10:00:00Z"
  }
}
```

**Fields:**
- `case_id` (string, required): Unique identifier, format: `CATEGORY_REGION_TYPE`
- `title` (string, required): Human-readable title
- `sector` (string, required): Industry sector (e.g., "Hospitality", "Healthcare")
- `region` (string, required): Geographic region code (e.g., "TR", "US", "EU")
- `access_level` (string, required): One of "public", "sales", "internal"
- `created_at` (string, ISO 8601): Creation timestamp
- `updated_at` (string, ISO 8601): Last update timestamp

***REMOVED******REMOVED******REMOVED*** 2. Objective Section

**Purpose:** Business goal description

```json
{
  "objective": {
    "paragraph": "Full paragraph description...",
    "one_liner": "Single sentence objective"
  }
}
```

**Fields:**
- `paragraph` (string): Full paragraph describing what the customer wanted
- `one_liner` (string): Single sentence clear objective

***REMOVED******REMOVED******REMOVED*** 3. Target Profile Section

**Purpose:** Define target audience

```json
{
  "target_profile": {
    "company_type": "3-5 star hotels",
    "geography": "Turkey nationwide",
    "decision_roles": ["Procurement Manager", "Housekeeping Director"]
  }
}
```

**Fields:**
- `company_type` (string): Type of target companies
- `geography` (string): Geographic scope description
- `decision_roles` (array of strings): List of decision-maker roles

***REMOVED******REMOVED******REMOVED*** 4. Sequence Section

**Purpose:** 5-step communication flow summary

```json
{
  "sequence": {
    "step_01": "Target: Verified company list created",
    "step_02": "Identify: Decision-maker roles mapped",
    "step_03": "Expose: Multi-channel visibility launched",
    "step_04": "Engage: High-intent outreach initiated",
    "step_05": "Meet: Confirmed meetings booked"
  }
}
```

**Fields:**
- `step_01` through `step_05` (strings): Summary of each step

***REMOVED******REMOVED******REMOVED*** 5. Outputs Section

**Purpose:** What was delivered to the customer

```json
{
  "outputs": {
    "companies_targeted": "280-320 verified hotel properties",
    "personas_targeted": "Procurement, housekeeping decision-makers",
    "locations_targeted": "Istanbul, Ankara, Antalya, Izmir",
    "campaigns_launched": "LinkedIn, Google Ads, Meta campaigns"
  }
}
```

***REMOVED******REMOVED******REMOVED*** 6. Analysis Result Section

**Purpose:** Standard advertising and funnel metrics

```json
{
  "analysis_result": {
    "impressions": {"min": 85000, "max": 120000, "unit": "number"},
    "reach": {"min": 42000, "max": 58000, "unit": "number"},
    "clicks": {"min": 1800, "max": 2400, "unit": "number"},
    "ctr": {"min": 2.1, "max": 2.8, "unit": "percent"},
    "cpc": {"min": 0.35, "max": 0.52, "unit": "USD"},
    "cpm": {"min": 12.5, "max": 18.2, "unit": "USD"},
    "spend": {"min": 630, "max": 1250, "unit": "USD"},
    "landing_views": {"min": 1450, "max": 1950, "unit": "number"},
    "lead_form_opens": {"min": 380, "max": 520, "unit": "number"},
    "lead_form_submits": {"min": 95, "max": 135, "unit": "number"},
    "meeting_requests": {"min": 24, "max": 38, "unit": "number"},
    "meetings_booked": {"min": 18, "max": 28, "unit": "number"},
    "qualified_meetings": {"min": 14, "max": 22, "unit": "number"},
    "conversion_rates": {
      "click_to_landing": {"min": 78.5, "max": 82.3, "unit": "percent"},
      "landing_to_lead": {"min": 24.2, "max": 28.7, "unit": "percent"},
      "lead_to_meeting": {"min": 18.9, "max": 23.5, "unit": "percent"}
    },
    "active_leads": {"min": 95, "max": 135, "unit": "number"},
    "passive_leads": {"min": 285, "max": 385, "unit": "number"},
    "timeframe_days": {"min": 45, "max": 75, "unit": "days"},
    "notes": "Additional analysis notes"
  }
}
```

**Metric Fields:**
All numeric metrics support range values with `min`, `max`, and `unit`:
- `impressions`, `reach`, `clicks` (number)
- `ctr` (percent)
- `cpc`, `cpm`, `spend` (USD)
- `landing_views`, `lead_form_opens`, `lead_form_submits` (number)
- `meeting_requests`, `meetings_booked`, `qualified_meetings` (number)
- `conversion_rates` (object with nested percent values)
- `active_leads`, `passive_leads` (number)
- `timeframe_days` (days)
- `notes` (string, optional)

***REMOVED******REMOVED******REMOVED*** 7. Usage Flags Section

**Purpose:** Indicate where this case can be used

```json
{
  "usage_flags": {
    "sales_demo": true,
    "onboarding": true,
    "pricing": true,
    "sponsor_ready": true,
    "seo_ready": true
  }
}
```

**Fields:** All booleans
- `sales_demo`: Use in sales demonstrations
- `onboarding`: Show during onboarding
- `pricing`: Use for pricing justification
- `sponsor_ready`: Ready for sponsor integration
- `seo_ready`: Ready for SEO/public marketing

***REMOVED******REMOVED*** Access Level Rules

***REMOVED******REMOVED******REMOVED*** Public Level
- Values must be ranges or rounded numbers
- No brand names or customer identifiers
- Suitable for external marketing
- All numbers should be rounded for anonymity

***REMOVED******REMOVED******REMOVED*** Sales/Demo Level
- More detailed than public
- May include approximate brand references
- Sector-specific focus
- Meeting-focused metrics

***REMOVED******REMOVED******REMOVED*** Internal Level
- Exact performance numbers allowed
- Full brand/customer context
- Complete analysis notes
- Used for product development reference

***REMOVED******REMOVED*** File Naming Convention

Files must be named: `{case_id}.json`

Example: `HOTEL_CLEANING_TR_NATIONWIDE.json`

***REMOVED******REMOVED*** API Endpoints

***REMOVED******REMOVED******REMOVED*** GET /api/v1/b2b/case-library/cases

**Query Parameters:**
- `access_level` (optional): Filter by access level (public|sales|internal)
- `sector` (optional): Filter by sector
- `region` (optional): Filter by region

**Response:**
```json
{
  "cases": [...]
}
```

***REMOVED******REMOVED******REMOVED*** GET /api/v1/b2b/case-library/cases/{case_id}

**Response:** Full case object

***REMOVED******REMOVED******REMOVED*** GET /api/v1/b2b/case-library/cases/{case_id}/analysis

**Response:**
```json
{
  "case_id": "HOTEL_CLEANING_TR_NATIONWIDE",
  "access_level": "public",
  "analysis_result": { ... }
}
```

***REMOVED******REMOVED*** Caching

Case files are cached in-memory for 60 seconds to reduce disk reads. Cache is invalidated automatically after TTL.

***REMOVED******REMOVED*** Validation Rules

1. `case_id` must be unique and stable
2. `access_level` must be one of: public, sales, internal
3. All numeric metrics in `analysis_result` must have `min` and `max` for public/sales levels
4. Public cases must not contain brand names
5. Dates must be in ISO 8601 format

***REMOVED******REMOVED*** Migration from Legacy Format

Legacy cases use `metadata`, `business_objective`, `results`, `usage` fields. The API supports both formats and will normalize responses. New cases should use the standard schema defined above.
