# Sim Trading CLI parameters

When generating commands, use the smallest parameter set: include only required parameters, parameters the user explicitly specified, or parameters required to change CLI default behavior. Do not unconditionally write CLI defaults into the command.

Paper trading always uses the high-level `futu sim ...` commands. Legacy `sim-trade-*` names are endpoint metadata only and are not user-facing commands.

## Global parameters

| Parameter | Default | When to pass |
| --- | --- | --- |
| `--format`, `-f` | `table` | Pass `--format json` only when the agent needs to parse the output. Usually omit it for commands the user will copy and run. |
| `--token-file` | config item `token_file` | Pass only when the user asks to use a non-default token file. |

Internal invocation convention: when this skill actually calls the CLI from Bash, always append the hidden internal marker `--source skill` at the end of the command. Do not include these internal markers in commands shown to the user.

## Global conventions

- Use only `futu sim ...` commands. Do not use the legacy `sim-trade-*` commands.
- Max buy/sell must use `futu sim order max-qty <symbol>`. Do not use the nonexistent `futu sim max-buy-sell`. Do not write the symbol as `--symbol`, and do not write the order type as `--order-type`.
- Symbols use `MARKET.CODE`, for example `HK.00700` and `US.AAPL`. Do not pass bare `AAPL`, `700`, or `700.HK`.
- `--account`, `-a` is the paper-trading account ID. If omitted, the CLI automatically uses the first paper account, but the skill should query and pass the account explicitly.
- There is no automatic fallback for `order_id`. Modify and cancel require an order ID.
- Historical orders are paginated with `--next-key`. The next page takes `pagination.next_key` from the previous response. See `references/pagination.md` for the full rules.
- Time parameters `--start` and `--end` use microsecond timestamps. `0` means unbounded. Do not pass seconds, milliseconds, or `YYYY-MM-DD` strings.
- Table output shows only common columns. Use `--format json` when you need full fields, account selection, pagination cursors, or error details.

## Enums

| CLI parameter | Common values | Notes |
| --- | --- | --- |
| `--market`, `-m` | `HK`, `US`, `US_OPTION`, `HKCC` | Default `HK`. The CLI converts these to BFF numeric enums internally. `OPTION` is an alias of `US_OPTION`. `CN` is an alias of `HKCC`. |
| `--type`, `-t` | `market`, `limit` | Default `market`. Limit orders usually need `--price`. |
| `buy` / `sell` / `--side` | `BUY`, `SELL` | The `buy` and `sell` subcommands fix the side. `place` uses `--side`. |
| `--session` | `RTH`, `EXTENDED` | Mainly the US trading session. If omitted, the backend default applies. |

## Accounts, funds, and positions

| Command | Purpose | Required | Default / omit | Optional parameters |
| --- | --- | --- | --- | --- |
| `futu sim account list` | Paper-account list | none | none | none |
| `futu sim account funds` | Paper-account funds | none; passing `--account` is recommended | if omitted, the CLI uses the first paper account | `--account` |
| `futu sim position` | Paper-account positions | none; passing `--account` is recommended | `--market HK` | `--account`, `--market` |

Underlying mapping:

| High-level command | BFF ID | Path / query |
| --- | --- | --- |
| `futu sim account list` | `sim_trade.account_list` | none |
| `futu sim account funds` | `sim_trade.cash_info` | path `acc_id` |
| `futu sim position` | `sim_trade.position_list` | path `acc_id` + query `market` |

Examples:

- Account list: `futu sim account list`
- Funds for a specific account: `futu sim account funds --account <sim-account-id>`
- US paper positions: `futu sim position --account <sim-account-id> --market US`

## Paper orders

| Command | Purpose | Required | Default / omit | Optional parameters |
| --- | --- | --- | --- | --- |
| `futu sim order buy <symbol> <qty>` | Paper buy | `symbol`, `qty`; passing `--account` is recommended | `--market HK`, `--type market` | `--account`, `--market`, `--type`, `--price`, `--text`, `--session` |
| `futu sim order sell <symbol> <qty>` | Paper sell | `symbol`, `qty`; passing `--account` is recommended | `--market HK`, `--type market` | same as `buy` |
| `futu sim order place <qty>` | Generic paper order | `qty`, `--symbol`, `--side`; passing `--account` is recommended | `--market HK`, `--type market` | `--account`, `--symbol`, `--side`, `--market`, `--type`, `--price`, `--text`, `--session` |

Internal order mapping: `--account` -> path `acc_id`; `--market` -> body `market`; `--symbol` / `<symbol>` -> body `symbol`; `<qty>` -> body `qty`; `--type` -> body `order_type`; side -> body `order_side`; `--session` -> body `order_trade_time_type`; `--text` -> body `text`.

Order examples:

- Market buy of a US stock: `futu sim order buy US.AAPL 1 --account <sim-account-id> --market US`
- Limit buy of a Hong Kong stock: `futu sim order buy HK.00700 100 --account <sim-account-id> --type limit --price 300`
- Generic order: `futu sim order place 1 --symbol US.AAPL --side BUY --account <sim-account-id> --market US`

## Order queries

| Command | Purpose | Required | Default / omit | Optional parameters |
| --- | --- | --- | --- | --- |
| `futu sim order list` | Current paper orders | none; passing `--account` is recommended | `--market HK` | `--account`, `--market` |
| `futu sim order history` | Historical paper orders | none; passing `--account` is recommended | `--market HK`, `--start 0`, `--end 0`, `--page-size 50` | `--account`, `--market`, `--start`, `--end`, `--page-size`, `--next-key` |
| `futu sim order max-qty <symbol>` | Max buy/sell | `symbol`; passing `--account` is recommended | `--market HK`, `--type market`, empty `--price` | `--account`, `--market`, `--type`, `--price`, `--order-id` |

For `max-qty`, the symbol is a positional argument, not `--symbol`. The order-type flag is `--type market|limit`, not `--order-type`. A limit-order max-quantity query must include a reference price, for example `--type limit --price 180`. When no price is specified, prefer the default market query and omit `--type`.

Internal query mapping:

| High-level command | BFF ID | Path / query |
| --- | --- | --- |
| `futu sim order list` | `sim_trade.order_list` | path `acc_id` + query `market` |
| `futu sim order history` | `sim_trade.history_order_list` | path `acc_id` + query `market/time_begin/time_end/page_size/next_key` |
| `futu sim order max-qty` | `sim_trade.max_buy_sell` | path `acc_id` + query `market/symbol/order_type/price/order_id` |

Query examples:

- Current orders: `futu sim order list --account <sim-account-id> --market US`
- First page of historical orders: `futu sim order history --account <sim-account-id> --market US --page-size 50`
- Next page of historical orders: `futu sim order history --account <sim-account-id> --market US --next-key '<next_key>'`
- Max market quantity: `futu sim order max-qty US.AAPL --account <sim-account-id> --market US`
- Max limit quantity: `futu sim order max-qty HK.00700 --account <sim-account-id> --market HK --type limit --price 300`

## Modify and cancel

| Command | Purpose | Required | Default / omit | Optional parameters |
| --- | --- | --- | --- | --- |
| `futu sim order modify <order-id>` | Modify a paper order | `order-id`; at least one of `--qty` and `--price`; passing `--account` is recommended | `--market HK` | `--account`, `--market`, `--qty`, `--price` |
| `futu sim order cancel <order-id>` | Cancel a paper order | `order-id`; passing `--account` is recommended | `--market HK` | `--account`, `--market` |

If the user did not provide an order ID, first run `futu sim order list --account <sim-account-id> --market <market>` to list current orders, then ask the user to confirm the target order.

Internal modify/cancel mapping:

| High-level command | BFF ID | Path / body |
| --- | --- | --- |
| `futu sim order modify <order-id>` | `sim_trade.modify_order` | path `acc_id/order_id` + body `market/new_qty/new_price` |
| `futu sim order cancel <order-id>` | `sim_trade.cancel_order` | path `acc_id/order_id` + body `market` |

Examples:

- Change price: `futu sim order modify <order-id> --account <sim-account-id> --market US --price 181`
- Change quantity and price: `futu sim order modify <order-id> --account <sim-account-id> --market US --qty 2 --price 181`
- Cancel: `futu sim order cancel <order-id> --account <sim-account-id> --market US`

## Recommended workflows

### Query assets and positions

```bash
futu sim account list --format json
futu sim account funds --account <sim-account-id> --format json
futu sim position --account <sim-account-id> --market HK --format json
```

### Place a paper order

```bash
futu sim account list --format json
futu sim order max-qty HK.00700 --account <sim-account-id> --market HK --type limit --price 300 --format json
futu sim order buy HK.00700 100 --account <sim-account-id> --market HK --type limit --price 300 --format json
futu sim order list --account <sim-account-id> --market HK --format json
```

### Modify and cancel

```bash
futu sim order list --account <sim-account-id> --market HK --format json
futu sim order modify <order-id> --account <sim-account-id> --market HK --price 301 --format json
futu sim order cancel <order-id> --account <sim-account-id> --market HK --format json
```

## Command selection cheat sheet

| User intent | Preferred command |
| --- | --- |
| List paper accounts | `futu sim account list --format json` |
| View paper funds | `futu sim account funds --account <sim-account-id> --format json` |
| View paper positions | `futu sim position --account <sim-account-id> --market <market> --format json` |
| View current paper orders | `futu sim order list --account <sim-account-id> --market <market> --format json` |
| View historical paper orders | `futu sim order history --account <sim-account-id> --market <market> --format json` |
| Next page of historical paper orders | `futu sim order history --account <sim-account-id> --market <market> --next-key '<pagination.next_key>' --format json` |
| Query max buy/sell | `futu sim order max-qty <symbol> --account <sim-account-id> --market <market> --format json` |
| Paper buy | `futu sim order buy <symbol> <qty> --account <sim-account-id> --market <market>` |
| Paper sell | `futu sim order sell <symbol> <qty> --account <sim-account-id> --market <market>` |
| Place an order with a dynamic side | `futu sim order place <qty> --symbol <symbol> --side BUY|SELL --account <sim-account-id> --market <market>` |
| Modify a paper order | `futu sim order modify <order-id> --account <sim-account-id> --market <market> --qty <qty> --price <price>` |
| Cancel a paper order | `futu sim order cancel <order-id> --account <sim-account-id> --market <market>` |
