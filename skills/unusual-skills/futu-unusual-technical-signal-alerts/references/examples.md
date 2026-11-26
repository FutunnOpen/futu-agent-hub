# Technical Signal Alerts: Examples

## Example User Requests

### Broad technical anomaly check

- "What technical anomalies has NVIDIA shown in the last 7 days?"
- "Check Tencent's recent technical signals."
- "Check Apple for recent technical anomalies."

Mapped request:

```json
{
  "stock_symbol": "US.NVDA",
  "time_range": 7,
  "language_id": 2
}
```

### MACD and RSI only

- "Have HK.00700 MACD and RSI been unusual in the last 7 days?"
- "Check NVDA's MACD and RSI signals."

Mapped request:

```json
{
  "stock_symbol": "HK.00700",
  "time_range": 7,
  "indicator_filters": ["MACD", "RSI6", "RSI12", "RSI24"],
  "language_id": 2
}
```

### ARBR only

- "Has Tencent's ARBR shown unusual activity recently?"

Mapped request:

```json
{
  "stock_symbol": "HK.00700",
  "time_range": 7,
  "indicator_filters": ["AR", "BR"],
  "language_id": 2
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
