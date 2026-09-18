param(
    [string]$OutputDirectory = "dist\windows-portable",
    [switch]$Console
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$destination = Join-Path $projectRoot $OutputDirectory
$staging = Join-Path $destination "staging"
$work = Join-Path $destination "work"
$spec = Join-Path $destination "spec"
$executable = Join-Path $staging "PlainChange.exe"
$archive = Join-Path $destination "PlainChange-windows-x64-portable.zip"
$consoleMode = if ($Console) { "--console" } else { "--windowed" }

Push-Location $projectRoot
try {
    Remove-Item -LiteralPath $staging, $work, $spec -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $archive -Force -ErrorAction SilentlyContinue
    uv run --extra release pyinstaller --noconfirm --clean --onefile $consoleMode `
        --name PlainChange --paths src --collect-data plainchange `
        --distpath $staging --workpath $work --specpath $spec scripts\portable-entry.py
    if (-not (Test-Path -LiteralPath $executable -PathType Leaf)) {
        throw "Portable executable was not produced: $executable"
    }
    Compress-Archive -LiteralPath $executable -DestinationPath $archive -CompressionLevel Optimal
    if (-not (Test-Path -LiteralPath $archive -PathType Leaf)) {
        throw "Portable archive was not produced: $archive"
    }
    Get-FileHash -LiteralPath $executable, $archive -Algorithm SHA256 |
        Select-Object Path, Hash
}
finally {
    Pop-Location
}
