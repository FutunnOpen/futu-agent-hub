# Paper-trading naming dictionary

This file maps a user's natural-language intent to the markets, sides, order types, trading sessions, and order statuses accepted by `futu sim ...` paper-trading commands. The official Futu trading naming dictionary is the source of truth for the full enums:

`https://open.futunn.com/zh-cn/api/trading/naming-dictionary`

## Usage rules

- When building CLI commands, prefer the CLI string parameters listed in `references/cli-parameters.md`. Do not pass OpenAPI SDK enum names or numeric values to the CLI unless the flag explicitly requires a number.
- When the user asks about field meanings, order status, trading markets, order sides, or order types, look up the official trading naming dictionary.
- If the official dictionary conflicts with the local CLI parameter notes, generate commands using the parameters the local CLI supports. When explaining a concept, describe the mapping between the official dictionary name and the CLI argument.
- Paper trading uses only `futu sim ...`. Do not apply parameters from the real-trading command `futu order ...` directly to paper trading.

## Accounts and markets

`--account` is the paper-trading account ID. The skill should first call `futu sim account list --format json` to get the account, then pass `--account <sim-account-id>` explicitly.

Common paper-trading `--market` values:

| CLI value | Meaning | Typical use |
| --- | --- | --- |
| `HK` | Hong Kong paper trading | Hong Kong stocks, such as `HK.00700` |
| `US` | US paper trading | US stocks, such as `US.AAPL` |
| `US_OPTION` | US option paper trading | US option symbols |
| `HKCC` | China Connect paper trading | China Connect symbols |

The CLI converts these strings to paper-trading BFF numeric enums internally: `HK -> 1`, `US -> 2`, `US_OPTION -> 3`, `HKCC -> 4`. `OPTION` is an alias of `US_OPTION`. `CN` is an alias of `HKCC`. Do not pass numeric market values unless the CLI parameter table explicitly requires them.

## Symbols

- US stocks: `US.AAPL`
- Hong Kong stocks: `HK.00700`
- China Connect: usually pass the `HKCC` market parameter. The symbol still needs to be a CLI-parseable `MARKET.CODE`.
- If the user gives a bare code, fill in the market only when it can be determined. If the market cannot be determined, ask first.

## Paper order side

| CLI value | Meaning | Usage |
| --- | --- | --- |
| `BUY` | Buy | `futu sim order place <qty> --side BUY`, or use `futu sim order buy` directly |
| `SELL` | Sell | `futu sim order place <qty> --side SELL`, or use `futu sim order sell` directly |

The `buy` and `sell` subcommands fix the side. Only the generic `place` command needs an explicit `--side`.

## Paper order type

| CLI value | Meaning | Guidance |
| --- | --- | --- |
| `market` | Market order | Default. If the user did not specify an order type, do not pass it explicitly. |
| `limit` | Limit order | Usually must also pass `--price`. |

When querying max buy/sell, if the user specifies a limit price or asks for quantity at a given price, use `--type limit --price <price>`.
If the user only asks for the max buy/sell quantity and does not specify a limit price, prefer the default market query: `futu sim order max-qty <symbol> --account <id> --market <market>`. Do not pass `--type limit`.

Internal CLI mapping: `market -> 3`, `limit -> 1`.

## Trading session

| CLI value | Meaning | Guidance |
| --- | --- | --- |
| `RTH` | Regular trading hours | Pass when the user explicitly wants regular hours only. |
| `EXTENDED` | Extended session, including pre-market and after-hours | Mainly for US stocks. Pass when the user mentions pre-market, after-hours, or an extended session. |

If the user did not specify a trading session, do not pass `--session`. Leave it to the backend default.

Internal CLI mapping: `RTH -> 1`, `EXTENDED -> 2`.

## Field mapping

| CLI parameter / concept | BFF field | Notes |
| --- | --- | --- |
| `--account` | `acc_id` | Path parameter, paper-trading account ID |
| `--market` | `market` | Query parameter or body field. The CLI converts the string to a number. |
| `<symbol>` / `--symbol` | `symbol` | `MARKET.CODE` symbol |
| `<qty>` / `--qty` | `qty` / `new_qty` | Order quantity / new quantity after modification |
| `--price` | `price` / `new_price` | Order price / new price after modification |
| `buy` / `sell` / `--side` | `order_side` | `BUY -> 1`, `SELL -> 2` |
| `--type` | `order_type` | `market -> 3`, `limit -> 1` |
| `--session` | `order_trade_time_type` | `RTH -> 1`, `EXTENDED -> 2` |
| `--start` | `time_begin` | Microsecond timestamp |
| `--end` | `time_end` | Microsecond timestamp |
| `--page-size` | `page_size` | Historical-order page size |
| `--next-key` | `next_key` | Historical-order pagination cursor |

## Paper order status

When the server returns an order status, explain it using the official trading naming dictionary. Common meanings:

| Status meaning | Notes |
| --- | --- |
| Waiting / submitting | The order is still in the submission path and should not be treated as filled. |
| Submitted | The order has entered the market or the paper matching system. |
| Partially filled | Part of the quantity is filled. The remainder may still fill or be cancelled. |
| Fully filled | The order is completely filled. |
| Cancelled | The order is cancelled. This may be a full cancel, or a cancel of the remainder after a partial fill. |
| Failed / disabled | The order did not validly enter later matching. Check the error message. |

When explaining response fields, keep the original status value and add its meaning. Do not classify an unknown status as filled or cancelled.

## Common error checks

- `account ID is required`: no paper account was passed and the CLI could not choose one automatically. List accounts with `futu sim account list`, then pass `--account` explicitly.
- `order_id is required` or a similar error: modify or cancel is missing an order ID. List orders with `futu sim order list`, or ask the user to provide one.
- `unsupported market`: `--market` does not match the symbol or the account. Confirm the account market and the symbol market.
- `unsupported order type`: the order type is not supported by the current market or symbol. Explain this to the user and switch to a supported type before placing the paper order.
- `at least one of --qty or --price is required`: a modification passed neither a new quantity nor a new price. Ask the user to provide at least one.
- `quantity must be greater than 0`: the quantity is not positive. Confirm the quantity again.
- `invalid price`: the price format is invalid. Confirm the price again.
- `PERMISSION_DENIED`: server-side permission denial. It does not mean the token was missing.
