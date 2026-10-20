# CLI parameters

When generating commands, use the smallest parameter set: include only required parameters, parameters the user explicitly specified, or parameters required to change CLI default behavior. Do not unconditionally write CLI defaults into the command.

## Current command tree

```text
futu
├── account
│   ├── list
│   └── funds
├── position
├── order
│   ├── buy <symbol> <qty>
│   ├── sell <symbol> <qty>
│   ├── place <qty>
│   ├── modify <order-id>
│   ├── cancel <order-id>
│   ├── list
│   ├── history
│   ├── detail <order-id> [order-id...]
│   └── max-qty <symbol>
└── deal
    └── history
```

`futu deal` with no extra arguments queries today's fills. `futu deal history` queries historical fills.

## Global parameters

| Parameter | Default | When to pass |
| --- | --- | --- |
| `--format`, `-f` | `table` | Pass `--format json` only when the agent needs to parse the output. Usually omit it for commands the user will copy and run. |
| `--token-file` | config item `token_file` | Pass only when the user asks to use a non-default token file. |

Internal invocation convention: when this skill actually calls the CLI from Bash, always append the hidden internal marker `--source skill` at the end of the command. With `--source skill`, the CLI automatically detects hosts such as Codex or Claude Code and reports `agent_name`. Append `--agent codex` or `--agent claude_code` only when auto-detection fails and the CLI is confirmed to support it. Do not include these internal markers in commands shown to the user.

JSON output drops empty strings, empty arrays, empty objects, and numeric 0. Boolean values are kept. Amounts, prices, and quantities are handled as strings or decimals.

## Auth and status

| Command | Required | Default / omit | Notes |
| --- | --- | --- | --- |
| `futu auth status` | none | `--format table` | Inspect the local token, accounts, and permissions. Add `--format json` when parsing. |
| `futu check` | none | none | Check local token availability and API connectivity. |
| `futu auth login` | none | `--client-name` defaults to username and hostname, `--no-browser=false` | Pass `--no-browser` only in an environment without a browser. |
| `futu auth logout` | none | none | Clear the local token. |
| `futu config set default_account <account-id>` | `key value` | none | Set the default trading account. Later commands that support `default_account` can omit `--account`. |

## Account resolution

- Any command whose rule is "also requires `--account` when no default account is configured" must not assume a default account exists. Omit `--account` only when this turn has already confirmed a default account from `futu auth status --format json` or config.
- If this turn has not confirmed a default account, run `futu account list --format json` or ask the user to choose an account, then pass `--account <account-id>` explicitly.
- If the user already gave an account ID in the request or recent context, pass `--account <account-id>` explicitly. Do not rely on the default.
- If the CLI returns `account ID is required`, do not retry the same command unchanged. Resolve the account first, then retry with `--account <account-id>`. Configure `default_account` only when the user explicitly asks.

## Accounts, funds, and positions

| Command | Required | Default / omit | Optional parameters |
| --- | --- | --- | --- |
| `futu account list` | none | none | none |
| `futu account funds` | none if `default_account` is configured | `--currency USD` | `--account`, `--currency` |
| `futu position` | none if `default_account` is configured | none | `--account`, `--symbol`, `--pl-ratio-min`, `--pl-ratio-max` |

Field mapping:

| CLI parameter | Backend field |
| --- | --- |
| `account funds --currency` | query parameter `currency` |
| `position --symbol` | `code` |
| `position --pl-ratio-min` | `pl_ratio_min` |
| `position --pl-ratio-max` | `pl_ratio_max` |

Examples:

- Default-account funds: `futu account funds`
- Funds for a specific account: `futu account funds --account <account-id>`
- Funds in a specific currency: `futu account funds --account <account-id> --currency HKD`
- A specific position: `futu position --symbol US.AAPL`

## Order placement

| Command | Required | Default / omit | Optional parameters |
| --- | --- | --- | --- |
| `futu order buy <symbol> <qty>` | `symbol`, `qty`; also `--account` when no default account is configured | `--type market`, `--time-in-force DAY` | `--account`, `--price`, `--type`, `--time-in-force`, `--lot-type`, `--remark`, `--session`, `--aux-price`, `--order-class`, `--multi-leg-info` |
| `futu order sell <symbol> <qty>` | `symbol`, `qty`; also `--account` when no default account is configured | `--type market`, `--time-in-force DAY` | same as above |
| `futu order place <qty>` | `qty`, `--side`; a regular order also needs `--symbol`; also `--account` when no default account is configured | `--type market`, `--time-in-force DAY` | same as above |

Field mapping: `<symbol>` / `--symbol` -> `code`, `BUY` / `SELL` / `--side` -> `side`, `--type` -> `order_type`, `<qty>` -> `qty`, `--price` -> `price`, `--time-in-force` -> `time_in_force`, `--lot-type` -> `lot_type`, `--remark` -> `remark`, `--session` -> `session`, `--aux-price` -> `aux_price`, `--order-class` -> `order_class`, `--multi-leg-info` -> `multi_leg_info`.

Order rules:

- `order buy` fixes the side to `BUY`. `order sell` fixes the side to `SELL`. Do not also pass `--side`.
- `order place` is for `SELL_SHORT`, `BUY_BACK`, conditional orders, and multi-leg orders. A regular order must pass `--symbol`. `--symbol` may be omitted when `--order-class MLEG`.
- `--multi-leg-info` must be a JSON object string.
- If the user did not specify an order type, do not pass `--type market` explicitly.

Order examples:

- User says "buy 1 share of Apple" and a default account exists: `futu order buy US.AAPL 1`
- User says "buy 1 share of Apple at a 280 limit": `futu order buy US.AAPL 1 --price 280 --type limit`
- User specifies an account: `futu order buy US.AAPL 1 --account <account-id> --price 280 --type limit`
- Multi-leg order: `futu order place 1 --side BUY --order-class MLEG --multi-leg-info '<json-object>'`

## Modify, cancel, and query

| Command | Required | Default / omit | Optional parameters |
| --- | --- | --- | --- |
| `futu order modify <order-id>` | `order-id`, `--exchange`, `--qty`; also `--account` when no default account is configured | omitting `--price` means the price is unchanged; omitting `--aux-price` means the trigger price is unchanged | `--account`, `--exchange`, `--qty`, `--price`, `--aux-price` |
| `futu order cancel <order-id>` | `order-id`, `--exchange`; also `--account` when no default account is configured | none | `--account`, `--exchange` |
| `futu order list` | none if `default_account` is configured | `--market HK`, `--page-size 50` | `--account`, `--market`, `--page-size` |
| `futu order history` | none if `default_account` is configured | `--market HK`, `--page-size 50`, `--start 0`, `--end 0`, no `--symbol` filter | `--account`, `--market`, `--start`, `--end`, `--symbol`, `--page-size` |
| `futu order detail <order-id> [order-id...]` | `order-id`, `--exchange`; also `--account` when no default account is configured | none | `--account`, `--exchange` |
| `futu order max-qty <symbol>` | `symbol`; also `--account` when no default account is configured | `--type market`, empty `--price`, empty `--order-id` | `--account`, `--price`, `--type`, `--order-id` |
| `futu deal` | none if `default_account` is configured | `--market HK`, `--page-size 50` | `--account`, `--market`, `--page-size` |
| `futu deal history` | none if `default_account` is configured | `--market HK`, `--page-size 50`, `--start 0`, `--end 0`, no `--symbol` filter | `--account`, `--market`, `--start`, `--end`, `--symbol`, `--page-size` |

Field mapping:

| CLI parameter | Backend field |
| --- | --- |
| `order modify --exchange` | `exchange` |
| `order modify --qty` | `qty` |
| `order modify --price` | `price` |
| `order modify --aux-price` | `aux_price` |
| `order cancel --exchange` | query parameter `exchange` |
| `order list --market` | `trd_market` |
| `order history --market` | `trd_market` |
| `deal --market` | `trd_market` |
| `deal history --market` | `trd_market` |
| `--start` | `start` |
| `--end` | `end` |
| `--symbol` | `code` |
| `--page-size` | `page_size` |
| `order detail --exchange` | body field `exchange` |
| `order detail <order-id>...` | body field `order_ids` array |
| `order max-qty <symbol>` | `code` |
| `order max-qty --type` | `order_type` |
| `order max-qty --price` | `price` |
| `order max-qty --order-id` | `order_id` |

Query and pagination rules:

- Current orders, historical orders, today's fills, and historical fills automatically follow the backend `page_flag` and emit a merged array.
- `--page-size` is sent to the backend only when it is in the range `10-100`. The default is `50`.
- When historical orders and historical fills omit `--start` / `--end`, no lower or upper time bound is set.
- `order detail` accepts at most 100 order IDs at once.
- For `order modify`, omitting `--price` means the price is unchanged, and omitting `--aux-price` means the trigger price is unchanged. `--qty` must be greater than 0.

Response parsing:

- Main order JSON fields: `order_id`, `symbol`, `side`, `type`, `price`, `qty`, `filled_qty`, `status`, `create_time`. Extra backend fields are preserved.
- Main fill JSON fields: `deal_id`, `order_id`, `symbol`, `stock_name`, `side`, `price`, `qty`, `time`, `updated_time`, `status`, `counter_broker_id`, `counter_broker_name`. Extra backend fields are preserved.

Backend APIs:

| CLI command | Backend API |
| --- | --- |
| `futu account list` | `GET /api/v1.0/accounts/authorized_trd_accs` |
| `futu account funds` | `GET /api/v1.0/accounts/{acc_id}/funds` |
| `futu position` | `GET /api/v1.0/accounts/{acc_id}/positions` |
| `futu order buy/sell/place` | `POST /api/v1.0/accounts/{acc_id}/orders` |
| `futu order modify` | `PUT /api/v1.0/accounts/{acc_id}/orders/{order_id}` |
| `futu order cancel` | `DELETE /api/v1.0/accounts/{acc_id}/orders/{order_id}` |
| `futu order list` | `GET /api/v1.0/accounts/{acc_id}/orders` |
| `futu order history` | `GET /api/v1.0/accounts/{acc_id}/orders_history` |
| `futu order detail` | `POST /api/v1.0/accounts/{acc_id}/orders/detail` |
| `futu order max-qty` | `GET /api/v1.0/accounts/{acc_id}/acctradinginfo` |
| Broker second confirmation | `POST /api/v1.0/accounts/{acc_id}/order_confirm` |
| `futu deal` | `GET /api/v1.0/accounts/{acc_id}/order_fills` |
| `futu deal history` | `GET /api/v1.0/accounts/{acc_id}/fills_history` |

Query examples:

- Current orders on the default market: `futu order list`
- Current US orders: `futu order list --market US`
- A specific order: `futu order detail <order-id> --exchange US`
- Max market buy/sell for Apple on the current account: `futu order max-qty US.AAPL`
- Max buy/sell for Apple at a 280 limit: `futu order max-qty US.AAPL --price 280 --type limit`
- Max buy/sell at a 280 limit when the default account is not confirmed: `futu order max-qty US.AAPL --account <account-id> --price 280 --type limit`
