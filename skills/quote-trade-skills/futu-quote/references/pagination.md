# Quote pagination

Read this file when handling more results, the next page, or all results.

## General rules

- The current quote CLI does not paginate automatically. The caller must read the cursor from the previous response and pass it explicitly on the next request.
- Pagination tasks must use `--format json`. Table output does not guarantee that `pagination`, `extra`, or cursor fields are shown in full.
- The usual cursor is `next_key`. The CLI flag is `--next-key`.
- The time cursor is `next_time`. The CLI flag is `--next-time`.
- Page size is usually `limit`. The CLI flag is `--limit`.
- `count` and `num` mainly mean the number of rows returned or fetched. They are not necessarily the page size. Do not treat them as cursor pagination parameters by default.
- Stop paging when the cursor is empty, missing, or `0`, or when the API returns an empty list.
- Keep filters unchanged while paging and replace only the cursor. For example, keep `--view`, `--type`, `--market`, `--start`, `--end`, and sort fields from the previous request.

## Where to read response cursors

| Cursor | Preferred location | Fallback locations | Next-page argument |
| --- | --- | --- | --- |
| `next_key` | `pagination.next_key` | top-level `next_key`, `data.next_key` | `--next-key <value>` |
| `next_time` | `extra.next_time` | top-level `next_time`, `data.next_time` | `--next-time <value>` |

## Commands paginated by next_key

The first page usually omits `--next-key`. The next page passes `pagination.next_key` from the previous response.

| CLI | selector | BFF ID | Size parameter |
| --- | --- | --- | --- |
| `futu company <symbol>` | `--view efficiency` | `quote.company_operational_efficiency` | `--limit` default `10` |
| `futu corporate-actions <symbol>` | `--type buybacks` | `quote.corporate_actions_buybacks` | `--limit` default `10` |
| `futu economic-calendar` | `--view hot` | `quote.economic_calendar_hot` | `--limit` default `10` |
| `futu economic-calendar [keyword]` | `--view search` | `quote.economic_calendar_search` | `--limit` default `20` |
| `futu financials <symbol>` | `--view statements` | `quote.financials_statements` | `--limit` default `10` |
| `futu plate [symbol]` | `--view stocks` | `quote.plate_stock` | `--limit` default `200` |
| `futu research <symbol>` | `--type rating` | `quote.research_rating_summary` | `--limit` default `10` |
| `futu shareholders <symbol>` | `--view institutional` | `quote.shareholders_institutional` | `--limit` default `10` |
| `futu shareholders <symbol>` | `--view changes` | `quote.shareholders_holding_changes` | `--limit` default `30` |
| `futu shareholders <symbol>` | `--view holder-detail` | `quote.shareholders_holder_detail` | `--limit` default `10` |
| `futu shareholders <symbol>` | `--view insider-holders` | `quote.insider_holder_list` | `--limit` default `10` |
| `futu shareholders <symbol>` | `--view insider-trades` | `quote.insider_trade_list` | `--limit` default `10` |
| `futu valuation [symbol]` | `--view plate-stocks` | `quote.valuation_plate_stock_list` | `--limit` default `10` |
| `futu valuation [symbol]` | `--view index-stocks` | `quote.valuation_index_component_stock_list` | `--limit` default `10` |
| `futu stock-screen` | standalone command | `quote.stock_screen` | `--limit` default `20` |
| `futu warrant-screen` | standalone command | `quote.warrant_screen` | `--limit` default `20` |
| `futu option-screen` | standalone command | `quote.option_screen` | `--limit` default `20` |

Example:

```bash
futu shareholders US.AAPL --view changes --limit 30 --format json
futu shareholders US.AAPL --view changes --limit 30 --next-key '<pagination.next_key>' --format json
```

## Commands paginated by next_time

`next_time` continues a reverse-time or historical series. It is usually an integer timestamp and must not be constructed from a date string.

| CLI | selector | BFF ID | Size parameter | Cursor |
| --- | --- | --- | --- | --- |
| `futu history-kline <symbol>` | static command | `quote.history_kline` | `--num` default `100`, max `370` | `--next-time` |
| `futu capital <symbol>` | `--view history` | `quote.capital_flow_history` | `--count` default `365` | `--next-time` default `0` |

`--next-time` for `history-kline` is a millisecond timestamp. When `--next-time` is passed, it takes priority over `--end`.

```bash
futu history-kline HK.00700 --start 2026-01-01 --end 2026-03-01 --num 100 --format json
futu history-kline HK.00700 --start 2026-01-01 --next-time 1779163200000 --num 100 --format json
```

The first page of `capital --view history` defaults to `--next-time 0`. The next page passes `next_time` from the response.

```bash
futu capital HK.00700 --view history --period-type DAY --count 365 --format json
futu capital HK.00700 --view history --period-type DAY --count 365 --next-time '<extra.next_time>' --format json
```

## Size limits, not cursor pagination

These parameters only control how many rows are returned. The current command does not expose a next-page cursor. Do not loop unless the response explicitly returns a cursor.

| CLI | Parameter | Meaning |
| --- | --- | --- |
| `futu kline <symbol>` | `--num` | Latest N K-lines |
| `futu ticker <symbol>` | `--num` / `--count` | Latest N ticks |
| `futu order-book <symbol>` / `futu depth <symbol>` | `--num` | N levels of the order book |
| `futu rank [type]` | `--count` | Number of ranking rows |
| `futu broker <symbol> --view history` | `--days-before` | Broker ranking N days ago; not pagination |
| `futu financials <symbol> --view earnings-move` | `--count` / `--overview-count` | Number of post-earnings price-move rows |
| `futu option-data <symbol> --view probability` | `--limit` | Number of probability rows; `next_key` is not currently exposed |
| `futu short <symbol>` | `--count` | Number of short-sale rows |
