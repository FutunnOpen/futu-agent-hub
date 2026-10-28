# Real-time quote push (WebSocket)

The `futu` CLI covers **REST** market-data queries. It does **not** replace OpenD TCP subscribe or the removed `futuapi/scripts/subscribe/*` scripts.

For **continuous** quote, order book, ticker, K-line, and **broker queue** streams, use **FUTUNN Open API Quote Push WebSocket**:

- Endpoint: `wss://webapi-quote.futunn.com/ws`
- Flow: connect → **auth** (OAuth Bearer recommended, same family as `futu auth login`) → **subscribe** → handle pushes by `type`
- Subscribe fields: `quote`, `order_book`, `ticker`, `kline` (see official subscribe doc)
- Broker queue: message type **`BROKER_QUEUE`** (usually after `order_book` subscribe on eligible HK symbols; not a separate subscribe key)

Hub user guide (Chinese, full examples): repo [`docs/websocket-quote-push.md`](../../../../docs/websocket-quote-push.md).

Official API:

- [Overview](https://open.futunn.com/api/quote/push/overview)
- [Auth](https://open.futunn.com/api/quote/push/auth)
- [Subscribe](https://open.futunn.com/api/quote/push/subscribe)
- [Data format](https://open.futunn.com/api/quote/push/data-format)

When the user asks for live push, streaming quotes, or real-time broker queue, **do not** fall back to OpenD or Python SDK. Point them to WebSocket integration above; use CLI only for one-off REST reads unless they already run a WS client.
