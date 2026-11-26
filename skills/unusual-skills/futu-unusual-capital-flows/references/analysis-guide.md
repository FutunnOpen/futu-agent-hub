# Unusual Capital Flows: Analysis Guide

## Normalize the Stock Target into a Standard Symbol

Before calling the CLI, convert the user-mentioned stock target into a standard symbol such as `US.TSLA`, `HK.00700`, `SH.600519`, or `SZ.000001`.

Normalization rules:

- If the user already gives a fully qualified symbol like `US.TSLA` or `HK.00700`, use it directly.
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

- `TSLA`, `AAPL`, `NVDA`, `MSFT`, `GOOG`, `META` usually mean US stocks, so normalize to `US.TSLA`, `US.AAPL`, `US.NVDA`, `US.MSFT`, `US.GOOG`, `US.META`.
- `00700` by itself is ambiguous in plain text; when the context clearly refers to Tencent, normalize to `HK.00700`.
- If the same company has both HK and US listings and the user does not specify the market, ask a clarifying question.

## Map Financial Intent to `analysis_dimensions`

Prefer these canonical `analysis_dimensions` values:

- `funds_distribution`: Capital distribution
- `funds_broker`: Buy/sell brokers
- `funds_flow`: Capital flow
- `short_sell_number`: Short sell volume
- `short_sell_ratio`: Short sell ratio
- `short_sell_number_and_ratio`: Short sell volume and ratio anomalous simultaneously

Selection guidance:

- If the user asks about `who is buying or selling / brokers`, include `funds_broker`.
- If the user asks about `large versus small orders / capital distribution`, include `funds_distribution`.
- If the user asks about `sustained institutional inflows or outflows / capital flow`, include `funds_flow`.
- If the user asks about `short sell volume`, include `short_sell_number`.
- If the user asks about `short sell ratio`, include `short_sell_ratio`.
- If the user asks about `simultaneous anomalies in short sell volume and ratio`, include `short_sell_number_and_ratio`.
- If the user asks a broad capital-flow question and does not narrow scope, omit `analysis_dimensions` and use the full interface.

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

1. Always normalize the user-mentioned stock target into a standard symbol before calling the CLI.
2. If the target stock is missing, ask a follow-up question.
3. If the market is ambiguous, ask a follow-up question instead of guessing.
4. If the user asks a broad capital-flow question, omit `analysis_dimensions` and use the full interface.
5. Do not output raw JSON by default when talking to the user, even if the CLI returns JSON.
6. Do not interpret the result as investment advice or trading guidance.
7. If the downstream service reports a permission issue, state that clearly and do not fabricate analysis.

---
