# train_all.ps1
# =============
# Trains LoRA adaptors for all 4 language pairs sequentially.
# Run from the Triveni/ directory:
#     .\train_all.ps1
#
# Optional: quick smoke-test with small sample cap:
#     .\train_all.ps1 -MaxSamples 200 -NoEval

param(
    [int]$MaxSamples = 0,
    [switch]$NoEval
)

$ErrorActionPreference = "Stop"

$Pairs  = @("he", "eh", "es", "ht")
$Failed = @()

$StartTime = Get-Date
Write-Host ""
Write-Host "============================================================"
Write-Host "  Triveni - Training all 4 LoRA adaptors"
Write-Host "  Started : $StartTime"
Write-Host "============================================================"
Write-Host ""

foreach ($pair in $Pairs) {
    Write-Host "------------------------------------------------------------"
    Write-Host "  Training pair: $pair"
    Write-Host "------------------------------------------------------------"

    $extraArgs = @()

    if ($MaxSamples -gt 0) {
        $extraArgs += "--max_samples"
        $extraArgs += "$MaxSamples"
    }

    if ($NoEval) {
        $extraArgs += "--no_eval"
    }

    $pairStart = Get-Date
    try {
        python train.py --pair $pair @extraArgs
        $elapsed = (Get-Date) - $pairStart
        Write-Host ""
        Write-Host "  [OK] $pair finished in $($elapsed.ToString('hh\:mm\:ss'))"
    }
    catch {
        Write-Host ""
        Write-Host "  [FAIL] $pair failed: $_" -ForegroundColor Red
        $Failed += $pair
    }
    Write-Host ""
}

$TotalElapsed = (Get-Date) - $StartTime

Write-Host "============================================================"
Write-Host "  All pairs processed."
Write-Host "  Total time: $($TotalElapsed.ToString('hh\:mm\:ss'))"

if ($Failed.Count -gt 0) {
    Write-Host "  FAILED pairs: $($Failed -join ', ')" -ForegroundColor Red
    exit 1
} else {
    Write-Host "  All adaptors trained successfully." -ForegroundColor Green
}
Write-Host "============================================================"
