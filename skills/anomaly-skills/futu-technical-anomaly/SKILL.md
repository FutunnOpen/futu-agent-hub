---
name: futu-technical-anomaly
description: >-
  Detects technical-analysis anomaly signals for a user-mentioned stock with
  `get_technical_unusual`, including K线形态 and indicator events such as CCI,
  KDJ, RSI, BIAS, ARBR, VR, PSY, OSC, WMSR, MACD, BOLL, and MA. Use when the
  user asks about 技术面情况、最近有什么技术信号、K线形态、形态识别、形态突破、金叉/死叉、
  超买超卖、MACD、RSI、KDJ、CCI、MA、BOLL、WMSR、VR、PSY、OSC、BIAS、ARBR，
  or gives a broad stock-anomaly request such as “英伟达异动”、“NVDA 异动”、
  “腾讯有没有异动/异常” without narrowing the dimension. For broad anomaly
  requests, this skill should be used together with `capital-anomaly` and
  `derivatives-anomaly`. Before calling the CLI, you must first normalize the
  user-mentioned stock name, Chinese company name, English company name, or
  ticker into a standard symbol such as `US.NVDA` or `HK.00700`.
allowed-tools: Bash Read
metadata:
  version: 0.0.2
  requires:
    bins:
      - futu
  author: Futu
license: MIT
---

# Technical Anomaly Skill

Detects technical-analysis anomalies for a specific stock and formats the result as a structured technical anomaly summary.

This skill is for **anomaly detection** rather than a regular technical overview. Focus on concrete abnormal events within the requested window. Do not add extra market commentary, fundamentals-based explanations, or investment advice.

If the user only says a broad request such as `英伟达异动`, `NVDA 异动`, `腾讯有没有异常` and does not specify a dimension, treat it as a bundled anomaly request. In that case, this skill should be used as one of the three default anomaly skills together with `capital-anomaly` and `derivatives-anomaly`.

---

## Prerequisite: Futu CLI

This skill calls **`futu anomaly technical`** (OAuth REST via the official CLI). Do **not** use OpenD, `futu-api`, or removed `futuapi` scripts.

Before the workflow, follow [CLI runtime](../references/cli-runtime.md): probe `futu auth status --format json` silently. If the CLI is missing or the user is not logged in, stop and resolve before calling anomaly commands. If `futu anomaly` is not recognized, say anomaly needs a newer CLI — see repo `docs/migration-gaps-and-rest-api.md`.

---

## Workflow

### 1. Parse User Input

Extract the following from the user's request:

- `stock_target`: stock code, Chinese stock name, English company name, or ticker explicitly mentioned by the user
- `time_range`: default `7`; if the user says `最近 3 天` / `过去两周` / `last 5 days`, convert it to a natural-day integer
- `indicator_filters`: optional; only extract when the user clearly asks for one or more specific indicators
- `language_id`: infer from the user's language

If the target stock is missing, ask a follow-up question instead of guessing.

### 2. Normalize the Stock Target into a Standard Symbol

Before calling the CLI, convert the user-mentioned stock target into a standard symbol such as `US.NVDA`, `HK.00700`, `SH.600519`, or `SZ.000001`.

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

### 3. Map Technical Intent to `indicator_filters`

Prefer these canonical `indicator_filters` values when the user clearly asks about a subset:

- `CCI`
- `KDJ`
- `BIAS`
- `AR`
- `BR`
- `VR`
- `PSY`
- `OSC`
- `WMSR`
- `MACD`
- `BOLL`
- `MA`
- `RSI6`
- `RSI12`
- `RSI24`

Selection guidance:

- If the user asks a broad technical question and does not limit indicators, omit `indicator_filters`.
- If the user asks about `MACD`, `金叉`, or `死叉`, include `MACD`.
- If the user asks about `RSI` or `超买超卖`, include `RSI6`, `RSI12`, and `RSI24`.
- If the user asks about `ARBR`, include both `AR` and `BR`.
- If the user asks about `BIAS24` or `乖离率`, include `BIAS`.
- If the user asks about one specific indicator, only pass that indicator's backend filter value when possible.

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

### 5. Call the CLI

After extracting and normalizing the parameters, run (repeat `--indicator-filters` for each filter, or pass a comma-separated list if the CLI accepts it):

```bash
futu anomaly technical <STANDARD_SYMBOL> --time-range <DAYS> [--indicator-filters <FILTER> ...] [--language-id <ID>] --format json --source skill
```

Examples:

```bash
futu anomaly technical US.NVDA --time-range 7 --format json --source skill
futu anomaly technical HK.00700 --time-range 7 --indicator-filters MACD RSI6 RSI12 RSI24 --language-id 0 --format json --source skill
futu anomaly technical SH.600519 --time-range 14 --indicator-filters BOLL MA --format json --source skill
```

### 6. Check the Result

- If the CLI exits successfully, use the JSON to build a structured technical-anomaly summary.
- If the CLI returns an error, surface the error message and do not fabricate results.
- If a requested indicator has no anomaly in the window, explicitly say `No anomaly`.

---

## Parameters

### Required

- `stock_symbol`: standard market-prefixed symbol, such as `US.NVDA`, `HK.00700`, `SH.600519`, `SZ.000001`

### Optional

- `time_range`: natural day window, default `7`
- `indicator_filters`: list of specific technical dimensions to inspect; omit for full scan
- `language_id`: output language, default `0`

---

## Output Rules

Present output by signal class. The response should cover:

- `Candlestick Patterns`
- requested indicator classes, or the full set returned by the interface

Formatting rules:

- Always display `Time Range` as an absolute date range in the format `YYYY.M.D - YYYY.M.D`. Calculate the start date from the current date minus `time_range` days (e.g., if today is 2026.4.24 and time_range is 7, write `Time Range: 2026.4.18 - 2026.4.24`).
- Show each class separately.
- If one class has multiple abnormal dates in the window, list them all in the same class.
- If one class has no anomaly in the window, write `No anomaly`.
- Preserve dates, pattern names, signal direction, probabilities, support/resistance, and interpretation from the tool output.
- Do not merge multiple indicator classes into one sentence.
- Do not invent thresholds or explanations beyond the returned content.
- If the user only asked about a subset of indicators, keep only `Candlestick Patterns` plus the requested indicator classes.

---

## Preferred Response Template

```markdown
Time Range: {YYYY.M.D - YYYY.M.D}

- Candlestick Patterns: {anomaly description or "No anomaly"}
- MACD: {anomaly description or "No anomaly"}
- RSI: {anomaly description or "No anomaly"}
- CCI: {anomaly description or "No anomaly"}
- KDJ: {anomaly description or "No anomaly"}
- BIAS: {anomaly description or "No anomaly"}
- ARBR: {anomaly description or "No anomaly"}
- VR: {anomaly description or "No anomaly"}
- PSY: {anomaly description or "No anomaly"}
- OSC: {anomaly description or "No anomaly"}
- WMSR: {anomaly description or "No anomaly"}
- BOLL: {anomaly description or "No anomaly"}
- MA: {anomaly description or "No anomaly"}
```

When the user only asks for a subset, keep only `Candlestick Patterns` plus the requested classes.

---

## Behavior Rules

1. Always normalize the user-mentioned stock target into a standard symbol before calling the CLI.
2. If the target stock is missing, ask a follow-up question.
3. If the market is ambiguous, ask a follow-up question instead of guessing.
4. If the user asks a broad technical question, omit `indicator_filters` and use the full interface.
5. Do not output raw JSON by default when talking to the user, even if the CLI returns JSON.
6. Do not interpret the result as investment advice or trading guidance.
7. Do not invent extra signal explanations beyond what the interface returns.

---

## Example User Requests

### Broad technical anomaly check

- "英伟达最近 7 天有什么技术面异动？"
- "看看腾讯最近的技术信号"
- "帮我查一下 Apple 最近有没有技术面异常"

Mapped request:

```json
{
  "stock_symbol": "US.NVDA",
  "time_range": 7,
  "language_id": 0
}
```

### MACD and RSI only

- "00700 最近 7 天 MACD 和 RSI 有没有异常？"
- "看看 NVDA 的 MACD、RSI 信号"

Mapped request:

```json
{
  "stock_symbol": "HK.00700",
  "time_range": 7,
  "indicator_filters": ["MACD", "RSI6", "RSI12", "RSI24"],
  "language_id": 0
}
```

### ARBR only

- "腾讯最近 ARBR 有异动吗？"

Mapped request:

```json
{
  "stock_symbol": "HK.00700",
  "time_range": 7,
  "indicator_filters": ["AR", "BR"],
  "language_id": 0
}
```

---

## Example Interpretation Style

```markdown
Time Range: 2026.4.2-2026.4.9

- Candlestick Patterns: On 4.5, a "bullish continuation triangle" formed, created by gradually lower highs and gradually higher lows, indicating that after forces converged the bulls took control and a breakout may lead to a further advance. The upside probability is 84.5%, support is 2.41, and resistance is 2.52.
- MACD: No anomaly
- RSI: On 4.2, RSI formed a golden cross, suggesting a potential upward leg; on 4.8, RSI formed a death cross, implying a possible downtrend.
- CCI: On 4.3, CCI broke above +100 and entered overbought territory, flagging near-term pullback risk.
- KDJ: On 4.6, the three KDJ lines formed a golden cross below 20, producing an oversold rebound signal.
```
