# Futu Trading CLI Parameters

Use `futu`. The commands below show public arguments only; append `--source skill` when invoking them from Bash, but do not display that internal marker to users. Use `--format json` when parsing results. Do not add optional flags merely to restate defaults.

## Authentication and account selection

- `futu auth status --format json` checks local authentication; use `futu auth login` if needed. Do not read token files.
- `futu account list` lists authorized accounts. Check `futu config get default_account` if relying on a configured default; otherwise ask the user to choose an account and pass `--account <account-id>`.
- Symbols use `MARKET.CODE`, for example `US.AAPL` or `HK.00700`. Most CLI `--symbol` inputs map to the API's `code` field. Cash logs explicitly use `--code`.
- The default output format is `table`; `--format json` is appropriate for automation. `--token-file` is optional and defaults to the configured token file.

## Account, positions, and cash logs

| Command | Arguments and behavior |
| --- | --- |
| `futu account list` | Lists authorized accounts; Japanese accounts can include `sub_accounts`. |
| `futu account funds` | `--account`, `--currency` (default `USD`), `--asset-category`. |
| `futu position` | `--account`, `--symbol`, `--pl-ratio-min`, `--pl-ratio-max`, `--asset-category`. |
| `futu account cash-logs` | Requires `--begin-time` and `--end-time` as Unix microseconds. Optional `--account`, `--direction IN/OUT`, `--code`, `--page-flag`, `--page-size` (default 10, maximum 20). Returns one page; use `page_flag` and `completed` to continue. |

`--asset-category` accepts `DOMESTIC` or `FOREIGN`; JP derivative accounts require it, and JP margin accounts default to `FOREIGN`. Order placement and max-quantity queries support `--sub-acc-id`: the only sub-account is selected automatically; specify it when multiple are available.

## Securities orders: preview and execution

`futu order buy <symbol> <qty>`, `sell <symbol> <qty>`, `place <qty>`, `modify <order-id>`, and `cancel <order-id>` return a preview by default. Parse `dry_run`, `submitted`, `confirmation_code`, and `preview`; do not describe a preview as an executed order. Obtain explicit user confirmation before rerunning with the same account and all the same arguments plus `--execute <confirmation_code>`. If the broker requests secondary confirmation, obtain separate user consent before responding.

The deterministic confirmation code covers only part of the request, and the preview does not necessarily display every flag. Verify the full command, account, symbol, side, quantity, price, order type, session, time in force, and any conditional, algorithmic, or multi-leg parameters independently; do not treat a matching code as proof that every option matches.

| Command | Required | Optional flags |
| --- | --- | --- |
| `futu order buy/sell <symbol> <qty>` | Symbol and positive quantity; account if no default | `--price`, `--type`, `--time-in-force`, `--expire-time`, `--lot-type`, `--remark`, `--session`, `--aux-price`, `--order-class`, `--multi-leg-info`, `--sub-acc-id`, `--position-id`, `--trail-type`, `--trail-value`, `--trail-spread`, `--position-open-type`, `--algo-info`, `--execute`. |
| `futu order place <qty>` | Positive quantity, `--side`; `--symbol` for non-multi-leg orders | Same flags as buy/sell. `--order-class MLEG` may omit `--symbol` but requires the `--multi-leg-info` JSON object. |
| `futu order modify <order-id>` | `--exchange`, positive `--qty`; account if no default | `--price`, `--aux-price`, `--trail-type`, `--trail-value`, `--trail-spread`, `--algo-info`, `--execute`. Omitted prices are left unchanged; the help notes a price requirement for limit orders. |
| `futu order cancel <order-id>` | `--exchange`; account if no default | `--execute`. |

Quantity can be fractional. Preserve order and fill price/quantity strings as decimal values rather than converting through binary floating point. Order type defaults to `market`; time in force defaults to `DAY`. `GTD` requires `--expire-time` in Unix microseconds. `FOK` is client-selectable for forex only. Forex closing orders with `SELL` or `BUY_BACK` require `--position-id`. Trailing and algorithmic flags are described in the [trading dictionary](dictionaries.md). `--algo-info` and `--multi-leg-info` are JSON objects.

## Queries

| Command | Arguments and behavior |
| --- | --- |
| `futu order list`, `futu deal` | `--account`, `--market` (default `HK`), `--page-size` (default 50; 1–100), `--page-flag` (initial cursor). |
| `futu order history`, `futu deal history` | Same flags plus `--symbol`, `--start`, and `--end` in Unix microseconds. If both time bounds are omitted, the server uses the last 90 days; if only one is supplied, the server derives the other. |
| `futu order detail <order-id>...` | Requires `--exchange`; optional `--account`. Up to 100 order IDs. |
| `futu order max-qty <symbol>` | `--account`, `--type`, `--price`, `--order-id`, `--sub-acc-id`, `--position-id`, `--session`. `--price` is required for non-market orders. |
| `futu order fees <order-id>` | Optional `--account`. Canadian broker accounts and forex orders are unsupported. |
| `futu order combo-info <qty>` | Requires `--multi-leg-info`, `--price`, and `--side`; optional `--account` and `--order-id`. Unsupported for Japanese brokers. |
| `futu margin-ratio` | Requires `--security-firm` and `--codes`; at most 10 comma-separated `MARKET.CODE` symbols. |

Order and fill lists automatically fetch remaining pages from the supplied initial cursor and return merged arrays without pagination metadata. Cash logs return a single page; follow their response cursor explicitly.

## CLI output mappings

The CLI normalizes order API fields `code`, `trd_side`, `order_type`, `dealt_qty`, and `order_status` to `symbol`, `side`, `type`, `filled_qty`, and `status`. Fill fields `code`, `trd_side`, `create_time`, and `update_time` map to `symbol`, `side`, `time`, and `updated_time`; legacy `updated_time` is also accepted. Other response fields are retained; `counter_broker_id` is handled as a string. Positions may retain backend field names such as `code`. Treat missing JSON fields carefully: output cleanup may omit empty values and numeric zero.

The official API dictionary is [dictionaries.md](dictionaries.md). For API-specific restrictions, consult the relevant official endpoint documentation and use `futu <command> --help` for the installed CLI version.

### Maximum tradable quantity fields

| Field | Meaning |
| --- | --- |
| `max_cash_buy` | Maximum cash purchase quantity |
| `max_cash_and_margin_buy` | Maximum purchase quantity using cash and margin |
| `max_position_sell` | Maximum quantity sellable from a position |
| `max_sell_short` | Maximum short-sale quantity |
| `max_buy_back` | Maximum buy-back quantity |
| `long_required_im` | Initial margin required for a long position |
| `short_required_im` | Initial margin required for a short position |

### Errors

- `account ID is required`: pass the selected `--account` or configure `default_account`.
- `unsupported order type`: the value is not supported by the CLI, market, or instrument. Before any real order, explain the issue and obtain the user's confirmation for any changed order type.
- `PERMISSION_DENIED`: the server denied permission; do not infer missing authentication headers.
