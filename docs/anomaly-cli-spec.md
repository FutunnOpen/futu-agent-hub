# futu-cli：`futu anomaly` 子命令接口草案

供 [futu-cli](https://github.com/FutunnOpen/futu-cli) 与 OAuth REST 实现对齐 [Futu Agent Hub](../README.md) 三个 anomaly Skill。OpenD SDK 等价方法：`get_technical_unusual`、`get_financial_unusual`、`get_derivative_unusual`。

## 1. 命令树（Cobra）

与现有 `futu capital`、`futu broker` 同级，建议 **独立命令组**（非 `quote_rest_specs` 单路由），因参数与响应结构与 BFF quote 不同：

```text
futu
└── anomaly
    ├── technical <symbol>   # get_technical_unusual
    ├── capital <symbol>     # get_financial_unusual
    └── derivatives <symbol> # get_derivative_unusual
```

全局标志（继承 root）：`--format json|table`、`--token-file`、内部 `--source skill`、`--agent`。

子命令共有 flags：

| Flag | 类型 | 默认 | 说明 |
|------|------|------|------|
| `--time-range` | int | `7` | 自然日窗口 |
| `--language-id` | int | `0` | `0` zh-CN, `1` zh-TW, `2` en, `4` th, `5` ja |
| `--analysis-dimensions` | string[] | 空=全量 | 仅 `capital` / `derivatives` |
| `--indicator-filters` | string[] | 空=全量 | 仅 `technical` |

示例（与 Skill 一致）：

```bash
futu anomaly technical HK.00700 --time-range 7 --indicator-filters MACD,RSI6 --language-id 0 --format json
futu anomaly capital US.NVDA --time-range 7 --analysis-dimensions funds_flow,funds_broker --format json
futu anomaly derivatives US.NVDA --time-range 7 --analysis-dimensions option_unusual --format json
```

重复 flag 与逗号分隔：`--analysis-dimensions a b` 与 `--analysis-dimensions a,b` 均应支持（与现有 CLI 习惯对齐即可）。

## 2. REST 映射（`internal/client/endpoints.go`）

建议新增 endpoint ID（Method/Path 以 API 定稿为准）：

| Endpoint ID | Method | Path（建议） | CLI |
|-------------|--------|--------------|-----|
| `quote.technical_unusual` | GET 或 POST | `/api/v1.0/quote/{symbol}/unusual/technical` | `anomaly technical` |
| `quote.financial_unusual` | GET 或 POST | `/api/v1.0/quote/{symbol}/unusual/capital` | `anomaly capital` |
| `quote.derivative_unusual` | GET 或 POST | `/api/v1.0/quote/{symbol}/unusual/derivatives` | `anomaly derivatives` |

Query / body 字段（与 OpenD SDK 对齐）：

| 字段 | 类型 | 适用 |
|------|------|------|
| `symbol` | string (path) | 全部；`MARKET.CODE` |
| `time_range` | int | 全部 |
| `language_id` | int | 全部 |
| `indicator_filters` | string[] | technical |
| `analysis_dimensions` | string[] | capital, derivatives |

`internal/reporting/routes.go` 同步注册三条路由供 telemetry。

## 3. 实现落点（futu-cli 仓库）

| 文件 | 改动 |
|------|------|
| [`cmd/anomaly.go`](https://github.com/FutunnOpen/futu-cli)（新建） | `anomalyCmd` + 三个子命令；解析 symbol、flags；调用 service |
| `internal/service/anomaly.go`（新建） | 封装三次 HTTP 调用、错误码映射 |
| `internal/client/endpoints.go` | 注册三个 endpoint |
| `cmd/root.go` | `rootCmd.AddCommand(anomalyCmd)`；**不要**加入 `noAuthCommands` |
| `internal/output` | JSON 输出保留后端原始结构；table 模式可选简表 |

不必走 `quoteRESTSpecs` / `registerQuoteRESTAggregateCommands` 动态注册，除非后端统一为 BFF 风格且响应可 `Wrap`。

## 4. JSON 响应契约（Skill 验收 T07）

CLI `--format json` 建议在顶层包含：

```json
{
  "symbol": "US.NVDA",
  "time_range": 7,
  "language_id": 0,
  "method": "get_technical_unusual",
  "data": {}
}
```

`method` 取值：`get_technical_unusual` | `get_financial_unusual` | `get_derivative_unusual`。

`data` **字段级等价**于当前 OpenD SDK 返回（Agent Hub 已删除 Python 脚本；以历史 `handle_*_anomaly.py` 或固定样本为 golden）。Skill 展示逻辑见：

- `skills/anomaly-skills/futu-technical-anomaly/SKILL.md`
- `skills/anomaly-skills/futu-capital-anomaly/SKILL.md`
- `skills/anomaly-skills/futu-derivatives-anomaly/SKILL.md`

### 4.1 `analysis_dimensions` 枚举（capital）

`funds_distribution`, `funds_broker`, `funds_flow`, `short_sell_number`, `short_sell_ratio`, `short_sell_number_and_ratio`

### 4.2 `analysis_dimensions` 枚举（derivatives）

含 Skill 文档中的 7 类：`option_unusual`, `option_volatility`, `option_volume_price`, `option_sentiment`, `option_comprehensive`, `warrant_ratio`, `warrant_price_distribution`（以 SKILL 为准）。

### 4.3 `indicator_filters` 枚举（technical）

含 K 线形态及 MACD、RSI6/12/24、KDJ、CCI、BOLL、MA、BIAS、AR/BR、VR、PSY、OSC、WMSR 等（以 SKILL 列表为准）。

## 5. 错误与 HTTP 状态

与现有 quote 命令一致：

| 场景 | CLI 行为 |
|------|----------|
| 未登录 / token 无效 | 非 0 退出；提示 `futu auth login` |
| `PERMISSION_DENIED` |  stderr 明确权限不足，勿解释为缺 token |
| 无数据 / 窗口内无异动 | HTTP 200 + 空或部分空 `data`；Skill 侧展示 `No anomaly` |
| 后端 5xx / 超时 | 非 0 退出；透传 `message` / `code` |

## 6. 测试建议

- 单元：`cmd/anomaly_*_test.go` mock `httpClient`
- 集成：固定 symbol + `time_range` 与 OpenD golden JSON diff（CI 可选）
- README：在 Commands 节增加 **Anomaly** 表格

## 7. moomoo-cli

命令与路径同构：`moomoo anomaly ...`，仅 binary 名与 `api_base` 不同。
