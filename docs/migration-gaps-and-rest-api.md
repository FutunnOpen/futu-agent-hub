# OpenD / futuapi 迁移：能力缺口与 REST API 补充清单

本文档记录移除 `skills/futu-api-skills/`（`futuapi`、`install-futu-opend`）后，**Skill Hub 不再提供的能力**，以及 **CLI/API 团队需补充的 RESTful 接口**。行情与四类交易由现有 `futu-*` Skills + `futu` CLI 承接。

参考：[Futu Skill Hub 升级需求文档](https://futu.feishu.cn/docx/MzvRdL9ZMooDqpxyYnJcP0TUnIb)

---

## 1. 已从仓库移除的包

| 原 Skill | 内容 |
|----------|------|
| `install-futu-opend` | 下载安装 OpenD、升级 `futu-api` Python SDK |
| `futuapi` | 64 个 Python 脚本：quote / trade / subscribe，经 OpenD `127.0.0.1:11111` |

升级路径见 [upgrade-from-opend.md](./upgrade-from-opend.md)。

---

## 2. 改完后仍缺失或未承诺的能力

### 2.1 阻塞：技术分析三类异动（P0）

原 OpenD SDK 方法，现由三个 anomaly Skill 通过 **`futu anomaly *` CLI** 调用（CLI/REST 联调完成前无法使用）。

| 原 SDK 方法 | Skill |
|-------------|--------|
| `get_technical_unusual` | `futu-technical-anomaly` |
| `get_financial_unusual` | `futu-capital-anomaly` |
| `get_derivative_unusual` | `futu-derivatives-anomaly` |

### 2.2 本期不迁移：实时订阅与推送（P1）

原 `futuapi/scripts/subscribe/`（subscribe、push_quote、push_orderbook、push_kline、push_ticker、push_rt_data、push_broker 等）。**Skill Hub 不再提供**；官网勿承诺「多类推送」。

### 2.3 原 futuapi 有、当前 CLI 未暴露的边角能力（P2，可选）

删除 `futuapi` 后，下列能力**不在**四个 quote/trade Skill 的主承诺内；若产品需要 Agent 可调用，需补 REST + CLI。

| 原脚本 | 说明 |
|--------|------|
| `get_order_fee.py` | 预估订单费用 |
| `get_margin_ratio.py` | 融资融券比例 |
| `get_acc_cash_flow.py` | 证券账户现金流水 |
| `get_crypto_cash_flow.py` | 加密货币账户流水（与 `crypto deal history` 可能不等价） |
| `get_history_kl_quota.py` | 历史 K 线额度 |
| `get_broker_queue.py` | 经纪队列（与 `futu broker` 十档/历史可能不等价） |
| `get_warrant.py` | 单权证报价（筛选见 `futu warrant-screen`） |
| `resolve_option_code.py` | 行权价/到期日 → 期权合约代码 |
| `set_price_reminder.py` / `get_price_reminder.py` | 到价提醒 |
| `modify_user_security.py` / `get_user_security_group.py` | 自选股分组细粒度管理（部分由 `futu watchlist` 覆盖） |
| `get_global_state.py` / `get_user_info.py` | OpenD 本地/登录态 → 用 `futu auth status`、`futu check` 替代 |

### 2.4 已由 CLI 覆盖（删除 futuapi 不丢主流程）

核心行情、实盘/模拟/加密交易、大部分 quote 聚合命令 — 见各 Skill 的 `references/cli-parameters.md` 与 [futu-cli README](https://github.com/FutunnOpen/futu-cli)。

---

## 3. 需要补充的 RESTful API

### P0 — 异动（与 OpenD SDK 字段级等价，验收 T07）

建议统一命名空间（路径以 API 团队定稿为准）：

| 方法 | 请求参数 | 建议 REST | 建议 CLI |
|------|----------|-----------|----------|
| `get_technical_unusual` | `stock_symbol`, `time_range`, `indicator_filters[]`, `language_id` | `GET/POST /api/v1.0/quote/unusual/technical` | `futu anomaly technical <symbol> ...` |
| `get_financial_unusual` | `stock_symbol`, `time_range`, `analysis_dimensions[]`, `language_id` | `GET/POST /api/v1.0/quote/unusual/capital` | `futu anomaly capital <symbol> ...` |
| `get_derivative_unusual` | `stock_symbol`, `time_range`, `analysis_dimensions[]`, `language_id` | `GET/POST /api/v1.0/quote/unusual/derivatives` | `futu anomaly derivatives <symbol> ...` |

**契约要点：**

- `language_id`：0/1/2/4/5（与现 anomaly Skill 一致）
- `analysis_dimensions` / `indicator_filters` 枚举与各 anomaly SKILL.md 一致
- 错误分态：无异常、无数据、不适用、权限不足、请求失败
- OAuth scope：与行情读权限对齐或独立 `unusual_read`（待确认）

### P1 — 订阅（若产品保留推送）

| 能力 | 建议 REST / 通道 |
|------|------------------|
| 订阅管理 | `POST/DELETE /api/v1.0/quote/subscriptions` |
| 推送 | WebSocket/SSE `wss://.../quote/stream`（QUOTE、ORDER_BOOK、TICKER、KLINE、BROKER 等） |

### P2 — 交易/行情增强（见 §2.3）

| 业务 | 建议 REST（示意） |
|------|-------------------|
| 预估费用 | `GET /api/v1.0/accounts/{acc_id}/order_fee` |
| 融资融券比例 | `GET /api/v1.0/accounts/{acc_id}/margin_ratio` |
| 现金流水 | `GET /api/v1.0/accounts/{acc_id}/cash_flow` |
| 加密流水 | `GET /api/v1.0/crypto/accounts/{acc_id}/cash_flow` |
| 历史 K 线额度 | `GET /api/v1.0/quote/history_kl_quota` |
| 经纪队列 | `GET /api/v1.0/quote/broker_queue` 或扩展 `futu broker --view queue` |
| 单权证 | `GET /api/v1.0/quote/warrant` |
| 期权代码解析 | `POST /api/v1.0/quote/option/resolve` |
| 到价提醒 | `GET/POST /api/v1.0/quote/price_reminders` |
| 自选分组 | 扩展 watchlist 相关 REST |

---

## 4. 维护说明

- CLI 最低版本：异动 Skill 的 `metadata` 在联调通过后写入具体版本号。
- 本表随 futu-cli Release 更新；完整脚本级对照可在 git 历史中查看已删除的 `skills/futu-api-skills/futuapi/scripts/`。
