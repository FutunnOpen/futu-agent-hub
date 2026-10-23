# 从 OpenD / futuapi 升级到 CLI Skills

若你此前安装过 **`futuapi`** 或 **`install-futu-opend`**，请按本指引迁移。新版 **无需安装或运行 OpenD**，也 **不需要** Python SDK `futu-api`。

## 1. 清理旧 Skill 目录

```bash
bash scripts/migrate-renamed-skills.sh
```

脚本会删除全局目录中的 `futuapi`、`install-futu-opend` 及历史短名 Skill。

## 2. 重新安装本仓库 Skills

```bash
npx skills add -y -g FutunnOpen/futu-agent-hub
npx skills update -g
```

## 3. 安装官方 CLI（只需一次）

行情与交易、异动检测均依赖 **`futu` CLI**。安装方式见 [futu-install.md](./futu-install.md) 或各 quote/trade Skill 内的安装说明。

```bash
futu version
futu auth login
futu auth status --format json
futu check
```

## 4. 能力映射：原 futuapi → 现 Skill

| 原用途 | 现 Skill |
|--------|----------|
| 查行情、K 线、板块、期权链等 | `futu-quote` |
| 实盘下单、持仓、订单 | `futu-trading` |
| 模拟盘 | `futu-sim-trading` |
| 加密货币交易 | `futu-crypto` |
| 技术面 / 资金 / 衍生品异动 | `futu-technical-anomaly`、`futu-capital-anomaly`、`futu-derivatives-anomaly`（需 CLI `futu anomaly`，见 [migration-gaps-and-rest-api.md](./migration-gaps-and-rest-api.md)） |
| 综合 OpenAPI 脚本包 | **已移除** — 按上表拆分到对应 Skill |

## 5. 不再支持的能力

实时订阅推送、部分 futuapi 边角脚本等 — 详见 [migration-gaps-and-rest-api.md](./migration-gaps-and-rest-api.md)。
