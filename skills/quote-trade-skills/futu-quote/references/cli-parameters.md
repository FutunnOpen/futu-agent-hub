# futu Quote CLI Parameters

Use `futu`. Append `--source skill` when invoking the CLI from Bash; omit this internal marker from commands displayed to users. Use `--format json` when parsing results. List more commands with `futu --help` and check any command’s current flags with `futu <command> --help`.

## General

- Symbols use `MARKET.CODE`, for example `US.AAPL`, `HK.00700`, `JP.7203` or `CC.BTC`. Numeric HK codes are padded to five digits. Search keywords are plain text.
- The default output is `table`; `--format json` produces machine-readable output. `--token-file` is optional.
- Quote commands query once; they do not provide a subscription. For multiple pages, use the response cursor as described in [pagination](pagination.md).

## Quotes and charts

| Command | Arguments and options |
| --- | --- |
| `futu quote <symbol...>` | One or more symbols. |
| `futu basicinfo <symbol...>` | One or more symbols. |
| `futu snapshot <symbol...>` | One or more symbols. |
| `futu kline <symbol>` | `--num` (default 100), `--ktype` (default 2, daily), `--autype` (default 1), `--extended-time`, `--pred-side`. |
| `futu history-kline <symbol>` | `--start`, `--end` (`yyyy-MM-dd`), `--num`, `--ktype`, `--autype`, `--extended-time`, `--pred-side`, `--next-time`. |
| `futu ticker <symbol>` | `--num` (default 20; 1–750); `--count` is an alias. `--period` can be repeated: `NORMAL`, `BEFORE`, `AFTER`, `OVERNIGHT`. |
| `futu rt-data <symbol>` | `--section NORMAL/FULL/PREMARKET/AFTERHOURS/HK_DARK/OVERNIGHT` (default `NORMAL`). |
| `futu order-book <symbol>` | `--num` caps depth; default 0 means the maximum allowed by permissions. `depth` is an alias. |
| `futu rank [type]` | `type` is `volume/turnover/gainers/losers/amplitude`; `--market HK/US/CN`, `--count`. |
| `futu option chain <symbol>` | `--start`, `--end`, `--filter-standard ALL/STANDARD/NON_STANDARD`, `--index-option-type`. If dates are omitted, the CLI chooses available expirations. |
| `futu future-info <symbol...>` | One or more futures symbols. |
| `futu market-state <symbol...>` | One or more symbols; optional `--is-contain-ba`, `--is-contain-overnight`, `--is-need-crypto-multi-broker`. |

`kline --autype` accepts 0–4; `history-kline --autype` accepts 0–2. See the command’s `--help` for K-line interval values and [dictionary](dictionaries.md) for terminology.

## Company, financials and market data

Select a view or type with the flag shown; other flags depend on the selection. Use `--help` for their complete list.

| Command | Selector and common options |
| --- | --- |
| `futu broker <symbol>` | `--view current/history`; `--date`, `--days-before`. |
| `futu capital <symbol>` | `--view intraday/history/distribution`; `--section`, `--period-type DAY/WEEK/MONTH`, `--start`, `--end`, `--count`, `--next-time`. |
| `futu company <symbol>` | `--view profile/executives/background/efficiency`; `--leader`, `--financial-type`, `--currency-code`, `--limit`, `--next-key`. For `background`, use the exact `leader_name` from executives. |
| `futu corporate-actions <symbol>` | `--type splits/buybacks/dividends/rehab`; `--divi-mode`, `--limit`, `--next-key`. |
| `futu economic-calendar [keyword]` | `--view hot/search`; `--search-type`, `--date`, `--timezone`, `--limit`, `--next-key`. |
| `futu financials <symbol>` | `--view statements/revenue/earnings-history/earnings-move`; `--statement-type`, `--financial-type`, `--date`, `--currency-code`, `--limit`, `--next-key`, `--count`, `--overview-count`. |
| `futu financials-earnings-card <symbol>` | Optional `--currency-code`. |
| `futu ipo-list` | `--market HK/US/SG/MY/CN` (default `HK`), `--request-type`. |
| `futu plate [symbol]` | `--view list/stocks/owner`; `--market`, `--plate-class`, `--plate-code`, `--sort-field`, `--price-type`, `--limit`, `--next-key`. |
| `futu research <symbol>` | `--type morningstar/consensus/rating`; `--rating-dimension-type`, `--limit`, `--next-key`. |
| `futu shareholders <symbol>` | `--view overview/institutional/changes/holder-detail/insider-holders/insider-trades`; `--holder-id`, `--holder-category`, `--period-id`, `--limit`, `--next-key`. |
| `futu short <symbol>` | `--type volume/interest`; `--count`. |
| `futu valuation [symbol]` | `--view detail/plate-stocks/index-stocks/index-plates`; `--valuation-type`, `--interval-type`, `--sort-id`, `--sort-type`, `--filter-symbol`, `--limit`, `--next-key`. |
| `futu trading-days` | `--market`, `--start`, `--end`; dates use `yyyy-MM-dd`. |

## Options, screening and unusual activity

| Command | Arguments and options |
| --- | --- |
| `futu option-data <symbol>` | `--view expiration/strategy/spread/probability/volatility`; `--expire-time`, `--far-expire-time`, `--strategy`, `--spread`, `--index-option-type`, `--filter-standard`. |
| `futu combo-option-quote` | `--combo-list` as a JSON array containing leg information. |
| `futu option-screen` | `--strategy`, `--strategy-param`, `--field-filter`, `--sort-obj` as JSON; `--limit`, `--next-key`, `--request-exact-data`. |
| `futu stock-screen` | `--screen-queries`, `--retrieve-queries`, `--sort`, `--sorts` as JSON; `--limit`, `--next-key`. |
| `futu warrant-screen` | `--symbol`, `--market-type`, `--screen-groups`, `--sorts`, `--limit`, `--next-key`, `--is-delay`, `--only-count`. |
| `futu unusual technical-signals <symbol>` | `--indicator-filters`, `--time-range`, `--language-id`. |
| `futu unusual capital-flows <symbol>` / `futu unusual derivatives-activity <symbol>` | `--analysis-dimensions`, `--time-range`, `--language-id`. |

## News, institutional data and watchlists

| Command | Arguments and options |
| --- | --- |
| `futu search [keyword]` | `--type news/community/feed` (default `community`). For news, keyword is required; `--news-type ALL/POST/NOTICE/REPORT`, `--sort-type TIME/PV`, `--source-ids`, `--sources`, `--lang`, `--page-size` (default 10; 1–50). |
| `futu crypto-institution-holding-list` | `--symbol` required; `--institution-type`, `--page-size`, `--page-flag`. |
| `futu crypto-institution-holding-overview` | `--symbol` required; optional `--institution-type`. |
| `futu institution-transaction-record` | `--institution-id` and `--symbol` required. |
| `futu watchlist [symbol...]` | `--action groups/list/add/delete/move-out`; `--group-name`, `--group-type`. Adding, deleting and moving symbols change the real watchlist and require the user’s explicit request. |

## Examples

```bash
futu quote US.AAPL
futu kline HK.00700 --ktype 2
futu history-kline US.AAPL --start 2026-01-01 --end 2026-01-31
futu search AAPL --type news --page-size 1
futu company US.AAPL --view executives
futu crypto-institution-holding-list --symbol CC.BTC
```

## Additional quote commands

For the commands below, the required flags are listed when applicable. Use `<command> --help` for optional flags, subcommands, defaults and enum values.

| Command | Required flags |
| --- | --- |
| `futu ark-active-transaction [flags]` | — |
| `futu ark-active-transaction-query [flags]` | — |
| `futu ark-fund-holding [flags]` | — |
| `futu ark-fund-holding-industry [flags]` | — |
| `futu ark-fund-return-rate [flags]` | — |
| `futu ark-net-turnover-rank [flags]` | — |
| `futu ark-stock-detail-daily <symbol> [flags]` | — |
| `futu ark-stock-detail-table <symbol> [flags]` | — |
| `futu ark-stock-dynamic <symbol> [flags]` | — |
| `futu broker-hold-detail <symbol> [flags]` | `--broker-code` |
| `futu broker-hold-ratio <symbol> [flags]` | — |
| `futu cbbc-basic-info <symbol> [flags]` | — |
| `futu cbbc-distribution <symbol> [flags]` | — |
| `futu chip-distribution <symbol> [flags]` | — |
| `futu combo-quotes [flags]` | `--mvc`, `--combo-legs` |
| `futu crypto-fear-greed-history [flags]` | — |
| `futu crypto-fear-greed-latest [flags]` | — |
| `futu crypto-market-data-card [flags]` | `--scene` |
| `futu crypto-market-overview [flags]` | — |
| `futu crypto-related-equity <symbol> [flags]` | — |
| `futu crypto-related-etf <symbol> [flags]` | — |
| `futu crypto-related-future <symbol> [flags]` | — |
| `futu depth <symbol> [flags]` | — |
| `futu dividend-calendar [flags]` | `--market`, `--date` |
| `futu earnings-calendar [flags]` | `--market` |
| `futu economic-calendar-list [flags]` | `--begin-date` |
| `futu etf-indicator-analysis <symbol> [flags]` | — |
| `futu etf-investment-distribution <symbol> [flags]` | — |
| `futu etf-net-assets <symbol> [flags]` | — |
| `futu etf-related-equity <symbol> [flags]` | — |
| `futu etf-screen [flags]` | `--market` |
| `futu etf-screen-options [flags]` | `--market` |
| `futu etf-style-box <symbol> [flags]` | — |
| `futu etf-top-holdings <symbol> [flags]` | — |
| `futu event-contract-category [flags]` | — |
| `futu event-contract-contracts [flags]` | `--event` |
| `futu event-contract-events [flags]` | `--series` |
| `futu event-contract-filter-competition [flags]` | `--category-id` |
| `futu event-contract-milestone [flags]` | `--milestone` |
| `futu event-contract-milestones [flags]` | — |
| `futu event-contract-series [flags]` | — |
| `futu financials-estimate <symbol> [flags]` | — |
| `futu financials-jp-performance-progress <symbol> [flags]` | — |
| `futu financials-jp-performance-revised <symbol> [flags]` | — |
| `futu future-correlation <symbol> [flags]` | `--related-codes` |
| `futu future-position-analysis <symbol> [flags]` | — |
| `futu future-seasonal <symbol> [flags]` | — |
| `futu heatmap [flags]` | `--market` |
| `futu heatmap-rise-fall-distribution [flags]` | — |
| `futu historical-info <symbol> [flags]` | `--date` |
| `futu index-related-etf <symbol> [flags]` | — |
| `futu indicator-backtest <symbol> [flags]` | `--indicator-id` |
| `futu indicator-polarity <symbol> [flags]` | — |
| `futu industrial-chain-by-plate [flags]` | — |
| `futu industrial-chain-detail [flags]` | `--chain-id` |
| `futu industrial-chain-list [flags]` | `--market` |
| `futu industrial-plate-info [flags]` | — |
| `futu industrial-plate-stock [flags]` | — |
| `futu influencer-holding-change [flags]` | `--influencer` |
| `futu influencer-holdings [flags]` | `--influencer` |
| `futu institution-distribution [flags]` | `--market`, `--institution-id` |
| `futu institution-holding-change [flags]` | `--market`, `--institution-id` |
| `futu institution-holdings [flags]` | `--market`, `--institution-id` |
| `futu institution-list [flags]` | `--market` |
| `futu institution-popular [flags]` | — |
| `futu institution-profile [flags]` | `--market`, `--institution-id` |
| `futu institution-return-rate [flags]` | `--institution-id` |
| `futu ipo-greenshoe <symbol> [flags]` | — |
| `futu ipo-hk-filings [flags]` | — |
| `futu ipo-institutions <symbol> [flags]` | — |
| `futu ipo-list-jp [flags]` | — |
| `futu ipo-placing-result <symbol> [flags]` | — |
| `futu kline-shape <symbol> [flags]` | — |
| `futu kline-shape-list [flags]` | — |
| `futu kline-shape-stocks [flags]` | `--shape-type` |
| `futu macro-fed-watch-dot-plot [flags]` | — |
| `futu macro-fed-watch-target-rate [flags]` | — |
| `futu macro-focus [flags]` | `--region` |
| `futu macro-indicator-chart [flags]` | `--indicator-id` |
| `futu macro-indicator-history [flags]` | `--indicator-id` |
| `futu macro-indicator-overview [flags]` | `--indicator-id` |
| `futu macro-indicator-related [flags]` | `--indicator-id` |
| `futu macro-indicator-summary [flags]` | `--indicator-id` |
| `futu macro-indicator-trend [flags]` | `--indicator-ids` |
| `futu macro-indicators [flags]` | `--region` |
| `futu macro-market-tab [flags]` | `--region` |
| `futu news-by-security [flags]` | — |
| `futu news-by-source [flags]` | — |
| `futu option-chain-statistic <symbol> [flags]` | — |
| `futu option-earnings-report-cycle <symbol> [flags]` | — |
| `futu option-earnings-screener [flags]` | `--option-market` |
| `futu option-event [flags]` | `--option-market` |
| `futu option-gamma-exposure <symbol> [flags]` | — |
| `futu option-iv-smile <symbol> [flags]` | — |
| `futu option-market-statistic [flags]` | `--option-market`, `--data-type`, `--begin-time`, `--end-time` |
| `futu option-max-pain <symbol> [flags]` | — |
| `futu option-rank [flags]` | `--option-market` |
| `futu option-seller-screener [flags]` | `--option-market`, `--seller-type` |
| `futu option-strategy-analysis [flags]` | `--combo-list` |
| `futu option-trade-interest-distribution <symbol> [flags]` | — |
| `futu option-underlying-his-statistic <symbol> [flags]` | `--begin-time`, `--end-time` |
| `futu option-underlying-his-volatility <symbol> [flags]` | — |
| `futu option-underlying-overview [flags]` | `--codes` |
| `futu option-underlying-rank [flags]` | `--option-market` |
| `futu option-zero-dte-contract [flags]` | `--code`, `--strike-date-timestamp` |
| `futu option-zero-dte-screener [flags]` | `--option-market` |
| `futu quote-research-analyst-ratings <symbol> [flags]` | `--analyst-uid` |
| `futu quote-research-institution-ratings <symbol> [flags]` | `--institution-uid` |
| `futu rank-dividend [flags]` | `--market`, `--rank-type` |
| `futu rank-earnings-beat [flags]` | `--market`, `--beat-type` |
| `futu rank-high-dividend-soe [flags]` | — |
| `futu rank-hot-list [flags]` | `--market` |
| `futu rank-period-change [flags]` | `--market` |
| `futu rank-short-selling [flags]` | `--market` |
| `futu rank-top-movers [flags]` | `--market` |
| `futu rank-us-after-hours [flags]` | — |
| `futu rank-us-overnight [flags]` | — |
| `futu rank-us-pre-market [flags]` | — |
| `futu referencefuture-list <symbol> [flags]` | — |
| `futu related-etf <symbol> [flags]` | — |
| `futu research-analyst-info [flags]` | `--uids` |
| `futu research-analyst-ratings [flags]` | `--analyst-uid` |
| `futu research-dimension-summary [flags]` | `--uid` |
| `futu research-dimension-summary-v2 [flags]` | `--uid` |
| `futu research-institution-info [flags]` | `--uids` |
| `futu research-institution-rating-summary <symbol> [flags]` | `--institution-uid` |
| `futu research-institution-ratings [flags]` | `--institution-uid` |
| `futu research-latest-ratings [flags]` | — |
| `futu research-rating-change [flags]` | — |
| `futu research-rating-plot <symbol> [flags]` | `--uid` |
| `futu research-rating-search [flags]` | `--keyword` |
| `futu research-stock-ratings <symbol> [flags]` | — |
| `futu research-target-plot <symbol> [flags]` | — |
| `futu research-target-price <symbol> [flags]` | — |
| `futu research-top-analysts [flags]` | — |
| `futu search-hot-stocks [flags]` | — |
| `futu search-hot-topics [flags]` | — |
| `futu short-jp-credit <symbol> [flags]` | — |
| `futu short-jp-deposit <symbol> [flags]` | — |
| `futu similar-kline <symbol> [flags]` | — |
| `futu stock-connect-cumulative [flags]` | `--channel` |
| `futu stock-connect-flow <symbol> [flags]` | — |
| `futu stock-connect-history [flags]` | `--channel` |
| `futu stock-connect-hold-ratio <symbol> [flags]` | — |
| `futu stock-connect-intraday [flags]` | `--channel` |
| `futu stock-connect-rank [flags]` | `--market` |
| `futu stock-connect-trade-top10 [flags]` | `--channel` |
| `futu valid-combos [flags]` | — |
