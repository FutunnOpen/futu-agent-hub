# 实时行情推送与经纪队列（WebSocket）

移除 OpenD / `futuapi` 后，**不再**使用 `127.0.0.1:11111` 上的 TCP 订阅，也**没有** `futu subscribe` 一类 CLI 子命令。原 `futuapi/scripts/subscribe/*`、`push_*`、`get_broker_queue.py` 等能力，请改用 **FUTUNN Open API 行情推送 WebSocket**。

官方文档（以线上为准）：

- [行情推送概览](https://open.futunn.com/zh-cn/api/quote/push/overview)
- [鉴权](https://open.futunn.com/zh-cn/api/quote/push/auth)
- [订阅与取消订阅](https://open.futunn.com/zh-cn/api/quote/push/subscribe)
- [推送数据格式](https://open.futunn.com/zh-cn/api/quote/push/data-format)
- [保活与重连](https://open.futunn.com/zh-cn/api/quote/push/heartbeat)

Moomoo 用户见 [MOOMOO Open API 行情推送](https://open.moomoo.com/api/quote/push/overview)（端点 `wss://webapi-quote.moomoo.com/ws`）。

---

## 1. 连接地址

| 品牌 | WebSocket Quote 端点 |
|------|----------------------|
| Futu | `wss://webapi-quote.futunn.com/ws` |
| Moomoo | `wss://webapi-quote.moomoo.com/ws` |

Skill Hub 的 **`futu-quote` / Agent 默认走 `futu` CLI 拉取 REST 快照**，不负责维持长连接。需要**持续推送**时，请在你的应用、脚本或服务里**自行实现 WebSocket 客户端**（或用任意支持 WSS 的语言/库）。

---

## 2. 推荐流程（6 步）

与 Open API 文档「接入流程」一致：

1. **建立连接** — 连上上表 WSS 地址。
2. **鉴权** — 连接成功后**先**发登录帧，成功后再订阅。推荐 OAuth 2.1 + PKCE 的 `access_token`（与 `futu auth login` 同源）；也可用 API Key（服务端场景）。详见 [鉴权文档](https://open.futunn.com/zh-cn/api/quote/push/auth)。
3. **订阅** — 在同一连接上发 JSON，`action` 为 `subscribe`，按类型声明标的列表。
4. **收包** — 按消息顶层 `type` 分发（`QUOTE`、`ORDER_BOOK`、`TICKER`、`KLINE` 等）。
5. **保活** — 使用 **WebSocket 协议层 ping/pong**；token 过期前刷新并**重连、重新鉴权**（勿发自定义 JSON heartbeat，见官方说明）。
6. **断线重连** — 重连后**必须重新鉴权并重新订阅**；订阅状态不会自动恢复。

### OAuth 鉴权示例（首帧）

```json
{
  "action": "auth",
  "data": {
    "auth_type": "oauth2",
    "authorization": "Bearer {access_token}"
  }
}
```

`access_token` 可从 CLI 登录后的 token 存储读取，或按 [Open API 快速开始](https://open.futunn.com/zh-cn/api/overview) 自行换取。**勿**把 token 提交到公开仓库或发给不可信第三方。

---

## 3. 订阅推送：对应原 OpenD / futuapi 能力

订阅请求在**已鉴权**的 WebSocket 上发送。可一次请求多种类型（字段省略表示本次不处理该类型）：

| 订阅字段（请求） | 推送 `type` | 近似原 futuapi |
|------------------|-------------|----------------|
| `quote` | `QUOTE` | `push_quote` / 基础报价 |
| `order_book` | `ORDER_BOOK` | `push_orderbook` |
| `ticker` | `TICKER` | `push_ticker` |
| `kline` | `KLINE` | `push_kline`（需带 `symbol` / `period` / `adjust`） |

标的代码统一 **`MARKET.CODE`**（如 `HK.00700`、`US.AAPL`），与 CLI 一致。

### 订阅示例

```json
{
  "id": "sub-realtime-001",
  "action": "subscribe",
  "quote": ["HK.00700", "US.AAPL"],
  "order_book": ["HK.00700"],
  "ticker": ["US.AAPL"],
  "kline": [
    {
      "symbol": "US.AAPL",
      "period": "1m",
      "adjust": "none"
    }
  ]
}
```

取消订阅：`action` 设为 `unsubscribe`，字段结构与 subscribe 相同。详见 [订阅与取消订阅](https://open.futunn.com/zh-cn/api/quote/push/subscribe)。

**权限**：市场、品类、行情权限档位（LV1/LV2/LV3）会影响可订阅类型、摆盘档数与推送内容；失败时以服务端返回为准。

---

## 4. 经纪队列（原 `get_broker_queue.py` / `push_broker`）

- 推送消息类型为 **`BROKER_QUEUE`**（不是单独的 `broker` 订阅字段）。
- 通常在订阅 **`order_book`** 且标的为**部分港股**等满足条件时，由服务端**附带推送**；是否返回取决于市场、品类与权限。
- 解析：`type === "BROKER_QUEUE"`，`data` 中含 `bid_brokers` / `ask_brokers` 等，见 [数据格式 — BROKER_QUEUE](https://open.futunn.com/zh-cn/api/quote/push/data-format)。

示例（结构以官方文档为准）：

```json
{
  "type": "BROKER_QUEUE",
  "symbol": "HK.00700",
  "data": {
    "data_time_ms": 1710000000000,
    "ask_brokers": [{ "rank": 1, "broker_id": "8465", "broker_name": "..." }],
    "bid_brokers": [{ "rank": 1, "broker_id": "8465", "broker_name": "..." }]
  }
}
```

**说明：** `futu broker <symbol>` CLI 提供的是**十大经纪持股**等 REST 查询，与实时**摆盘经纪队列**不是同一接口；实时队列请用 WebSocket `BROKER_QUEUE`。

---

## 5. 其它推送类型

- **`MARKET_STATE`** — 市场状态，多为市场级推送，一般**不是**在 subscribe 里单独传 `market_state` 字段；收到后按 [数据格式](https://open.futunn.com/zh-cn/api/quote/push/data-format) 解析即可。

---

## 6. 与 Skill Hub 的关系

| 场景 | 建议 |
|------|------|
| Agent 偶发查价、K 线、摆盘快照 | 使用 **`futu-quote`** + `futu quote ...` |
| 仪表盘、策略、持续 tick / 摆盘 / 经纪队列 | **自研 WebSocket 客户端** + 本文与 Open API 文档 |
| 原 OpenD `subscribe.py` 一键订阅 | **无 CLI 替代**；按 §2–§4 实现 |

升级总览：[upgrade-from-opend.md](./upgrade-from-opend.md)。仍缺能力清单：[migration-gaps-and-rest-api.md](./migration-gaps-and-rest-api.md)。
