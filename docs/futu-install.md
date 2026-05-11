---
name: futu-skill
description: |
  Futu AI Skill installation guide, covering setup for mainstream AI clients.
  Capabilities: news search, stock news digest, comment sentiment analysis, capital anomaly detection, derivatives anomaly detection, technical anomaly detection, real-time quotes, order book & tick data, trading, portfolio management, K-line charts, options & futures, stock screening, capital flow, sector analysis, push subscriptions, watchlist management, price alerts, OpenD installation.
metadata:
  author: futu
  version: "2.2.0"
  last_updated: "2026-05-07"
---

# Futu Skill Installation Guide

By installing Futu Skills, you can search news, analyze comment sentiment, detect stock anomaly signals, and access real-time quotes, execute trades, and manage portfolios via OpenAPI — all within your AI conversations, without switching between apps.

---

## Feature Overview

Futu Skills include three categories: **Search Skills** (no additional setup required), **Anomaly Detection Skills** (requires OpenD), and **OpenAPI Skills** (requires OpenD).

### Search Skills — Ready to Use

| Capability | Description | Example |
|------------|-------------|---------|
| News Search | Search news, announcements, and research reports on the Futu platform; sortable by popularity / time | `Search for the latest Tencent news` |
| Stock News Digest | Batch-fetch news for multiple stocks, scrape article content, and generate structured summaries | `Show me the latest news for Tencent, Apple, and BYD` |
| Comment Sentiment | Scrape stock comments / posts, analyze bullish / bearish sentiment distribution with a temperature score | `What's the sentiment on NVIDIA comments` |

### Anomaly Detection Skills — Requires OpenD

| Capability | Description | Example |
|------------|-------------|---------|
| Capital Anomaly Detection | Detect capital distribution, buy/sell brokers, capital flow, and short-sell volume/ratio anomalies | `Any capital anomalies on Tencent recently?` |
| Derivatives Anomaly Detection | Detect CBBC open-interest ratio, unusual option trades, implied volatility, and option sentiment anomalies | `Any option anomalies on NVIDIA recently?` |
| Technical Anomaly Detection | Detect candlestick patterns and indicator anomalies (MACD, RSI, KDJ, CCI, Bollinger, etc.) | `Any technical anomalies on Apple recently?` |

### OpenAPI Skills — Requires OpenD

| Capability | Description | Example |
|------------|-------------|---------|
| Real-time Quotes | Fetch quotes, snapshots, change %, and volume | `What's Tencent's current price?` |
| K-line Charts | Retrieve daily / weekly / minute K-line data, historical and real-time | `Show TSLA's daily K-line for the last month` |
| Order Book / Ticks | View real-time order book depth, tick-by-tick trades, and intraday chart | `Show Tencent's order book` |
| Trading | Place, cancel, and modify orders — simulated or live | `Simulated buy 100 shares of AAPL` |
| Portfolio | View positions, P&L, asset allocation, and cash details | `Show my positions` |
| Options Trading | Parse option shorthand, query option chain and expiries, place option orders | `What option is JPM 260320 267.50C?` |
| Futures Trading | Query futures contracts, place simulated / live futures orders | `What's the current A50 futures price?` |
| Stock Screening | Screen stocks by market cap, PE, change %, and other dimensions | `Top 20 HK stocks by market cap` |
| Capital Flow | View inflows / outflows and large-order distribution | `Show Tencent's capital flow` |
| Sector Analysis | Query sector lists, constituents, and a stock's sector membership | `Hang Seng TECH Index constituents` |
| Push Subscriptions | Subscribe to real-time quote / K-line / order-book pushes | `Subscribe to Tencent's real-time quote` |
| Watchlist | View / modify watchlist groups | `What's in my watchlist?` |
| Price Alerts | Set / query price alerts on stocks | `Alert me when Tencent drops to 400` |
| OpenD Installation | One-click download and install of Futu OpenD, auto-upgrade SDK; supports Windows / macOS / Linux | `Help me install OpenD` |

---

## Installing OpenAPI Skills and OpenD

OpenAPI Skills can only be used once OpenD is ready. Ask the user for permission first, then install as follows:

1. Check whether the current AI client has the `/install-futu-opend` skill registered.

2. **IF the skill EXISTS:**
    - Invoke `/install-futu-opend` directly
    - Wait for it to finish before proceeding

3. **IF the skill DOES NOT EXIST:**
    - After getting the user's consent, run the command below to install the OpenAPI skills (including `install-futu-opend`) into the current AI client's global skills directory via `npx`:

      ```bash
      npx skills add -y -g https://gitlab.futunn.com/FTOpenAPI/ftopend-skills.git#master --path skills
      ```

    - Immediately invoke `/install-futu-opend` after installation to continue installing OpenD and upgrading the SDK

> The command above installs every OpenAPI skill under `skills/` in the `ftopend-skills` repository (including `futuapi`, `install-futu-opend`, etc.) and writes them to the matching directory of the current AI client (Claude-family -> `~/.claude/skills/`).

**This procedure is a hard prerequisite for OpenAPI Skills and must run before any other business request. Always confirm with the user before executing.**

---

## Quick Start

### Prerequisites

Running the skills and the accompanying CLI requires the following on your machine:

| Dependency | Purpose | Check Command |
|------------|---------|---------------|
| `python3` | Runs the anomaly-detection skill scripts and the `futu-skills` CLI | `python3 --version` |
| `curl` | Downloads `install.sh` and fetches remote files during installation | `curl --version` |
| Node.js 18+ | Provides `npx` so `npx skills add` can install skill files | `node -v` |

> macOS ships with `python3` and `curl` by default. On Linux, install them with `apt install python3 curl` / `yum install python3 curl`. On Windows, use WSL or Git Bash and install the official Node.js package.

### Step 1. Install the `futu-skills` CLI

`futu-skills` is the command-line tool that manages Futu Skills versions and self-upgrades. Download and run `install.sh` with a single command:

```bash
curl -fsSL https://gitlab.futunn.com/futu-common/futu-skills-hub/-/raw/v20260428-futu-cli_v2/internal/futu/futu-install.sh | bash
```

The installer places `futu-skills` in `~/.local/bin` (or `/usr/local/bin`, depending on permissions). After installation, run `futu-skills --version` to verify:

```bash
futu-skills --version
futu-skills check        # Check installed skills for updates
```

If the `futu-skills` command is not found, make sure the target directory is in your `PATH` or open a new terminal session.

### Step 2. Install Skill Files

Install the search and anomaly-detection skills in one command. `npx skills add` clones the repository and copies SKILL files into your AI client's skills directory:

```bash
npx skills add -y -g https://gitlab.futunn.com/futu-common/futu-skills-hub.git#v20260428-futu-cli_v2
```

> **Prerequisite:** [Node.js](https://nodejs.org/) 18+ is installed on your machine (`npx` ships with Node.js). A private GitLab repository requires an SSH key or an HTTPS credential helper already configured locally.
>
> **Flags:** `-y` skips interactive confirmation (installs every skill in the repo); `-g` installs into the user-level global directory (applies to all projects). Drop `-y` to pick skills interactively; drop `-g` to install into the current project only.

The command installs the following skills:

```
search-skills/          <- Search skills (ready to use)
  ├── futu-news-search/
  ├── futu-stock-digest/
  └── futu-comment-sentiment/
anomaly-skills/         <- Anomaly-detection skills (require OpenD)
  ├── futu-capital-anomaly/
  ├── futu-derivatives-anomaly/
  └── futu-technical-anomaly/
```

Common flags:

```bash
# Switch to another branch / tag / commit (ref after #)
npx skills add -y -g https://gitlab.futunn.com/futu-common/futu-skills-hub.git#main
npx skills add -y -g https://gitlab.futunn.com/futu-common/futu-skills-hub.git#v2.2.0

# Install only a subdirectory of skills
npx skills add -y -g https://gitlab.futunn.com/futu-common/futu-skills-hub.git#v20260428-futu-cli_v2 --path internal/futu/search-skills

# Interactive selection (drop -y)
npx skills add -g https://gitlab.futunn.com/futu-common/futu-skills-hub.git#v20260428-futu-cli_v2

# Upgrade installed skills to the latest version
npx skills update futu-skill
```

> Anomaly-detection skills require the OpenD service to run locally. For OpenAPI Skills (including OpenD), see the "Installing OpenAPI Skills and OpenD" section above.

---

## Per-Client Setup

`npx skills add` auto-detects the active AI client and writes to the matching directory. **Claude-family clients are fully installed with a single command.** A few built-in AIs outside the Claude ecosystem require manual paste-in configuration.

| AI Client | Installation | Scope |
|-----------|--------------|-------|
| OpenClaw | Send a single message in the chat; installs automatically | Global |
| Claude Code CLI | `npx skills add -y -g <git-url>` -> `~/.claude/skills/` | Global (all projects) |
| VS Code (Claude plugin) | Shares `~/.claude/skills/` with Claude Code | Global (all projects) |
| Cursor (Claude plugin) | Shares `~/.claude/skills/` with Claude Code | Global (all projects) |
| JetBrains (Claude plugin) | Shares `~/.claude/skills/` with Claude Code | Global (all projects) |
| Cursor (built-in AI) | `npx skills add -y -g <git-url> --target cursor` -> `~/.cursor/rules/` | Global (all projects) |
| JetBrains (built-in AI) | `npx skills add -y -g <git-url> --target junie` -> `~/.junie/guidelines/` | Global (all projects) |
| VS Code (Cline / Roo Code) | Paste SKILL.md content into global custom instructions | Global (all projects) |
| Claude Desktop / Claude.ai | Paste content into Custom Instructions | Global (all conversations) |

---

### Detailed Setup Steps

<details>
<summary><b>OpenClaw</b> — install via chat, ready immediately</summary>

Send the following message in the chat window:

```
Install Futu Developers Skill from this Git repo: https://gitlab.futunn.com/futu-common/futu-skills-hub.git#v20260428-futu-cli_v2
```

OpenClaw clones and loads the skills automatically; no restart is required and the current session can use them right away.

</details>

<details>
<summary><b>Claude Code CLI / VS Code / Cursor / JetBrains (with Claude plugin)</b> — one-command global install</summary>

These tools share the `~/.claude/skills/` directory. Just run:

```bash
npx skills add -y -g https://gitlab.futunn.com/futu-common/futu-skills-hub.git#v20260428-futu-cli_v2
```

> `~/.claude/skills/` is a user-level directory, so **all projects** will have access after installation — no per-project setup needed. To install only a subset of skills, pass `--path` with a subdirectory.

</details>

<details>
<summary><b>Cursor (built-in AI, no Claude plugin)</b> — Rules directory</summary>

`npx skills add` writes to `~/.cursor/rules/` when `--target cursor` is set:

```bash
npx skills add -y -g https://gitlab.futunn.com/futu-common/futu-skills-hub.git#v20260428-futu-cli_v2 --target cursor
```

The command copies each skill's SKILL.md into a standalone `.md` rule file and places the anomaly-detection skill `scripts/` directory under your home directory.

</details>

<details>
<summary><b>JetBrains (built-in AI Assistant)</b> — Guidelines directory</summary>

`npx skills add` writes to `~/.junie/guidelines/` when `--target junie` is set:

```bash
npx skills add -y -g https://gitlab.futunn.com/futu-common/futu-skills-hub.git#v20260428-futu-cli_v2 --target junie
```

> `~/.junie/guidelines/` is a user-level global directory; **all projects** load it automatically — no per-project setup needed.

</details>

<details>
<summary><b>VS Code (Cline / Roo Code)</b> — global custom instructions</summary>

Cline / Roo Code does not read file directories, so paste the SKILL.md content into extension settings:

1. Run `npx skills add <git-url>` first to clone the repo into the local cache (default `~/.cache/skills/futu-skills-hub/`)
2. Open VS Code settings and search for `cline.customInstructions` (Cline) or `roo-cline.customInstructions` (Roo Code)
3. Paste the SKILL.md content you want to use into that field

> The setting is written to VS Code's global `settings.json` and **applies to all projects**.

</details>

<details>
<summary><b>Claude Desktop / Claude.ai</b> — Custom Instructions (global)</summary>

Claude.ai's web UI does not support npx, so paste manually:

1. Open [Claude.ai](https://claude.ai) -> click the avatar in the bottom-left -> **Settings**
2. Find **Custom Instructions**
3. Paste the skill content into the instructions box
4. Save; all new conversations pick it up automatically

> Custom Instructions apply globally — no need to upload per Project. If the content exceeds the length limit, trim the core SKILL.md content before pasting.

</details>

---

## Verifying the Installation

### Verify Search Skills

After installation, try any of the following commands in chat to confirm the skills loaded correctly:

```
Search for the latest Tencent news
```

| Scenario | Try This |
|----------|----------|
| News search | `Search for recent Apple announcements` |
| Multi-stock digest | `Aggregate the latest news for Tencent, BYD, and Apple` |
| Sentiment analysis | `Is the Tesla comment section bullish or bearish?` |

### Verify Anomaly Detection Skills

Try the following prompts to confirm the anomaly-detection skills loaded:

```
Any capital anomalies on Tencent recently?
```

| Scenario | Try This |
|----------|----------|
| Capital anomaly | `Who's buying and selling Tencent recently?` |
| Derivatives anomaly | `Any option anomalies on NVIDIA recently?` |
| Technical anomaly | `Any technical signals on Apple recently?` |

### Verify OpenAPI Skills

Try the following prompts to confirm the OpenAPI skills loaded:

```
Show Tencent's K-line
```

| Scenario | Try This |
|----------|----------|
| Real-time quote | `What's Tencent's current price?` |
| K-line data | `Show TSLA's daily K-line for the last month` |
| Portfolio | `Show my positions` |
| Simulated order | `Simulated buy 100 shares of AAPL` |
| Stock screening | `Top 20 HK stocks by market cap` |
| Option query | `What expiries does AAPL have?` |

On clients that support slash commands (e.g. Claude Code), you can also invoke `/openapi` and `/install-futu-opend` directly.

---

## Multi-language SkillHub Entry Points

| Language | URL |
|----------|-----|
| Simplified Chinese | [www.futunn.com/skillhub](https://www.futunn.com/skillhub) |
| Traditional Chinese | [www.futunn.com/hk/skillhub](https://www.futunn.com/hk/skillhub) |
| English | [www.futunn.com/en/skillhub](https://www.futunn.com/en/skillhub) |

---

## Troubleshooting

<details>
<summary><b>Chat says Futu-related capabilities cannot be found</b></summary>

Some clients require restarting the app or starting a new chat to load newly-installed skills. Make sure all installation steps are complete, then retry in a fresh conversation.

</details>

<details>
<summary><b>Search returns empty results or errors</b></summary>

- Make sure your network can reach `ai-news-search.futunn.com`
- Try different keywords, e.g. the Chinese stock name or English company name
- If error codes persist, the service may be temporarily unavailable — try again later

</details>

<details>
<summary><b>OpenAPI connection failure</b></summary>

- Make sure OpenD has started and logged in (the UI shows "connected")
- Check the port number — it should be `11111` by default
- If OpenD is not installed yet, see the "Installing OpenAPI Skills and OpenD" section above

</details>

<details>
<summary><b>Quotes work, but trading does not</b></summary>

Trading requires extra steps:

1. Confirm the trading environment: simulated (SIMULATE) is used by default; live must be specified explicitly
2. Live trading requires unlocking the trade password manually in the OpenD GUI
3. Verify your account has the trading permission for the target market

</details>

<details>
<summary><b>Is sentiment analysis accurate?</b></summary>

Comment sentiment analysis infers sentiment from the most recent batch of comments / posts. It reflects the leaning of the sampled discussion rather than the whole market. Treat results as reference only, not investment advice.

</details>

<details>
<summary><b><code>npx skills add</code> fails</b></summary>

- Confirm Node.js 18+ is installed: `node -v`
- If it reports `command not found: skills`, upgrade npx: `npm install -g npm@latest`
- Private-repo clone failures: make sure your machine has an SSH key or HTTPS credential helper configured for `gitlab.futunn.com`; verify with a manual `git clone` first
- If the network is restricted, switch to HTTPS with a personal access token: `npx skills add -y -g https://<token>@gitlab.futunn.com/futu-common/futu-skills-hub.git#v20260428-futu-cli_v2`

</details>
