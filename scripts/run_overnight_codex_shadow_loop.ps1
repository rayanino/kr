param(
    [string]$Distro = "Ubuntu-24.04",
    [string]$RuntimeDir = "~/kr-codex",
    [double]$CycleHours = 1.5,
    [int]$IntervalMinutes = 120,
    [double]$TotalHours = 8.0,
    [string]$SingleTask = "",
    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$resumeScript = Join-Path $repoRoot "scripts\overnight_codex_wsl_resume.ps1"

if (-not (Test-Path -LiteralPath $resumeScript)) {
    throw "Missing resume script at $resumeScript"
}

$startedAt = Get-Date
$deadline = $startedAt.AddHours($TotalHours)
$iteration = 0

Write-Host "=== KR Overnight Codex Shadow Loop ==="
Write-Host "Started:        $($startedAt.ToString('u'))"
Write-Host "Deadline:       $($deadline.ToString('u'))"
Write-Host "Cycle hours:    $CycleHours"
Write-Host "Interval mins:  $IntervalMinutes"
if ($SingleTask) {
    Write-Host "Single task:    $SingleTask"
}
Write-Host

while ((Get-Date) -lt $deadline) {
    $iteration += 1
    $cycleStart = Get-Date
    Write-Host "== Cycle $iteration =="
    Write-Host "Start: $($cycleStart.ToString('u'))"

    $args = @(
        "-ExecutionPolicy", "Bypass",
        "-File", $resumeScript,
        "-Distro", $Distro,
        "-RuntimeDir", $RuntimeDir,
        "-RunCycle",
        "-Hours", $CycleHours.ToString([System.Globalization.CultureInfo]::InvariantCulture)
    )
    if ($SingleTask) {
        $args += @("-SingleTask", $SingleTask)
    }
    if ($DryRun) {
        $args += "-DryRun"
    }

    & powershell @args
    $exitCode = $LASTEXITCODE
    $cycleEnd = Get-Date
    Write-Host "End:  $($cycleEnd.ToString('u'))"
    Write-Host "Exit: $exitCode"
    Write-Host

    if ($exitCode -ne 0) {
        Write-Host "Cycle failed; stopping overnight loop."
        exit $exitCode
    }

    $nextStart = $cycleStart.AddMinutes($IntervalMinutes)
    if ($nextStart -gt $deadline) {
        break
    }

    $sleepSeconds = [Math]::Floor(($nextStart - (Get-Date)).TotalSeconds)
    if ($sleepSeconds -gt 0) {
        Write-Host "Sleeping $sleepSeconds seconds until next cycle."
        Start-Sleep -Seconds $sleepSeconds
        Write-Host
    }
}

Write-Host "Shadow loop complete."
