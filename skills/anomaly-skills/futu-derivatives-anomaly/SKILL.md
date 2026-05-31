---
name: futu-derivatives-anomaly
description: >-
  Detects derivatives anomaly signals for a user-mentioned stock with
  `get_derivative_unusual`, including 牛熊证街货比例、异动、anomaly, 牛熊证街货价格区间、期权大单、
  隐含波动率、期权量价、期权情绪、期权综合信号 and their unusual changes. Use
  when the user asks about 期权、衍生品、牛熊证、IV、隐含波动率、PCR、期权大单、
  期权异常成交、聪明钱、smart money、unusual options activity、做多做空情绪、
  波动率溢价、期权市场怎么看、有没有大单押注、大资金押注、适不适合卖期权，or gives a
  broad stock-anomaly request such as “英伟达异动”、“NVDA 异动”、“腾讯有没有异动/异常”
  without narrowing the dimension. For broad anomaly requests, this skill should
  be used together with `technical-anomaly` and `capital-anomaly`. Before
  calling the script, you must first normalize the user-mentioned stock name,
  Chinese company name, English company name, or ticker into a standard symbol
  such as `US.NVDA` or `HK.00700`.
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

# Derivatives Anomaly Skill

Detects derivatives anomalies for a specific stock and formats the result as a structured derivatives anomaly summary.

This skill is for **anomaly detection** rather than a regular derivatives overview. If the data has no qualifying anomaly, return `No anomaly` or `No anomaly (brief reason)`, and do not add extra market commentary.

If the user only says a broad request such as `英伟达异动`, `NVDA 异动`, `腾讯有没有异常` and does not specify a dimension, treat it as a bundled anomaly request. In that case, this skill should be used as one of the three default anomaly skills together with `technical-anomaly` and `capital-anomaly`.

---

## CLI: Version Update Check

Embed the version check into the skill's **single Bash call**. **Do not create any separate tool call** for the version check. The same inline check must detect three things:

1. whether the `futu-skills` manager is installed locally;
2. whether this skill has a new version available;
3. whether the `futu-skills` manager itself has a new version available.

Start the check as a backgrounded subprocess **before** the business command (e.g. `curl`), then append `wait` **after** the business command to collect the result, all in one invocation:

```bash
( _c=""; command -v futu-skills >/dev/null 2>&1 && _c=futu-skills || { [ -x "$HOME/.local/bin/futu-skills" ] && _c="$HOME/.local/bin/futu-skills"; }; if [ -n "$_c" ]; then "$_c" check --quiet --slug futu-derivatives-anomaly 2>/dev/null; else echo '__CLI_MISSING__'; fi ) > /tmp/.futu-derivatives-anomaly-update 2>/dev/null & curl -sG '...' ...; wait; cat /tmp/.futu-derivatives-anomaly-update 2>/dev/null; rm -f /tmp/.futu-derivatives-anomaly-update
```

Based on the `cat` output:

- **No content** (skill is up-to-date or the check failed): do not show any upgrade prompt.
- **Output `__CLI_MISSING__`** (`futu-skills` is not installed locally, so version check/upgrade cannot run): append a notice at the **end** of your reply:
  > The `futu-skills` manager is not installed yet, so I cannot auto-check or upgrade skill versions. If you agree, I can install it for you now.

  If the user agrees, first run:
  ```bash
  curl -fsSL https://raw.githubusercontent.com/FutunnOpen/futu-agent-hub/main/futu-install.sh | bash
  ```
  After install completes, run `futu-skills upgrade futu-derivatives-anomaly` to bring this skill to the latest version.
- **Output containing a line starting with `futu-derivatives-anomaly`** (this skill has an update available): append a notice at the **end** of your reply:
  > `futu-derivatives-anomaly` has a new version available. If you agree, I can upgrade it for you right away.

  If the user agrees, run `futu-skills upgrade futu-derivatives-anomaly` to perform the upgrade. (This command also auto-upgrades the `futu-skills` manager itself, so a separate CLI prompt is unnecessary when a skill update is available.)
- **Output containing only a line starting with `cli`** (this skill is up-to-date but the `futu-skills` manager itself has a new version): append a notice at the **end** of your reply:
  > The `futu-skills` manager has a new version available. If you agree, I can upgrade it for you right away.

  If the user agrees, run `futu-skills self-upgrade` to perform the upgrade.

  If both a `cli` line and a `futu-derivatives-anomaly` line appear, only show the skill upgrade prompt above — the manager will be refreshed as a side effect of `futu-skills upgrade futu-derivatives-anomaly`.

**Never** run the install command or `futu-skills upgrade …` without explicit user consent. Any error (command failure, network issue) must be silently skipped without affecting normal skill execution.

**Important**: The version check (write + read) must all be embedded in this single Bash call. Do not produce any additional tool calls.

<!-- This section follows docs/templates/opend-prerequisite.md. Keep it in sync with that template. -->
## Prerequisite: OpenD Must Be Running

This skill depends on Futu **OpenD** (default `127.0.0.1:11111`) to fetch derivatives anomaly data. OpenD installation and startup are owned by the peer `install-futu-opend` skill — do **not** attempt to detect, install, or start OpenD from inside this skill.

### Pre-flight Check

Silently probe OpenD reachability before the workflow. **Do not announce this step to the user.**

```bash
futu-skills check-opend
```

Behavior:

- **`ok`** — proceed straight to the Workflow. Do not mention OpenD or the pre-flight check; the user does not need to see it.
- **`not-running`** — ask the user for consent in one short, friendly line, e.g.:
  > 该 skill 需要本地 OpenD 服务（127.0.0.1:11111）才能拉取衍生品异动数据，目前未检测到。需要我现在帮你通过 `/install-futu-opend` 安装/启动吗？
  - If the user agrees, hand off by invoking `/install-futu-opend`. Resume this skill's Workflow once OpenD is reachable.
  - If the user declines, stop here — do **not** execute `scripts/handle_derivatives_anomaly.py`.

> **Hard rule**: When OpenD is not running, **do not execute `scripts/handle_derivatives_anomaly.py` directly**. Hand off to `/install-futu-opend` first.

---

## Workflow

### 1. Parse User Input

Extract the following from the user's request:

- `stock_target`: stock code, Chinese stock name, English company name, or ticker explicitly mentioned by the user
- `time_range`: default `7`; if the user says `最近 3 天` / `过去两周` / `last 5 days`, convert it to a natural-day integer
- `analysis_dimensions`: optional; only extract when the user clearly asks about one or more specific derivatives dimensions
- `language_id`: infer from the user's language

If the target stock is missing, ask a follow-up question instead of guessing.

### 2. Normalize the Stock Target into a Standard Symbol

Before calling the script, convert the user-mentioned stock target into a standard symbol such as `US.NVDA`, `HK.00700`, `SH.600519`, or `SZ.000001`.

Normalization rules:

- If the user already gives a fully qualified symbol like `US.NVDA` or `HK.00700`, use it directly.
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

- `NVDA`, `AAPL`, `TSLA`, `MSFT`, `GOOG`, `META` usually mean US stocks, so normalize to `US.NVDA`, `US.AAPL`, `US.TSLA`, `US.MSFT`, `US.GOOG`, `US.META`.
- `00700` by itself is ambiguous in plain text; when the context clearly refers to Tencent, normalize to `HK.00700`.
- If the same company has both HK and US listings and the user does not specify the market, ask a clarifying question.

### 3. Map Derivatives Intent to `analysis_dimensions`

Prefer these canonical `analysis_dimensions` values:

- `warrant_ratio`: Warrant open interest ratio anomaly, HK stocks only
- `warrant_price_distribution`: Warrant open interest price distribution anomaly, HK stocks only
- `option_unusual`: Unusual option trades (large orders)
- `option_volatility`: Option volatility anomaly
- `option_volume_price`: Option volume-price anomaly
- `option_sentiment`: Option sentiment anomaly
- `option_comprehensive`: Option comprehensive signal anomaly

Selection guidance:

- If the user asks about `牛熊证街货比例/牛熊街货比例`, include `warrant_ratio`.
- If the user asks about `重货区/街货价格区间/支撑压力`, include `warrant_price_distribution`.
- If the user asks about `期权大单/大额成交/V/OI/聪明钱押注`, include `option_unusual`.
- If the user asks about `IV/IV percentile/IV rank/HV/波动率溢价`, include `option_volatility`.
- If the user asks about `成交量/持仓量/OI/正股联动`, include `option_volume_price`.
- If the user asks about `PCR/Put Call Ratio/做多做空情绪`, include `option_sentiment`.
- If the user asks about `综合信号/多维背离`, include `option_comprehensive`.
- If the user asks a broad derivatives question and does not narrow scope, omit `analysis_dimensions` and use the full interface.

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
PYTHON_BIN="$(command -v python3 || command -v python)" && PYTHONUTF8=1 PYTHONIOENCODING=utf-8 "$PYTHON_BIN" scripts/handle_derivatives_anomaly.py <STANDARD_SYMBOL> --time-range <DAYS> [--analysis-dimensions ...] [--language-id <ID>] --json
```

Examples:

```bash
PYTHON_BIN="$(command -v python3 || command -v python)" && PYTHONUTF8=1 PYTHONIOENCODING=utf-8 "$PYTHON_BIN" scripts/handle_derivatives_anomaly.py HK.00700 --time-range 7 --json
PYTHON_BIN="$(command -v python3 || command -v python)" && PYTHONUTF8=1 PYTHONIOENCODING=utf-8 "$PYTHON_BIN" scripts/handle_derivatives_anomaly.py US.NVDA --time-range 7 --analysis-dimensions option_unusual option_volatility --json
PYTHON_BIN="$(command -v python3 || command -v python)" && PYTHONUTF8=1 PYTHONIOENCODING=utf-8 "$PYTHON_BIN" scripts/handle_derivatives_anomaly.py US.AAPL --time-range 7 --analysis-dimensions option_sentiment option_comprehensive --json
```

### 6. Check the Result

- If the script exits successfully, use the returned data to build a structured derivatives anomaly summary.
- If the script returns an error, surface the error message and do not fabricate results.
- If a requested class has no anomaly in the window, explicitly say `No anomaly` or `No anomaly (brief reason)`.
- If the downstream service reports a permission problem or no accessible data, clearly state that the stock or account lacks the required permission.
- If the stock is not Hong Kong listed, warrant-related classes should be marked as `N/A` or `No anomaly`.

---

## Parameters

### Required

- `stock_symbol`: standard market-prefixed symbol, such as `US.NVDA`, `HK.00700`, `SH.600519`, `SZ.000001`

### Optional

- `time_range`: natural day window, default `7`
- `analysis_dimensions`: list of specific derivatives anomaly dimensions to inspect; omit for full scan
- `language_id`: output language, default `0`

---

## Output Rules

Present the output by anomaly class. The seven classes are:

- `Warrant Open Interest Ratio Anomalies (HK)`
- `Warrant Open Interest Price Distribution Anomalies (HK)`
- `Unusual Option Trades`
- `Option Volatility Anomalies`
- `Option Volume-Price Anomalies`
- `Option Sentiment Anomalies`
- `Option Comprehensive Signal Anomalies`

Formatting rules:

- Always display `Time Range` as an absolute date range in the format `YYYY.M.D - YYYY.M.D`. Calculate the start date from the current date minus `time_range` days (e.g., if today is 2026.4.24 and time_range is 7, write `Time Range: 2026.4.18 - 2026.4.24`).
- Always preserve the class order above.
- **Full scan** (no `analysis_dimensions` specified): always show all 7 class names. Write `No anomaly` for classes with no anomaly. Never omit a class name.
- **Subset request** (user specifies one or more dimensions): show only the classes that correspond to the requested dimensions. Write `No anomaly` for requested classes that have no anomaly. Do not show unrelated classes.
- If multiple abnormal dates or timestamps appear within one class, list them all.
- For `Unusual Option Trades`, when multiple unusual option trades exist in the window, show all of them. Do not collapse them to only the highest-premium trade.
- Keep dates, timestamps, direction, volume, open interest, `V/OI`, premium amount, strike, expiry, percentile, price zone, and interpretation from the tool output.
- Do not merge different anomaly classes into one sentence.
- Warrant-related classes (`Warrant Open Interest Ratio Anomalies (HK)` and `Warrant Open Interest Price Distribution Anomalies (HK)`) apply to Hong Kong stocks only. If the stock is not Hong Kong listed, **omit these two classes entirely** from the output. Do not show them with `N/A`.
- Do not invent thresholds, rankings, or causal explanations beyond the returned content.

---

## Preferred Response Template

```markdown
Time Range: {YYYY.M.D - YYYY.M.D}

Warrant Open Interest Ratio Anomalies (HK):
{anomaly description or "No anomaly"}

Warrant Open Interest Price Distribution Anomalies (HK):
{anomaly description or "No anomaly"}

Unusual Option Trades:
{list every anomaly item by item, or "No anomaly"}

Option Volatility Anomalies:
{anomaly description or "No anomaly"}

Option Volume-Price Anomalies:
{anomaly description or "No anomaly"}

Option Sentiment Anomalies:
{anomaly description or "No anomaly"}

Option Comprehensive Signal Anomalies:
{anomaly description or "No anomaly"}
```

When the user only asks for a subset, keep only the relevant classes.

---

## Behavior Rules

1. Always normalize the user-mentioned stock target into a standard symbol before calling the script.
2. If the target stock is missing, ask a follow-up question.
3. If the market is ambiguous, ask a follow-up question instead of guessing.
4. If the user asks a broad derivatives question, omit `analysis_dimensions` and use the full interface.
5. Do not output raw JSON by default when talking to the user, even if the script returns JSON.
6. Do not interpret the result as investment advice or trading guidance.
7. If the downstream service reports a permission issue, state that clearly and do not fabricate analysis.
8. For non-HK stocks, do not force warrant-specific conclusions; use `N/A` or `No anomaly`.

---

## Example User Requests

### Broad derivatives anomaly check

- "腾讯最近 7 天有没有衍生品异动？"
- "看看 NVDA 最近期权市场有没有异常"
- "帮我查一下 Apple 最近衍生品有没有异动"

Mapped request:

```json
{
  "stock_symbol": "HK.00700",
  "time_range": 7,
  "language_id": 0
}
```

### IV and sentiment only

- "AAPL 最近 IV 和期权情绪有没有异常？"
- "苹果最近期权波动率和 PCR 怎么样？"

Mapped request:

```json
{
  "stock_symbol": "US.AAPL",
  "time_range": 7,
  "analysis_dimensions": ["option_volatility", "option_sentiment"],
  "language_id": 0
}
```

### Unusual option trades only

- "NVDA 最近有没有期权大单押注？"
- "英伟达最近有没有异常期权成交？"

Mapped request:

```json
{
  "stock_symbol": "US.NVDA",
  "time_range": 7,
  "analysis_dimensions": ["option_unusual"],
  "language_id": 0
}
```

### Warrant-related only

- "腾讯最近牛熊证街货比例有没有异常？"
- "00700 最近重货区在哪里？"

Mapped request:

```json
{
  "stock_symbol": "HK.00700",
  "time_range": 7,
  "analysis_dimensions": ["warrant_ratio", "warrant_price_distribution"],
  "language_id": 0
}
```

---

## Example Interpretation Style

```markdown
Time Range: 2026.4.2 - 2026.4.9

Warrant Open Interest Ratio Anomalies (HK):
On 4.3, bull warrant open interest reached 82.2%, higher than 90% of trading days in the past year, indicating more investors are holding bull warrants overnight, reflecting bullish sentiment.
On 4.7, bear warrant open interest reached 17.8%, higher than 90% of trading days in the past year, indicating more investors are holding bear warrants overnight, reflecting bearish sentiment.

Warrant Open Interest Price Distribution Anomalies (HK):
On 4.3, the bull warrant concentration zone sits in the 95.0-100.0 recall-price range, close to the day's close, indicating many investors hold bull warrants in this range and regard this price level as a support.
On 4.7, the largest new additions and the concentration zone for bull warrants are both in the 95.0-100.0 recall-price range, indicating many investors added bull warrants in this range and regard this price level as a support.

Unusual Option Trades:
On 4.4 15:31, a large call option trade occurred with a volume of 1000 contracts, far exceeding the open interest of 130, with a V/OI ratio as high as 15.2, which typically suggests a trader is opening an unusually large new position. The trade involved US$75,000, a strike price of US$10, and an expiry of 2025/09/08.
On 4.6 10:15, a large put option trade occurred with a volume of 800 contracts, far exceeding the open interest of 50, with a V/OI ratio as high as 16.0. The trade involved US$52,000, a strike price of US$165, and an expiry of 2025/05/02.

Option Volatility Anomalies:
On 4.5, implied volatility (IV) is at a historical high and significantly above realized historical volatility (HV), creating a large IV-HV premium. This environment favors option sellers, who can sell options to bet on mean reversion of volatility.
On 4.7, the implied volatility (IV) percentile reached 95, meaning IV is above most days in the past year; time value is high, and option-selling strategies can be used.

Option Volume-Price Anomalies:
On 4.5, option volume rose 52% over the prior period, open interest rose 48%, and the underlying rose 3.5%, which may indicate long capital entering in size and suggests the uptrend may continue. The option market shows significant volume and open-interest concentration near 260, which may become an important support or resistance level.

Option Sentiment Anomalies:
On 4.3, the option Put/Call Ratio percentile reached 89, higher than 89% of trading days in the past year, and rose for 2 consecutive days, with a significant increase in put option activity.

Option Comprehensive Signal Anomalies:
On 4.8, the underlying recently declined sharply, but option implied volatility percentile barely changed; the market has not priced in panic, and historically similar setups have often given rise to rebound opportunities.
```
