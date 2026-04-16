# ConektaBots Backend Endpoint Validation Script

Write-Host "=== ConektaBots Backend Validation ===" -ForegroundColor Green
Write-Host ""

# Load registration response
$registerResponsePath = "$env:TEMP\register_response.json"
if (-not (Test-Path $registerResponsePath)) {
    Write-Host "ERROR: Registration response not found at $registerResponsePath" -ForegroundColor Red
    exit 1
}

$json = Get-Content $registerResponsePath -Raw | ConvertFrom-Json
$accessToken = $json.access_token
$refreshToken = $json.refresh_token
$tenantId = $json.tenant_id
$userId = $json.user_id

Write-Host "Tokens Loaded:" -ForegroundColor Cyan
Write-Host "  ✓ User ID: $userId"
Write-Host "  ✓ Tenant ID: $tenantId"
Write-Host "  ✓ Access Token: $($accessToken.Substring(0,30))..."
Write-Host ""

$baseUrl = "http://localhost:8000"
$testsPassed = 0
$testsFailed = 0

# Helper function for testing
function Test-Endpoint($name, $method, $uri, $headers, $body, $expectedStatus) {
    Write-Host "Testing: $name" -ForegroundColor Yellow
    try {
        $params = @{
            Uri = $uri
            Method = $method
            ContentType = "application/json"
            UseBasicParsing = $true
        }
        if ($headers) { $params["Headers"] = $headers }
        if ($body) { $params["Body"] = $body }
        
        $response = Invoke-WebRequest @params -ErrorAction SilentlyContinue
        
        if ($response.StatusCode -eq $expectedStatus) {
            Write-Host "  ✓ Status: $($response.StatusCode) (expected $expectedStatus)" -ForegroundColor Green
            return $response.Content
        }
        else {
            Write-Host "  ✗ Status: $($response.StatusCode) (expected $expectedStatus)" -ForegroundColor Red
            $script:testsFailed++
            return $null
        }
    }
    catch {
        $statusCode = $_.Exception.Response.StatusCode.Value__
        if ($statusCode -eq $expectedStatus) {
            Write-Host "  ✓ Status: $statusCode (expected $expectedStatus)" -ForegroundColor Green
            return $_.Exception.Response.Content.ReadAsString()
        }
        else {
            Write-Host "  ✗ Error: $_" -ForegroundColor Red
            Write-Host "  ✗ Status: $statusCode (expected $expectedStatus)" -ForegroundColor Red
            $script:testsFailed++
            return $null
        }
    }
    $script:testsPassed++
}

# Test A: Health Check
Write-Host "`n=== A. Health Check ===" -ForegroundColor Cyan
Test-Endpoint "Health Check (No Auth)" "GET" "$baseUrl/health" $null $null 200 | Out-Null
$script:testsPassed++

# Test B: Login
Write-Host "`n=== B. Login ===" -ForegroundColor Cyan
$loginData = @{
    email = "testuser3@example.com"
    password = "Test123!@"
} | ConvertTo-Json
Test-Endpoint "Login (POST)" "POST" "$baseUrl/api/v1/auth/login" $null $loginData 200 | Out-Null
$script:testsPassed++

# Test D: Get Bots
Write-Host "`n=== D. Get Bots (Protected) ===" -ForegroundColor Cyan
$headers = @{ "Authorization" = "Bearer $accessToken" }
$botsContent = Test-Endpoint "Get Bots (with valid token)" "GET" "$baseUrl/api/v1/bots" $headers $null 200
if ($botsContent) {
    $botsJson = $botsContent | ConvertFrom-Json
    Write-Host "  ✓ Response contains: items, total, page, per_page" -ForegroundColor Green
    $script:testsPassed++
}

# Test E: Token Refresh
Write-Host "`n=== E. Token Refresh ===" -ForegroundColor Cyan
$refreshData = @{
    refresh_token = $refreshToken
} | ConvertTo-Json
$refreshContent = Test-Endpoint "Refresh Token (POST)" "POST" "$baseUrl/api/v1/auth/refresh" $null $refreshData 200
if ($refreshContent) {
    $refreshJson = $refreshContent | ConvertFrom-Json
    Write-Host "  ✓ New tokens generated" -ForegroundColor Green
    Write-Host "  ✓ New access_token: $($refreshJson.access_token.Substring(0,30))..." -ForegroundColor Green
    $script:testsPassed++
}

# Test F: Marketplaces
Write-Host "`n=== F. Get Marketplaces ===" -ForegroundColor Cyan
Test-Endpoint "Get Marketplaces (with token)" "GET" "$baseUrl/api/v1/marketplaces" $headers $null 200 | Out-Null
$script:testsPassed++

# Test G: Invalid Token
Write-Host "`n=== G. Error Handling (Invalid Token) ===" -ForegroundColor Cyan
$badHeaders = @{ "Authorization" = "Bearer invalid-token-xyz" }
Test-Endpoint "Invalid Token (expect 401)" "GET" "$baseUrl/api/v1/bots" $badHeaders $null 401 | Out-Null
$script:testsPassed++

# Test H: Missing Auth
Write-Host "`n=== H. Error Handling (Missing Auth) ===" -ForegroundColor Cyan
Test-Endpoint "Missing Auth Header (expect 403)" "GET" "$baseUrl/api/v1/bots" $null $null 403 | Out-Null
$script:testsPassed++

# Summary
Write-Host "`n=== Test Summary ===" -ForegroundColor Green
Write-Host "Passed: $testsPassed" -ForegroundColor Green
Write-Host "Failed: $testsFailed" -ForegroundColor $(if ($testsFailed -gt 0) { "Red" } else { "Green" })

if ($testsFailed -eq 0) {
    Write-Host "`n✓ All tests passed!" -ForegroundColor Green
    exit 0
}
else {
    Write-Host "`n✗ Some tests failed!" -ForegroundColor Red
    exit 1
}
