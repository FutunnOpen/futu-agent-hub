# Dictionaries

## Pair and currency inference

- `symbol` is uppercased automatically and may include or omit the `CC.` prefix. For example, `CC.ETHHKD` is requested as `ETHHKD`.
- If `--coin` is omitted, the CLI derives the base currency by stripping the settlement-currency suffix from `symbol`.
- `--currency` defaults to `USD`. If the pair suffix is not `USD`, pass the settlement currency explicitly.

Examples:

| Pair | Suggested parameters |
| --- | --- |
| `BTCUSD` | `--currency` may be omitted, or pass `--currency USD` explicitly |
| `ETHHKD` | pass `--currency HKD` |
| `CC.ETHHKD` | pass `--currency HKD` |

## Crypto side and order type

| Field | Values | Notes |
| --- | --- | --- |
| `--side` | `BUY`, `SELL` | Required for `order place`. The `buy` and `sell` subcommands already fix the side, so do not pass it again. |
| `--type` | `LIMIT`, `MARKET`, `TAKE_PROFIT_LIMIT`, `TAKE_PROFIT_MARKET`, `STOP_LOSS_LIMIT`, `STOP_LOSS_MARKET` | CLI default is `LIMIT`. Do not change a type the user specified on a real order. |
| `--time-in-force` | `TIF_GTC`, `TIF_IOC`, `TIF_FOK`, `TIF_GTD` | CLI default is `TIF_GTC`. A market buy by cash amount commonly uses `TIF_IOC`. `TIF_GTD` requires `--expire-time`. |

Conditional orders:

- Conditional orders use `--conditional-info '<json>'`. The CLI parses it into the backend `conditional_info` object.
- When modifying a take-profit or stop-loss market order, `--price` may be `0`.
- `--conditional-info` is a required flag for `order modify`. A regular order may pass `{}`.

## Crypto order status

| Value | Meaning |
| --- | --- |
| `PENDING_TRIGGER` | Waiting to trigger |
| `SUBMITTING` | Submitting |
| `SUBMITTED` | Submitted |
| `PARTIAL_FILLED` | Partially filled |
| `FILLED` | Fully filled |
| `CANCELLING` | Cancelling |
| `CANCELLED` | Cancelled |
| `FAILED` | Order failed |
| `EXPIRED` | Expired |

## max-qty response fields

| Field | Meaning |
| --- | --- |
| `max_cash_buy_qty` | Max cash buy quantity |
| `max_cash_buy_amount` | Max cash buy amount |
| `max_sell_qty` | Max sellable quantity |

`max-qty` is a read-only query. If `max_cash_buy_qty` and `max_cash_buy_amount` are `0` but `max_sell_qty` is greater than `0`, the account usually has a sellable position but no cash buying power in the settlement currency.

## Order and fill filters

- `--order-status`: order-status filter. Use values returned by the API. Multiple values may be comma-separated.
- `--side`: `BUY` or `SELL`. Multiple values may be comma-separated.
- `--type`: order-type filter. Multiple values may be comma-separated.
- `--currency`: settlement-currency filter. Multiple values may be comma-separated.
- `--start` / `--end`: microsecond timestamps. Historical orders and fills default to the last 3 months.
- `--page-size` / `--page-flag`: pagination parameters. The CLI does not paginate automatically. The next page uses `page_flag` from the previous response.

## Common response fields and compatibility aliases

### Orders

| Meaning | CLI table read order |
| --- | --- |
| Order ID | `order_id` |
| Pair | `symbol`, `code`, `trade_pair`, `trading_pair`, `symbol_pair.symbol`, `coin+currency`, `symbol_pair.base+symbol_pair.quote` |
| Side | `side`, `trd_side` |
| Order type | `ord_type`, `order_type`, `type` |
| Order quantity | `qty`, `quantity`, `order_qty`, `order_quantity` |
| Filled quantity | `filled_qty`, `dealt_qty`, `filled_quantity`, `dealt_quantity`, `cum_qty` |
| Status | `status`, `order_status`, `ord_status`, `order_state` |
| Time | `create_time`, `created_time`, `time` |

Common order-detail fields: `order_id`, `symbol`, `avg_px`, `cash_order_qty`, `create_time`, `cum_qty`, `fill_amount`, `ord_status`, `ord_type`, `order_amount`, `order_qty`, `price`, `side`, `time_in_force`, `trigger_price`, `trigger_time`, `update_time`, `version`.

### Fills

| Meaning | CLI table read order |
| --- | --- |
| Fill ID | `fill_id`, `deal_id`, `id` |
| Order ID | `order_id`, `ord_id`, `order_show_id` |
| Pair | `symbol`, `code`, `trade_pair`, `trading_pair`, `symbol_pair.symbol`, `coin+currency`, `symbol_pair.base+symbol_pair.quote` |
| Side | `side`, `trd_side` |
| Fill price | `price`, `fill_price`, `deal_price` |
| Fill quantity | `qty`, `quantity`, `fill_qty`, `deal_qty` |
| Fill amount | `amount`, `fill_amount`, `deal_amount`, `exec_amount` |
| Fill time | `fill_time`, `filled_time`, `deal_time`, `trade_time`, `create_time`, `created_time`, `time`, `update_time` |

Fill-list JSON prefers `order_fills`. The CLI also accepts a backend response that returns only `fills` or `deals`.

## Error handling

- `unsupported order type`: the current pair or API does not accept the given order type. A read-only `max-qty` may retry once with `--type MARKET`. Do not switch the order type on a real order.
- `account ID is required`: `default_account` is not configured and `--account` was not passed. List accounts, or ask the user to specify one.
- `PERMISSION_DENIED`: server-side permission denial. It does not mean the token was missing.
