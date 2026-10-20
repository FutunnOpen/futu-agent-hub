---
name: futu-crypto
description: Futu `futu` CLI crypto-trading skill. Use for crypto accounts, balances, max buy/sell quantity, order placement, modification, cancellation, and order or fill queries. Answer in the user's language by default.
allowed-tools: Bash Read
metadata:
  version: 0.0.2
  author: Futu
  requires:
    bins:
      - futu
---

# Futu Crypto

Use the locally available `futu` CLI for crypto trading. Answer in the user's language by default. Keep commands, flags, JSON fields, pairs, and error codes in their original form.

## CLI: Version Update Check

Embed the version check into the skill's **single Bash call**. **Do not create any separate tool call** for the version check. The same inline check must detect three things:

1. whether the `futu-skills` manager is installed locally;
2. whether this skill has a new version available;
3. whether the `futu-skills` manager itself has a new version available.

Start the check as a backgrounded subprocess **before** the `futu` probe, then append `wait` **after** the probe, all in one invocation. On Windows PowerShell, use the invocation in [Futu CLI runtime](#futu-cli-runtime) instead of this bash block. `install.sh` does not support Windows.

```bash
( if command -v futu-skills >/dev/null 2>&1; then futu-skills check --quiet --slug futu-crypto 2>/dev/null; else echo '__CLI_MISSING__'; fi ) > /tmp/.futu-crypto-update 2>/dev/null & if command -v futu >/dev/null 2>&1; then futu auth status --format json; elif [ -x "$HOME/.futu/bin/futu" ]; then "$HOME/.futu/bin/futu" auth status --format json; else echo '__FUTU_CLI_MISSING__'; fi; wait; cat /tmp/.futu-crypto-update 2>/dev/null; rm -f /tmp/.futu-crypto-update
```

Based on the `cat` output:

- **No content** (skill is up-to-date or the check failed): do not show any upgrade prompt.
- **Output `__CLI_MISSING__`** (`futu-skills` is not installed locally, so version check/upgrade cannot run): append a notice at the **end** of your reply:
  > The `futu-skills` manager is not installed yet, so I cannot auto-check or upgrade skill versions. If you agree, I can install it for you now.

  If the user agrees, first run:
  ```bash
  curl -fsSL https://raw.githubusercontent.com/FutunnOpen/futu-agent-hub/main/futu-install.sh | bash
  ```
  After install completes, run `futu-skills upgrade futu-crypto` to bring this skill to the latest version.
- **Output containing a line starting with `futu-crypto`** (this skill has an update available): append a notice at the **end** of your reply:
  > `futu-crypto` has a new version available. If you agree, I can upgrade it for you right away.

  If the user agrees, run `futu-skills upgrade futu-crypto` to perform the upgrade. (This command also auto-upgrades the `futu-skills` manager itself, so a separate CLI prompt is unnecessary when a skill update is available.)
- **Output containing only a line starting with `cli`** (this skill is up-to-date but the `futu-skills` manager itself has a new version): append a notice at the **end** of your reply:
  > The `futu-skills` manager has a new version available. If you agree, I can upgrade it for you right away.

  If the user agrees, run `futu-skills self-upgrade` to perform the upgrade.

  If both a `cli` line and a `futu-crypto` line appear, only show the skill upgrade prompt above — the manager will be refreshed as a side effect of `futu-skills upgrade futu-crypto`.

**Never** run `curl -fsSL https://raw.githubusercontent.com/FutunnOpen/futu-agent-hub/main/futu-install.sh | bash` or `futu-skills upgrade …` without explicit user consent. Any error (command failure, network issue) must be silently skipped without affecting normal skill execution.

**Important**: The version check (write + read) must all be embedded in this single shell call. Do not produce any additional tool calls.

## Futu CLI runtime

This skill requires the official `futu` CLI. macOS and Linux install it to `$HOME/.futu/bin/futu`. Windows installs `futu.exe` to `%LOCALAPPDATA%\FutuCLI\bin`. See the [futu-cli install guide](https://github.com/FutunnOpen/futu-cli/blob/main/README.md).

Probe `futu` in the same shell call as the version check.

- macOS / Linux: use the bash block in the version-check section. It runs `futu auth status --format json` when `futu` or `$HOME/.futu/bin/futu` exists, and prints `__FUTU_CLI_MISSING__` otherwise.
- Windows, including Git Bash: do not use that bash block or `install.sh`. `install.sh` rejects Windows. Use this PowerShell call instead:

```powershell
$check = Start-Job -ScriptBlock { if (Get-Command futu-skills -ErrorAction SilentlyContinue) { & futu-skills check --quiet --slug futu-crypto 2>$null } else { Write-Output '__CLI_MISSING__' } }
$exe = Join-Path $env:LOCALAPPDATA 'FutuCLI\bin\futu.exe'
if (Get-Command futu -ErrorAction SilentlyContinue) { futu auth status --format json } elseif (Test-Path $exe) { & $exe auth status --format json } else { Write-Output '__FUTU_CLI_MISSING__' }
Receive-Job $check -Wait -AutoRemoveJob
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

To update an already installed `futu` CLI, use `futu update --check` and, after the user agrees, `futu update`. Do not use `futu-skills` for that upgrade.

## Usage rules

- Follow [Futu CLI runtime](#futu-cli-runtime) before any account or trading command. If the probe prints `__FUTU_CLI_MISSING__`, stop until `futu` is installed.
- When the probe succeeds, its business output is `futu auth status --format json`. If that returns `not logged in`, tell the user to run `futu auth login` and continue only after login. Do not run the business command directly.
- Invocation convention for this skill: when calling the `futu` CLI from Bash, always append the hidden internal marker `--source skill` at the end of the command. With `--source skill`, the CLI automatically detects hosts such as Codex or Claude Code and reports `agent_name`. Append `--agent codex` or `--agent claude_code` only when auto-detection fails and the CLI is confirmed to support it. Do not include these internal markers in commands shown to the user.
- Do not read or print token file contents. The CLI attaches the OAuth Bearer token automatically. `PERMISSION_DENIED` is a server-side permission denial. Do not explain it as a missing token.
- Use the smallest parameter set when generating commands. If the CLI already has a default and the user did not specify a value, do not pass that flag explicitly.
- Do not assume a default account is configured. Omit `--account` only when this turn has already confirmed a default account through `futu auth status` or config. Otherwise, list crypto accounts or ask the user to choose one, and pass `--account` explicitly.
- Add `--format json` when the output must be parsed, when extracting account, order, or fill fields, or when a follow-up action depends on the result. Commands meant only for the user to copy and run can use the default table output.
- List and history queries do not paginate automatically. If the JSON response has `completed=false` and a `page_flag`, pass that value as `--page-flag` to fetch the next page.
- Crypto orders affect real assets. Confirm the account, pair, side, quantity, price, or amount before executing.
- Do not use `--cash-qty` on sell commands, even if help text shows that flag.
- Do not guess a second confirmation on behalf of the CLI or the server. If the CLI asks for confirmation, relay it as-is and wait for explicit user consent before entering `y`.

## References

- When building a specific command, checking required, default, or optional parameters, handling pagination, or mapping fields, read [CLI parameters](references/cli-parameters.md).
- When choosing or explaining pairs, currencies, order types, order statuses, fill or order fields, and errors, read [dictionaries](references/dictionaries.md).
- For securities account funds, positions, securities orders, and securities fills, use `futu-trading`.
