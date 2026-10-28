<h1 align="center">Futu Agent Hub</h1>
<p align="center">
  <b>将 AI 助手连接到富途 — 用自然语言交易、查行情、获取投资洞察。</b>
</p>

<p align="center">
  <a href="https://openapi.futunn.com/futu-api-doc/"><img src="https://img.shields.io/badge/Futu_API-文档-blue?style=flat-square" alt="Futu API Docs" /></a>
  <a href="#license"><img src="https://img.shields.io/badge/License-MIT-yellow?style=flat-square" alt="License" /></a>
  <a href="https://modelcontextprotocol.io/"><img src="https://img.shields.io/badge/MCP-Compatible-purple?style=flat-square" alt="MCP Compatible" /></a>
</p>

<p align="center">
  <a href="#快速开始">快速开始</a> · <a href="#skills-概览">Skills 概览</a> · <a href="#行情交易-skills">行情交易 Skills</a> · <a href="#异动检测-skills">异动检测 Skills</a> · <a href="#内容-skills">内容 Skills</a> · <a href="#使用示例">使用示例</a>
</p>



---

## 什么是 Futu Agent Hub？

Futu Agent Hub 是 **富途** 官方推出的 AI Agent 技能中心，把官方 `futu` CLI 和金融内容服务封装为标准化的 Skills。行情与交易通过 CLI 接入，**无需安装或运行 OpenD**。让 AI 助手能够查询行情、执行交易、识别异动、检索资讯、感知市场情绪 — 全部通过自然语言完成。

支持 **Claude Code**、**Cursor**、**Claude Desktop**、**VS Code** 等 MCP 兼容的 AI 工具接入。

---

## Skills 概览

Futu Agent Hub 提供 **10 个 Skills**（另含量化策略由交易团队单独交付），分为行情交易、异动检测、内容三类。

| Skill | 类别 | 运行依赖 | 说明 |
|-------|------|----------|------|
| 行情（`futu-quote`） | 行情交易 | `futu` CLI | 报价、K 线、买卖盘、资金流向、公司资料、自选股等；不下单 |
| 证券交易（`futu-trading`） | 行情交易 | `futu` CLI | 证券账户、资金、持仓、下单、改单、撤单、成交 |
| 模拟交易（`futu-sim-trading`） | 行情交易 | `futu` CLI | 模拟账户的资金、持仓与纸面委托；不影响真实账户 |
| 加密货币（`futu-crypto`） | 行情交易 | `futu` CLI | 加密货币账户、余额、下单、改单、撤单、成交 |
| 资金异动（`futu-capital-anomaly`） | 异动检测 | `futu` CLI | `futu anomaly capital`；资金面异常信号 |
| 衍生品异动（`futu-derivatives-anomaly`） | 异动检测 | `futu` CLI | `futu anomaly derivatives`；期权/牛熊证异动 |
| 技术面异动（`futu-technical-anomaly`） | 异动检测 | `futu` CLI | `futu anomaly technical`；K 线与指标异动 |
| 资讯搜索（`futu-news-search`） | 内容 | `curl` | 搜索富途平台上的新闻、公告、研报 |
| 个股解读（`futu-stock-digest`） | 内容 | `curl` | 围绕标的整理最新事实并给出核心解读 |
| 情绪温度计（`futu-comment-sentiment`） | 内容 | `curl` | 聚合社区情绪、大V观点，输出标准化情绪参考 |

原 **`futuapi` / `install-futu-opend`** 已移除。升级见 [`docs/upgrade-from-opend.md`](docs/upgrade-from-opend.md)；能力缺口与待补 REST API 见 [`docs/migration-gaps-and-rest-api.md`](docs/migration-gaps-and-rest-api.md)。**实时订阅与经纪队列**改用 Open API WebSocket，见 [`docs/websocket-quote-push.md`](docs/websocket-quote-push.md)。

---

## 行情交易 Skills

通过官方 [`futu` 命令行](https://github.com/FutunnOpen/futu-cli) 查行情和下单，不经过 OpenD。macOS / Linux 安装到 `$HOME/.futu/bin/futu`，Windows 安装到 `%LOCALAPPDATA%\FutuCLI\bin\futu.exe`。使用前需要 `futu auth login`。更新命令行本身用 `futu update`。

四个 skill 分工明确：行情查询不下单；证券实盘、模拟盘、加密货币各自独立。

### 行情（`futu-quote`）

| 功能 | 说明 |
|------|------|
| 报价与快照 | 实时报价、市场快照、标的基本信息 |
| K 线 / 逐笔 / 分时 | 最新与历史 K 线、逐笔成交、盘中分时 |
| 买卖盘与排行 | 多档买卖盘、成交量 / 成交额 / 涨跌幅排行 |
| 期权 | 期权链、组合期权报价、期权筛选 |
| 资金与公司 | 资金流向、公司资料、财务、股东、估值 |
| 板块 / 自选 / 日历 | 板块成份、自选股、交易日历、新股列表、选股、窝轮筛选、期货信息 |

**示例提问：**
```
查一下腾讯现在的报价
特斯拉最近 30 天的日 K 线
美股今天涨幅排行
把苹果加到我的自选
```

---

### 证券交易（`futu-trading`）

真实证券账户。下单、改单、撤单会改动资产，执行前需要用户明确确认。

| 功能 | 说明 |
|------|------|
| 账户与资金 | 账户列表、可用资金 |
| 持仓 | 当前持仓 |
| 委托 | 买入、卖出、下单、改单、撤单 |
| 查询 | 当日与历史订单、订单详情、当日与历史成交 |
| 可买可卖 | 指定标的的最大可买 / 可卖数量 |

**示例提问：**
```
我的港股账户还有多少可用资金？
查看我的美股持仓
以 150 港元限价买入腾讯 1000 股
撤销刚才那笔挂单
```

---

### 模拟交易（`futu-sim-trading`）

只操作模拟账户，不改动真实持仓和资金。账户、标的、方向、数量或价格不明确时先查询再下单。

| 功能 | 说明 |
|------|------|
| 模拟账户 | 账户列表、资金、持仓 |
| 纸面委托 | 买入、卖出、下单、改单、撤单 |
| 查询 | 当前委托、历史委托（可翻页）、最大可买 / 可卖数量 |

**示例提问：**
```
列出我的模拟账户
用模拟账户市价买入 1 股苹果
看看模拟账户里腾讯的持仓
撤销模拟账户里的那笔挂单
```

---

### 加密货币（`futu-crypto`）

加密货币账户的余额和真实委托。下单前确认账户、币对、方向和数量。证券账户的资金、持仓和委托走 `futu-trading`。

| 功能 | 说明 |
|------|------|
| 账户与余额 | 加密货币账户列表、余额 |
| 委托 | 下单、买入、卖出、改单、撤单 |
| 查询 | 当前与历史订单、订单详情、成交、最大可买 / 可卖数量 |

**示例提问：**
```
看看我的加密货币账户余额
买入 0.01 个 BTC
这笔加密货币订单成交了没有？
撤销刚才的 BTC 挂单
```

---

## 异动检测 Skills

围绕一只股票自动识别"市场上正在发生什么不寻常的事"。三个 Skill 分别覆盖资金面、衍生品和技术面三个维度；当用户给出宽泛的异动请求（如"英伟达异动"、"腾讯有没有异常"）时，会同时调用三者输出一份综合异动报告。

> 异动检测 Skill 通过 **`futu anomaly`** 子命令拉取数据（与行情/交易共用 `futu` CLI 与 OAuth）。`futu anomaly` 需 CLI/API 联调版本，见 [`docs/migration-gaps-and-rest-api.md`](docs/migration-gaps-and-rest-api.md)。

### 资金异动（`futu-capital-anomaly`）

围绕 `get_financial_unusual` 检测资金面异动信号。

| 维度 | 涵盖内容 |
|------|----------|
| 资金分布 | 大单 / 中单 / 小单结构变化 |
| 买卖经纪商 | 主力席位异动 |
| 资金流向 | 净流入 / 净流出异常 |
| 卖空 | 卖空数量、卖空比例异动 |

**示例提问：**
```
腾讯今天主力资金有没有异动？
看看 NVDA 最近的卖空情况
英伟达异动（自动联动三个异动 Skill）
```

---

### 衍生品异动（`futu-derivatives-anomaly`）

围绕 `get_derivative_unusual` 检测期权与牛熊证异动信号。

| 维度 | 涵盖内容 |
|------|----------|
| 期权大单 | 异常成交、聪明钱押注 |
| 隐含波动率 | IV 异动、波动率溢价 |
| PCR | 期权多空情绪 |
| 牛熊证 | 街货比例 / 价格区间异动 |

**示例提问：**
```
特斯拉期权市场最近有没有大单押注？
看看 0700 的牛熊证街货分布
NVDA 隐含波动率有异动吗？
```

---

### 技术面异动（`futu-technical-anomaly`）

围绕 `get_technical_unusual` 检测 K 线形态和技术指标异动。

| 维度 | 涵盖内容 |
|------|----------|
| K 线形态 | 形态识别、形态突破 |
| 趋势指标 | MACD、MA、BOLL |
| 摆动指标 | RSI、KDJ、CCI、WMSR |
| 强弱指标 | BIAS、ARBR、VR、PSY、OSC |

**示例提问：**
```
腾讯最近有什么技术信号？
英伟达有没有金叉 / 死叉？
苹果的 MACD 出现异动了吗？
```

---

## 内容 Skills

### 资讯搜索

在富途平台上搜索新闻、公告和研报，返回包含标题、发布时间和跳转链接的结构化结果。

| 特性 | 详情 |
|------|------|
| 接口 | `GET /news_search`，经由 `ai-news-search.futunn.com` |
| 认证 | 公开接口 — 无需 API 密钥 |
| 语言 | 简体中文（`zh-CN`）、繁体中文（`zh-HK`）、英文（`en`） |
| 内容类型 | 新闻（`1`）、公告（`2`）、研报（`3`） |
| 排序方式 | 按浏览量（`1`）、按时间（`2`）、按热度（`3`） |
| 单次上限 | 最多返回 50 条结果 |

**示例提问：**
```
搜索一下腾讯最近的重要新闻
帮我找找特斯拉最近的公告
英伟达有什么最新研报？
```

---

### 个股解读

围绕用户选择的标的，持续推送最新事实信息与核心解读。帮助用户在一个入口里快速了解标的发生了什么、为什么值得关注。

**示例提问：**
```
帮我解读一下比亚迪最近发生了什么
阿里巴巴近期有什么值得关注的？
苹果最近的核心变化是什么？
```

---

### 情绪温度计

聚合社区情绪、热议风向、大V观点，输出一个标准化的情绪参考 — 帮助你在做决策前快速感知市场情绪。

**示例提问：**
```
看看社区对小米的情绪怎么样
美团现在的市场情绪如何？
大家怎么看特斯拉？
```

---

## 快速开始

### 前置条件

| 依赖 | 用途 | 检查 |
|------|------|------|
| [富途牛牛](https://www.futunn.com/) 账户 | 交易 & 行情（API 权限需在 App 内开通） | — |
| [Claude Code](https://docs.anthropic.com/en/docs/claude-code) 或其它 MCP 兼容客户端 | 加载并调用 Skills | — |
| Node.js 22.20+ | 提供 `npx skills add` / `npx skills update` | `node -v` |
| `curl` | 内容 Skill 请求公开接口 | `curl --version` |
| `futu` CLI | 行情、交易、异动 Skill | `futu version` |

安装命令写在对应 Skill 里，macOS / Linux 用 `install.sh`，Windows 用 `install.ps1`。

---

### Step 1 — 安装 Skill 文件

通过 `npx skills add` 将本仓库的 Skills 安装到 AI 客户端的 skills 目录。各 skill 的触发条件写在自己的 `description` 里，客户端扫描目录即可发现，不需要单独的发现工具。

```bash
npx skills add -y -g FutunnOpen/futu-agent-hub
```

> `-y` 跳过交互式选择；`-g` 安装到全局（所有项目共享）。去掉 `-y` 可交互选择部分 Skill；去掉 `-g` 仅安装到当前项目。

升级已安装的 skill：

```bash
npx skills update -g
```

更详细的客户端适配（Cursor / JetBrains / Claude Desktop 等）见 [`docs/futu-install.md`](docs/futu-install.md)。

仅使用 **内容 Skills**（资讯搜索 / 个股解读 / 情绪温度计）的话，到此即可结束 — 直接对话：

```
> 搜索一下腾讯最近的重要新闻
> 帮我解读一下比亚迪最近发生了什么
> 看看社区对小米的情绪怎么样
```

如果以前装过旧目录名（`news-search`、`stock-digest`、`comment-sentiment`、`install-opend`、`capital-anomaly`、`derivatives-anomaly`、`technical-anomaly`），`npx skills update` 不会删掉旧目录。先跑一次改名清理，再执行上面的安装命令：

```bash
bash scripts/migrate-renamed-skills.sh
```

---

### Step 2 — 安装并授权 Futu CLI

行情、交易、异动 Skill 需要官方 **`futu` CLI**（OAuth）。**不需要 OpenD**。详见 [`docs/futu-install.md`](docs/futu-install.md)。

```bash
futu auth login
futu auth status --format json
futu check
```

```
> 查一下腾讯的实时报价
> 用模拟账户市价买入 1 股苹果
> 英伟达最近有没有异动？
```

---

## 使用示例

配置完成后，用自然语言与 AI 助手交互：

### 行情查询
```
查一下腾讯的实时报价
帮我看看特斯拉最近 30 天的日 K 线
美团的买卖盘情况怎么样？
苹果的期权链有哪些到期日？
```

### 交易操作
```
以 150 港元限价买入腾讯 1000 股
帮我改一下刚才那笔挂单，价格改成 148
撤销我最近的挂单
查一下今天的成交记录
```

### 账户管理
```
我的港股账户还有多少可用资金？
查看我的美股持仓
目前的购买力是多少？
```

### 资讯 & 洞察
```
搜索一下英伟达最近的重要新闻
帮我解读一下比亚迪最近发生了什么
看看社区对小米的情绪怎么样
腾讯有什么最新研报？
```

### 命令行行情与交易
```
美股今天涨幅排行
用模拟账户市价买入 1 股苹果
看看我的加密货币账户余额
```

---

## 架构

```
┌──────────────────────────────────────────────────────────────────────────┐
│                               AI 助手                                     │
│                 Claude Code / Cursor / Claude Desktop                    │
└──────────────────────────────────┬───────────────────────────────────────┘
                                   │ Skills
                                   ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                            Futu Agent Hub                                 │
│                                                                           │
│  ┌──────────────────────────────┐  ┌────────────┐  ┌───────────┐ │
│  │ 行情交易                      │  │ 异动检测    │  │ 内容       │ │
│  │ futu-quote / futu-trading    │  │ 资金/衍生品 │  │ 资讯搜索   │ │
│  │ futu-sim-trading / futu-crypto│  │ / 技术面    │  │ 个股解读   │ │
│  └──────────────┬───────────────┘  └──────┬─────┘  │ 情绪温度计 │ │
└─────────────────┼─────────────────────────┼────────┴─────┬─────┘ │
                  │                         │              │
                  ▼                         ▼              ▼
         ┌─────────────────┐     ┌──────────────────┐
         │    futu CLI     │     │ 富途内容服务 API  │
         │ OAuth + REST    │     │ ai-news-search   │
         └────────┬────────┘     │ .futunn.com      │
                  │              └──────────────────┘
                  ▼
         ┌─────────────────┐
         │    富途服务器     │
         └─────────────────┘
```

---

## 安全

- **凭证仅通过环境变量传递** — 不会硬编码到配置或源码中
- **交易二次确认** — 下单、改单、撤单等写操作需用户明确确认
- **CLI OAuth** — Token 存于本机，由 CLI 附加 Bearer；勿在对话或仓库中粘贴 token
- **职责拆分** — 行情 Skill 不下单；实盘 / 模拟 / 加密交易分 Skill 路由
- **频率限制** — 遵循 Futu API 内置的频率限制和权限控制
- **内容 Skills** — 调用公开接口，不传输用户凭证；返回数据仅供参考
- **行情交易 Skills** — 通过 `futu` 命令行的 OAuth 登录访问账户；skill 不读取 token 文件

---

## 常见问题

**Q: 所有 Skills 都需要 OpenD 吗？**
A: 不需要。行情、交易、异动均通过 **`futu` CLI**（OAuth）。内容类 Skills 走公开 HTTP。原 `futuapi` / OpenD 已移除，见 [`docs/upgrade-from-opend.md`](docs/upgrade-from-opend.md)。

**Q: 使用 Futu Agent Hub 有额外费用吗？**
A: 没有。通过 Futu API 交易不收取额外费用，仅按正常佣金标准收费。

**Q: 支持哪些编程语言？**
A: Futu API SDK 支持 Python、Java、C#、C++ 和 JavaScript。Agent Hub 的 Skills 在更高层级运行，与编程语言无关 — 安装后直接用自然语言交互即可。

---

## 免责声明

本项目仅供信息参考和学习研究用途。通过 Futu Agent Hub 执行的所有交易操作由用户自行承担风险。AI 生成的分析和建议不构成投资建议。请在充分了解相关风险后谨慎使用交易功能。Futu Agent Hub 不对任何投资损失承担责任。

---

## License

[MIT](LICENSE)

---

<p align="center">
  由 <a href="https://www.futunn.com/">富途</a> 构建 · 基于 <a href="https://openapi.futunn.com/">Futu API</a>
</p>
