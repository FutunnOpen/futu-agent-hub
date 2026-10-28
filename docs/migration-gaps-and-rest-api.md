# OpenD / futuapi 迁移：能力缺口清单

本文档记录移除 `skills/futu-api-skills/` 后 **Skill Hub / futu-cli 仍缺的能力**。

**约定：** [FUTUNN Open API](https://open.futunn.com/zh-cn/api/overview) **文档里已列出的 HTTP/WS 接口，视为服务端已实现**（Host 一般为 `https://webapi.futunn.com`，行情 WS 见快速开始）。本仓 backlog **不是**「让后端再写一遍 REST」，而是 **CLI 接入、OAuth 网关暴露（若与 OpenD Skill 路径不同）、Skill 是否承诺**。

参考：[Futu Skill Hub 升级需求文档](https://futu.feishu.cn/docx/MzvRdL9ZMooDqpxyYnJcP0TUnIb)

**产品已确认：** 到价提醒 **不做**；**历史 K 线额度**（原 `get_history_kl_quota.py`）**暂时不做**，不排 Open API/CLI/Skill；实时经纪队列走 Open API WebSocket 推送 **`BROKER_QUEUE`**（见 [websocket-quote-push.md](./websocket-quote-push.md)），不单独立项 REST 拉取。

---

## 1. 已从仓库移除的包

| 原 Skill | 内容 |
|----------|------|
| `install-futu-opend` | 下载安装 OpenD、升级 `futu-api` Python SDK |
| `futuapi` | 64 个 Python 脚本：quote / trade / subscribe，经 OpenD `127.0.0.1:11111` |

升级路径见 [upgrade-from-opend.md](./upgrade-from-opend.md)。

---

## 2. 改完后仍缺失或未承诺的能力

### 2.1 三类异动（P0）

原 OpenD SDK 方法，由三个 anomaly Skill 通过 **`futu anomaly *` CLI** 调用。CLI 已实现；**发版、OAuth/`api_base` 网关、T07 验收**未闭环前，生产环境需确认 SkillWrap 路径可达。

| 原 SDK 方法 | Skill |
|-------------|--------|
| `get_technical_unusual` | `futu-technical-anomaly` |
| `get_financial_unusual` | `futu-capital-anomaly` |
| `get_derivative_unusual` | `futu-derivatives-anomaly` |

### 2.2 实时订阅与推送（P1）— Hub 已处理

原 `futuapi/scripts/subscribe/`（subscribe、push_quote、push_orderbook、push_kline、push_ticker、push_rt_data、push_broker 等）。**OpenD TCP 推送已移除**；官方替代为 **Open API 行情推送 WebSocket（WSS）**。

| 项 | 状态 |
|----|------|
| 服务端 | Open API 已实现（[行情推送概览](https://open.futunn.com/zh-cn/api/quote/push/overview)） |
| 端点 | `wss://webapi-quote.futunn.com/ws` |
| Hub 用户文档 | [websocket-quote-push.md](./websocket-quote-push.md)（鉴权 → subscribe → 收包；**`BROKER_QUEUE`** 经纪队列） |
| 升级指引 | [upgrade-from-opend.md](./upgrade-from-opend.md) §5 |
| Agent | **`futu-quote`**：REST 用 CLI；实时流/经纪队列 **指引 WSS**，禁止回退 OpenD（见 `references/websocket-push.md`） |
| futu-cli | **不计划**封装 `futu subscribe`；推送由用户/集成方 **自建 WSS 客户端**（OAuth 与 `futu auth login` 同源 token） |

WSS 流程摘要：连接 → **auth**（Bearer）→ **subscribe**（`quote` / `order_book` / `ticker` / `kline`）→ 按 `type` 分发；断线须 **重新鉴权并重新订阅**。

### 2.3 原 futuapi 有、Open API 多已具备（P2，可选）

下列能力**不在** `futu-quote` 主路径内；订单费用 / 融资融券 / 资金流水已由 **`futu-trading`** + CLI 覆盖。文档未列出者单独标注。

| 原脚本 | 说明 |
|--------|------|
| `get_order_fee.py` | 订单费用 → [get-order-fees](https://open.futunn.com/zh-cn/api/trading/order/get-order-fees)；CLI **`futu order fees`**（**`futu-trading`** Skill 已文档化） |
| `get_margin_ratio.py` | 融资融券 → [get-margin-ratio](https://open.futunn.com/zh-cn/api/trading/trade/get-margin-ratio)；CLI **`futu margin-ratio`**（**`futu-trading`**） |
| `get_acc_cash_flow.py` | 资金流水 → [get-cash-logs](https://open.futunn.com/zh-cn/api/trading/account/get-cash-logs)；CLI **`futu account cash-logs`**（**`futu-trading`**） |
| `get_crypto_cash_flow.py` | 加密货币账户流水（与 `crypto deal history` 可能不等价） |
| `get_history_kl_quota.py` | 历史 K 线额度 → **产品暂时不做**（与 `futu history-kline` 拉 K 线数据不同；额度查询不迁移） |
| `get_broker_queue.py` | 实时经纪队列 → WebSocket 推送 **`BROKER_QUEUE`**（订阅 `order_book` 后由服务端附带；见 [websocket-quote-push.md](./websocket-quote-push.md)） |
| `get_warrant.py` | **已有替代：** OpenD `Qot_GetWarrant`(3210) 与 `Qot_WarrantScreen`(3254) 均落到后端 `FetchWarrantListV2`；BFF **`POST /api/v1.0/quote/warrant-screen`** → CLI **`futu warrant-screen`**。单标的/简单条件用 `stock_owner` + 筛选组即可；**涡轮筛选**为同链路 **V2 加强版**（跨市场、`screen_groups`、多字段排序）。见 `futu-quote` / `quote.warrant_screen` |
| `resolve_option_code.py` | **已有替代：** BFF 用 `securitycache`（`stock_id` / `id_to_symbol`）在网关内换算，**不必**再调已废弃的 6320/6321。简写「标的 + 到期 + 行权价 + Call/Put」→ CLI **`futu option chain <标的> --start/--end`**（`GET .../option-chain`），在返回的 `option_chain` 里按到期、行权价、`option_type` 取标准 **`MARKET.CODE`** |
| `set_price_reminder.py` / `get_price_reminder.py` | 到价提醒 → **产品不做**，不排 REST/CLI |
| `modify_user_security.py` / `get_user_security_group.py` / `get_user_security.py` | **与 OpenD 三接口等价：** `futu watchlist`（groups / list / add / delete / move-out）→ BFF user-security-group / user-security / modify-user-security。OpenD **无**建组/改名/删空组/组内排序 API；App 侧分组管理不在 API 范围 |
| `get_global_state.py` / `get_user_info.py` | OpenD 本地/登录态 → 用 `futu auth status`、`futu check` 替代 |

### 2.4 已由 CLI 覆盖（删除 futuapi 不丢主流程）

核心行情、实盘/模拟/加密交易、大部分 quote 聚合命令 — 见各 Skill 的 `references/cli-parameters.md` 与 [futu-cli README](https://github.com/FutunnOpen/futu-cli)。

---

## 3. 待办按类型拆分（非「后端缺 REST」）

### P0 — 异动（OpenD Skill HTTP；**通常不在 Open API 文档**）

OpenD 走 **Pb 3801–3803 → POST** `https://api.futunn.com/api/v1/get_*_unusual`（见 FutuOpenD `NNBiz_Qot_SkillWrap.cpp`）。与 `webapi.futunn.com` 的 `/api/v1.0/...` 不是同套文档。**待办：** OAuth/CLI 暴露同等 JSON + `futu anomaly *`（验收 T07）。若产品要求只走 Open API 文档内接口，需单独在 Open API 立项，不在「文档已实现」范围内。

#### 3.1 命令字对照（**NN_ProtoCmd** / OpenAPI Pb / HTTP / CLI）

在 **FutuOpenD 现网代码**里检索 `NNBase_Define_ProtoCmd.h`、`NNProtoFile/Server/PB/`：**P0 三条异动没有 `NN_ProtoCmd`**，也 **没有** 对应的 `FTCmd*.proto`。OpenD 路径是：OpenAPI Pb（3801–3803）→ `INNBiz_Qot_SkillWrap::Pull*Unusual` → **`StartHttpRequest_CommonPost`**（`NNBiz_Qot_SkillWrap.cpp`），不调用 `SendTCPProto_ProtoBuf(..., NN_ProtoCmd_*, ...)`。

| 能力 | Python / Skill | **`NN_ProtoCmd`（行情 TCP）** | OpenAPI Pb `ProtoId` | Req / Rsp | Skill **HTTP** | futu-cli |
|------|----------------|-------------------------------|----------------------|-----------|----------------|----------|
| 技术面异动 | `get_technical_unusual` | **无** | **3801** `SkillWrap_TechnicalUnusual` | `TechnicalUnusualReq` / `Rsp` | `POST /api/v1/get_technical_unusual` | `futu anomaly technical` |
| 资金面异动 | `get_financial_unusual` | **无** | **3802** `SkillWrap_FinancialUnusual` | `FinancialUnusualReq` / `Rsp` | `POST /api/v1/get_financial_unusual` | `futu anomaly capital` |
| 衍生品异动 | `get_derivative_unusual` | **无** | **3803** `SkillWrap_DerivativeUnusual` | `DerivativeUnusualReq` / `Rsp` | `POST /api/v1/get_derivative_unusual` | `futu anomaly derivatives` |

**对照（有 ProtoCmd 的行情能力，便于对齐文档习惯）：**

| OpenAPI | `NN_ProtoCmd` | OpenD 发请求方式 |
|---------|---------------|------------------|
| `Qot_GetCapitalFlow`（3211） | `NN_ProtoCmd_Qot_Pull_CapitalFlow` = **6694** | `SendTCPProto_ProtoBuf` + `FTCmd6516` 等 |
| P0 异动（3801–3803） | **未定义** | 仅 HTTP → `api.futunn.com` / `api.moomoo.com` |

**OpenD 内部回调（不是 ProtoCmd）：** `NN_OMEvent_Qot_Pull_SkillWrap*` = `NN_OMEvSatrt + 43703/43704/43705`（`NNBase_Define_OMEvent.h`）— 这是 OpenD 模块间 OM 消息，**不能**当作 `NN_ProtoCmd` 填表。

**Agent Hub / futu-cli P0：** 应对齐 **OpenAPI Pb + Skill HTTP**；**无法**从 OpenD 抄现成的 ProtoCmd 号。若平台要求 OAuth 也走行情 TCP ProtoCmd，需在 **`NNBase_Define_ProtoCmd.h` + 后台 Skill 服务 + OpenD** 联合新增三条 Pull 命令（当前仓库未实现）。

Pb 定义：`FutuOpenD/Src/NNProtoFile/API/PB/SkillWrapAPI.proto`；SDK：`ProtoId.SkillWrap_*`（`constant.py`）。OpenD 限频：**3801–3803**，30 次 / 30 秒。

#### 3.2 OpenD 实际调用的 HTTP（Skill 后端）

OpenD **不**走 `/api/v1.0/quote/...` BFF，而是 CommonPost JSON body：

| 能力 | Method | Path | Host（OpenD 按客户端类型） |
|------|--------|------|---------------------------|
| 技术面 | POST | `/api/v1/get_technical_unusual` | Futu：`https://api.futunn.com`；Moomoo：`https://api.moomoo.com` |
| 资金面 | POST | `/api/v1/get_financial_unusual` | 同上 |
| 衍生品 | POST | `/api/v1/get_derivative_unusual` | 同上 |

实现：`Src/NNProtoCenter/Quote/NNBiz_Qot_SkillWrap.cpp`（`Pull*Unusual` → `PostSkillWrapUnusualWithJsonBody`）。

**futu-cli P0 建议：** 在 CLI `api_base` 上调用与 OpenD **同 body/响应** 的三条 POST（或网关 rewrite 到 Skill 域）；Bearer OAuth + 行情权限。

#### 3.3 请求 JSON body（POST）

OpenD 将 `SkillWrapAPI.*UnusualReq` 转为 JSON（`preserve_proto_field_names=true`），字段名如下：

**TechnicalUnusualReq**

| 字段 | 类型 | 默认 / 说明 |
|------|------|-------------|
| `stock_symbol` | string | 必填，`HK.00700` / `US.AAPL` 等（OpenD 支持 HK/US/SH/SZ/SG/JP 前缀） |
| `time_range` | int32 | 缺省或 ≤0 时 OpenD 置 **7**（自然日） |
| `indicator_filters` | string[] | 可选；不传表示全量指标 |
| `language_id` | int32 | 缺省 **0**；0 简中 / 1 繁中 / 2 英文 / 4 泰语 / 5 日语 |

**FinancialUnusualReq / DerivativeUnusualReq**

| 字段 | 类型 | 默认 / 说明 |
|------|------|-------------|
| `stock_symbol` | string | 必填 |
| `time_range` | int32 | 默认 7 |
| `analysis_dimensions` | string[] | 可选；不传表示全量维度 |
| `language_id` | int32 | 默认 0 |

枚举取值见各 anomaly `SKILL.md`（`funds_*`、`option_*`、`warrant_*`、指标名等）。

示例 body：

```json
{
  "stock_symbol": "US.NVDA",
  "time_range": 7,
  "language_id": 0,
  "indicator_filters": ["MACD", "RSI6"]
}
```

#### 3.4 HTTP 响应 JSON → OpenAPI / CLI

Skill 服务 HTTP 回包为 JSON 对象，OpenD 映射为 `*UnusualRsp`（`APIServer_Qot_SkillWrap.cpp` → `FillSkillWrapRspFromJson`）：

| HTTP 字段 | OpenAPI 字段 | 说明 |
|-----------|--------------|------|
| `code` | `errCode` | 业务错误码（OpenD 注释：多种含义，透传） |
| `message` | `retMsg` | 错误或提示文案 |
| `time_range` | `time_range` | 展示用区间，如 `"2026.4.2-2026.4.9"` |
| `content` | `content` | **异动正文**（Skill 解析展示的主载荷，常为结构化文本/JSON 字符串） |

OpenAPI 层还有 `retType`（成功/失败）。CLI `--format json` 建议同时输出：`retType`/`errCode`/`retMsg`/`time_range`/`content`，并与 Skill 历史 golden 对齐；可选附加 `method: get_*_unusual` 便于 Agent 路由。

#### 3.5 futu-cli 实现要点（P0）

| Endpoint ID | HTTP | CLI | 状态 |
|-------------|------|-----|------|
| `skillwrap.technical_unusual` | `POST /api/v1/get_technical_unusual` | `futu anomaly technical` | **已接**（本地 futu-cli / moomoo-cli） |
| `skillwrap.financial_unusual` | `POST /api/v1/get_financial_unusual` | `futu anomaly capital` | **已接** |
| `skillwrap.derivative_unusual` | `POST /api/v1/get_derivative_unusual` | `futu anomaly derivatives` | **已接** |

moomoo-cli 同构（`moomoo anomaly *`）；Host 用各自 `api_base`。联调前需确认网关是否在 `webapi.*` 上暴露 `/api/v1/get_*_unusual`，否则配置 `api_base` 指向 `api.futunn.com` / `api.moomoo.com`。

**契约要点：**

- 与 OpenD 链路 **字段级等价**（T07 固定样本 diff）
- OAuth scope：与行情读权限对齐或独立 `unusual_read`（待产品/API 确认）

### P1 — 推送（WSS）

**Hub 侧已闭环**（文档 + Skill 路由），详见 **§2.2**。Moomoo 端点：`wss://webapi-quote.moomoo.com/ws`，文档 [open.moomoo.com 行情推送](https://open.moomoo.com/api/quote/push/overview)。

后续可选（非 Hub 阻塞）：`futu-cli` 封装 WSS 订阅子命令。

### P2 — Open API 已实现；CLI / Skill 见 §2.3

[P2 可选能力](https://open.futunn.com/zh-cn/api/overview) 在服务端 **多数已在 Open API 文档列出**；本仓 **不按「缺 REST」跟踪**，只看 **futu-cli / moomoo-cli 是否注册** 与 **Skill 是否写进 references**。

- **逐条对照（原 futuapi 脚本 → 现 CLI/Skill/WSS）**：见 **§2.3** 表格。
- **交易 P2 三条**（订单费用、融资融券、资金流水）：CLI 已接，**`futu-trading`** 已文档化。
- **自选股**：OpenD/Open API 仅三接口；**`futu watchlist`** 已覆盖（§2.3）。
- **仍待核对**：加密账户流水是否在 Open API 列出及 CLI 是否接。
- **暂时不做**：历史 K 线额度（§2.3）。
- **不做**：到价提醒。实时经纪队列走 **P1 WSS**（§2.2），非 REST。

---

## 4. 维护说明

- CLI 最低版本：异动 Skill 的 `metadata` 在联调通过后写入具体版本号。
- 本表随 futu-cli Release 更新；完整脚本级对照可在 git 历史中查看已删除的 `skills/futu-api-skills/futuapi/scripts/`。
