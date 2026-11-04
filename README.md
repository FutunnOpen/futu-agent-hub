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
  <a href="#快速开始">快速开始</a> · <a href="#skills-概览">Skills 概览</a> · <a href="#行情与交易-skills">行情与交易 Skills</a> · <a href="#技术分析-skills">技术分析 Skills</a> · <a href="#内容分析-skills">内容分析 Skills</a> · <a href="#量化策略">量化策略</a> · <a href="#使用示例">使用示例</a>
</p>



---

## 什么是 Futu Agent Hub？

Futu Agent Hub 是 **富途** 官方推出的 AI Agent 技能中心，把官方 `futu` CLI 和金融内容服务封装为标准化的 Skills。行情与交易通过 CLI 接入，**无需安装或运行 OpenD**。让 AI 助手能够查询行情、执行交易、识别异动、检索资讯、感知市场情绪 — 全部通过自然语言完成。

支持 **Claude Code**、**Cursor**、**Claude Desktop**、**VS Code** 等 MCP 兼容的 AI 工具接入。

---

## Skills 概览

Futu Agent Hub 提供 **11 个 Skills**，分为四类：行情与交易、内容分析、技术分析、量化策略。量化策略目前是仓库内的网格策略 `futu-grid-strategy`。

| Skill | 类别 | 运行依赖 | 说明 |
|-------|------|----------|------|
| 行情（`futu-quote`） | 行情与交易 | `futu` CLI | 股票、期权、期货及加密货币行情；不下单 |
| 股票实盘交易（`futu-trading`） | 行情与交易 | `futu` CLI | 用户选定的实盘账户、资金、持仓、委托与成交 |
| 股票模拟交易（`futu-sim-trading`） | 行情与交易 | `futu` CLI | 用户选定的模拟账户；调用 `futu sim` |
| 加密货币交易（`futu-crypto`） | 行情与交易 | `futu` CLI | 加密货币账户、余额、委托与成交；行情走 `futu-quote` |
| 技术面异动（`futu-unusual-technical-signal-alerts`） | 技术分析 | `futu` CLI | K 线与指标异动 |
| 资金面异动（`futu-unusual-capital-flows`） | 技术分析 | `futu` CLI | 资金分布、流向、经纪商与卖空 |
| 衍生品异动（`futu-unusual-derivatives-activity`） | 技术分析 | `futu` CLI | 期权与牛熊证异动 |
| 资讯搜索（`futu-news-search`） | 内容分析 | `curl` | 新闻、公告、研报 |
| 个股解读（`futu-stock-digest`） | 内容分析 | `curl` | 基于资讯时间与原文的标的解读 |
| 情绪温度计（`futu-comment-sentiment`） | 内容分析 | `curl` | 社区情绪，带统计窗口与样本量 |
| 网格策略（`futu-grid-strategy`） | 量化策略 | OpenAPI | 单标的基准价网格；默认在模拟账户验收 |

原 **`futuapi` / `install-futu-opend`** 已移除。升级见 [`docs/upgrade-from-opend.md`](docs/upgrade-from-opend.md)；能力缺口见 [`docs/migration-gaps-and-rest-api.md`](docs/migration-gaps-and-rest-api.md)。Skill 默认用 CLI 拉取 REST。持续推送和经纪队列没有 `futu subscribe` 命令，调用方自行连接 Open API WebSocket，见 [`docs/websocket-quote-push.md`](docs/websocket-quote-push.md)。

---

## 行情与交易 Skills

通过官方 [`futu` 命令行](https://github.com/FutunnOpen/futu-cli) 查行情和下单，不经过 OpenD。macOS / Linux 安装到 `$HOME/.futu/bin/futu`，Windows 安装到 `%LOCALAPPDATA%\FutuCLI\bin\futu.exe`。使用前需要 `futu auth login`。更新命令行本身用 `futu update`。CLI 只安装一次，各 Skill 可以分开安装。

四个 Skill 分工明确：行情覆盖各交易品种，包括加密货币行情，并且不下单。股票实盘、股票模拟、加密货币交易各自使用用户选定的账户，不互相串命令。

### 行情（`futu-quote`）

报价结果包含标的、价格、涨跌、币种、数据时间和来源。延迟、权限不足、无数据和请求失败分开提示。自选股的添加和删除是写操作。

| 功能 | 说明 |
|------|------|
| 报价与快照 | 股票、期权、期货及加密货币的实时报价、市场快照、标的基本信息 |
| K 线 / 逐笔 / 分时 | 最新与历史 K 线、逐笔成交、盘中分时；历史 K 线处理日期、时区、周期、复权和分页 |
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

### 股票实盘交易（`futu-trading`）

只使用用户明确选定的股票实盘账户。第一次先列出可用实盘账户让用户选择，之后沿用该账户。账户或交易环境不清楚时先确认，不自动切换到模拟盘或加密货币账户。

下单、改单、撤单会改动资产。执行前确认账户、环境、标的、方向、数量、订单类型和价格。Agent 不代替用户确认。返回订单编号和实际状态；提交成功不等于成交。超时或状态未知时先查询，避免重复下单。

| 功能 | 说明 |
|------|------|
| 账户与资金 | 实盘账户列表、可用资金 |
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

### 股票模拟交易（`futu-sim-trading`）

只操作股票模拟账户，调用 `futu sim`，并显式传入用户选定的模拟账户。不自动使用第一个模拟账户，不调用实盘或加密货币交易命令。委托前的确认规则与股票实盘交易相同。模拟结果使用虚拟资金，可能与实盘不同。

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

### 加密货币交易（`futu-crypto`）

加密货币账户的余额和真实委托，调用 `futu crypto`。币对使用 CLI 格式，例如 `BTCUSD`。只使用用户选定的加密货币账户。行情查询走 `futu-quote`。股票账户的资金、持仓和委托走 `futu-trading`。下单前确认账户、币对、方向、数量或金额、价格。

| 功能 | 说明 |
|------|------|
| 账户与余额 | 加密货币账户列表、余额 |
| 委托 | 下单、买入、卖出、改单、撤单 |
| 查询 | 当前与历史订单、订单详情、成交、最大可买 / 可卖数量 |

**示例提问：**
```
看看我选定的加密货币账户余额
查询 BTCUSD 的可买数量
在已选账户提交一笔 BTCUSD 限价委托，确认后再执行
这笔加密货币订单现在是什么状态？
```

---

## 技术分析 Skills

围绕一只股票识别不寻常的变化。三个 Skill 的顺序是 **技术面异动**、**资金面异动**、**衍生品异动**。用户只说「英伟达异动」或「腾讯有没有异常」时，三个一起调用。

结果要区分无异常、无数据、不适用、权限不足和请求失败。信号来自 `futu unusual`（`anomaly` 为兼容别名），不用普通行情指标代替异动接口。子命令是 `technical-signals`、`capital-flows`、`derivatives-activity`。

### 技术面异动 · Technical Signal Alerts（`futu-unusual-technical-signal-alerts`）

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

### 资金面异动 · Unusual Capital Flows（`futu-unusual-capital-flows`）

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

### 衍生品异动 · Unusual Derivatives Activity（`futu-unusual-derivatives-activity`）

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

## 内容分析 Skills

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

围绕用户选择的标的，整理资讯摘要、方向判断和来源。输出写明结论依据的资讯时间，并给出原文链接。静态示例标明「示例」，不写成今天的实时结果。

**示例提问：**
```
帮我解读一下比亚迪最近发生了什么
阿里巴巴近期有什么值得关注的？
苹果最近的核心变化是什么？
```

---

### 情绪温度计

聚合社区讨论和大 V 观点，输出多空比例和代表观点，并写明统计窗口、样本量和来源。样本不足时单独说明。内容分析不要求 CLI 行情或交易授权。

**示例提问：**
```
看看社区对小米的情绪怎么样
美团现在的市场情绪如何？
大家怎么看特斯拉？
```

---

## 量化策略

仓库内的量化策略是网格策略 `futu-grid-strategy`。它指导 Agent 按 OpenAPI 文档编写单标的基准价网格程序：先做参数检查，再写可重启的限价单对账循环。

| 项 | 说明 |
|----|------|
| 范围 | 一只股票或 ETF：`HK.00700`、`US.AAPL`、`SH.600519`、`SZ.000001` |
| 订单 | 按百分比间距的当日限价单；跨日通过对账循环重新挂单 |
| 环境 | 默认连接模拟账户。用户当次明确说使用实盘后，才切到实盘页面 |
| 不含 | 期权、期货、加密货币、多标的、市价单 |

接口字段以 [OpenAPI llms.md](https://open.futunn.com/zh-cn/llm/llms.md) 为准，调用 `webapi.futunn.com`。这个 Skill 不复制请求体，也不读取 token。

```bash
npx skills add -y -g FutunnOpen/futu-agent-hub --skill futu-grid-strategy
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

按需安装当前 Skill。CLI 只安装一次，已安装的 CLI 不重复安装。安装 Skill 不等于已经拥有账户或行情权限。

```bash
npx skills add -y -g FutunnOpen/futu-agent-hub --skill futu-quote
```

> `-y` 跳过交互式选择；`-g` 安装到全局（所有项目共享）。把 `futu-quote` 换成上表中的 slug 即可安装其他 Skill。去掉 `--skill` 会安装仓库内全部 Skill。去掉 `-g` 仅安装到当前项目。

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

如果以前装过旧目录名（含 `futu-capital-anomaly` 等已废弃 slug，或 `news-search`、`capital-anomaly` 等短名），`npx skills update` 不会删掉旧目录。先跑一次改名清理，再执行上面的安装命令：

```bash
bash scripts/migrate-renamed-skills.sh
```

---

### Step 2 — 安装并授权 Futu CLI

行情、交易、异动 Skill 需要官方 **`futu` CLI**（OAuth）。**不需要 OpenD**。详见 [`docs/futu-install.md`](docs/futu-install.md)。

```bash
futu version
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
│  │ 行情与交易                    │  │ 技术分析    │  │ 内容分析   │ │
│  │ futu-quote / futu-trading    │  │ 技术/资金   │  │ 资讯搜索   │ │
│  │ futu-sim-trading / futu-crypto│  │ / 衍生品    │  │ 个股解读   │ │
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

- **不在仓库或对话中保存凭证** — CLI 的 OAuth token 存在本机，由 CLI 附加 Bearer；网格策略按 OpenAPI 文档调用，不把 token 写进代码
- **交易二次确认** — 下单、改单、撤单由用户确认账户、标的、方向、数量和价格；Agent 不代为确认
- **提交不等于成交** — 返回订单编号和实际状态；状态未知时先查询
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
