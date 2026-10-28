---
name: futu-quote
description: Futu `futu` CLI market-data skill. Use for stock, option, and futures quotes, K-lines, snapshots, tickers, intraday data, order books, rankings, capital flow, company profiles, financials, shareholders, valuation, plates, IPOs, calendars, watchlists, and paginated queries. Do not use it to place orders.
allowed-tools: Bash Read
metadata:
  version: 0.0.2
  author: Futu
  requires:
    bins:
      - futu
---

# Futu Quote

Use the locally available `futu` CLI for market-data queries. Answer in the user's language by default. Keep commands, flags, JSON fields, symbols, and error codes in their original form.

## Futu CLI runtime

This skill requires the official `futu` CLI. macOS and Linux install it to `$HOME/.futu/bin/futu`. Windows installs `futu.exe` to `%LOCALAPPDATA%\FutuCLI\bin`. See the [futu-cli install guide](https://github.com/FutunnOpen/futu-cli/blob/main/README.md).

Probe `futu` before any business command.

macOS / Linux:

```bash
if command -v futu >/dev/null 2>&1; then futu auth status --format json; elif [ -x "$HOME/.futu/bin/futu" ]; then "$HOME/.futu/bin/futu" auth status --format json; else echo '__FUTU_CLI_MISSING__'; fi
```

Windows, including Git Bash: do not use that bash block or `install.sh`. `install.sh` rejects Windows. Use this PowerShell call instead:

```powershell
$exe = Join-Path $env:LOCALAPPDATA 'FutuCLI\bin\futu.exe'
if (Get-Command futu -ErrorAction SilentlyContinue) { futu auth status --format json } elseif (Test-Path $exe) { & $exe auth status --format json } else { Write-Output '__FUTU_CLI_MISSING__' }
```

`__FUTU_CLI_MISSING__` means stop. Do not run a quote command yet. Ask the user before installing. After they agree:

macOS / Linux:

```bash
curl -fsSL https://raw.githubusercontent.com/FutunnOpen/futu-cli/main/scripts/install.sh | sh
```

Windows PowerShell. The official Windows installer supports amd64:

```powershell
iwr -UseBasicParsing https://raw.githubusercontent.com/FutunnOpen/futu-cli/main/scripts/install.ps1 -OutFile install.ps1
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

If the Windows installer reports an unsupported architecture, stop and relay that message. Never run either installer without explicit consent. Then run `futu version`. If the current shell still cannot see `futu`, call `$HOME/.futu/bin/futu` or `%LOCALAPPDATA%\FutuCLI\bin\futu.exe` directly.

To update an already installed `futu` CLI, use `futu update --check` and, after the user agrees, `futu update`.

## Usage rules

- Follow [Futu CLI runtime](#futu-cli-runtime) before any quote command. If the probe prints `__FUTU_CLI_MISSING__`, stop until `futu` is installed.
- When the probe succeeds, its business output is `futu auth status --format json`. If that returns `not logged in`, tell the user to run `futu auth login` and continue only after login. Do not run the business command directly.
- Invocation convention for this skill: when calling the `futu` CLI from Bash, always append the hidden internal marker `--source skill` at the end of the command. With `--source skill`, the CLI automatically detects hosts such as Codex or Claude Code and reports `agent_name`. Append `--agent codex` or `--agent claude_code` only when auto-detection fails and the CLI is confirmed to support it. Do not include these internal markers in commands shown to the user.
- Do not read or print token file contents. The CLI attaches the OAuth Bearer token automatically. `PERMISSION_DENIED` usually means a server-side permission or quote-permission denial. Do not explain it as a missing token.
- Use the smallest parameter set when generating commands. If the CLI already has a default and the user did not specify a value, do not pass that flag explicitly.
- Add `--format json` only when the output must be parsed programmatically. Commands meant for the user to copy and run can use the default table output.
- Quote symbols must be `MARKET.CODE`, for example `HK.00700`, `US.AAPL`, and `CC.BTCUSD`. If the user gives a bare code or a legacy format, fill in the market only when it can be determined; otherwise ask first.
- When the user mentions a legacy REST endpoint name, map it to the current aggregate command and selector flag. Do not call unregistered legacy command names.
- The current quote CLI does not paginate automatically. When the user asks for more, the next page, or the full list, use `--format json`, read the response cursor, and continue according to the pagination reference.
- `watchlist --action add/delete/move-out` modifies the user's watchlist. Confirm the target group and symbol first unless the user has already explicitly asked to change it.
- Do not run real-trading or paper-trading commands. Use `futu-trading` for securities trading, `futu-sim-trading` for paper trading, and `futu-crypto` for crypto trading.
- For **live streaming** (subscribe, push quote/order book/ticker/K-line, real-time **broker queue**), the CLI does not replace OpenD. Direct the user to **Open API Quote Push WebSocket** (`wss://webapi-quote.futunn.com/ws`): auth, then subscribe; broker queue arrives as `BROKER_QUEUE` messages. Read [WebSocket push reference](references/websocket-push.md) and hub [websocket-quote-push.md](../../../../docs/websocket-quote-push.md). Do not use OpenD or removed `futuapi` subscribe scripts.

## References

- When building a specific quote command, choosing a selector, or checking required, default, or pagination parameters, read [CLI parameters](references/cli-parameters.md).
- When explaining or choosing markets, security types, K-line types, adjustment types, trading sessions, plate types, option filters, and other quote enums, read [quote naming dictionary](references/dictionaries.md).
- When handling the next page, more results, or all results, or when `next_key`, `next_time`, `limit`, or `count` is needed, read [quote pagination](references/pagination.md).
- When the user needs live push or broker queue instead of one-off REST quotes, read [websocket-push](references/websocket-push.md).
