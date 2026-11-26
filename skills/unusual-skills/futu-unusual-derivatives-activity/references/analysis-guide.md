# Unusual Derivatives Activity: Analysis Guide

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

## Map Derivatives Intent to `analysis_dimensions`

Prefer these canonical `analysis_dimensions` values:

- `warrant_ratio`: Warrant open interest ratio anomaly, HK stocks only
- `warrant_price_distribution`: Warrant open interest price distribution anomaly, HK stocks only
- `option_unusual`: Unusual option trades (large orders)
- `option_volatility`: Option volatility anomaly
- `option_volume_price`: Option volume-price anomaly
- `option_sentiment`: Option sentiment anomaly
- `option_comprehensive`: Option comprehensive signal anomaly

Selection guidance:

- If the user asks about `bull/bear warrant open interest ratio`, include `warrant_ratio`.
- If the user asks about `concentrated warrant positions / open interest price range / support and resistance`, include `warrant_price_distribution`.
- If the user asks about `large option trades / V/OI / smart-money bets`, include `option_unusual`.
- If the user asks about `IV / IV percentile / IV rank / HV / volatility premium`, include `option_volatility`.
- If the user asks about `option volume / open interest / OI / underlying-stock interaction`, include `option_volume_price`.
- If the user asks about `PCR / put-call ratio / bullish or bearish sentiment`, include `option_sentiment`.
- If the user asks about `comprehensive signals / divergence across dimensions`, include `option_comprehensive`.
- If the user asks a broad derivatives question and does not narrow scope, omit `analysis_dimensions` and use the full interface.

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

1. Always normalize the user-mentioned stock target into a standard symbol before calling the CLI.
2. If the target stock is missing, ask a follow-up question.
3. If the market is ambiguous, ask a follow-up question instead of guessing.
4. If the user asks a broad derivatives question, omit `analysis_dimensions` and use the full interface.
5. Do not output raw JSON by default when talking to the user, even if the CLI returns JSON.
6. Do not interpret the result as investment advice or trading guidance.
7. If the downstream service reports a permission issue, state that clearly and do not fabricate analysis.
8. For non-HK stocks, do not force warrant-specific conclusions; use `N/A` or `No anomaly`.

---
