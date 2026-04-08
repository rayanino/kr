param(
    [ValidateRange(0.1, 24.0)]
    [double]$CycleHours = 1.5,
    [ValidateRange(1, 1440)]
    [int]$IntervalMinutes = 120,
    [ValidateRange(0.1, 72.0)]
    [double]$TotalHours = 8.0,
    [string]$ManifestPath = "",
    [string]$SingleTask = "",
    [switch]$DryRun,
    [switch]$Resume,
    [switch]$SkipPreflight,
    [switch]$SkipOrchestratorPreflight
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-RepoRoot {
    return (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
}

function Resolve-PythonCommand {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RepoRoot
    )

    $candidates = @(
        (Join-Path $RepoRoot ".venv\Scripts\python.exe"),
        (Join-Path $RepoRoot ".venv\bin\python")
    )

    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate) {
            return $candidate
        }
    }

    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($null -ne $python) {
        return $python.Source
    }

    throw "Python is not available. Install Python or create a repo-local .venv before running the shadow loop."
}

$repoRoot = Resolve-RepoRoot
$python = Resolve-PythonCommand -RepoRoot $repoRoot
$launcher = Join-Path $repoRoot "scripts\start_codex_kr.ps1"
$orchestrator = Join-Path $repoRoot "scripts\overnight_codex_orchestrator.py"
$mutexName = "Local\KR-Overnight-Codex-Shadow-Loop"
$loopMutex = [System.Threading.Mutex]::new($false, $mutexName)
$hasHandle = $false

try {
    $hasHandle = $loopMutex.WaitOne(0, $false)
    if (-not $hasHandle) {
        throw "Another KR shadow loop instance is already running."
    }

    if (-not (Test-Path -LiteralPath $launcher)) {
        throw "Missing Windows launcher at $launcher"
    }
    if (-not (Test-Path -LiteralPath $orchestrator)) {
        throw "Missing overnight orchestrator at $orchestrator"
    }

    Push-Location $repoRoot
    try {
        if (-not $SkipPreflight) {
            $preflightArgs = @(
                "-ExecutionPolicy", "Bypass",
                "-File", $launcher,
                "-Profile", "kr_shadow",
                "-RunAuthPreflight",
                "-NoLaunch"
            )

            Write-Host "Running KR shadow-loop preflight..."
            & powershell @preflightArgs
            $preflightExit = $LASTEXITCODE
            if ($preflightExit -ne 0) {
                throw "KR shadow-loop preflight failed with exit code $preflightExit."
            }
            Write-Host
        }

        $startedAt = Get-Date
        $deadline = $startedAt.AddHours($TotalHours)
        $iteration = 0

        Write-Host "=== KR Overnight Codex Shadow Loop ==="
        Write-Host "Repo:            $repoRoot"
        Write-Host "Started:         $($startedAt.ToString('u'))"
        Write-Host "Deadline:        $($deadline.ToString('u'))"
        Write-Host "Cycle hours:     $CycleHours"
        Write-Host "Interval mins:   $IntervalMinutes"
        if ($ManifestPath) {
            Write-Host "Manifest path:   $ManifestPath"
        }
        if ($SingleTask) {
            Write-Host "Single task:     $SingleTask"
        }
        Write-Host

        while ((Get-Date) -lt $deadline) {
            $iteration += 1
            $cycleStart = Get-Date
            Write-Host "== Cycle $iteration =="
            Write-Host "Start: $($cycleStart.ToString('u'))"

            $cycleArgs = @(
                "scripts/overnight_codex_orchestrator.py",
                "--hours", $CycleHours.ToString([System.Globalization.CultureInfo]::InvariantCulture)
            )
            if ($ManifestPath) {
                $cycleArgs += @("--manifest", $ManifestPath)
            }
            if ($SingleTask) {
                $cycleArgs += @("--task", $SingleTask)
            }
            if ($DryRun) {
                $cycleArgs += "--dry-run"
            }
            if ($Resume) {
                $cycleArgs += "--resume"
            }
            if ($SkipOrchestratorPreflight) {
                $cycleArgs += "--skip-preflight"
            }

            & $python @cycleArgs
            $exitCode = $LASTEXITCODE
            $cycleEnd = Get-Date
            Write-Host "End:  $($cycleEnd.ToString('u'))"
            Write-Host "Exit: $exitCode"
            Write-Host

            if ($exitCode -ne 0) {
                throw "Shadow cycle $iteration failed with exit code $exitCode."
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
    }
    finally {
        Pop-Location
    }
}
finally {
    if ($hasHandle) {
        $loopMutex.ReleaseMutex() | Out-Null
    }
    $loopMutex.Dispose()
}
