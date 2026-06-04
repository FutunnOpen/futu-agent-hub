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
  <a href="#快速开始">快速开始</a> · <a href="#skills-概览">Skills 概览</a> · <a href="#futu-api-skill">Futu API Skill</a> · <a href="#异动检测-skills">异动检测 Skills</a> · <a href="#内容-skills">内容 Skills</a> · <a href="#使用示例">使用示例</a>
</p>



---

## 什么是 Futu Agent Hub？

Futu Agent Hub 是 **富途** 官方推出的 AI Agent 技能中心，将 Futu API 的完整能力和金融内容服务封装为标准化的 Skills。让 AI 助手能够直接查询实时行情、执行交易、检索金融资讯、感知市场情绪 — 全部通过自然语言完成。

支持 **Claude Code**、**Cursor**、**Claude Desktop**、**VS Code** 等 MCP 兼容的 AI 工具接入。

---

## Skills 概览

Futu Agent Hub 提供 **7 个开箱即用的 Skills**，分为三大类：

| Skill | 类别 | 是否需要 OpenD | 说明 |
|-------|------|----------------|------|
| Futu API（`futuapi`） | 交易 & 行情 | ✅ | 封装 Futu API 全部能力 — 实时报价、K 线、下单、持仓、账户管理等 |
| 资金异动（`futu-capital-anomaly`） | 异动检测 | ✅ | 资金流向、买卖经纪商、卖空异动等资金面异常信号 |
| 衍生品异动（`futu-derivatives-anomaly`） | 异动检测 | ✅ | 期权大单、隐含波动率、牛熊证街货、PCR 等衍生品异常信号 |
| 技术面异动（`futu-technical-anomaly`） | 异动检测 | ✅ | K 线形态及 MACD / RSI / KDJ / BOLL 等技术指标异常信号 |
| 资讯搜索（`futu-news-search`） | 内容 | ❌ | 搜索富途平台上的新闻、公告、研报 |
| 个股解读（`futu-stock-digest`） | 内容 | ❌ | 围绕标的推送最新事实信息与核心解读 |
| 情绪温度计（`futu-comment-sentiment`） | 内容 | ❌ | 聚合社区情绪、大V观点，输出标准化情绪参考 |

> 此外随 Futu API Skill 附带一个安装助手 `install-futu-opend`，用于一键安装 / 升级本地 OpenD 网关与 Python SDK。

---

## Futu API Skill

Futu API Skill 将 [Futu API](https://openapi.futunn.com/futu-api-doc/) 的完整能力封装为 AI 可调用的接口。一个 Skill，全面覆盖。

### 行情数据

| 功能 | 说明 |
|------|------|
| 实时报价 | 获取股票、ETF、期权、期货、指数的实时价格 |
| K 线数据 | 查询任意粒度的历史和实时 K 线 |
| 买卖盘 | 获取多档买卖盘口深度数据 |
| 逐笔成交 | 查询逐笔成交明细 |
| 分时数据 | 获取盘中分时走势 |
| 快照 | 批量获取市场快照 |
| 板块行情 | 查询板块列表及板块内成份股 |
| 期权链 | 获取期权到期日、行权价及完整期权链 |

### 交易执行

| 功能 | 说明 |
|------|------|
| 下单 | 支持市价单 / 限价单 / 条件单等多种订单类型 |
| 改单 | 修改未成交订单 |
| 撤单 | 撤销挂单 |
| 查询订单 | 查询当日及历史委托记录 |
| 查询成交 | 查询当日及历史成交明细 |

### 账户 & 资产

| 功能 | 说明 |
|------|------|
| 账户列表 | 查询可用交易账户 |
| 资金查询 | 查询可用资金、购买力、保证金状态 |
| 持仓查询 | 查询当前持仓及盈亏情况 |

### 支持市场

| 市场 | 覆盖品种 |
|------|----------|
| 🇭🇰 港股 | 股票、ETF、窝轮、牛熊证、期权、期货、指数 |
| 🇺🇸 美股 | NYSE / AMEX / NASDAQ 股票、ETF、期权、期货 |
| 🇨🇳 A 股 | 股票、ETF、指数 |
| 🇸🇬 新加坡 | 股票 |
| 🇯🇵 日本 | 股票 |

---

## 异动检测 Skills

围绕一只股票自动识别"市场上正在发生什么不寻常的事"。三个 Skill 分别覆盖资金面、衍生品和技术面三个维度；当用户给出宽泛的异动请求（如"英伟达异动"、"腾讯有没有异常"）时，会同时调用三者输出一份综合异动报告。

> 异动检测 Skill 通过 OpenD 调用 Futu API 拉取数据，因此**与 Futu API Skill 共用同一套环境**（OpenD + Python SDK）。

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
| `python3` | 运行异动检测脚本与 `futu-skills` CLI | `python3 --version` |
| `curl` | 下载安装器 | `curl --version` |
| Node.js 18+ | 提供 `npx skills add` | `node -v` |

---

### Step 1 — 安装 `futu-skills` CLI

`futu-skills` 用于管理 Skill 版本与自升级，所有用法（含纯内容 Skill）都建议先装 CLI。

```bash
curl -fsSL https://raw.githubusercontent.com/FutunnOpen/futu-agent-hub/main/futu-install.sh | bash
```

验证：

```bash
futu-skills --version
futu-skills check
```

---

### Step 2 — 安装 Skill 文件

通过 `npx skills add` 一键将本仓库的 Skills 安装到 AI 客户端的 skills 目录：

```bash
npx skills add -y -g FutunnOpen/futu-agent-hub
```

> `-y` 跳过交互式选择；`-g` 安装到全局（所有项目共享）。去掉 `-y` 可交互选择部分 Skill；去掉 `-g` 仅安装到当前项目。

更详细的客户端适配（Cursor / JetBrains / Claude Desktop 等）见 [`docs/futu-install.md`](docs/futu-install.md)。

仅使用 **内容 Skills**（资讯搜索 / 个股解读 / 情绪温度计）的话，到此即可结束 — 直接对话：

```
> 搜索一下腾讯最近的重要新闻
> 帮我解读一下比亚迪最近发生了什么
> 看看社区对小米的情绪怎么样
```

---

### Step 3 — 安装 OpenD（仅 Futu API / 异动检测 Skill 需要）

`futuapi` 与三个异动检测 Skill 通过本地 **OpenD** 网关连接富途服务器；纯内容 Skill 可跳过本步。

完成 Step 2 后，在 AI 客户端中调用 `/install-futu-opend`，Agent 会自动完成：

1. 下载并安装 OpenD（支持 **Windows / macOS / CentOS / Ubuntu**）
2. 安装 / 升级 Python SDK（`futu-api`）
3. 引导登录与启动

> **注意：** 使用 Futu API / 异动检测 Skill 需要开通 API 权限。请在 App 内完成问卷评估和协议确认 — 参考[权限说明](https://openapi.futunn.com/futu-api-doc/intro/authority.html)。

完成后确认以下 Skill 可用：

- `install-futu-opend` — OpenD 安装助手
- `futuapi` — 行情交易助手
- `futu-capital-anomaly` / `futu-derivatives-anomaly` / `futu-technical-anomaly` — 异动检测

```
> 查一下腾讯的实时报价
> 以 150 港元限价买入腾讯 1000 股
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

---

## 架构

```
┌──────────────────────────────────────────────────────┐
│                    AI 助手                            │
│      (Claude Code / Cursor / Claude Desktop)         │
└──────────────────────┬───────────────────────────────┘
                       │ Skills 协议
                       ▼
┌──────────────────────────────────────────────────────┐
│                 Futu Agent Hub                       │
│                                                      │
│  ┌──────────┐  ┌─────────────┐  ┌────────────────┐   │
│  │ Futu API │  │ 异动检测     │  │   内容 Skills  │   │
│  │  Skill   │  │ Skills       │  │                │   │
│  │          │  │              │  │ ┌────────────┐ │   │
│  │ 交易执行 │  │ 资金异动     │  │ │ 资讯搜索   │ │   │
│  │ 行情查询 │  │ 衍生品异动   │  │ ├────────────┤ │   │
│  │ 账户管理 │  │ 技术面异动   │  │ │ 个股解读   │ │   │
│  │ 期权数据 │  │              │  │ ├────────────┤ │   │
│  │   ...    │  │              │  │ │ 情绪温度计 │ │   │
│  └────┬─────┘  └──────┬───────┘  │ └─────┬──────┘ │   │
│       │               │           │       │        │   │
└───────┼───────────────┼───────────┴───────┼────────┘   │
        │               │                   │
        └───────┬───────┘                   │
                ▼                           ▼
       ┌────────────────┐         ┌──────────────────────┐
       │     OpenD      │         │   富途内容服务 API   │
       │    (网关)      │         │   (公开 HTTP)        │
       │                │         │                      │
       │  本地 TCP 连接 │         │  ai-news-search      │
       │                │         │  .futunn.com         │
       └────────┬───────┘         └──────────────────────┘
                │
                ▼
       ┌────────────────┐
       │   富途服务器   │
       │  (港股/美股/   │
       │  A股/新/日)    │
       └────────────────┘
```

---

## 安全

- **凭证仅通过环境变量传递** — 不会硬编码到配置或源码中
- **交易二次确认** — 下单、改单、撤单等写操作需用户明确确认
- **本地优先** — Futu API 流量通过本地 OpenD 网关加密传输
- **只读模式** — 不配置交易密码即可限制为仅查询行情
- **频率限制** — 遵循 Futu API 内置的频率限制和权限控制
- **内容 Skills** — 调用公开接口，不传输用户凭证；返回数据仅供参考

---

## 常见问题

**Q: 所有 Skills 都需要 OpenD 吗？**
A: 不需要。**Futu API Skill** 与**三个异动检测 Skill**（资金 / 衍生品 / 技术面异动）依赖 OpenD；**内容类 Skills**（资讯搜索、个股解读、情绪温度计）直接调用公开 HTTP 接口，无需 OpenD。

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
