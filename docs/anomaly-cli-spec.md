# futu-cli：`futu unusual` 子命令接口草案

供 [futu-cli](https://github.com/FutunnOpen/futu-cli) 与 OAuth REST 实现对齐 [Futu Agent Hub](../README.md) 三个 Unusual Skill（`futu-unusual-*`）。OpenD SDK 等价方法：`get_technical_unusual`、`get_financial_unusual`、`get_derivative_unusual`。

## 1. 命令树（Cobra）

与现有 `futu capital`、`futu broker` 同级，建议 **独立命令组**（非 `quote_rest_specs` 单路由），因参数与响应结构与 BFF quote 不同：

```text
futu
└── unusual          # 别名: anomaly
    ├── technical-signals <symbol>   # get_technical_unusual（别名: technical）
    ├── capital-flows <symbol>       # get_financial_unusual（别名: capital）
    └── derivatives-activity <symbol> # get_derivative_unusual（别名: derivatives）
```

全局标志（继承 root）：`--format json|table`、`--token-file`、内部 `--source skill`、`--agent`。

子命令共有 flags：

| Flag | 类型 | 默认 | 说明 |
|------|------|------|------|
| `--time-range` | int | `7` | 自然日窗口 |
| `--language-id` | int | `0` | `0` zh-CN, `1` zh-TW, `2` en, `4` th, `5` ja |
| `--analysis-dimensions` | string[] | 空=全量 | 仅 `capital-flows` / `derivatives-activity` |
| `--indicator-filters` | string[] | 空=全量 | 仅 `technical-signals` |

示例（与 Skill 一致）：

```bash
futu unusual technical-signals HK.00700 --time-range 7 --indicator-filters MACD,RSI6 --language-id 0 --format json
futu unusual capital-flows US.NVDA --time-range 7 --analysis-dimensions funds_flow,funds_broker --format json
futu unusual derivatives-activity US.NVDA --time-range 7 --analysis-dimensions option_unusual --format json
```

重复 flag 与逗号分隔：`--analysis-dimensions a b` 与 `--analysis-dimensions a,b` 均应支持（与现有 CLI 习惯对齐即可）。

## 2. REST 映射（对齐 FutuOpenD SkillWrap）

OpenD 现网（`FutuOpenD/Src/NNProtoCenter/Quote/NNBiz_Qot_SkillWrap.cpp`）：

- **POST** `{api_host}/api/v1/get_technical_unusual`
- **POST** `{api_host}/api/v1/get_financial_unusual`
- **POST** `{api_host}/api/v1/get_derivative_unusual`

`api_host`：Futu `https://api.futunn.com`，Moomoo `https://api.moomoo.com`。OAuth CLI 应在用户 `api_base` 上提供**同 path、同 JSON body** 的三条接口（或网关等价转发）。

OpenAPI **Pb Proto 协议号**（SDK `ProtoId.SkillWrap_*`，与 OpenD 头同值）：**3801 / 3802 / 3803**（`SkillWrapAPI.proto` + `constant.py`）。不是 `NN_ProtoCmd`。

| Endpoint ID（建议） | Method | Path | CLI |
|---------------------|--------|------|-----|
| `skillwrap.technical_unusual` | POST | `/api/v1/get_technical_unusual` | `unusual technical-signals` |
| `skillwrap.financial_unusual` | POST | `/api/v1/get_financial_unusual` | `unusual capital-flows` |
| `skillwrap.derivative_unusual` | POST | `/api/v1/get_derivative_unusual` | `unusual derivatives-activity` |

POST body（proto 字段名，`SkillWrapAPI.proto`）：

| 字段 | 适用 |
|------|------|
| `stock_symbol` | 全部（CLI  positional `<symbol>` 写入此字段） |
| `time_range` | 全部，默认 7 |
| `language_id` | 全部，默认 0 |
| `indicator_filters` | technical |
| `analysis_dimensions` | capital, derivatives |

HTTP 响应 JSON 字段（OpenD 映射）：`code` → errCode，`message`，`time_range`，`content`（主内容）。详见 [migration-gaps-and-rest-api.md](./migration-gaps-and-rest-api.md) §3.4。

`internal/reporting/routes.go` 同步注册三条路由供 telemetry。

## 3. 实现落点（futu-cli 仓库）

| 文件 | 改动 |
|------|------|
| [`cmd/unusual.go`](https://github.com/FutunnOpen/futu-cli) | `unusualCmd`（`anomaly` 别名）+ 三个子命令；解析 symbol、flags；调用 service |
| `internal/service/skillwrap.go` | 封装三次 HTTP 调用、错误码映射 |
| `internal/client/endpoints.go` | 注册三个 endpoint |
| `cmd/root.go` | `rootCmd.AddCommand(unusualCmd)`；**不要**加入 `noAuthCommands` |
| `internal/output` | JSON 输出保留后端原始结构；table 模式可选简表 |

不必走 `quoteRESTSpecs` / `registerQuoteRESTAggregateCommands` 动态注册，除非后端统一为 BFF 风格且响应可 `Wrap`。

## 4. JSON 响应契约（Skill 验收 T07）

CLI `--format json` 最小集应对齐 OpenD `*UnusualRsp` + HTTP 回包：

```json
{
  "retType": 0,
  "errCode": 0,
  "retMsg": "",
  "time_range": "2026.4.2-2026.4.9",
  "content": "...",
  "method": "get_technical_unusual"
}
```

`content` 与 OpenD SDK 返回的 `content` **字段级等价**（T07 golden）。可选附加请求镜像字段 `stock_symbol` / `time_range` / filters。Skill 展示逻辑见：

- `skills/unusual-skills/futu-unusual-technical-signal-alerts/SKILL.md`
- `skills/unusual-skills/futu-unusual-capital-flows/SKILL.md`
- `skills/unusual-skills/futu-unusual-derivatives-activity/SKILL.md`

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

命令与路径同构：`moomoo unusual ...`（`anomaly` 别名），仅 binary 名与 `api_base` 不同。
