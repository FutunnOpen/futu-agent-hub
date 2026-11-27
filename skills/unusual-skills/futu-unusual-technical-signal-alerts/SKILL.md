---
name: futu-unusual-technical-signal-alerts
description: >-
  Detect unusual candlestick patterns and technical indicators for a stock via
  `futu unusual technical-signals`. Use for technical-signal anomalies or broad
  stock anomaly requests; combine with the capital-flow and derivatives unusual
  skills for broad requests.
allowed-tools: Bash Read
metadata:
  version: 0.0.2
  requires:
    bins:
      - futu
  author: Futu
license: MIT
---

# Technical Signal Alerts

Detects technical signal alerts for a specific stock and formats the result as a structured Technical Signal Alerts summary.

This skill is for **unusual-move detection** rather than a regular technical overview. Focus on concrete alert events within the requested window. Do not add extra market commentary, fundamentals-based explanations, or investment advice.

If the user asks broadly about unusual activity in a stock without specifying a dimension, treat it as a bundled anomaly request. In that case, use this skill together with `futu-unusual-capital-flows` and `futu-unusual-derivatives-activity`.

---

## Prerequisite: Futu CLI

This skill calls **`futu unusual technical-signals`** (OAuth REST via the official CLI). Do **not** use OpenD, `futu-api`, or removed `futuapi` scripts.

This skill requires the official `futu` CLI. Probe it before any unusual command. Use the executable found on `PATH` or at the default install location for all subsequent commands.

macOS / Linux:

```bash
if command -v futu >/dev/null 2>&1; then futu auth status --format json; elif [ -x "$HOME/.futu/bin/futu" ]; then "$HOME/.futu/bin/futu" auth status --format json; else echo '__FUTU_CLI_MISSING__'; fi
```

Windows (including Git Bash): use PowerShell, not the Bash probe or `install.sh`.

```powershell
$exe = Join-Path $env:LOCALAPPDATA 'FutuCLI\bin\futu.exe'
if (Get-Command futu -ErrorAction SilentlyContinue) { futu auth status --format json } elseif (Test-Path $exe) { & $exe auth status --format json } else { Write-Output '__FUTU_CLI_MISSING__' }
```

If the probe prints `__FUTU_CLI_MISSING__`, stop and ask the user before installing the CLI. After they agree, use the official installer:

macOS / Linux:

```bash
curl -fsSL https://raw.githubusercontent.com/FutunnOpen/futu-cli/main/scripts/install.sh | sh
```

Windows PowerShell (amd64):

```powershell
iwr -UseBasicParsing https://raw.githubusercontent.com/FutunnOpen/futu-cli/main/scripts/install.ps1 -OutFile install.ps1
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

If the Windows installer reports an unsupported architecture, stop and relay the error. After installation, run `futu version` using the installed executable. If auth status says the user is not logged in, tell them to run `futu auth login` and continue only after login. If `futu unusual` is not recognized, check for an update with `futu update --check`; update after the user agrees.

---

## Workflow

### 1. Parse User Input

Extract the following from the user's request:

- `stock_target`: stock code, Chinese stock name, English company name, or ticker explicitly mentioned by the user
- `time_range`: default `7`; if the user says `last 3 days` / `past two weeks` / `last 5 days`, convert it to a natural-day integer
- `indicator_filters`: optional; only extract when the user clearly asks for one or more specific indicators
- `language_id`: infer from the user's language

If the target stock is missing, ask a follow-up question instead of guessing.

### 2. Normalize the Stock Target

Convert the stock name or ticker to a market-prefixed symbol such as `US.NVDA` or `HK.00700`. Ask if the market or listing is ambiguous. Use the [analysis guide](references/analysis-guide.md) for mappings.

### 3. Select `indicator_filters`

Use the full technical scan unless the user asks for specific indicators. For targeted requests, use the [analysis guide](references/analysis-guide.md) to choose backend filter values.

### 4. Infer `language_id`

Use the following language mapping:

- `0`: Simplified Chinese
- `1`: Traditional Chinese
- `2`: English
- `4`: Thai
- `5`: Japanese

Default strategy:

- Chinese user -> `0`
- Traditional Chinese request -> `1`
- English user -> `2`
- If unclear, default to `0`

### 5. Call the CLI

After extracting and normalizing the parameters, run (repeat `--indicator-filters` for each filter, or pass a comma-separated list if the CLI accepts it):

```bash
futu unusual technical-signals <STANDARD_SYMBOL> --time-range <DAYS> [--indicator-filters <FILTER> ...] [--language-id <ID>] --format json --source skill
```

Examples:

```bash
futu unusual technical-signals US.NVDA --time-range 7 --format json --source skill
futu unusual technical-signals HK.00700 --time-range 7 --indicator-filters MACD RSI6 RSI12 RSI24 --language-id 0 --format json --source skill
futu unusual technical-signals SH.600519 --time-range 14 --indicator-filters BOLL MA --format json --source skill
```

### 6. Check the Result

- If the CLI exits successfully, use the JSON to build a structured Technical Signal Alerts summary.
- If the CLI returns an error, surface the error message and do not fabricate results.
- If a requested indicator has no anomaly in the window, explicitly say `No anomaly`.

---

## Reporting

Read the [analysis guide](references/analysis-guide.md) for parameter details and output rules. Consult [examples](references/examples.md) only when needed. Do not present raw JSON, invent explanations, or give investment advice.
