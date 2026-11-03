# SkillWrap 异动三接口 REST 规格（OpenD 对齐）

> **读者**：REST / Open API 网关（restfut）开发  
> **用途**：在 OAuth 公网链路上暴露与 OpenD / Skill 后端一致的异动能力，供 [Futu Agent Hub](https://github.com/FutunnOpen/futu-agent-hub) 与官方 `futu` / `moomoo` CLI 调用。  
> **版本**：2026-10-28  
> **关联**：Hub 内 `docs/migration-gaps-and-rest-api.md` §3、`docs/anomaly-cli-spec.md`

---

## 1. 背景与目标

### 1.1 业务是什么

三条接口用于 **单标的、近 N 自然日** 的「异动」摘要（非普通行情快照）：

| 原 OpenD SDK 方法 | 业务名称 | Agent Hub Skill |
|-------------------|----------|-----------------|
| `get_technical_unusual` | 技术面异动 · Technical Signal Alerts | `futu-unusual-technical-signal-alerts` |
| `get_financial_unusual` | 资金异动 · Unusual Capital Flows | `futu-unusual-capital-flows` |
| `get_derivative_unusual` | 衍生品异动 · Unusual Derivatives Activity | `futu-unusual-derivatives-activity` |

### 1.2 和 `webapi.futunn.com` 行情 REST 的关系

- 这三条 **不属于** 现有 Open API 文档中的 `/api/v1.0/quote/...` BFF 体系。
- OpenD 现网走的是 **Skill 域 HTTP**：`https://api.futunn.com`（Moomoo：`https://api.moomoo.com`）上的 **`POST /api/v1/get_*_unusual`**。
- **去 OpenD 迁移目标**：OAuth 用户通过 CLI/REST 访问 **与 OpenD 相同的 path、JSON body、响应字段语义**；网关可在 `webapi.*` 上 **新增转发路由**，或让 CLI `api_base` 直连 Skill 域（需产品定 Host 与鉴权模型）。

### 1.3 OpenD 内部实现（供对齐，非要求网关复刻 Pb）

OpenD **没有** 对应的 `NN_ProtoCmd` 行情 TCP 拉数；链路为：

1. 客户端发 **OpenAPI Pb**（协议号 **3801 / 3802 / 3803**，定义见 `SkillWrapAPI.proto`）。
2. OpenD `Pull*Unusual` → `PostSkillWrapUnusualWithJsonBody`（参考 `FutuOpenD/Src/NNProtoCenter/Quote/NNBiz_Qot_SkillWrap.cpp`）。
3. HTTP POST Skill 后端，响应 JSON 映射为 `*UnusualRsp`（参考 `APIServer_Qot_SkillWrap.cpp` / `FillSkillWrapRspFromJson`）。

**限频（OpenD 侧约定）**：协议 3801–3803，**30 次 / 30 秒**（按连接/用户策略以现网为准）。

---

## 2. 对外 REST 契约（与 Skill 后端 / OpenD 对齐）

### 2.1 总览

| 能力 | HTTP Method | Path | CLI |
|------|-------------|------|-----|
| 技术面异动 | POST | `/api/v1.0/quote/{symbol}/unusual/technical` | `futu unusual technical-signals <symbol>` |
| 资金面异动 | POST | `/api/v1.0/quote/{symbol}/unusual/capital` | `futu unusual capital-flows <symbol>` |
| 衍生品异动 | POST | `/api/v1.0/quote/{symbol}/unusual/derivatives` | `futu unusual derivatives-activity <symbol>` |

**Host（Skill 业务源站，OpenD 使用）**

| 品牌 | Host |
|------|------|
| Futu | `https://api.futunn.com` |
| Moomoo | `https://api.moomoo.com` |

**Content-Type**：`application/json`  
**鉴权（OAuth 公网，待 restfut 定稿）**：建议 `Authorization: Bearer <access_token>`，scope 与 **行情读** 对齐或单独 `unusual_read`（需产品确认）。

---

### 2.2 请求（路径参数 + JSON body）

`symbol` 在路径中，格式为 `市场.代码`（`HK` / `US` / `SH` / `SZ` / `SG` / `JP`）。请求体不包含 `stock_symbol`。

#### 公共字段

| 字段 | 类型 | 位置 | 必填 | 说明 |
|------|------|------|------|------|
| `symbol` | string | 路径 | 是 | 例如 `HK.00700`、`US.NVDA`、`SH.600519`。 |
| `time_range` | integer | 请求体 | 否 | 回溯自然日；不传或 ≤0 时按 **7**，最大 **365**。 |
| `language_id` | integer | 请求体 | 否 | `0` 简中（默认），`1` 繁中，`2` 英文，`4` 泰语，`5` 日语。 |

#### 技术面：`POST /api/v1.0/quote/{symbol}/unusual/technical`

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `indicator_filters` | string[] | 否 | 指定指标子集；**不传或空数组表示全量**（含 K 线形态及指标异动，以 Skill 服务为准）。 |

**`indicator_filters` 常用枚举（Agent Hub 约定）**

`CCI`, `KDJ`, `BIAS`, `AR`, `BR`, `VR`, `PSY`, `OSC`, `WMSR`, `MACD`, `BOLL`, `MA`, `RSI6`, `RSI12`, `RSI24`

#### 资金面：`POST /api/v1.0/quote/{symbol}/unusual/capital`

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `analysis_dimensions` | string[] | 否 | 不传表示全量维度。 |

**`analysis_dimensions` 枚举**

| 值 | 含义 |
|----|------|
| `funds_distribution` | 资金分布 |
| `funds_broker` | 买卖经纪商 |
| `funds_flow` | 资金流向 |
| `short_sell_number` | 卖空数量 |
| `short_sell_ratio` | 卖空比例 |
| `short_sell_number_and_ratio` | 卖空数量与比例同时异常 |

#### 衍生品：`POST /api/v1.0/quote/{symbol}/unusual/derivatives`

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `analysis_dimensions` | string[] | 否 | 不传表示全量（共 7 类）。 |

**`analysis_dimensions` 枚举**

| 值 | 含义 |
|----|------|
| `warrant_ratio` | 牛熊证街货比例（港股） |
| `warrant_price_distribution` | 牛熊证街货价格分布（港股） |
| `option_unusual` | 期权大单/异常成交 |
| `option_volatility` | 期权波动率异动 |
| `option_volume_price` | 期权量价异动 |
| `option_sentiment` | 期权情绪（如 PCR） |
| `option_comprehensive` | 期权综合信号 |

---

### 2.3 请求示例

**技术面**

```http
POST /api/v1.0/quote/US.NVDA/unusual/technical HTTP/1.1
Host: webapi.futunn.com
Authorization: Bearer <token>
Content-Type: application/json

{
  "time_range": 7,
  "language_id": 0,
  "indicator_filters": ["MACD", "RSI6"]
}
```

**资金面** `POST /api/v1.0/quote/HK.00700/unusual/capital`

```json
{
  "time_range": 7,
  "language_id": 0,
  "analysis_dimensions": ["funds_flow", "funds_broker"]
}
```

**衍生品** `POST /api/v1.0/quote/US.AAPL/unusual/derivatives`

```json
{
  "time_range": 7,
  "language_id": 0,
  "analysis_dimensions": ["option_unusual", "option_volatility"]
}
```

---

### 2.4 响应体

网关成功时 HTTP 200，正文为 Open API 信封：

| 字段 | 说明 |
|------|------|
| `ret_code` | 网关状态码，**0 表示成功** |
| `ret_msg` | 网关提示 |
| `data.code` | 下游业务状态：**0 有异动，1 无异动** |
| `data.message` | 下游提示 |
| `data.time_range` | 展示用区间，如 `"2026.4.2-2026.4.9"` |
| `data.content` | 异动正文；无异动时为空字符串 |

`ret_code != 0` 为失败。`data.code = 1` 仍是成功调用。CLI `--format json` 把 `ret_code` 写入 `retType`，把 `data.code` 写入 `errCode`，并附加 `method` 便于 Agent 路由：

```json
{
  "retType": 0,
  "errCode": 0,
  "retMsg": "",
  "time_range": "2026.4.2-2026.4.9",
  "content": "...",
  "method": "get_technical_unusual",
  "stock_symbol": "US.NVDA"
}
```

**HTTP 状态码建议**

| 场景 | 建议 |
|------|------|
| 鉴权失败 | 401 |
| 无行情/异动权限 | 403 |
| 参数错误（缺 symbol、非法 market 等） | 400 |
| 网关失败 | HTTP 200 且 `ret_code != 0`，或 4xx |
| 窗口内无异动 | 200，`ret_code=0`，`data.code=1`，`data.content` 为空 |
| 上游 Skill 超时/5xx | 502/504 |

---

## 3. restfut 网关实现要点

### 3.1 推荐架构

```text
Client (futu CLI / 第三方)
    → Authorization: Bearer (OAuth)
    → POST https://webapi.futunn.com/api/v1.0/quote/{symbol}/unusual/{technical|capital|derivatives}
    → 校验 token + scope + 标的权限
    → 转发至 Skill 源站（或内网等价服务）
    ← Skill JSON (code/message/time_range/content)
    ← 可选：映射为 Open API 统一 envelope
```

CLI 与第三方在当前 `api_base` 上用 Bearer 调用上述 path。正式环境 host 为 `https://webapi.futunn.com`。标的放在路径里，请求体不带 `stock_symbol`。

### 3.2 与 OpenD 鉴权差异（勿混用）

OpenD 访问 Skill 时使用 **CommonPost** 模型：URL query（`user_id`, `auth_token`, `clienttype`, `clientver`, …）+ 特定 Header/Cookie（`web_sig` 等）。  
**OAuth 公网 REST 不应要求客户端拼这些参数**；由网关用登录态换票或内网服务身份访问 Skill。

### 3.3 权限与标的

OpenD 网关侧（可参考开源复刻 `futu-gateway-qot/skill_wrap.rs`）在发 HTTP 前会：

- 解析 `stock_symbol` 市场前缀；
- 校验静态标的与 **行情读权限**。

restfut 建议在 OAuth 层做 **等价校验**，避免无权限用户打穿 Skill。

### 3.4 限流

- 对齐 OpenD：**3801–3803 合计或分协议 30 次/30 秒**（以现网 Skill/OpenD 配置为准）。
- 公网 API 建议按 **app_id + user_id** 限流，并返回标准 `429`。

---

## 4. 客户端（futu-cli）已实现的调用方式

便于联调对照（Go 仓库 `FutunnOpen/futu-cli`）：

| Endpoint ID | Method | Path |
|-------------|--------|------|
| `skillwrap.technical_unusual` | POST | `/api/v1.0/quote/{symbol}/unusual/technical` |
| `skillwrap.financial_unusual` | POST | `/api/v1.0/quote/{symbol}/unusual/capital` |
| `skillwrap.derivative_unusual` | POST | `/api/v1.0/quote/{symbol}/unusual/derivatives` |

`symbol` 走路径参数。请求体只含 `time_range`、`language_id`，以及技术面的 `indicator_filters` 或资金面/衍生品的 `analysis_dimensions`。见 `internal/service/skillwrap.go`。

**联调命令示例**

```bash
futu auth login
futu unusual technical-signals HK.00700 --time-range 7 --format json
futu unusual capital-flows US.NVDA --analysis-dimensions funds_flow --format json
futu unusual derivatives-activity US.NVDA --analysis-dimensions option_unusual --format json
```

---

## 5. Proto 参考（Pb 3801–3803）

定义文件（OpenD / SDK 同源）：`SkillWrapAPI.proto`

```protobuf
message TechnicalUnusualReq {
  optional string stock_symbol = 1;
  optional int32 time_range = 2;
  repeated string indicator_filters = 3;
  optional int32 language_id = 4;
}
message TechnicalUnusualRsp {
  required int32 retType = 1 [default = -400];
  optional string retMsg = 2;
  optional int32 errCode = 3;
  optional string time_range = 4;
  optional string content = 5;
}
// FinancialUnusualReq/Rsp、DerivativeUnusualReq/Rsp 结构相同，
// 仅 Req 用 analysis_dimensions 替代 indicator_filters。
```

Python SDK：`ProtoId.SkillWrap_TechnicalUnusual = 3801`（3802/3803 同理），`OpenQuoteContext.get_*_unusual`。

---

## 6. 验收标准（Hub T07）

1. 固定 symbol + `time_range` + filters/dimensions，**响应 `content` / `time_range` / 错误码** 与 OpenD SDK 同参调用 **字段级一致**（golden diff）。
2. OAuth 用户无 OpenD 亦可完成三条 Skill 工作流。
3. 文档：在 Open API 站点列出 path、body、响应、scope、限流（若对外发布）。

---

## 7. 待 restfut / 产品确认项

| # | 问题 |
|---|------|
| 1 | 对外 path 已定为 `POST /api/v1.0/quote/{symbol}/unusual/technical|capital|derivatives`。 |
| 2 | OAuth scope 名称与错误码是否与现有 quote 读接口共用。 |
| 3 | 业务失败时 HTTP 200 + `code` 还是统一 4xx（与全局 Open API 规范一致）。 |
| 4 | 响应是否强制 Open API `{s,d}` 信封；若强制，CLI 已兼容 `d` 内 Skill 字段。 |
| 5 | Moomoo 双品牌：`api.moomoo.com` 与 Futu 是否同一套网关规则。 |

---

## 8. 参考代码位置（本机/内网仓库）

| 组件 | 路径 |
|------|------|
| OpenD Skill HTTP | `FutuOpenD/Src/NNProtoCenter/Quote/NNBiz_Qot_SkillWrap.cpp` |
| OpenD API 层 JSON 映射 | `FutuOpenD/.../APIServer_Qot_SkillWrap.cpp` |
| Pb 定义 | `FutuOpenD/Src/NNProtoFile/API/PB/SkillWrapAPI.proto` |
| Python SDK | `ftapi4python/futu/quote/open_quote_context.py` + `quote_query.py`（SkillWrap*Query） |
| OpenD 行为复刻（Rust） | `futu-opend-rs/crates/futu-gateway-qot/src/handlers/qot/skill_wrap.rs` |
| OAuth CLI | `futu-cli/internal/service/skillwrap.go`、`cmd/unusual.go` |

---

## 9. 变更记录

| 日期 | 说明 |
|------|------|
| 2026-10-28 | 初版：restfut 对齐 OpenD SkillWrap 三接口 |
