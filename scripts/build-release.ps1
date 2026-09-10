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
        Where-Object { $_.Name -like "plainchange-*.whl" -or $_.Name -like "plainchange-*.tar.gz" } |
        Sort-Object Name
    if ($artifacts.Count -ne 2) {
        throw "Expected exactly one PlainChange wheel and one source archive."
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
