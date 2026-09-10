param(
    [string]$OutputDirectory = "dist"
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$destination = Join-Path $projectRoot $OutputDirectory

Push-Location $projectRoot
try {
    uv build --out-dir $destination
    $artifacts = Get-ChildItem -LiteralPath $destination -File |
        Where-Object { $_.Extension -in @(".whl", ".gz") } |
        Sort-Object Name
    if (-not $artifacts) {
        throw "No wheel or source archive was built."
    }
    $rows = foreach ($artifact in $artifacts) {
        $hash = (Get-FileHash -LiteralPath $artifact.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
        "$hash  $($artifact.Name)"
    }
    Set-Content -LiteralPath (Join-Path $destination "SHA256SUMS.txt") -Value $rows -Encoding utf8
    $rows
}
finally {
    Pop-Location
}
