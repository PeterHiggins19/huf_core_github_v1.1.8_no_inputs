param(
  [string]$Path = "README.md"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if (!(Test-Path -LiteralPath $Path)) {
  throw "File not found: $Path"
}

function StrFromCodes([int[]]$codes) {
  $sb = New-Object System.Text.StringBuilder
  foreach ($c in $codes) { [void]$sb.Append([char]$c) }
  return $sb.ToString()
}

# Read as UTF-8 first; if it fails, fall back to Windows-1252 and convert to UTF-8.
try {
  $txt = Get-Content -LiteralPath $Path -Raw -Encoding utf8
} catch {
  $txt = [System.IO.File]::ReadAllText((Resolve-Path -LiteralPath $Path), [System.Text.Encoding]::GetEncoding(1252))
}

# Mojibake patterns (ASCII-only script: build patterns from codepoints)
# First-level common sequences (UTF-8 bytes decoded as CP1252 once)
$A_LQ = StrFromCodes @(0x00E2,0x20AC,0x0153)   # â€œ
$A_RQ = StrFromCodes @(0x00E2,0x20AC,0x009D)   # â€ (often shows as control; CP1252 0x9D)
$A_RS = StrFromCodes @(0x00E2,0x20AC,0x2122)   # â€™
$A_MD = StrFromCodes @(0x00E2,0x20AC,0x201D)   # â€” (varies; catch below too)
$A_AR = StrFromCodes @(0x00E2,0x2020,0x2019)   # â†’ (approx; catch below too)
$A_HY = StrFromCodes @(0x00E2,0x20AC,0x2018)   # â€‘ (approx; catch below too)

# Second-level common sequences (double-encoded): Ã¢â‚¬Å“ etc.
$B_LQ = StrFromCodes @(0x00C3,0x00A2,0x00E2,0x201A,0x00AC,0x00C5,0x201C) # Ã¢â‚¬Å“
$B_RQ = StrFromCodes @(0x00C3,0x00A2,0x00E2,0x201A,0x00AC,0x00C5,0x201D) # Ã¢â‚¬Å”
$B_RS = StrFromCodes @(0x00C3,0x00A2,0x00E2,0x201A,0x00AC,0x00E2,0x201E,0x00A2) # Ã¢â‚¬â„¢ (variant)

# Additional frequent sequences (built as plain ASCII literals where safe)
$pairs = @(
  @($A_LQ, '"'),
  @($A_RQ, '"'),
  @($A_RS, "'"),
  @($B_LQ, '"'),
  @($B_RQ, '"'),
  @($B_RS, "'"),
  @("â€”", "--"),  # if already present as visible chars
  @("â†’", "->"),
  @("â€‘", "-"),
  @("Â·", "·")
)

foreach ($p in $pairs) {
  $from = $p[0]
  $to = $p[1]
  if ($from -and ($txt.Contains($from))) {
    $txt = $txt.Replace($from, $to)
  }
}

# Also normalize any remaining curly quotes to ASCII (optional but helps)
$txt = $txt.Replace([char]0x201C, '"').Replace([char]0x201D, '"').Replace([char]0x2019, "'").Replace([char]0x2018, "'").Replace([char]0x2014, "--")

Set-Content -LiteralPath $Path -Value $txt -Encoding utf8
Write-Host "[ok] Normalized encoding + punctuation in $Path (UTF-8)"
