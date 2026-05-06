***REMOVED*** PS Verification Commands - Case Library

***REMOVED******REMOVED*** Prerequisites

Server must be running:
```powershell
cd backend
.\scripts\run_local.ps1
```

Wait for server startup message: "Uvicorn running on http://127.0.0.1:8000"

***REMOVED******REMOVED*** Verification Steps

***REMOVED******REMOVED******REMOVED*** 1. Check OpenAPI Schema Contains Case Library Endpoints

```powershell
$response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/openapi.json" -UseBasicParsing
$openapi = $response.Content | ConvertFrom-Json
$paths = $openapi.PSObject.Properties.Name

Write-Host "Checking for case library endpoints..." -ForegroundColor Cyan
$casesEndpoint = $paths | Where-Object { $_ -like "*/case-library/cases" }
$analysisEndpoint = $paths | Where-Object { $_ -like "*/case-library/cases/{case_id}/analysis" }

if ($casesEndpoint -and $analysisEndpoint) {
    Write-Host "SUCCESS: Both endpoints found in OpenAPI" -ForegroundColor Green
    Write-Host "  - $casesEndpoint" -ForegroundColor Green
    Write-Host "  - $analysisEndpoint" -ForegroundColor Green
} else {
    Write-Host "FAILED: Endpoints missing from OpenAPI" -ForegroundColor Red
    if (-not $casesEndpoint) { Write-Host "  - Missing: /api/v1/b2b/case-library/cases" -ForegroundColor Red }
    if (-not $analysisEndpoint) { Write-Host "  - Missing: /api/v1/b2b/case-library/cases/{case_id}/analysis" -ForegroundColor Red }
}
```

**Expected SUCCESS Output:**
```
Checking for case library endpoints...
SUCCESS: Both endpoints found in OpenAPI
  - /api/v1/b2b/case-library/cases
  - /api/v1/b2b/case-library/cases/{case_id}/analysis
```

***REMOVED******REMOVED******REMOVED*** 2. Test TR Case Endpoint (Returns 200)

```powershell
$headers = @{"X-API-Key" = "dev-key-12345"}
$caseId = "HOTEL_CLEANING_TR_NATIONWIDE"

try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/v1/b2b/case-library/cases/$caseId" -Headers $headers -UseBasicParsing -ErrorAction Stop
    $case = $response.Content | ConvertFrom-Json
    
    Write-Host "SUCCESS: TR case endpoint returns 200" -ForegroundColor Green
    Write-Host "  Status Code: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "  Case ID: $($case.meta.case_id)" -ForegroundColor Green
    Write-Host "  Title: $($case.meta.title)" -ForegroundColor Green
    Write-Host "  Region: $($case.meta.region)" -ForegroundColor Green
    Write-Host "  Access Level: $($case.meta.access_level)" -ForegroundColor Green
    
    if ($case.meta.region -eq "TR" -and $case.meta.access_level -eq "public") {
        Write-Host "  Validation: Case data structure correct" -ForegroundColor Green
    } else {
        Write-Host "  WARNING: Case data structure mismatch" -ForegroundColor Yellow
    }
} catch {
    Write-Host "FAILED: TR case endpoint error" -ForegroundColor Red
    Write-Host "  Status: $($_.Exception.Response.StatusCode.value__)" -ForegroundColor Red
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
}
```

**Expected SUCCESS Output:**
```
SUCCESS: TR case endpoint returns 200
  Status Code: 200
  Case ID: HOTEL_CLEANING_TR_NATIONWIDE
  Title: Hotel Cleaning Supplies - Turkey Nationwide
  Region: TR
  Access Level: public
  Validation: Case data structure correct
```

***REMOVED******REMOVED******REMOVED*** 3. Test Analysis Endpoint (Returns 200)

```powershell
$headers = @{"X-API-Key" = "dev-key-12345"}
$caseId = "HOTEL_CLEANING_TR_NATIONWIDE"

try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/v1/b2b/case-library/cases/$caseId/analysis" -Headers $headers -UseBasicParsing -ErrorAction Stop
    $analysis = $response.Content | ConvertFrom-Json
    
    Write-Host "SUCCESS: Analysis endpoint returns 200" -ForegroundColor Green
    Write-Host "  Status Code: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "  Case ID: $($analysis.case_id)" -ForegroundColor Green
    Write-Host "  Access Level: $($analysis.access_level)" -ForegroundColor Green
    
    if ($analysis.analysis_result) {
        Write-Host "  Analysis Result Keys: $($analysis.analysis_result.PSObject.Properties.Name -join ', ')" -ForegroundColor Green
        
        $hasMetrics = $false
        if ($analysis.analysis_result.impressions) { $hasMetrics = $true; Write-Host "    - impressions: $($analysis.analysis_result.impressions.min) - $($analysis.analysis_result.impressions.max)" -ForegroundColor Gray }
        if ($analysis.analysis_result.clicks) { $hasMetrics = $true; Write-Host "    - clicks: $($analysis.analysis_result.clicks.min) - $($analysis.analysis_result.clicks.max)" -ForegroundColor Gray }
        if ($analysis.analysis_result.meeting_requests) { $hasMetrics = $true; Write-Host "    - meeting_requests: $($analysis.analysis_result.meeting_requests.min) - $($analysis.analysis_result.meeting_requests.max)" -ForegroundColor Gray }
        
        if ($hasMetrics) {
            Write-Host "  Validation: Analysis result contains metrics" -ForegroundColor Green
        } else {
            Write-Host "  WARNING: Analysis result missing expected metrics" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  ERROR: Analysis result missing from response" -ForegroundColor Red
    }
} catch {
    Write-Host "FAILED: Analysis endpoint error" -ForegroundColor Red
    Write-Host "  Status: $($_.Exception.Response.StatusCode.value__)" -ForegroundColor Red
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
}
```

**Expected SUCCESS Output:**
```
SUCCESS: Analysis endpoint returns 200
  Status Code: 200
  Case ID: HOTEL_CLEANING_TR_NATIONWIDE
  Access Level: public
  Analysis Result Keys: impressions, reach, clicks, ctr, cpc, cpm, spend, landing_views, lead_form_opens, lead_form_submits, meeting_requests, meetings_booked, qualified_meetings, conversion_rates, active_leads, passive_leads, timeframe_days, notes
    - impressions: 85000 - 120000
    - clicks: 1800 - 2400
    - meeting_requests: 24 - 38
  Validation: Analysis result contains metrics
```

***REMOVED******REMOVED******REMOVED*** 4. Test Case Library List with Filters

```powershell
$headers = @{"X-API-Key" = "dev-key-12345"}

Write-Host "Testing case library filters..." -ForegroundColor Cyan

***REMOVED*** Test public cases
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/v1/b2b/case-library/cases?access_level=public" -Headers $headers -UseBasicParsing -ErrorAction Stop
    $data = $response.Content | ConvertFrom-Json
    Write-Host "SUCCESS: Public cases endpoint returns $($data.cases.Count) cases" -ForegroundColor Green
} catch {
    Write-Host "FAILED: Public cases endpoint error: $($_.Exception.Message)" -ForegroundColor Red
}

***REMOVED*** Test TR region filter
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/v1/b2b/case-library/cases?access_level=public&region=TR" -Headers $headers -UseBasicParsing -ErrorAction Stop
    $data = $response.Content | ConvertFrom-Json
    $trCases = $data.cases | Where-Object { ($_.meta.region -eq "TR") -or ($_.metadata.region -eq "TR") }
    Write-Host "SUCCESS: TR region filter returns $($trCases.Count) TR cases" -ForegroundColor Green
} catch {
    Write-Host "FAILED: TR region filter error: $($_.Exception.Message)" -ForegroundColor Red
}

***REMOVED*** Test Hospitality sector filter
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/v1/b2b/case-library/cases?access_level=public&sector=Hospitality" -Headers $headers -UseBasicParsing -ErrorAction Stop
    $data = $response.Content | ConvertFrom-Json
    $hospitalityCases = $data.cases | Where-Object { ($_.meta.sector -eq "Hospitality") -or ($_.metadata.sector -eq "Hospitality") }
    Write-Host "SUCCESS: Hospitality sector filter returns $($hospitalityCases.Count) cases" -ForegroundColor Green
} catch {
    Write-Host "FAILED: Hospitality sector filter error: $($_.Exception.Message)" -ForegroundColor Red
}
```

**Expected SUCCESS Output:**
```
Testing case library filters...
SUCCESS: Public cases endpoint returns 2 cases
SUCCESS: TR region filter returns 1 TR cases
SUCCESS: Hospitality sector filter returns 2 cases
```

***REMOVED******REMOVED*** All-in-One Verification Script

```powershell
***REMOVED*** Run all verifications
$scriptPath = Join-Path $PSScriptRoot "VERIFICATION_CASE_LIBRARY.md"
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "Case Library Verification" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

***REMOVED*** Check OpenAPI
Write-Host "[1/4] Checking OpenAPI schema..." -ForegroundColor Yellow
***REMOVED*** (Copy OpenAPI check from Step 1 above)

***REMOVED*** Check TR case
Write-Host "[2/4] Testing TR case endpoint..." -ForegroundColor Yellow
***REMOVED*** (Copy TR case check from Step 2 above)

***REMOVED*** Check analysis endpoint
Write-Host "[3/4] Testing analysis endpoint..." -ForegroundColor Yellow
***REMOVED*** (Copy analysis check from Step 3 above)

***REMOVED*** Check filters
Write-Host "[4/4] Testing filters..." -ForegroundColor Yellow
***REMOVED*** (Copy filter checks from Step 4 above)

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "Verification Complete" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
```

***REMOVED******REMOVED*** Expected Final Status

All 4 verification steps should show "SUCCESS" messages with green output.

If any step fails, check:
1. Server is running on port 8000
2. API key is correct: "dev-key-12345"
3. Case file exists: `backend/src/ui/case_library/hotel_cleaning_tr_nationwide.json`
4. No syntax errors in router code
