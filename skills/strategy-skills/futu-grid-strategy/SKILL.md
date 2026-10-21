---
name: futu-grid-strategy
description: >-
  Guides an AI to implement a single-symbol base-price grid program on Futu OpenAPI:
  validate six parameter checks first, then write a restart-safe limit-order
  reconciliation loop, and accept it on a paper account.
  Use when the user wants a grid strategy, grid program, quantitative grid, or grid
  trading bot, or says 网格策略, 网格程序, 量化网格, 网格交易机器人, 实现网格, or 帮我写一个网格.
  Request fields follow the OpenAPI llms.md. This skill does not repeat request bodies.
  Paper account by default.
---

# Futu grid strategy implementation

The user can already place, modify, and cancel orders and query quotes with the Futu OpenAPI `llms.md`. This skill adds how those actions become one grid program: whether the parameters can run, how level prices are calculated, how the base price and orders line up after a restart, and when the program must stop.

Open the user's OpenAPI `llms.md` for paths, field names, and enum values (public index: <https://open.futunn.com/zh-cn/llm/llms.md>), open the matching page, then send the request. This file does not copy request bodies. Calls go to the `webapi.futunn.com` product line.

## 1. First version scope

- One symbol, a stock or ETF, with a market prefix: `HK.00700`, `US.AAPL`, `SH.600519`, `SZ.000001`
- Base-price grid, percentage spacing (use a price difference only when the user explicitly asks)
- Limit orders, valid for the day. The grid re-places orders across days through the reconciliation loop
- Markets: Hong Kong, US, Shanghai, Shenzhen
- Trading environment: paper trading. Switch to the live-trading pages only after the user explicitly says so in the current conversation (for example 「使用实盘」). Keep the second confirmation and trading password required by the docs. Do not write passwords, AppKeys, private keys, or tokens into the repository, and do not print them in logs

Out of scope: range grids, adding size after a break below the lower bound, options, futures, crypto, multiple symbols, market orders, and quoting profit while skipping fees.

## 2. Implementation order

Follow this order. Stop at the first step that fails.

1. Collect the parameters. Read shares per lot from `lot_size` in the stock basic-info endpoint. If it cannot be found, ask the user. Do not guess 100.
2. Run the six checks in section 5. On any FAIL: give the correction and the formula. Do not write trading code. Do not place orders.
3. On WARN only: show the parameter card and the warnings first. Write code only after the user accepts them.
4. Write the program. Use section 6 for structure and section 7 for behavior. Match the language of the user's existing project. If there is no project, ask once. If the user does not answer, use Go.
5. Run the acceptance checks in section 9. If a test fails, do not tell the user the program is ready.
6. When the user asks to run it, connect only to the paper account.

## 3. Parameters

| Field | Meaning | When omitted |
| --- | --- | --- |
| Symbol | With market prefix | Must ask. Do not pick a symbol for the user |
| Initial base price | Grid center `P0` | Use the latest price from the quote snapshot. After it is written to the state file, restarts only read it |
| Move type | Percentage or price difference | Percentage |
| Buy-on-dip, sell-on-rise | A user-stated 1.5% is `0.015` in the formula | When at least 120 daily bars exist, use average daily range × 0.67; otherwise ask |
| Levels per side `N` | `N` levels above and below, range 3–50 | 5, and it must still pass the checks |
| Lots per level | Positive integer | 1 lot, and say so in the output |
| Budget | Optional | If absent, only report the capital required and mark G3 as "budget not checked" |
| Drawdown stop | Ratio versus the grid position cost, optional | Ask once. If the user declines, leave it unset and say so in the output |

Percentage: `P_down[i] = P0 / (1+a)^i`, `P_up[i] = P0 × (1+b)^i`. Price difference: `P_down[i] = P0 − i×d`, `P_up[i] = P0 + i×d`. `a`, `b`, and `d` are decimals. Round a buy price down to the tick and a sell price up to the tick. After rounding, the gap must be at least the gap the user asked for.

Shares per level = lots per level × `lot_size`. Amount per level `A = shares per level × P0`. Round-trip width `w = min(a, b)`. Compute fees on `w`, so an asymmetric grid does not understate the cost.

## 4. Minimum price increment

Basic info has no tick field. Use the table below for order prices and G1, and state in the output that this is the common cash-equity tick table. Check the exchange's current tick schedule before going live.

Hong Kong, by the price band the quote falls in:

| Price upper bound (exclusive) | tick |
| --- | --- |
| 0.25 | 0.001 |
| 0.50 | 0.005 |
| 10 | 0.01 |
| 20 | 0.02 |
| 100 | 0.05 |
| 200 | 0.10 |
| 500 | 0.20 |
| 1000 | 0.50 |
| 2000 | 1 |
| 5000 | 2 |
| 9995 | 5 |
| above | 5 |

US: use `0.0001` when the price is below 1, otherwise `0.01`. Shanghai and Shenzhen: `0.01`. If the market is not in this table, stop and explain why.

## 5. Six checks

The fee rates are order-of-magnitude figures. Say in the output "check the broker's current fee schedule before going live". Do not use them for reconciliation.

| Market | One-side rate | Fixed fee per order | Intraday round trip |
| --- | --- | --- | --- |
| Hong Kong | 0.14% | 15 HKD | Allowed |
| US | 0.005% | 1 USD | Allowed |
| Shanghai / Shenzhen | 0.026%, plus 0.05% stamp duty on sells | 5 CNY | Not allowed. Sell quantity is limited by the sellable quantity |

G1 tick share = `tick / (P0 × w)`. ≤ 10% PASS, 10%–20% WARN, > 20% FAIL. On FAIL, raise the grid width above `tick / (P0 × 0.1)`, or change the symbol.

G2 fees as a share of gross profit = `(2 × one-side rate × A + stamp-duty rate × A + 2 × fixed fee) / (A × w)`. ≤ 25% PASS, 25%–40% WARN, > 40% FAIL.

G3 capital required = the sum of `price × shares per level` across every buy level × 1.15. PASS when a budget exists and the requirement is ≤ the budget. Otherwise FAIL and write the shortfall. With no budget, only report the requirement and mark the result "not checked".

G4 uses the P10 and P90 of the closing prices over the last 120 trading days. The lower bound is the lowest buy level. The upper bound is the highest sell level. PASS when both sides are covered, WARN when only one side is covered, FAIL when neither is covered. If there are fewer than 120 daily bars, mark "not checked". Also report `N × w`: when it is below 10%, state that a one-sided breakout within half a year is likely.

G5 = `w / average daily range`. Average daily range is the median of `(high − low) / close` over the last 120 trading days. 0.5–0.7 PASS; 0.4–0.5 or 0.7–0.8 WARN; < 0.4 or ≥ 0.8 FAIL. If there are not 120 daily bars, mark "not checked".

G6: FAIL when `N < 3` or `N > 50`; WARN when `N > 10`; otherwise PASS.

Use daily bars from the historical K-line endpoint, and keep the adjustment basis consistent. When the data is insufficient, G4 and G5 may be skipped. The result must say "not checked". Do not fill in an estimate and mark it PASS.

Math self-check (approximate Hong Kong fees, `lot_size = 100`): `HK.00700`, base price 410.40, 1% spacing, 5 levels, 1 lot. tick = 0.20. G1 = 4.9% PASS, G2 = 35.3% WARN, notional of the five buy levels is about 199,000 HKD, capital required is about 229,000 HKD. The pure functions in the program must match this set of numbers before the trading loop is written.

## 6. Split the program into four parts

- **Grid**: level prices, the six checks, and capital required. No network access.
- **State file**: local JSON. Fields must include at least the symbol, move type, down spacing, up spacing, level count, lot count, shares per lot, base price, whether it is stopped, the stop reason, the share quantity already in the account at startup, whether that quantity has been recorded, and the save time.
- **Broker adapter**: wrap only the `llms.md` pages for account, funds, positions, place order, cancel order, open orders, order detail, quote snapshot, quote push, and trade push. Fields follow those pages.
- **Loop**: reconcile on startup, then wake on pushes and a timer and reconcile again.

Base-price rules:

- On the first start with a given parameter set, write the base price to the state file.
- On a later start, if the symbol, move type, spacing, level count, and lot count are unchanged, keep using the base price in the file.
- If the parameters changed, stop placing orders. Tell the user the old base price does not match the new parameters, and wait for the user to decide. Do not quietly recompute from the latest price.
- If the state is stopped and the user has not explicitly said to continue, only query orders. Do not place new ones.

Order marks use short ASCII: `g1b`, `g1s`. The number is the level, `b` is buy, `s` is sell. Before placing an order, check the `remark` length limit on the order page. Cancel only open orders for the same symbol whose mark belongs to this strategy. Leave other orders in the account alone.

Read positions at startup. Record the shares already held then in the state file. Do not place sell orders for them, and do not use their cost for the drawdown check. Grid position = current position − this starting quantity, floored at 0.

## 7. Reconciliation loop

Quote pushes and trade pushes only wake the loop. After a disconnect, a duplicate push, or a partial fill, the next order query and position query decide which orders to place. Also reconcile on a timer of about 20 seconds. On a rate-limit error, back off and do not place replacement orders in that round.

If the price is below the lowest buy level or above the highest sell level: record the stop reason, cancel this strategy's open orders, leave the position in place, and save the state. Do not add levels downward or upward.

When the user set a drawdown stop: estimate the grid position cost from the buy-level prices of the shares still held. Do not use the account's blended cost. Stop and keep the position when `(cost − latest price) / cost` reaches the threshold.

Each level may change an order at most once per reconciliation. If that side already has one identical open order (same side, price, quantity, and mark), keep it. If the same level and side has two, cancel the extra one and decide whether to replace it on the next round.

For level `i` (`i` from 1 to `N`):

- The buy price is the `i`-th lower level. The sell price is the `i`-th upper level. The quantity is the shares per level.
- Net position at this level = filled buy shares at this level − filled sell shares. Partial fills use the filled quantity. A cancelled remainder is not a position.
- Net position > 0: cancel this level's buy order and place a sell order for the sellable quantity. Round the sell quantity down to a whole lot. Do not exceed the shares per level or the sellable quantity. If the sellable quantity is not enough, wait for the next round.
- When the net position returns to 0 and this level has had a sell fill: do not place a buy order again until the latest price rises through that level's sell price.
- When the net position is 0 and a new buy is allowed: the buy price must be below the latest price. If it is not, cancel a resting buy and do not place a new one.
- Check the sellable quantity before selling. Shares bought the same day in Shanghai or Shenzhen cannot be treated as sellable yet.

On process exit, cancel this strategy's open orders, keep the position, and write the state file.

## 8. Show this before handing it to the user

Before writing code or placing an order, show the four blocks below. If any check is FAIL, do not write "start implementing" in the first block.

1. **Parameter card**: symbol, base price, move type, both spacings, level count, shares per lot, lots per level, budget, drawdown stop, paper or live. Print every defaulted value.
2. **Check table**: the G1–G6 numbers and PASS / WARN / FAIL / not checked.
3. **Calculation basis**: one formula line for every number that did not come from the user's own words.
4. **Risk**: how this parameter set is most likely to lose money (at a drop to the lower bound, the price gap of each buy level versus the lower bound, times the shares per level); which items were not checked; whether the next step is to change the parameters, run the tests first, or connect to the paper account.

This skill generates and constrains a program. It does not forecast returns, and it does not replace the user's trading decision.

## 9. Acceptance

Make these checks into tests that do not access the network. Only after all of them pass may you say the program is written.

- The `HK.00700` self-check in section 5: G1, G2, and capital required match.
- Buy prices round down and sell prices round up. After rounding, the price is farther from the base price than the raw price.
- A second read of the state file with the same parameters leaves the base price unchanged.
- A parameter change does not generate a new base price.
- Two open orders with the same mark on the same level and side leave only one after reconciliation.
- After a level's buy order is fully filled, the next round places a sell at that level's sell price. It does not move the order to somewhere near the fill price.
- After the latest price breaks below the lowest buy level, the state is stopped and no new buy order is produced.
- Shares already held at startup do not generate a sell order.
- When the Shanghai or Shenzhen sellable quantity is 0, no sell order is placed.

When the user explicitly asks to run it, use the paper account's account, funds, positions, and orders pages. A live order happens only after the user has said to use the live account (for example 「使用实盘」).

## 10. Refuse outright

When the request is one of these, explain why and stop:

- Level count below 3 or above 50
- A check is still FAIL, but the user asks to place the orders anyway
- Increase the lot size or add levels downward after a break below the lower bound
- Design the grid as same-day buy and same-day sell for Shanghai or Shenzhen
- Skip the fee calculation, or subtract one estimated fee from total profit only at the end
- Remove the out-of-range stop because one look-back showed the stop missed some profit
- Cancel or modify an order that does not carry this strategy's mark
- Ask for, echo, or write a trading password or key in the conversation
