# Real-time quote push

Use `futu quote subscribe` for continuous quote, order book, ticker, K-line, and broker-queue data. The CLI opens the WebSocket, authenticates with the stored OAuth token, and prints each server message as one compact JSON line. Do not read the token file and do not open `wss://webapi-quote.futunn.com/ws` from the skill.

```bash
futu quote subscribe --symbols HK.00700 --types quote,order_book --format json --source skill
```

When calling the CLI from Bash, append `--source skill` as with other commands. Omit `--duration` and `--max-messages` unless the user asks for a different window. The defaults are 20 seconds and 50 push messages. The maximum duration is 30 minutes.

| Flag | Default | Meaning |
| --- | --- | --- |
| `--symbols` | required | Comma-separated `MARKET.CODE` symbols |
| `--types` | `quote` | `quote`, `order_book`, `ticker`, `kline` |
| `--duration` | `20s` | Stop when this time elapses |
| `--max-messages` | `50` | Stop after this many subscribed pushes (`QUOTE`, `ORDER_BOOK`, `TICKER`, `KLINE`, and `BROKER_QUEUE` when `order_book` is subscribed). `MARKET_STATE` is printed and does not count. `0` removes the cap |
| `--kline-period` | `1m` | Used only when `types` includes `kline` |
| `--kline-adjust` | `none` | Used only when `types` includes `kline` |

Stdout lines are JSON. A line with `type` is a push: `QUOTE`, `ORDER_BOOK`, `TICKER`, `KLINE`, or `BROKER_QUEUE`. `BROKER_QUEUE` arrives after `order_book` is subscribed for an eligible symbol. It is not a `--types` value. An empty stdout means the window ended without a push.

Pass `--format json` when the output will be parsed. The token is not included in stdout or stderr.
