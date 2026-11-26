# Unusual Derivatives Activity: Examples

## Example User Requests

### Broad derivatives anomaly check

- "Has Tencent had unusual derivatives activity in the last 7 days?"
- "Check NVDA for recent unusual options activity."
- "Check Apple for recent derivatives anomalies."

Mapped request:

```json
{
  "stock_symbol": "HK.00700",
  "time_range": 7,
  "language_id": 2
}
```

### IV and sentiment only

- "Have AAPL implied volatility and option sentiment been unusual recently?"
- "How have Apple's option volatility and put-call ratio changed recently?"

Mapped request:

```json
{
  "stock_symbol": "US.AAPL",
  "time_range": 7,
  "analysis_dimensions": ["option_volatility", "option_sentiment"],
  "language_id": 2
}
```

### Unusual option trades only

- "Have there been any unusually large NVDA option trades recently?"
- "Has NVIDIA had unusual option transactions recently?"

Mapped request:

```json
{
  "stock_symbol": "US.NVDA",
  "time_range": 7,
  "analysis_dimensions": ["option_unusual"],
  "language_id": 2
}
```

### Warrant-related only

- "Has Tencent's bull/bear warrant open interest ratio been unusual recently?"
- "Where are the concentrated warrant positions for HK.00700?"

Mapped request:

```json
{
  "stock_symbol": "HK.00700",
  "time_range": 7,
  "analysis_dimensions": ["warrant_ratio", "warrant_price_distribution"],
  "language_id": 2
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
