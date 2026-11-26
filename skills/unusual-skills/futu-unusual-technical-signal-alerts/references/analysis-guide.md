# Technical Signal Alerts: Analysis Guide

## Normalize the Stock Target into a Standard Symbol

Before calling the CLI, convert the user-mentioned stock target into a standard symbol such as `US.NVDA`, `HK.00700`, `SH.600519`, or `SZ.000001`.

Normalization rules:

- If the user already gives a fully qualified symbol like `US.NVDA` or `HK.00700`, use it directly.
- If the user gives a Chinese company name, English company name, or common ticker, map it to the matching market-prefixed symbol.
- If the symbol is ambiguous, ask a follow-up question instead of guessing.

Common mappings:

| User mention | Standard symbol |
|--------------|-----------------|
| Tencent | `HK.00700` |
| Alibaba | `HK.09988` |
| Apple | `US.AAPL` |
| Tesla | `US.TSLA` |
| NVIDIA | `US.NVDA` |
| Microsoft | `US.MSFT` |
| Google, Alphabet | `US.GOOG` |
| Amazon | `US.AMZN` |
| Meta, Facebook | `US.META` |
| TSMC, TSM | `US.TSM` |
| Kweichow Moutai | `SH.600519` |
| CATL | `SZ.300750` |

Ticker inference guidance:

- `NVDA`, `AAPL`, `TSLA`, `MSFT`, `GOOG`, `META` usually mean US stocks, so normalize to `US.NVDA`, `US.AAPL`, `US.TSLA`, `US.MSFT`, `US.GOOG`, `US.META`.
- `00700` by itself is ambiguous in plain text; when the context clearly refers to Tencent, normalize to `HK.00700`.
- If the same company has both HK and US listings and the user does not specify the market, ask a clarifying question.

## Map Technical Intent to `indicator_filters`

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
- If the user asks about `MACD`, a golden cross, or a death cross, include `MACD`.
- If the user asks about `RSI` or overbought/oversold conditions, include `RSI6`, `RSI12`, and `RSI24`.
- If the user asks about `ARBR`, include both `AR` and `BR`.
- If the user asks about `BIAS24` or the bias ratio, include `BIAS`.
- If the user asks about one specific indicator, only pass that indicator's backend filter value when possible.

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
