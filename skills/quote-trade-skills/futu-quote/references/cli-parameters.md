# Quote CLI parameters

When generating commands, use the smallest parameter set: include only required parameters, parameters the user explicitly specified, or parameters required to change CLI default behavior. Do not unconditionally write CLI defaults into the command.

Do not rely on this file alone for pagination details. When the user asks to page through results, read `references/pagination.md`.

## Global parameters

| Parameter | Default | When to pass |
| --- | --- | --- |
| `--format`, `-f` | `table` | Pass `--format json` only when the agent needs to parse the output. Usually omit it for commands the user will copy and run. |
| `--token-file` | config item `token_file` | Pass only when the user asks to use a non-default token file. |

Internal invocation convention: when this skill actually calls the CLI from Bash, always append the hidden internal marker `--source skill` at the end of the command. Do not include these internal markers in commands shown to the user.

## Symbol, JSON, and pagination entry points

- Symbols use `MARKET.CODE`, for example `HK.00700`, `US.AAPL`, and `CC.BTCUSD`. Do not pass bare `AAPL`, `700`, or `700.HK`.
- Left-pad numeric Hong Kong codes to 5 digits. Generally uppercase the market prefix and the stock code.
- For multi-symbol commands, append multiple `<symbol>` arguments directly.
- `json` flags must be valid JSON strings, for example `--strategy '{"market_category_list":[3]}'`.
- Defaults such as `TODAY` and `TODAY+30` are resolved by the CLI at runtime.
- Paginated APIs usually use `--next-key` or `--next-time`. The next page takes `pagination.next_key` or `extra.next_time` from the previous response. The current quote CLI does not paginate automatically. See `references/pagination.md` for the full rules.

## Static quote commands

| Command | Purpose | Required | Default / omit | Optional parameters |
| --- | --- | --- | --- | --- |
| `futu quote <symbol...>` | Real-time quote | `symbol...` | none | none |
| `futu basicinfo <symbol...>` | Static instrument info | `symbol...` | none | none |
| `futu snapshot <symbol...>` | Market snapshot | `symbol...` | none | none |
| `futu kline <symbol>` | Latest K-line | `symbol` | `--num 100`, `--ktype 2`, `--autype 1`, `--extended-time 0`, `--pred-side 0` | `--num`, `--ktype`, `--autype`, `--extended-time`, `--pred-side` |
| `futu history-kline <symbol>` | Historical K-line | `symbol` | `--end today`, `--num 100`, `--ktype 2`, `--autype 1`, `--next-time 0` | `--start`, `--end`, `--next-time`, `--num`, `--ktype`, `--autype`, `--extended-time`, `--pred-side` |
| `futu ticker <symbol>` | Tick trades | `symbol` | `--num 20` | `--num`, `--count`, repeatable `--period NORMAL/BEFORE/AFTER/OVERNIGHT` |
| `futu rt-data <symbol>` | Intraday data | `symbol` | `--section NORMAL` | `--section NORMAL/FULL/PREMARKET/AFTERHOURS/HK_DARK/OVERNIGHT` |
| `futu order-book <symbol>` | Order-book depth | `symbol` | `--num 0`, meaning the maximum depth allowed by permissions | `--num` 1-60 |
| `futu depth <symbol>` | Alias of `order-book` | `symbol` | same as `order-book` | same as `order-book` |
| `futu rank [type]` | Market ranking | none | `type=volume`, `--market HK`, `--count 20` | `type volume/turnover/gainers/losers/amplitude`, `--market HK/US/CN`, `--count` |
| `futu option chain <symbol>` | Option chain | `symbol` | automatically selects a 30-day forward window when no date is passed | `--start`, `--end`, `--index-option-type`, `--filter-standard ALL/STANDARD/NON_STANDARD` |

Common examples:

- Quote: `futu quote HK.00700 US.AAPL`
- Snapshot: `futu snapshot HK.00700 US.AAPL`
- US overnight K-line: `futu kline US.AAPL --ktype 1 --extended-time 2`
- Historical K-line: `futu history-kline HK.00700 --start 2026-01-01 --end 2026-03-01`
- Tick trades: `futu ticker US.AAPL --num 50 --period OVERNIGHT`
- Intraday: `futu rt-data US.AAPL --section PREMARKET`
- Order book: `futu order-book HK.00700 --num 10`
- Ranking: `futu rank gainers --market US --count 30`
- Option chain: `futu option chain HK.00700 --start 2026-05-01 --end 2026-05-31`

## Aggregate REST quote commands

These commands use a selector flag to map multiple underlying endpoints. Selector values are case-insensitive. Pass only the parameters required by the current selector. When the user mentions a legacy endpoint name, do not call the old root command directly. Map it to the aggregate command and selector.

### Broker

| Command | selector | Purpose | Extra parameters |
| --- | --- | --- | --- |
| `futu broker <symbol>` | `--view current` default | Current holdings of the top 10 brokers | `--date` |
| `futu broker <symbol>` | `--view history` | Historical top-10 broker holdings | `--days-before`, default `1` |

Example: `futu broker HK.00700 --view history --days-before 5`

### Capital

| Command | selector | Purpose | Extra parameters |
| --- | --- | --- | --- |
| `futu capital <symbol>` | `--view intraday` default | Intraday capital flow | `--section NORMAL/FULL/PREMARKET/AFTERHOURS` |
| `futu capital <symbol>` | `--view history` | Historical capital flow | `--period-type DAY/WEEK/MONTH`, `--start`, `--end`, `--count`, `--next-time` |
| `futu capital <symbol>` | `--view distribution` | Capital distribution | none |

Example: `futu capital HK.00700 --view history --period-type WEEK --count 52`

### Company

| Command | selector | Purpose | Extra parameters |
| --- | --- | --- | --- |
| `futu company <symbol>` | `--view profile` default | Company profile | none |
| `futu company <symbol>` | `--view executives` | Executive list | none |
| `futu company <symbol> [leader]` | `--view background` | Executive background | `[leader]` or `--leader`; if omitted, the CLI automatically uses the first executive |
| `futu company <symbol>` | `--view efficiency` | Operating efficiency | `--limit`, `--next-key`, `--currency-code`, `--financial-type 7/102` |

Example: `futu company US.AAPL "Tim Cook" --view background`

### Corporate Actions

| Command | selector | Purpose | Extra parameters |
| --- | --- | --- | --- |
| `futu corporate-actions <symbol>` | `--type dividends` default | Dividends | none |
| `futu corporate-actions <symbol>` | `--type splits` | Stock splits | none |
| `futu corporate-actions <symbol>` | `--type buybacks` | Buybacks | `--next-key`, `--limit` |
| `futu corporate-actions <symbol>` | `--type rehab` | Adjustment factors | `--divi-mode compat/exclude_divi/include_divi` |

### Economic Calendar

| Command | selector | Purpose | Extra parameters |
| --- | --- | --- | --- |
| `futu economic-calendar [keyword]` | `--view hot` default | Hot economic calendar | `--limit`, `--next-key`, `--date`, `--timezone` |
| `futu economic-calendar [keyword]` | `--view search` | Search economic calendar | `[keyword]`, `--search-type 1/2/3/4`, `--limit`, `--next-key`, `--time-order-type 0/1` |

### Financials

| Command | selector | Purpose | Extra parameters |
| --- | --- | --- | --- |
| `futu financials <symbol>` | `--view statements` default | Financial statements | `--statement-type`, `--financial-type`, `--currency-code`, `--next-key`, `--limit` |
| `futu financials <symbol>` | `--view revenue` | Revenue breakdown | `--date`, `--financial-type`, `--currency-code` |
| `futu financials <symbol>` | `--view earnings-history` | Post-earnings price history | none |
| `futu financials <symbol>` | `--view earnings-move` | Post-earnings price move | `--count`, `--overview-count` |

### IPO List

| Command | selector | Purpose | Extra parameters |
| --- | --- | --- | --- |
| `futu ipo-list` | `--market HK/US/SG/MY` | IPO list | `--request-type 9/10/11` |
| `futu ipo-list` | `--market CN` | China A-share IPO list | `--request-type 1/2/3/4/5` |

### Option Data

| Command | selector | Purpose | Extra parameters |
| --- | --- | --- | --- |
| `futu option-data <symbol>` | `--view expiration` default | Expiration dates | `--index-option-type`, `--filter-standard`, `--filter-expiration-cycles` |
| `futu option-data <symbol>` | `--view strategy` | Strategy filter | `--strategy`, `--expire-time`, `--far-expire-time`, `--spread`, `--index-option-type`, `--filter-standard` |
| `futu option-data <symbol>` | `--view spread` | Strategy spread | `--strategy`, `--expire-time`, `--far-expire-time`, `--index-option-type`, `--filter-standard` |
| `futu option-data <symbol>` | `--view probability` | Exercise probability | `--limit` |
| `futu option-data <symbol>` | `--view volatility` | Volatility | `--query-time-period`, `--hv-time-period` |

### Plate

| Command | selector | Purpose | Extra parameters |
| --- | --- | --- | --- |
| `futu plate [symbol]` | `--view list` default | Plate list | `--market HK/US/SH/SZ/SG/JP/AU/CA/MY/KR`, `--plate-class ALL/INDUSTRY/REGION/CONCEPT/OTHER` |
| `futu plate [symbol]` | `--view stocks` | Plate constituents | `[symbol]` defaults to `HK.LIST1045`, `--sort-field`, `--ascend`, `--price-type`, `--next-key`, `--limit` |
| `futu plate <symbol>` | `--view owner` | Plates that own a stock | `<symbol>` required |

### Research

| Command | selector | Purpose | Extra parameters |
| --- | --- | --- | --- |
| `futu research <symbol>` | `--type consensus` default | Analyst consensus | none |
| `futu research <symbol>` | `--type morningstar` | Morningstar report | none |
| `futu research <symbol>` | `--type rating` | Rating summary | `--rating-dimension-type`, `--next-key`, `--limit` |

### Search

| Command | selector | Purpose | Extra parameters |
| --- | --- | --- | --- |
| `futu search [keyword]` | `--type news` default | News search | `[keyword]` should be a full symbol, `--size`, `--news-type`, `--sort-type`, `--lang` |
| `futu search [keyword]` | `--type community` | Community search | `[keyword]` should be a full symbol, `--size`, `--community-type`, `--sort-type`, `--lang` |
| `futu search [keyword]` | `--type feed` | Stock feed | `[keyword]` should be a full symbol, `--size` |

### Shareholders

| Command | selector | Purpose | Extra parameters |
| --- | --- | --- | --- |
| `futu shareholders <symbol>` | `--view overview` default | Shareholder overview | `--period-id` |
| `futu shareholders <symbol>` | `--view institutional` | Institutional holdings | `--limit`, `--next-key` |
| `futu shareholders <symbol>` | `--view changes` | Holding changes | `--limit`, `--next-key`, `--sort-column`, `--sort-type`, `--filter-type`, `--holder-category` |
| `futu shareholders <symbol>` | `--view holder-detail` | Holder detail | `--request-type`, `--next-key`, `--limit`, `--sort-column`, `--sort-type`, `--period-id`, `--holder-id` |
| `futu shareholders <symbol>` | `--view insider-holders` | Insider holders | `--next-key`, `--limit` |
| `futu shareholders <symbol>` | `--view insider-trades` | Insider trades | `--next-key`, `--limit`, `--holder-id` |

### Short

| Command | selector | Purpose | Extra parameters |
| --- | --- | --- | --- |
| `futu short <symbol>` | `--type volume` default | Short volume | `--count` |
| `futu short <symbol>` | `--type interest` | Short interest | `--count` |

### Watchlist

| Command | selector | Purpose | Extra parameters |
| --- | --- | --- | --- |
| `futu watchlist [symbol...]` | `--action list` default | Watchlist | `--group-name` |
| `futu watchlist` | `--action groups` | Watchlist groups | `--group-type ALL/CUSTOM/SYSTEM` |
| `futu watchlist <symbol...>` | `--action add` | Add to watchlist | `--group-name`, may override `--op` |
| `futu watchlist <symbol...>` | `--action delete` | Delete from watchlist | `--group-name`, may override `--op` |
| `futu watchlist <symbol...>` | `--action move-out` | Move out of watchlist | `--group-name`, may override `--op` |

### Valuation

| Command | selector | Purpose | Extra parameters |
| --- | --- | --- | --- |
| `futu valuation <symbol>` | `--view detail` default | Valuation detail | `--valuation-type`, `--interval-type` |
| `futu valuation [symbol]` | `--view plate-stocks` | Plate valuation constituents | `[symbol]` defaults to `HK.LIST1003`, `--valuation-type`, `--next-key`, `--limit`, `--sort-type asc/desc`, `--sort-id` |
| `futu valuation [symbol]` | `--view index-stocks` | Index valuation constituents | `[symbol]` defaults to `HK.800000`, `--valuation-type`, `--next-key`, `--limit`, `--sort-type 1/2`, `--sort-id 51/52/53/54`, `--filter-symbol` |
| `futu valuation [symbol]` | `--view index-plates` | Index-related plates | `[symbol]` defaults to `HK.800000` |

## Standalone REST quote commands

| Command | Purpose | Required | Default / omit | Optional parameters |
| --- | --- | --- | --- | --- |
| `futu future-info <symbol...>` | Futures info | `symbol...` | none | none |
| `futu market-state <symbol...>` | Market state | `symbol...` | `--is-contain-ba false`, `--is-contain-overnight false`, `--is-need-crypto-multi-broker false` | corresponding boolean flags |
| `futu combo-option-quote` | Combo option quote | `--combo-list` | default `[]` is not a valid business request | `--combo-list '<json-array>'`. Each element must contain a `legs` array. Each leg contains `code` (an option contract such as `US.AAPL261012C335000`), `side` (`BUY`/`SELL`), and `quantity` (a positive integer). At most 20 combos, and at most one underlying stock per combo. |
| `futu referencefuture-list <symbol>` | Related futures | `symbol` | none | none |
| `futu stock-screen` | Stock screen | none; usually pass screen conditions | `--limit 20` | `--screen-queries`, `--retrieve-queries`, `--sort`, `--sorts`, `--next-key`, `--limit`, `--watchlist-stock-ids`, `--holding-stock-ids`, `--user-stock-list-mode` |
| `futu warrant-screen` | Warrant screen | none; usually pass `--symbol` | `--market-type 1`, `--limit 20`; for the default HK market the CLI may fill in `HK.00700` automatically | `--market-type`, `--is-delay`, `--only-count`, `--symbol`, `--screen-groups`, `--sorts`, `--next-key`, `--limit` |
| `futu option-screen` | Option screen | `--strategy` | `--limit 20`, `--request-exact-data 1` | `--strategy`, `--strategy-param`, `--field-filter`, `--sort-obj`, `--next-key`, `--limit`, `--request-exact-data` |
| `futu trading-days` | Trading calendar | none | `--market HK`, `--start TODAY`, `--end TODAY+30` | `--market`, `--start`, `--end` |

Examples:

- `futu future-info HK.HSImain`
- `futu market-state HK.00700 US.AAPL --is-contain-overnight true`
- `futu combo-option-quote --combo-list '[{"legs":[{"code":"US.AAPL261012C335000","side":"BUY","quantity":1},{"code":"US.AAPL261012P335000","side":"BUY","quantity":1}]}]'`
- `futu option-screen --strategy '{"market_category_list":[3]}' --limit 20`
- `futu trading-days --market US --start 2026-10-01 --end 2026-10-31`

## Command selection cheat sheet

| User intent | Preferred command |
| --- | --- |
| Real-time quote, last price, change | `futu quote <symbol> --format json` |
| Basic info, security type, lot size, exchange | `futu basicinfo <symbol> --format json` |
| Full market snapshot | `futu snapshot <symbol> --format json` |
| Latest K-line | `futu kline <symbol>` |
| K-line for a time range | `futu history-kline <symbol> --start <yyyy-mm-dd> --end <yyyy-mm-dd>` |
| Tick trades | `futu ticker <symbol>` |
| Intraday data | `futu rt-data <symbol>` |
| Bid/ask, order book, depth | `futu order-book <symbol>` |
| Gainers, losers, volume ranking | `futu rank <type> --market <market>` |
| Capital flow | `futu capital <symbol> --view intraday/history/distribution` |
| Company profile, executives, operating efficiency | `futu company <symbol> --view profile/executives/background/efficiency` |
| Financials, revenue breakdown, post-earnings price | `futu financials <symbol> --view statements/revenue/earnings-history/earnings-move` |
| Shareholders, institutional holdings, insider trades | `futu shareholders <symbol> --view ...` |
| Valuation | `futu valuation <symbol> --view detail/plate-stocks/index-stocks/index-plates` |
| Plate list, constituents, owning plates | `futu plate [symbol] --view list/stocks/owner` |
| Watchlist | `futu watchlist --action list/groups/add/delete/move-out` |
