param([string]$DestinationRoot)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$packageRoot = Join-Path $projectRoot 'package'
if (-not $DestinationRoot) {
    $petConfigRoot = $env:CODEX_HOME
    if (-not $petConfigRoot) {
        $petConfigRoot = Join-Path ([Environment]::GetFolderPath('UserProfile')) '.codex'
    }
    $DestinationRoot = Join-Path $petConfigRoot 'pets'
}
$petTarget = Join-Path $DestinationRoot 'bvb-emma-2627'
if (Test-Path -LiteralPath $petTarget) { throw "Refusing to overwrite existing pet: $petTarget" }
$validation = Get-Content -LiteralPath (Join-Path $projectRoot 'validation.json') -Raw | ConvertFrom-Json
if (-not $validation.ok) { throw 'Sprite validation has not passed.' }
$sourceHash = (Get-FileHash -LiteralPath (Join-Path $packageRoot 'spritesheet.png') -Algorithm SHA256).Hash.ToLowerInvariant()
if ($sourceHash -ne $validation.sha256) { throw 'Sprite hash differs from validation report.' }
$petMetadata = Get-Content -LiteralPath (Join-Path $packageRoot 'pet.json') -Raw | ConvertFrom-Json
if ($petMetadata.id -ne 'bvb-emma-2627' -or $petMetadata.spritesheetPath -ne 'spritesheet.png') { throw 'Unexpected package metadata.' }
New-Item -ItemType Directory -Path $petTarget -Force | Out-Null
foreach ($petFile in @('pet.json','spritesheet.png')) {
    Copy-Item -LiteralPath (Join-Path $packageRoot $petFile) -Destination (Join-Path $petTarget $petFile)
}
$installedHash = (Get-FileHash -LiteralPath (Join-Path $petTarget 'spritesheet.png') -Algorithm SHA256).Hash.ToLowerInvariant()
if ($installedHash -ne $sourceHash) { throw 'Installed file does not match source.' }
Write-Output "Installed and verified: $petTarget"
