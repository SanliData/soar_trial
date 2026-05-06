***REMOVED*** REMOVE_LOCALHOST_POWERSHELL.ps1
***REMOVED*** PURPOSE: Remove ALL localhost:7243 API calls from production UI files (Windows/PowerShell)
***REMOVED*** ENCODING: UTF-8 WITHOUT BOM

param(
    [string]$BaseDir = "backend\src\ui"
)

Write-Host "🔧 Removing ALL localhost API calls from production UI files" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path $BaseDir)) {
    Write-Host "❌ ERROR: Directory not found: $BaseDir" -ForegroundColor Red
    Write-Host "Usage: .\REMOVE_LOCALHOST_POWERSHELL.ps1 [-BaseDir 'path']"
    exit 1
}

Write-Host "📁 Scanning directory: $BaseDir" -ForegroundColor Yellow
Write-Host ""

***REMOVED*** Count total occurrences before removal
$totalBefore = (Select-String -Path "$BaseDir\*.html" -Pattern "127\.0\.0\.1:7243" -Recurse -ErrorAction SilentlyContinue | Measure-Object).Count
Write-Host "📊 Found $totalBefore localhost call(s) before removal" -ForegroundColor Yellow
Write-Host ""

if ($totalBefore -eq 0) {
    Write-Host "✅ No localhost calls found. Files are already clean." -ForegroundColor Green
    exit 0
}

***REMOVED*** Find all HTML files
$htmlFiles = Get-ChildItem -Path $BaseDir -Filter "*.html" -Recurse -File

$fixedCount = 0
$totalRemoved = 0

foreach ($file in $htmlFiles) {
    $content = Get-Content $file.FullName -Raw
    $count = ([regex]::Matches($content, "127\.0\.0\.1:7243")).Count
    
    if ($count -gt 0) {
        Write-Host "🔍 Found $count localhost call(s) in: $($file.Name)" -ForegroundColor Yellow
        
        ***REMOVED*** Create backup
        $backupPath = "$($file.FullName).bak"
        Copy-Item $file.FullName $backupPath
        
        ***REMOVED*** Remove lines containing localhost:7243
        $lines = Get-Content $file.FullName
        $newLines = $lines | Where-Object { $_ -notmatch "127\.0\.0\.1:7243" }
        
        ***REMOVED*** Also remove surrounding comment blocks
        $cleaned = @()
        $skipNext = $false
        foreach ($line in $newLines) {
            if ($line -match "// ***REMOVED***region agent log") {
                $skipNext = $true
                continue
            }
            if ($skipNext -and $line -match "// ***REMOVED***endregion") {
                $skipNext = $false
                continue
            }
            if (-not $skipNext) {
                $cleaned += $line
            }
        }
        
        ***REMOVED*** Write cleaned content
        $cleaned | Set-Content $file.FullName -NoNewline
        
        ***REMOVED*** Verify removal
        $remaining = ([regex]::Matches((Get-Content $file.FullName -Raw), "127\.0\.0\.1:7243")).Count
        
        if ($remaining -eq 0) {
            Write-Host "  ✅ Removed $count call(s) from $($file.Name)" -ForegroundColor Green
            $fixedCount++
            $totalRemoved += $count
            ***REMOVED*** Remove backup if successful
            Remove-Item $backupPath -ErrorAction SilentlyContinue
        } else {
            Write-Host "  ⚠️  WARNING: $remaining call(s) still remain in $($file.Name)" -ForegroundColor Red
            ***REMOVED*** Restore backup
            Move-Item $backupPath $file.FullName -Force
        }
    }
}

Write-Host ""
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "Summary:"
Write-Host "  Files scanned: $($htmlFiles.Count)"
Write-Host "  Files with localhost calls: $fixedCount"
Write-Host "  Total calls removed: $totalRemoved"
Write-Host ""

***REMOVED*** Final verification
$totalAfter = (Select-String -Path "$BaseDir\*.html" -Pattern "127\.0\.0\.1:7243" -Recurse -ErrorAction SilentlyContinue | Measure-Object).Count

if ($totalAfter -eq 0) {
    Write-Host "✅ SUCCESS: All localhost calls removed!" -ForegroundColor Green
    Write-Host "✅ Verification: No remaining localhost calls found" -ForegroundColor Green
} else {
    Write-Host "⚠️  WARNING: $totalAfter localhost call(s) still remain" -ForegroundColor Red
    Write-Host "   Run 'Select-String -Path `"$BaseDir\*.html`" -Pattern `"127.0.0.1:7243`" -Recurse' to find them" -ForegroundColor Yellow
}

Write-Host "==============================================" -ForegroundColor Cyan
