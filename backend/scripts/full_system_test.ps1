***REMOVED*** Full System Test Script for SOAR B2B
***REMOVED*** Tests all endpoints and core functionality

$BASE = "http://127.0.0.1:8000"
$API_KEY = "dev-key-12345"  ***REMOVED*** Default dev API key
$testsPassed = 0
$testsFailed = 0

function Hit {
    param(
        [string]$method,
        [string]$url,
        [hashtable]$body = $null,
        [hashtable]$headers = $null
    )
    
    Write-Host ""
    Write-Host ">>> $method $url" -ForegroundColor Cyan
    
    try {
        $params = @{
            Method = $method
            Uri = "$BASE$url"
            ErrorAction = "Stop"
        }
        
        if ($headers) {
            $params.Headers = $headers
        }
        
        if ($body) {
            $params.Body = ($body | ConvertTo-Json -Depth 10)
            $params.ContentType = "application/json"
        }
        
        $response = Invoke-RestMethod @params
        Write-Host "[OK]" -ForegroundColor Green
        $script:testsPassed++
        return $response
    }
    catch {
        $statusCode = $null
        $responseBody = $null
        
        if ($_.Exception.Response) {
            $statusCode = $_.Exception.Response.StatusCode.value__
            try {
                $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
                $responseBody = $reader.ReadToEnd() | ConvertFrom-Json
                $reader.Close()
            } catch {
                $responseBody = "Could not parse response body"
            }
        }
        
        if ($statusCode) {
            Write-Host "[FAIL] Status: $statusCode" -ForegroundColor Red
        } else {
            Write-Host "[FAIL]" -ForegroundColor Red
        }
        
        if ($responseBody) {
            Write-Host "Response: $($responseBody | ConvertTo-Json -Compress)" -ForegroundColor Yellow
        }
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
        $script:testsFailed++
        return $null
    }
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SOAR B2B - Full System Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

***REMOVED*** CORE
Write-Host ""
Write-Host "--- CORE ENDPOINTS ---" -ForegroundColor Yellow
Hit GET "/healthz"
Hit GET "/readyz"
Hit GET "/metrics"

***REMOVED*** UI
Write-Host ""
Write-Host "--- UI PAGES ---" -ForegroundColor Yellow
Hit GET "/ui/tr/soarb2b_home.html"
Hit GET "/ui/tr/soarb2b_onboarding_5q.html"
Hit GET "/ui/tr/demo_showcase.html"

***REMOVED*** SUBSCRIPTIONS
Write-Host ""
Write-Host "--- SUBSCRIPTIONS ---" -ForegroundColor Yellow
Hit GET "/v1/subscriptions/plans"

***REMOVED*** ONBOARDING
Write-Host ""
Write-Host "--- ONBOARDING ---" -ForegroundColor Yellow
Hit POST "/api/v1/b2b/onboarding/create-plan" @{
    target_type = "3-5 star hotels"
    geography = "Dallas, TX"
    decision_roles = "Procurement Manager, Housekeeping Manager"
    product_service = "Professional cleaning supplies"
    meeting_goal = "initial-consultation"
} -headers @{"X-API-Key" = $API_KEY}

***REMOVED*** DEMO
Write-Host ""
Write-Host "--- DEMO ---" -ForegroundColor Yellow
Hit GET "/api/v1/b2b/demo/hotels" -headers @{"X-API-Key" = $API_KEY}

***REMOVED*** EXPLORER (NEW)
Write-Host ""
Write-Host "--- EXPLORER MODE (NEW) ---" -ForegroundColor Yellow
Hit GET "/api/v1/explorer/markets"

***REMOVED*** MATCHING
Write-Host ""
Write-Host "--- MATCHING ---" -ForegroundColor Yellow
Hit GET "/v1/matching/health"
Hit GET "/v1/matching/sample"

***REMOVED*** ANALYTICS
Write-Host ""
Write-Host "--- ANALYTICS ---" -ForegroundColor Yellow
Hit GET "/v1/analytics/health"
Hit POST "/v1/analytics/events" @{
    event_type = "page_view"
    entity_id = "test-entity-001"
    payload = @{
        page = "/test"
        timestamp = (Get-Date).ToUniversalTime().ToString("o")
    }
}

***REMOVED*** GROWTH
Write-Host ""
Write-Host "--- GROWTH ACTIVATION ---" -ForegroundColor Yellow
Hit GET "/v1/v1/growth-activation/health"
Hit POST "/v1/v1/growth-activation/v1/growth/evaluate" @{
    supplier = @{
        supplier_id = "test-supplier-001"
        name = "Test Supplier"
        category = "hvac"
        address = "123 Test St, Istanbul"
        lat = 41.0082
        lon = 28.9784
        phone = "+90 555 123 4567"
        email = "test@example.com"
    }
    target_lat = 41.0082
    target_lon = 28.9784
    radius_meters = 50.0
    context = @{}
}

***REMOVED*** PRODUCTS
Write-Host ""
Write-Host "--- PRODUCTS ---" -ForegroundColor Yellow
Hit GET "/v1/v1/products/health"
Hit POST "/v1/v1/products/create" @{
    name = "Sample Blanket"
    identification_type = "name"
    description = "Test product"
    category = "textiles"
}

***REMOVED*** CAMPAIGNS
Write-Host ""
Write-Host "--- CAMPAIGNS ---" -ForegroundColor Yellow
Hit GET "/v1/v1/campaigns/health"
Hit POST "/v1/v1/campaigns/create" @{
    name = "Test Campaign"
    ad_content_type = "text"
    ad_content = "Test ad content"
    ad_type = "location-based"
    target = @{
        company_ids = @()
        personnel_ids = @()
        location_ids = @()
        location_polygons = @()
        filters = $null
    }
}

***REMOVED*** DISCOVERY
Write-Host ""
Write-Host "--- DISCOVERY ---" -ForegroundColor Yellow
Hit GET "/v1/v1/discovery/health"

***REMOVED*** AUTH
Write-Host ""
Write-Host "--- AUTHENTICATION ---" -ForegroundColor Yellow
Hit GET "/v1/auth/health"
Hit GET "/v1/auth/config"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TEST SUMMARY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Tests Passed: $testsPassed" -ForegroundColor Green
Write-Host "Tests Failed: $testsFailed" -ForegroundColor $(if ($testsFailed -gt 0) { "Red" } else { "Green" })
Write-Host ""

if ($testsFailed -eq 0) {
    Write-Host "[SUCCESS] ALL TESTS PASSED!" -ForegroundColor Green
} else {
    Write-Host "[WARNING] Some tests failed. Check errors above." -ForegroundColor Yellow
}

Write-Host ""
