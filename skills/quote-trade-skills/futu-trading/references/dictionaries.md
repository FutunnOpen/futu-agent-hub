# Dictionaries

## Accounts and markets

Account types:

| Value | Meaning |
| --- | --- |
| `cash` | Cash account |
| `margin` | Margin account |

Numeric account `markets` values:

| Value | Meaning |
| --- | --- |
| `1` | Hong Kong |
| `2` | United States |
| `4` | China Connect |
| `5` | Futures |
| `6` | Singapore |
| `7` | Cryptocurrency |
| `8` | Australia |
| `9` | Foreign Exchange |
| `10` | Bonds |
| `11` | Malaysia |
| `12` | Canada |
| `14` | Mutual Funds |
| `15` | Japan |
| `16` | Structured Notes |
| `17` | Event Contracts |
| `18` | South Korea |

Common `--market` values: `HK`, `US`, `HKCC`, `SG`, `JP`, `AU`, `MY`, `KR`.

`--exchange` is used for order modification, cancellation, and order detail. Common values: `US` for US stocks; `HK` or the API-required `SEHK` for Hong Kong stocks.

## Symbols

- US stocks: `US.AAPL`
- Hong Kong stocks: `HK.00700`
- The CLI converts an input code into the format the API requires. If the market cannot be determined, ask the user first.
- CLI arguments use `symbol` / `--symbol`. They map to `code` in backend requests.

## Securities order side

| Value | Meaning |
| --- | --- |
| `BUY` | Buy |
| `SELL` | Sell |
| `SELL_SHORT` | Sell short |
| `BUY_BACK` | Buy to cover |

## Securities order type

The CLI uppercases the input. If the user did not specify an order type, do not pass `--type market` explicitly.

| Value | Meaning |
| --- | --- |
| `limit` / `LIMIT` | Limit order |
| `market` / `MARKET` | Market order |
| `AUCTION` | Auction market order |
| `AUCTION_LIMIT` | Auction limit order |
| `STOP` | Stop order |
| `STOP_LIMIT` | Stop-limit order |
| `MARKET_IF_TOUCHED` | Market-if-touched order |
| `LIMIT_IF_TOUCHED` | Limit-if-touched order |

## Other order enums

| Parameter | Values |
| --- | --- |
| `--time-in-force` | `DAY`, `GTC` |
| `--lot-type` | `ROUND`, `ODD` |
| `--session` | `RTH`, `RTH+Pre/Post-Mkt`, `OVERNIGHT`, `ALL_DAY` |
| `--order-class` | `MLEG` |

Multi-leg orders use `--order-class MLEG` with `--multi-leg-info '<json-object>'`. A regular order must provide a symbol. An MLEG order may omit `--symbol`.

## Order status

| Value | Meaning |
| --- | --- |
| `WAITING_SUBMIT` | Waiting to submit |
| `SUBMITTING` | Submitting |
| `SUBMITTED` | Submitted |
| `FILLED_PART` | Partially filled |
| `FILLED_ALL` | Fully filled |
| `CANCELLED_PART` | Partially filled, remainder cancelled |
| `CANCELLED_ALL` | Fully cancelled |
| `FAILED` | Order failed |
| `DISABLED` | Disabled |
| `DELETED` | Deleted |

## Common response fields and compatibility aliases

### Orders

| Meaning | Field |
| --- | --- |
| Order ID | `order_id` |
| Symbol | `symbol`, or backend `code`; CLI JSON always emits `symbol` |
| Side | `side`, or backend `trd_side`; CLI JSON always emits `side` |
| Order type | `type`, or backend `order_type`; CLI JSON always emits `type` |
| Order price | `price` |
| Order quantity | `qty` |
| Filled quantity | `filled_qty`, or backend `dealt_qty`; CLI JSON always emits `filled_qty` |
| Status | `status`, or backend `order_status`; CLI JSON always emits `status` |
| Created time | `create_time` |

Order detail preserves extra backend fields. In table detail, numeric fields whose names end with `_time` are formatted as local time.

### Fills

| Meaning | Field |
| --- | --- |
| Fill ID | `deal_id` |
| Order ID | `order_id` |
| Symbol | `symbol`, or backend `code`; CLI JSON always emits `symbol` |
| Name | `stock_name` |
| Side | `side`, or backend `trd_side`; CLI JSON always emits `side` |
| Fill price | `price` |
| Fill quantity | `qty` |
| Fill time | `time` or `create_time`; CLI JSON always emits `time` |
| Updated time | `updated_time` |
| Status | `status` |
| Counter broker ID | `counter_broker_id` |
| Counter broker name | `counter_broker_name` |

Fill JSON preserves extra backend fields. When querying lists, the CLI paginates automatically and merges the output.

### Max buy/sell quantity

| Field | Meaning |
| --- | --- |
| `max_cash_buy` | Max quantity buyable with cash |
| `max_cash_and_margin_buy` | Max quantity buyable with cash plus margin |
| `max_position_sell` | Max quantity sellable from the position |
| `max_sell_short` | Max short-sell quantity |
| `max_buy_back` | Max buy-to-cover quantity |
| `long_required_im` | Long initial-margin requirement |
| `short_required_im` | Short initial-margin requirement |

## Common error checks

- `account ID is required`: `default_account` is not configured and `--account` was not passed. List accounts with `futu account list`, or ask the user to specify an account.
- `unsupported order type`: the order type is not supported by the current API, market, or symbol. Query commands may retry with a more general type. Before a real order, explain the limitation to the user and get confirmation.
- `PERMISSION_DENIED`: server-side permission denial. It does not mean the token was missing.
