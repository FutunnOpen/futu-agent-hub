# Paper-trading pagination

Only historical paper orders expose the pagination this skill needs to handle.

## General rules

- Among the current high-level paper-trading commands, only `futu sim order history` exposes pagination parameters.
- Pagination tasks must use `--format json`. Otherwise, do not try to parse `pagination.next_key`.
- The first page usually omits `--next-key`. The next page passes `pagination.next_key` from the previous response.
- `--page-size` defaults to `50` and maps to the BFF field `page_size`.
- `--start` / `--end` are microsecond timestamps and map to `time_begin` / `time_end`. `0` or omitting them means unbounded.
- Stop paging when the cursor is empty or missing, or when the order list is empty.
- While paging, keep `--account`, `--market`, `--start`, `--end`, and `--page-size` unchanged. Replace only `--next-key`.

## Command

| CLI | BFF ID | Cursor | Size parameter | Time parameters |
| --- | --- | --- | --- | --- |
| `futu sim order history` | `sim_trade.history_order_list` | `--next-key` -> `next_key` | `--page-size` -> `page_size` | `--start` / `--end` -> `time_begin` / `time_end` |

## Examples

```bash
# Page 1
futu sim order history --account <sim-account-id> --market US --page-size 50 --format json

# Page 2
futu sim order history --account <sim-account-id> --market US --page-size 50 --next-key '<pagination.next_key>' --format json
```

For a time range, pass microsecond timestamps:

```bash
futu sim order history --account <sim-account-id> --market US --start 1767225600000000 --end 1769817600000000 --page-size 50 --format json
```

## Skill handling guidance

- When the user asks for more historical orders or the next page, first confirm that the previous page's JSON contains `pagination.next_key`. Without a cursor, do not continue paging.
- When the user asks for all historical orders, loop `futu sim order history` and stop when `pagination.next_key` is empty. If the user did not set a limit, summarize in batches and report how many pages were fetched.
- When the user gives a date string, convert it to a Unix microsecond timestamp before passing it to `--start` / `--end`.
