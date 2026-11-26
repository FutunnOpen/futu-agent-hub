# Unusual Capital Flows: Examples

## Example User Requests

### Broad capital anomaly check

- "Has Tesla shown unusual capital flows in the last 7 days?"
- "Has Tencent had unusual institutional capital activity recently?"
- "Check Apple for recent capital-flow anomalies."

Mapped request:

```json
{
  "stock_symbol": "US.TSLA",
  "time_range": 7,
  "language_id": 2
}
```

### Broker and capital-distribution only

- "Which brokers have been buying and selling Tencent recently?"
- "Have large and small orders in HK.00700 diverged recently?"

Mapped request:

```json
{
  "stock_symbol": "HK.00700",
  "time_range": 7,
  "analysis_dimensions": ["funds_distribution", "funds_broker"],
  "language_id": 2
}
```

### Funds flow only

- "Has Apple had sustained institutional inflows or outflows recently?"

Mapped request:

```json
{
  "stock_symbol": "US.AAPL",
  "time_range": 5,
  "analysis_dimensions": ["funds_flow"],
  "language_id": 2
}
```

### Short sell only

- "Has TSLA's short sell ratio been unusual recently?"

Mapped request:

```json
{
  "stock_symbol": "US.TSLA",
  "time_range": 7,
  "analysis_dimensions": ["short_sell_ratio"],
  "language_id": 2
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
