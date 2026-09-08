[CmdletBinding()]
param(
    [ValidateRange(1, 65535)]
    [int]$Port = 8080
)

$ErrorActionPreference = "Stop"
$paylabRoot = Split-Path -Parent $PSScriptRoot
$paylabPython = Get-Command python -ErrorAction Stop

Push-Location $paylabRoot
try {
    & $paylabPython.Source scripts/paylab.py doctor
    if ($LASTEXITCODE -ne 0) {
        throw "PayLab doctor failed"
    }
    Write-Host "Open http://127.0.0.1:$Port"
    & $paylabPython.Source scripts/paylab.py serve --port $Port
}
finally {
    Pop-Location
}
