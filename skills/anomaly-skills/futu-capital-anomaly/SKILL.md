---
name: futu-capital-anomaly
description: >-
  Detects capital-flow anomaly signals for a user-mentioned stock with
  `get_financial_unusual`, including 资金分布、买卖经纪商、资金流向、卖空数量、
  卖空比例 and their unusual changes. Use when the user asks about 资金动向、资金异动、
  净流入、净流出、主力行为、大单小单、谁在买谁在卖、买卖经纪商、卖空异动、
  卖空/做空/沽空、主力是否在进场或离场，or gives a
  broad stock-anomaly request such as “英伟达异动”、“NVDA 异动”、“腾讯有没有异动/异常”
  without narrowing the dimension. For broad anomaly requests, this skill should
  be used together with `technical-anomaly` and `derivatives-anomaly`. Before
  calling the script, you must first normalize the user-mentioned stock name,
  Chinese company name, English company name, or ticker into a standard symbol
  such as `US.TSLA` or `HK.00700`.
metadata:
  version: 0.0.1
  requires:
    bins: 
        - python3 
    skills:
        - install-futu-opend
        - futuapi
  author: Futu
license: MIT
---

# Capital Anomaly Skill

Detects capital-flow anomalies for a specific stock and formats the result as a structured capital anomaly summary.

This skill is for **anomaly detection** rather than a regular capital-flow overview. If the data has no qualifying anomaly, return `No anomaly` or the interface's no-data result, and do not add extra market commentary.

If the user only says a broad request such as `英伟达异动`, `NVDA 异动`, `腾讯有没有异常` and does not specify a dimension, treat it as a bundled anomaly request. In that case, this skill should be used as one of the three default anomaly skills together with `technical-anomaly` and `derivatives-anomaly`.

---

## CLI: Version Update Check

Embed the version check into the skill's **single Bash call**. **Do not create any separate tool call** for the version check. The same inline check must detect three things:

1. whether the `futu-skills` manager is installed locally;
2. whether this skill has a new version available;
3. whether the `futu-skills` manager itself has a new version available.

Start the check as a backgrounded subprocess **before** the business command (e.g. `curl`), then append `wait` **after** the business command to collect the result, all in one invocation:

```bash
( _c=""; command -v futu-skills >/dev/null 2>&1 && _c=futu-skills || { [ -x "$HOME/.local/bin/futu-skills" ] && _c="$HOME/.local/bin/futu-skills"; }; if [ -n "$_c" ]; then "$_c" check --quiet --slug futu-capital-anomaly 2>/dev/null; else echo '__CLI_MISSING__'; fi ) > /tmp/.futu-capital-anomaly-update 2>/dev/null & curl -sG '...' ...; wait; cat /tmp/.futu-capital-anomaly-update 2>/dev/null; rm -f /tmp/.futu-capital-anomaly-update
```

Based on the `cat` output:

- **No content** (skill is up-to-date or the check failed): do not show any upgrade prompt.
- **Output `__CLI_MISSING__`** (`futu-skills` is not installed locally, so version check/upgrade cannot run): append a notice at the **end** of your reply:
  > The `futu-skills` manager is not installed yet, so I cannot auto-check or upgrade skill versions. If you agree, I can install it for you now.

  If the user agrees, first run:
  ```bash
  curl -fsSL https://raw.githubusercontent.com/FutunnOpen/futu-agent-hub/main/futu-install.sh | bash
  ```
  After install completes, run `futu-skills upgrade futu-capital-anomaly` to bring this skill to the latest version.
- **Output containing a line starting with `futu-capital-anomaly`** (this skill has an update available): append a notice at the **end** of your reply:
  > `futu-capital-anomaly` has a new version available. If you agree, I can upgrade it for you right away.

  If the user agrees, run `futu-skills upgrade futu-capital-anomaly` to perform the upgrade. (This command also auto-upgrades the `futu-skills` manager itself, so a separate CLI prompt is unnecessary when a skill update is available.)
- **Output containing only a line starting with `cli`** (this skill is up-to-date but the `futu-skills` manager itself has a new version): append a notice at the **end** of your reply:
  > The `futu-skills` manager has a new version available. If you agree, I can upgrade it for you right away.

  If the user agrees, run `futu-skills self-upgrade` to perform the upgrade.

  If both a `cli` line and a `futu-capital-anomaly` line appear, only show the skill upgrade prompt above — the manager will be refreshed as a side effect of `futu-skills upgrade futu-capital-anomaly`.

**Never** run the install command or `futu-skills upgrade …` without explicit user consent. Any error (command failure, network issue) must be silently skipped without affecting normal skill execution.

**Important**: The version check (write + read) must all be embedded in this single Bash call. Do not produce any additional tool calls.

<!-- This section follows docs/templates/opend-prerequisite.md. Keep it in sync with that template. -->
## Prerequisite: OpenD Must Be Running

This skill depends on Futu **OpenD** (default `127.0.0.1:11111`) to fetch capital anomaly data. OpenD installation and startup are owned by the peer `install-futu-opend` skill — do **not** attempt to detect, install, or start OpenD from inside this skill.

### Pre-flight Check

Silently probe OpenD reachability before the workflow. **Do not announce this step to the user.**

```bash
futu-skills check-opend
```

Behavior:

- **`ok`** — proceed straight to the Workflow. Do not mention OpenD or the pre-flight check; the user does not need to see it.
- **`not-running`** — ask the user for consent in one short, friendly line, e.g.:
  > 该 skill 需要本地 OpenD 服务（127.0.0.1:11111）才能拉取资金异动数据，目前未检测到。需要我现在帮你通过 `/install-futu-opend` 安装/启动吗？
  - If the user agrees, hand off by invoking `/install-futu-opend`. Resume this skill's Workflow once OpenD is reachable.
  - If the user declines, stop here — do **not** execute `scripts/handle_capital_anomaly.py`.

> **Hard rule**: When OpenD is not running, **do not execute `scripts/handle_capital_anomaly.py` directly**. Hand off to `/install-futu-opend` first.

---

## Workflow

### 1. Parse User Input

Extract the following from the user's request:

- `stock_target`: stock code, Chinese stock name, English company name, or ticker explicitly mentioned by the user
- `time_range`: default `7`; if the user says `最近 3 天` / `过去两周` / `last 5 days`, convert it to a natural-day integer
- `analysis_dimensions`: optional; only extract when the user clearly asks about one or more specific financial dimensions
- `language_id`: infer from the user's language

If the target stock is missing, ask a follow-up question instead of guessing.

### 2. Normalize the Stock Target into a Standard Symbol

Before calling the script, convert the user-mentioned stock target into a standard symbol such as `US.TSLA`, `HK.00700`, `SH.600519`, or `SZ.000001`.

Normalization rules:

- If the user already gives a fully qualified symbol like `US.TSLA` or `HK.00700`, use it directly.
- If the user gives a Chinese company name, English company name, or common ticker, map it to the matching market-prefixed symbol.
- If the symbol is ambiguous, ask a follow-up question instead of guessing.

Common mappings:

| User mention | Standard symbol |
|--------------|-----------------|
| 腾讯 | `HK.00700` |
| 阿里巴巴、阿里 | `HK.09988` |
| 苹果、Apple | `US.AAPL` |
| 特斯拉、Tesla | `US.TSLA` |
| 英伟达、NVIDIA | `US.NVDA` |
| 微软、Microsoft | `US.MSFT` |
| 谷歌、Google、Alphabet | `US.GOOG` |
| 亚马逊、Amazon | `US.AMZN` |
| Meta、脸书、Facebook | `US.META` |
| 台积电、TSM | `US.TSM` |
| 贵州茅台、茅台 | `SH.600519` |
| 宁德时代 | `SZ.300750` |

Ticker inference guidance:

- `TSLA`, `AAPL`, `NVDA`, `MSFT`, `GOOG`, `META` usually mean US stocks, so normalize to `US.TSLA`, `US.AAPL`, `US.NVDA`, `US.MSFT`, `US.GOOG`, `US.META`.
- `00700` by itself is ambiguous in plain text; when the context clearly refers to Tencent, normalize to `HK.00700`.
- If the same company has both HK and US listings and the user does not specify the market, ask a clarifying question.

### 3. Map Financial Intent to `analysis_dimensions`

Prefer these canonical `analysis_dimensions` values:

- `funds_distribution`: Capital distribution
- `funds_broker`: Buy/sell brokers
- `funds_flow`: Capital flow
- `short_sell_number`: Short sell volume
- `short_sell_ratio`: Short sell ratio
- `short_sell_number_and_ratio`: Short sell volume and ratio anomalous simultaneously

Selection guidance:

- If the user asks about `谁在买/谁在卖/经纪商`, include `funds_broker`.
- If the user asks about `大单小单/资金分歧/资金分布`, include `funds_distribution`.
- If the user asks about `主力连续流入流出/资金流向`, include `funds_flow`.
- If the user asks about `卖空数量`, include `short_sell_number`.
- If the user asks about `卖空比例`, include `short_sell_ratio`.
- If the user asks about `卖空数量和比例是否同时异常`, include `short_sell_number_and_ratio`.
- If the user asks a broad capital-flow question and does not narrow scope, omit `analysis_dimensions` and use the full interface.

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

### 5. Call the Script

After extracting and normalizing the parameters, call the script with a Python 3 interpreter. Prefer `python3`; only fall back to `python` when `python3` is unavailable. This avoids the common macOS case where `python` is not installed or not on `PATH`.

Script entry:

```bash
PYTHON_BIN="$(command -v python3 || command -v python)" && "$PYTHON_BIN" scripts/handle_capital_anomaly.py <STANDARD_SYMBOL> --time-range <DAYS> [--analysis-dimensions ...] [--language-id <ID>] --json
```

Examples:

```bash
PYTHON_BIN="$(command -v python3 || command -v python)" && "$PYTHON_BIN" scripts/handle_capital_anomaly.py US.NVDA --time-range 7 --json
PYTHON_BIN="$(command -v python3 || command -v python)" && "$PYTHON_BIN" scripts/handle_capital_anomaly.py HK.00700 --time-range 7 --analysis-dimensions funds_distribution funds_broker --json
PYTHON_BIN="$(command -v python3 || command -v python)" && "$PYTHON_BIN" scripts/handle_capital_anomaly.py US.AAPL --time-range 5 --analysis-dimensions funds_flow --json
```

### 6. Check the Result

- If the script exits successfully, use the returned data to build a structured capital-flow anomaly summary.
- If the script returns an error, surface the error message and do not fabricate results.
- If a requested class has no anomaly in the window, explicitly say `No anomaly`.
- If the downstream service reports a permission problem or no accessible data, clearly state that the stock or account lacks the required permission.

---

## Parameters

### Required

- `stock_symbol`: standard market-prefixed symbol, such as `US.TSLA`, `HK.00700`, `SH.600519`, `SZ.000001`

### Optional

- `time_range`: natural day window, default `7`
- `analysis_dimensions`: list of specific financial anomaly dimensions to inspect; omit for full scan
- `language_id`: output language, default `0`

---

## Output Rules

Present the output by anomaly class. The three high-level classes are:

- `Capital Distribution & Buy/Sell Brokers`
- `Capital Flow`
- `Short Selling`

Formatting rules:

- Always display `Time Range` as an absolute date range in the format `YYYY.M.D - YYYY.M.D`. Calculate the start date from the current date minus `time_range` days (e.g., if today is 2026.4.24 and time_range is 7, write `Time Range: 2026.4.18 - 2026.4.24`).
- If multiple abnormal dates appear within the window for one class, list them all.
- If a class has no anomaly in the window, write `No anomaly`.
- Preserve dates, direction, amount, ratio, broker names, and interpretation from the tool output.
- Do not merge different anomaly classes into one sentence.
- Do not invent thresholds, rankings, or causal explanations beyond the returned content.
- If the user only asked about a subset of financial dimensions, keep only the relevant classes.

---

## Preferred Response Template

```markdown
Time Range: {YYYY.M.D - YYYY.M.D}

- Capital Distribution & Buy/Sell Brokers: {anomaly description or "No anomaly"}
- Capital Flow: {anomaly description or "No anomaly"}
- Short Selling: {anomaly description or "No anomaly"}
```

When the user only asks for a subset, keep only the relevant classes.

---

## Behavior Rules

1. Always normalize the user-mentioned stock target into a standard symbol before calling the script.
2. If the target stock is missing, ask a follow-up question.
3. If the market is ambiguous, ask a follow-up question instead of guessing.
4. If the user asks a broad capital-flow question, omit `analysis_dimensions` and use the full interface.
5. Do not output raw JSON by default when talking to the user, even if the script returns JSON.
6. Do not interpret the result as investment advice or trading guidance.
7. If the downstream service reports a permission issue, state that clearly and do not fabricate analysis.

---

## Example User Requests

### Broad capital anomaly check

- "特斯拉最近 7 天有没有资金面异动？"
- "看看腾讯最近主力有没有异常动作"
- "帮我查一下 Apple 最近资金面有没有异常"

Mapped request:

```json
{
  "stock_symbol": "US.TSLA",
  "time_range": 7,
  "language_id": 0
}
```

### Broker and capital-distribution only

- "腾讯最近谁在买谁在卖？"
- "00700 最近大单小单有没有分歧？"

Mapped request:

```json
{
  "stock_symbol": "HK.00700",
  "time_range": 7,
  "analysis_dimensions": ["funds_distribution", "funds_broker"],
  "language_id": 0
}
```

### Funds flow only

- "苹果最近主力资金有连续流入流出吗？"

Mapped request:

```json
{
  "stock_symbol": "US.AAPL",
  "time_range": 5,
  "analysis_dimensions": ["funds_flow"],
  "language_id": 0
}
```

### Short sell only

- "TSLA 最近卖空比例有没有异常？"

Mapped request:

```json
{
  "stock_symbol": "US.TSLA",
  "time_range": 7,
  "analysis_dimensions": ["short_sell_ratio"],
  "language_id": 0
}
```

---

## Example Interpretation Style

```markdown
Time Range: 2026.4.2 - 2026.4.9

- Capital Distribution & Buy/Sell Brokers: On 4.3, extra-large orders had a net inflow of 113 million yuan with inflow/outflow magnitudes differing by more than 2x, while small orders had a net outflow of 178 million yuan in the opposite direction, indicating a divergence between large and small capital. From the broker side, the top two buyers were China Investment (Shanghai-HK Connect) and Futu Securities, while the top two sellers were UBS and Barclays Asia.
- Capital Flow: On 4.4, main capital had net outflows for 4 consecutive days, and that day's net outflow was 120% higher than the previous 3-day average, indicating main capital is accelerating its exit.
- Short Selling: On 4.5, short sell volume and short sell ratio were both anomalous: short sell volume rose day-over-day and the short sell ratio rose in parallel, both above the recent one-month average, reflecting a notably bearish outlook.
```
