# CLI parameters

When generating commands, use the smallest parameter set: include only required parameters, parameters the user explicitly specified, or parameters required to change CLI default behavior. Do not unconditionally write CLI defaults into the command.

## Current command tree

```text
futu crypto
├── account
│   └── list
├── balance
├── max-qty <symbol>
├── order
│   ├── place <symbol>
│   ├── buy <symbol>
│   ├── sell <symbol>
│   ├── modify <order-id>
│   ├── cancel <order-id>
│   ├── list
│   ├── history
│   └── detail <order-id> [order-id...]
└── deal <order-id>
    └── history
```

`futu crypto deal` is both the command that queries fills for a specific order and the parent of `deal history`. Historical fills must use the full command `futu crypto deal history`.

## Global parameters

| Parameter | Default | When to pass |
| --- | --- | --- |
| `--format`, `-f` | `table` | Pass `--format json` only when the agent needs to parse the output. Usually omit it for commands the user will copy and run. |
| `--token-file` | config item `token_file` | Pass only when the user asks to use a non-default token file. |

Internal invocation convention: when this skill actually calls the CLI from Bash, always append the hidden internal marker `--source skill` at the end of the command. With `--source skill`, the CLI automatically detects hosts such as Codex or Claude Code and reports `agent_name`. Append `--agent codex` or `--agent claude_code` only when auto-detection fails and the CLI is confirmed to support it. Do not include these internal markers in commands shown to the user.

JSON output drops empty strings, empty arrays, empty objects, and numeric 0. Boolean values are kept. Amounts, prices, and quantities are handled as strings or decimals to avoid floating-point precision issues.

## Auth and accounts

| Command | Required | Default / omit | Notes |
| --- | --- | --- | --- |
| `futu auth status` | none | `--format table` | Inspect the local token, accounts, and permissions. |
| `futu check` | none | none | Check local token availability and API connectivity. |
| `futu auth login` | none | `--client-name` defaults to username and hostname, `--no-browser=false` | Pass `--no-browser` only in an environment without a browser. |
| `futu crypto account list` | none | none | Lists only authorized accounts with the crypto market enabled. |
| `futu crypto balance` | none if `default_account` is configured | none | Pass `--account` to select an account. |

## Account resolution

- Any crypto command whose rule is "also requires `--account` when no default account is configured" must not assume a default account exists. Omit `--account` only when this turn has already confirmed a usable default account from `futu auth status --format json` or config.
- If this turn has not confirmed a default account, run `futu crypto account list --format json` or ask the user to choose a crypto account, then pass `--account <account-id>` explicitly.
- If the user already gave an account ID in the request or recent context, pass `--account <account-id>` explicitly. Do not rely on the default.
- If the CLI returns `account ID is required`, do not retry the same command unchanged. Resolve the account first, then retry with `--account <account-id>`. Configure `default_account` only when the user explicitly asks.

## Max buy/sell quantity

| Command | Required | Default / omit | Optional parameters |
| --- | --- | --- | --- |
| `futu crypto max-qty <symbol>` | `symbol`; also `--account` when no default account is configured | `--type LIMIT`, `--currency USD`, `--coin` inferred from `symbol`, empty `--price` | `--account`, `--type`, `--currency`, `--coin`, `--price` |

Field mapping: `--type` -> `order_type`, `--currency` -> `currency`, `--coin` -> `coin`, `--price` -> `price`.

Practical rules:

- If the user only says max buy, max sell, or max tradable quantity and does not specify a limit price, pass `--type MARKET` and usually omit `--price`. This is a business inference for `max-qty`, not a CLI default.
- If the user explicitly asks to calculate at a limit price, pass `--type LIMIT --price <price>`.
- When the pair is not USD-settled, `--currency <suffix>` is required. For example, `ETHHKD` needs `--currency HKD`. Otherwise the CLI default `USD` can infer the wrong currency.
- If a read-only `max-qty` returns `unsupported order type`, retry once with `--type MARKET` and explain that the switch follows the API error.

Examples:

- `futu crypto max-qty ETHHKD --account <account-id> --currency HKD --type MARKET`
- `futu crypto max-qty BTCUSD --account <account-id> --type MARKET`
- `futu crypto max-qty BTCUSD --account <account-id> --type LIMIT --price 65000`

## Crypto order placement

| Command | Required | Default / omit | Optional parameters |
| --- | --- | --- | --- |
| `futu crypto order place <symbol>` | `symbol`, `--side`; also `--account` when no default account is configured; exactly one of `--qty` and `--cash-qty` | `--type LIMIT`, `--time-in-force TIF_GTC`, `--req-id` generated automatically | `--account`, `--side`, `--req-id`, `--type`, `--time-in-force`, `--price`, `--qty`, `--cash-qty`, `--expire-time`, `--conditional-info` |
| `futu crypto order buy <symbol>` | `symbol`; also `--account` when no default account is configured; exactly one of `--qty` and `--cash-qty` | `--side BUY`, `--type LIMIT`, `--time-in-force TIF_GTC`, `--req-id` generated automatically | same as above, but do not pass `--side` |
| `futu crypto order sell <symbol>` | `symbol`; also `--account` when no default account is configured; usually needs `--qty` | `--side SELL`, `--type LIMIT`, `--time-in-force TIF_GTC`, `--req-id` generated automatically | same as above, but do not pass `--side` |

Field mapping: `--req-id` -> `req_id`, `--side` -> `side`, `<symbol>` -> `symbol`, `--type` -> `ord_type`, `--time-in-force` -> `time_in_force`, `--price` -> `price`, `--qty` -> `qty`, `--cash-qty` -> `cash_order_qty`, `--expire-time` -> `expire_time`, `--conditional-info` -> `conditional_info`.

Order rules:

- `order buy` always sends `side=BUY`. Do not also pass `--side`.
- `order sell` always sends `side=SELL`. Do not also pass `--side`. Do not use `--cash-qty` on a sell.
- Limit-style orders need `--price`. A market buy by cash amount commonly uses `--type MARKET --time-in-force TIF_IOC --cash-qty <amount>`.
- `--conditional-info` must be a JSON object string. If it is omitted, the CLI does not send `conditional_info`.

Order examples:

- Limit buy: `futu crypto order buy BTCUSD --qty 0.01 --price 65000`
- Market buy by cash amount: `futu crypto order buy BTCUSD --type MARKET --time-in-force TIF_IOC --cash-qty 100`
- Sell on a specific account: `futu crypto order sell ETHHKD --account <account-id> --qty 0.02 --price 50000`

## Crypto modify, cancel, and query

| Command | Required | Default / omit | Optional parameters |
| --- | --- | --- | --- |
| `futu crypto order modify <order-id>` | `order-id`, `--price`, `--qty`, `--order-version`, `--conditional-info`; also `--account` when no default account is configured | `--req-id` generated automatically | `--account`, `--req-id`, `--price`, `--qty`, `--order-version`, `--conditional-info` |
| `futu crypto order cancel <order-id>` | `order-id`; also `--account` when no default account is configured | `--req-id` generated automatically | `--account`, `--req-id` |
| `futu crypto order list` | none if `default_account` is configured | `--page-size 50`, `--page-flag ""` | `--account`, `--page-size`, `--page-flag` |
| `futu crypto order history` | none if `default_account` is configured | last 3 months, `--page-size 50`, `--page-flag ""`, no filters | `--account`, `--start`, `--end`, `--page-size`, `--page-flag`, `--symbol`, `--order-status`, `--currency`, `--side`, `--type` |
| `futu crypto order detail <order-id> [order-id...]` | `order-id`; also `--account` when no default account is configured | none | `--account` |
| `futu crypto deal <order-id>` | `order-id`; also `--account` when no default account is configured | `--page-size 50`, `--page-flag ""`, `--group-by-order=false` | `--account`, `--page-size`, `--page-flag`, `--group-by-order` |
| `futu crypto deal history` | none if `default_account` is configured | last 3 months, `--page-size 50`, `--page-flag ""`, `--group-by-order=false`, no `--symbol` filter | `--account`, `--start`, `--end`, `--symbol`, `--page-size`, `--page-flag`, `--group-by-order` |

Field mapping:

| CLI parameter | Backend field |
| --- | --- |
| `order modify --req-id` | `req_id` |
| `order modify --price` | `price` |
| `order modify --qty` | `qty` |
| `order modify --order-version` | `order_version` |
| `order modify --conditional-info` | `conditional_info` |
| `order cancel --req-id` | query parameter `req_id` |
| `--start` | `start_time` |
| `--end` | `end_time` |
| `--page-size` | `page_size` |
| `--page-flag` | `page_flag` |
| `--symbol` | `symbol` |
| `order history --order-status` | `order_status` |
| `order history --currency` | `currency` |
| `order history --side` | `side` |
| `order history --type` | `ord_type` |
| `deal <order-id>` | query parameter `order_id` |

Query and pagination rules:

- List and history queries do not paginate automatically. If the response has `completed=false` and a `page_flag`, pass that value to `--page-flag` for the next page.
- When historical orders and historical fills omit `--start` / `--end`, the default range is the last 3 months.
- Multi-order detail accepts at most 20 orders. The CLI joins multiple `<order-id>` values with commas into the path parameter `{order_id}`.
- `--order-version` for `order modify` comes from `version` on the order detail or order list.
- When modifying a regular order, `--conditional-info` is still a required flag. `{}` is acceptable.

Response parsing:

- Order-list JSON: main fields are `orders`, `page_flag`, and `completed`.
- Fill-list JSON: main fields are `order_fills`, `page_flag`, and `completed`. The CLI accepts backend `order_fills`, `fills`, and `deals`, and normalizes them to `order_fills`.
