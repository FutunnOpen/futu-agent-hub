---
name: futu-trading
description: Futu `futu` CLI securities-trading skill. Use for OAuth status, securities accounts, funds, positions, cash logs, order fees, margin ratio, order placement, modification, cancellation, order queries, fill queries, and max buy/sell quantity. Answer in the user's language by default.
allowed-tools: Bash Read
metadata:
  version: 0.0.3
  author: Futu
  requires:
    bins:
      - futu
---

# Futu Trading

Use the locally available `futu` CLI for securities trading. Answer in the user's language by default. Keep commands, flags, JSON fields, error codes, and symbols in their original form.

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

`__FUTU_CLI_MISSING__` means stop. Do not run an account or trading command yet. Ask the user before installing. After they agree:

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

- Follow [Futu CLI runtime](#futu-cli-runtime) before any account or trading command. If the probe prints `__FUTU_CLI_MISSING__`, stop until `futu` is installed.
- When the probe succeeds, its business output is `futu auth status --format json`. If that returns `not logged in`, tell the user to run `futu auth login` and continue only after login. Do not run the business command directly.
- Invocation convention for this skill: when calling the `futu` CLI from Bash, always append the hidden internal marker `--source skill` at the end of the command. With `--source skill`, the CLI automatically detects hosts such as Codex or Claude Code and reports `agent_name`. Append `--agent codex` or `--agent claude_code` only when auto-detection fails and the CLI is confirmed to support it. Do not include these internal markers in commands shown to the user.
- Do not read or print token file contents. The CLI attaches the OAuth Bearer token automatically. `PERMISSION_DENIED` is a server-side permission denial. Do not explain it as a missing token.
- Use the smallest parameter set when generating commands. If the CLI already has a default and the user did not specify a value, do not pass that flag explicitly.
- Do not assume a default account is configured. Omit `--account` only when this turn has already confirmed a default account through `futu auth status` or config. Otherwise, list accounts or ask the user to choose one, and pass `--account` explicitly.
- Add `--format json` when the output must be parsed, when extracting account, order, or fill fields, or when a follow-up action depends on the result. Commands meant only for the user to copy and run can use the default table output.
- Securities order and fill lists are paginated and merged by the CLI. Do not pass `page_flag` manually. Adjust `--page-size` only when needed.
- `account cash-logs` returns one page per call. Use `--format json`, read `page_flag` and `completed`, and call again with `--page-flag` until `completed` is true or the user has enough rows.
- `order fees` needs a concrete `order_id` (from `order list`, `order history`, or `order detail`). Open API does not support FX order fees yet.
- `margin-ratio` requires `--security-firm` and `--codes` (up to 10 symbols). Prefer `security_firm` from `account list --format json` for the user's account.
- Commands that change real assets require explicit user confirmation, including `order buy`, `order sell`, `order place`, `order modify`, and `order cancel`.
- Do not guess a second confirmation on behalf of the CLI or the server. If the CLI reports broker confirmation because the API returned `need_order_confirm=true` or `confirm_id`, relay it as-is and wait for explicit user consent before entering `y`.

## References

- When building a specific command, checking required, default, or optional parameters, handling pagination, or mapping fields, read [CLI parameters](references/cli-parameters.md).
- When choosing or explaining markets, trade sides, order types, statuses, account-market dictionaries, and response fields, read [dictionaries](references/dictionaries.md).
- For crypto trading, use `futu-crypto`.
