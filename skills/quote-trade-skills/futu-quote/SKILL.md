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

## CLI: Version Update Check

Embed the version check into the skill's **single Bash call**. **Do not create any separate tool call** for the version check. The same inline check must detect three things:

1. whether the `futu-skills` manager is installed locally;
2. whether this skill has a new version available;
3. whether the `futu-skills` manager itself has a new version available.

Start the check as a backgrounded subprocess **before** the `futu` probe, then append `wait` **after** the probe, all in one invocation. On Windows PowerShell, use the invocation in [Futu CLI runtime](#futu-cli-runtime) instead of this bash block. `install.sh` does not support Windows.

```bash
( if command -v futu-skills >/dev/null 2>&1; then futu-skills check --quiet --slug futu-quote 2>/dev/null; else echo '__CLI_MISSING__'; fi ) > /tmp/.futu-quote-update 2>/dev/null & if command -v futu >/dev/null 2>&1; then futu auth status --format json; elif [ -x "$HOME/.futu/bin/futu" ]; then "$HOME/.futu/bin/futu" auth status --format json; else echo '__FUTU_CLI_MISSING__'; fi; wait; cat /tmp/.futu-quote-update 2>/dev/null; rm -f /tmp/.futu-quote-update
```

Based on the `cat` output:

- **No content** (skill is up-to-date or the check failed): do not show any upgrade prompt.
- **Output `__CLI_MISSING__`** (`futu-skills` is not installed locally, so version check/upgrade cannot run): append a notice at the **end** of your reply:
  > The `futu-skills` manager is not installed yet, so I cannot auto-check or upgrade skill versions. If you agree, I can install it for you now.

  If the user agrees, first run:
  ```bash
  curl -fsSL https://raw.githubusercontent.com/FutunnOpen/futu-agent-hub/main/futu-install.sh | bash
  ```
  After install completes, run `futu-skills upgrade futu-quote` to bring this skill to the latest version.
- **Output containing a line starting with `futu-quote`** (this skill has an update available): append a notice at the **end** of your reply:
  > `futu-quote` has a new version available. If you agree, I can upgrade it for you right away.

  If the user agrees, run `futu-skills upgrade futu-quote` to perform the upgrade. (This command also auto-upgrades the `futu-skills` manager itself, so a separate CLI prompt is unnecessary when a skill update is available.)
- **Output containing only a line starting with `cli`** (this skill is up-to-date but the `futu-skills` manager itself has a new version): append a notice at the **end** of your reply:
  > The `futu-skills` manager has a new version available. If you agree, I can upgrade it for you right away.

  If the user agrees, run `futu-skills self-upgrade` to perform the upgrade.

  If both a `cli` line and a `futu-quote` line appear, only show the skill upgrade prompt above — the manager will be refreshed as a side effect of `futu-skills upgrade futu-quote`.

**Never** run `curl -fsSL https://raw.githubusercontent.com/FutunnOpen/futu-agent-hub/main/futu-install.sh | bash` or `futu-skills upgrade …` without explicit user consent. Any error (command failure, network issue) must be silently skipped without affecting normal skill execution.

**Important**: The version check (write + read) must all be embedded in this single shell call. Do not produce any additional tool calls.

## Futu CLI runtime

This skill requires the official `futu` CLI. macOS and Linux install it to `$HOME/.futu/bin/futu`. Windows installs `futu.exe` to `%LOCALAPPDATA%\FutuCLI\bin`. See the [futu-cli install guide](https://github.com/FutunnOpen/futu-cli/blob/main/README.md).

Probe `futu` in the same shell call as the version check.

- macOS / Linux: use the bash block in the version-check section. It runs `futu auth status --format json` when `futu` or `$HOME/.futu/bin/futu` exists, and prints `__FUTU_CLI_MISSING__` otherwise.
- Windows, including Git Bash: do not use that bash block or `install.sh`. `install.sh` rejects Windows. Use this PowerShell call instead:

```powershell
$check = Start-Job -ScriptBlock { if (Get-Command futu-skills -ErrorAction SilentlyContinue) { & futu-skills check --quiet --slug futu-quote 2>$null } else { Write-Output '__CLI_MISSING__' } }
$exe = Join-Path $env:LOCALAPPDATA 'FutuCLI\bin\futu.exe'
if (Get-Command futu -ErrorAction SilentlyContinue) { futu auth status --format json } elseif (Test-Path $exe) { & $exe auth status --format json } else { Write-Output '__FUTU_CLI_MISSING__' }
Receive-Job $check -Wait -AutoRemoveJob
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

To update an already installed `futu` CLI, use `futu update --check` and, after the user agrees, `futu update`. Do not use `futu-skills` for that upgrade.

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

## References

- When building a specific quote command, choosing a selector, or checking required, default, or pagination parameters, read [CLI parameters](references/cli-parameters.md).
- When explaining or choosing markets, security types, K-line types, adjustment types, trading sessions, plate types, option filters, and other quote enums, read [quote naming dictionary](references/dictionaries.md).
- When handling the next page, more results, or all results, or when `next_key`, `next_time`, `limit`, or `count` is needed, read [quote pagination](references/pagination.md).
