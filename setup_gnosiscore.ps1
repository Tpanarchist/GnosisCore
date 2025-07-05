# Windows PowerShell Setup Script for GnosisCore
# Save this as setup_gnosiscore.ps1 in E:\Dev\GnosisCore

# Change to project directory
Set-Location E:\Dev\GnosisCore

# Create __init__.py files to ensure proper package structure
$initContent = '"""GnosisCore package"""'
$packages = @(
    "gnosiscore",
    "gnosiscore\primitives",
    "gnosiscore\planes", 
    "gnosiscore\memory",
    "gnosiscore\selfmap",
    "gnosiscore\transformation",
    "gnosiscore\messaging",
    "gnosiscore\plugins"
)

foreach ($package in $packages) {
    $initPath = Join-Path $package "__init__.py"
    if (-not (Test-Path $initPath)) {
        New-Item -ItemType File -Path $initPath -Force | Out-Null
        Set-Content -Path $initPath -Value $initContent
    }
}

Write-Host "Setup complete! __init__.py files created." -ForegroundColor Green
