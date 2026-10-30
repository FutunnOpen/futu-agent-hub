# Futu Skill Installation Guide

Install Futu Skills into your AI client with `npx`. Each skill's `description` is what the client uses to decide when to trigger it.

---

## Prerequisites

| Dependency | Purpose | Check |
|------------|---------|-------|
| Node.js 22.20+ | Provides `npx` for `npx skills add` and `npx skills update` | `node -v` |
| `curl` | Content skills call public HTTP APIs | `curl --version` |
| `futu` CLI | Quote, trading, and Unusual skills | `futu version` |

> macOS ships `curl`. Quote, trading, and Unusual skills need the official `futu` CLI (`install.sh` on macOS / Linux, `install.ps1` on Windows). See [futu-cli](https://github.com/FutunnOpen/futu-cli). Upgrading from OpenD: [upgrade-from-opend.md](./upgrade-from-opend.md).

---

## Step 1 — Install Skill Files

```bash
npx skills add -y -g FutunnOpen/futu-agent-hub
```

> `-y` skips interactive selection; `-g` installs globally (all projects). Drop `-y` to pick skills interactively, or `-g` to install only into the current project.

Other useful invocations:

```bash
# Switch to another branch / tag / commit
npx skills add -y -g FutunnOpen/futu-agent-hub#<branch-or-tag>

# Upgrade installed skills
npx skills update -g
```

`npx skills update` refreshes the current slug and leaves a renamed directory in place. If an older short name is still installed (`news-search`, `stock-digest`, `comment-sentiment`, `install-opend`, `capital-anomaly`, `derivatives-anomaly`, `technical-anomaly`), remove it once, then install again:

```bash
bash scripts/migrate-renamed-skills.sh
npx skills add -y -g FutunnOpen/futu-agent-hub
```

### Per-Client Targets

`npx skills add` auto-detects Claude-family clients. For others, pass `--target` or paste manually.

| AI Client | Command / Setup | Scope |
|-----------|-----------------|-------|
| Claude Code / VS Code / Cursor / JetBrains (Claude plugin) | Default — writes to `~/.claude/skills/` | Global |
| **Codex (OpenAI Codex CLI)** | Default — writes to `~/.codex/skills/`. **Must run in "Work locally" mode** (not Cloud — Cloud has network restrictions that block CLI/MCP install) | Global |
| OpenClaw | Send in chat: `Install Futu Developers Skill from this Git repo: <git-url>` | Global |
| Cursor (built-in AI) | Add `--target cursor` -> `~/.cursor/rules/` | Global |
| JetBrains (built-in AI) | Add `--target junie` -> `~/.junie/guidelines/` | Global |
| VS Code (Cline / Roo Code) | Paste SKILL.md into `cline.customInstructions` / `roo-cline.customInstructions` | Global |
| Claude Desktop / Claude.ai | Paste SKILL.md into **Custom Instructions** | Global |

> **Codex notes**: OpenAI ships a couple of global skills in `~/.codex/skills/.system/`; user-installed skills coexist alongside under `~/.codex/skills/`. Any directory layout under that path works — Codex's Discovery skill scans the tree and exposes skills via the system prompt.

---

## Step 2 — Install and authorize Futu CLI

Quote, trading, and Unusual skills use the official **`futu` CLI** (OAuth). OpenD and Python SDK are **not** required.

After Step 1, install the CLI if needed (see `futu-quote` or [futu-cli README](https://github.com/FutunnOpen/futu-cli/blob/main/README.md)), then:

```bash
futu version
futu auth login
futu auth status --format json
futu check
futu quote HK.00700 --format json
```

Unusual skills call `futu unusual ...`（`futu anomaly` 仍可用作别名）；若子命令不存在，请升级 CLI — see [migration-gaps-and-rest-api.md](./migration-gaps-and-rest-api.md).

---

## Troubleshooting

<details>
<summary><b>Skill not found in chat</b></summary>

Some clients require a restart or a new chat session to pick up newly installed skills. Restart the client and retry in a fresh conversation.

</details>

<details>
<summary><b><code>npx skills add</code> fails</b></summary>

- Confirm Node.js 22.20+: `node -v`
- `command not found: skills` -> upgrade npm: `npm install -g npm@latest`
- Private-repo clone failure -> ensure an SSH key or HTTPS credential helper is configured for `github.com`; verify with a manual `git clone`
- Restricted network -> use HTTPS with a token: `npx skills add -y -g https://<token>@github.com/FutunnOpen/futu-agent-hub.git`

</details>

<details>
<summary><b><code>futu</code> CLI or quote fails</b></summary>

- Run `futu auth status` — if not logged in, run `futu auth login`
- Run `futu check` for connectivity
- `PERMISSION_DENIED` usually means missing quote/trade permission in the app, not a missing local token
- 异动：若 `futu unusual` 不存在，见 [migration-gaps-and-rest-api.md](./migration-gaps-and-rest-api.md)

</details>
