---
name: futu-sim-trading
description: Futu `futu` CLI paper-trading skill. Use for sim accounts, funds, positions, paper-order queries, historical-order pagination, max buy/sell quantity, paper order placement, modification, and cancellation. Do not use it for real trading.
allowed-tools: Bash Read
metadata:
  version: 0.0.2
  author: Futu
  requires:
    bins:
      - futu
---

# Futu Sim Trading

Use the locally available `futu sim ...` CLI for paper trading. Answer in the user's language by default. Keep commands, flags, JSON fields, symbols, and error codes in their original form.

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

`__FUTU_CLI_MISSING__` means stop. Do not run a paper-trading command yet. Ask the user before installing. After they agree:

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

- Follow [Futu CLI runtime](#futu-cli-runtime) before any paper-trading command. If the probe prints `__FUTU_CLI_MISSING__`, stop until `futu` is installed.
- When the probe succeeds, its business output is `futu auth status --format json`. If that returns `not logged in`, tell the user to run `futu auth login` and continue only after login. Do not run the business command directly.
- Invocation convention for this skill: when calling the `futu` CLI from Bash, always append the hidden internal marker `--source skill` at the end of the command. With `--source skill`, the CLI automatically detects hosts such as Codex or Claude Code and reports `agent_name`. Append `--agent codex` or `--agent claude_code` only when auto-detection fails and the CLI is confirmed to support it. Do not include these internal markers in commands shown to the user.
- Do not read or print token file contents. The CLI attaches the OAuth Bearer token automatically. `PERMISSION_DENIED` is a server-side permission denial. Do not explain it as a missing token.
- Always use the high-level `futu sim ...` commands. Treat `sim-trade-*` only as legacy endpoint metadata. Do not call those commands directly.
- Use the smallest parameter set when generating commands. If the CLI already has a default and the user did not specify a value, do not pass that flag explicitly.
- Prefer calling `futu sim account list --format json` first to identify the paper account, then pass an explicit `--account` to later commands. Do not silently rely on the first paper account.
- Add `--format json` only when the output must be parsed programmatically. Commands meant for the user to copy and run can use the default table output.
- Historical paper orders are paginated with `--next-key`. When the user asks for the next page, more results, or all historical orders, use `--format json` and read `pagination.next_key`.
- Historical query time parameters `--start` and `--end` use microsecond timestamps. Do not pass seconds, milliseconds, or date strings.
- Paper orders do not affect the real account, but they do change paper-account state. Execute when the user's intent is clear. If the target account, symbol, side, quantity, price, or order ID is unclear, query or ask first.
- Symbols must be `MARKET.CODE`, for example `HK.00700` and `US.AAPL`. If the user gives a bare code or a legacy format, fill in the market only when it can be determined; otherwise ask first.
- Use `futu-trading` for real securities trading, `futu-crypto` for crypto trading, and `futu-quote` for market-data queries.

## References

- When building a specific paper-trading command, or checking required, default, optional, and enum parameters, read [CLI parameters](references/cli-parameters.md).
- When choosing or explaining paper-trading markets, order sides, order types, trading sessions, order statuses, and server-returned enums, read [trading naming dictionary](references/dictionaries.md).
- When handling the next page, more results, or all historical orders, or when `--next-key`, `--page-size`, `--start`, or `--end` is involved, read [paper-trading pagination](references/pagination.md).
