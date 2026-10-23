# Futu CLI runtime (anomaly skills)

Anomaly skills use the same CLI probe and auth rules as `futu-quote`. Minimum CLI version for `futu anomaly` subcommands: **TBD after API/CLI release** (see repo `docs/migration-gaps-and-rest-api.md`).

## Probe

macOS / Linux:

```bash
if command -v futu >/dev/null 2>&1; then futu auth status --format json; elif [ -x "$HOME/.futu/bin/futu" ]; then "$HOME/.futu/bin/futu" auth status --format json; else echo '__FUTU_CLI_MISSING__'; fi
```

Windows PowerShell:

```powershell
$exe = Join-Path $env:LOCALAPPDATA 'FutuCLI\bin\futu.exe'
if (Get-Command futu -ErrorAction SilentlyContinue) { futu auth status --format json } elseif (Test-Path $exe) { & $exe auth status --format json } else { Write-Output '__FUTU_CLI_MISSING__' }
```

- `__FUTU_CLI_MISSING__`: stop; offer [futu-cli install](https://github.com/FutunnOpen/futu-cli/blob/main/README.md) after user consent.
- `not logged in`: ask user to run `futu auth login`; do not call anomaly commands until logged in.

## Invocation

- Append `--format json` when parsing output.
- Append hidden marker `--source skill` at the end of Bash-invoked commands (not in user-visible examples).
- If `futu anomaly` returns unknown command, tell the user anomaly requires a newer CLI (see migration gaps doc); do not fall back to OpenD or Python SDK.
