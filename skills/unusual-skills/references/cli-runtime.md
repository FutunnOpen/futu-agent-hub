# Futu CLI runtime（Unusual skills）

Unusual skills（`futu-unusual-*`）与 `futu-quote` 共用 CLI 探测与 OAuth。子命令：**`futu unusual`**（`anomaly` 为兼容别名）。最低 CLI 版本见仓库 `docs/migration-gaps-and-rest-api.md`。

| Skill | 推荐命令 |
|-------|----------|
| 资金异动 | `futu unusual capital-flows <symbol>` |
| 衍生品异动 | `futu unusual derivatives-activity <symbol>` |
| 技术面异动 | `futu unusual technical-signals <symbol>` |

## 探测

macOS / Linux：

```bash
if command -v futu >/dev/null 2>&1; then futu auth status --format json; elif [ -x "$HOME/.futu/bin/futu" ]; then "$HOME/.futu/bin/futu" auth status --format json; else echo '__FUTU_CLI_MISSING__'; fi
```

Windows PowerShell：

```powershell
$exe = Join-Path $env:LOCALAPPDATA 'FutuCLI\bin\futu.exe'
if (Get-Command futu -ErrorAction SilentlyContinue) { futu auth status --format json } elseif (Test-Path $exe) { & $exe auth status --format json } else { Write-Output '__FUTU_CLI_MISSING__' }
```

- `__FUTU_CLI_MISSING__`：停止；经用户同意后再引导安装 [futu-cli](https://github.com/FutunnOpen/futu-cli/blob/main/README.md)。
- 未登录：先 `futu auth login`，再调用 unusual 子命令。

## 调用约定

- 解析输出时追加 `--format json`。
- Bash 调用时在末尾追加隐藏参数 `--source skill`（用户可见示例可省略）。
- 若 `futu unusual` 不存在，提示需升级 CLI（见 migration gaps）；勿回退 OpenD / Python SDK。
