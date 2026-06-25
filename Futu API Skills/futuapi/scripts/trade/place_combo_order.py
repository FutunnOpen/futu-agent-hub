#!/usr/bin/env python3
"""
组合下单

功能：提交组合期权/组合策略订单
用法：python place_combo_order.py '[{"code":"US.AAPL260529C302500","trd_side":"BUY","qty_ratio":1},{"code":"US.AAPL","trd_side":"SELL","qty_ratio":100}]' --price 9.9 --quantity 1

接口限制：
- 同一账户 ID 每 30 秒最多请求 15 次
- 连续两次下单间隔不可小于 0.02 秒
- 与 place_order 共用一个限频

参数说明：
- combo_leg_list: 组合腿 JSON 列表，元素字段：code/trd_side/qty_ratio/position_id(可选)
- price: 订单价格（市价/竞价单也需要传）
- qty: 组合数量；每条腿实际数量 = qty * qty_ratio
- order_type: 订单类型，默认 NORMAL
- time_in_force: 有效期限，默认 DAY；当 GTD 时可配合 expire_time
"""
import argparse
import json
import sys
import os as _os

sys.path.insert(0, _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..")))
from common import (
    create_trade_context,
    parse_trd_env,
    parse_security_firm,
    get_default_acc_id,
    get_default_trd_env,
    infer_market_from_code,
    check_ret,
    safe_close,
    format_enum,
    safe_get,
    safe_float,
    parse_trd_side,
    is_empty,
)


def _audit_log(entry):
    import datetime
    try:
        log_path = _os.path.join(_os.path.expanduser("~"), ".futu_trade_audit.jsonl")
        entry["timestamp"] = datetime.datetime.now().isoformat()
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass


def _resolve_order_type(name):
    from futu import OrderType
    key = str(name).upper()
    val = getattr(OrderType, key, None)
    if val is None:
        raise ValueError(f"不支持的 order_type: {name}")
    return val


def _resolve_time_in_force(name):
    from futu import TimeInForce
    key = str(name).upper()
    val = getattr(TimeInForce, key, None)
    if val is None:
        raise ValueError(f"不支持的 time_in_force: {name}")
    return val


def _parse_combo_legs(legs_json):
    from futu import ComboLeg

    try:
        items = json.loads(legs_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"组合腿 JSON 解析失败: {e}")
    if not isinstance(items, list) or len(items) == 0:
        raise ValueError("组合腿必须是非空 JSON 数组")

    combo_legs = []
    for idx, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"第 {idx} 条组合腿必须是对象")
        code = str(item.get("code", "")).strip()
        if not code:
            raise ValueError(f"第 {idx} 条组合腿缺少 code")
        qty_ratio = item.get("qty_ratio", None)
        if qty_ratio is None:
            raise ValueError(f"第 {idx} 条组合腿缺少 qty_ratio")
        trd_side = item.get("trd_side", None)
        if trd_side is None:
            raise ValueError(f"第 {idx} 条组合腿缺少 trd_side")

        leg = ComboLeg()
        leg.code = code
        leg.trd_side = parse_trd_side(str(trd_side))
        leg.qty_ratio = float(qty_ratio)
        if "position_id" in item and item["position_id"] not in (None, ""):
            leg.position_id = int(item["position_id"])
        combo_legs.append(leg)
    return combo_legs


def place_combo_order(legs_json, price, quantity, order_type="NORMAL",
                      acc_id=None, trd_env=None, security_firm=None, remark="",
                      time_in_force="DAY", expire_time=None, confirmed=False,
                      output_json=False):
    acc_id = acc_id or get_default_acc_id()
    trd_env = parse_trd_env(trd_env) if trd_env else get_default_trd_env()

    combo_legs = _parse_combo_legs(legs_json)
    first_code = safe_get(combo_legs[0], "code", default="")
    market = infer_market_from_code(first_code)
    if not market:
        msg = f"无法从第一条组合腿代码 '{first_code}' 推导交易市场"
        if output_json:
            print(json.dumps({"error": msg}, ensure_ascii=False))
        else:
            print(f"错误: {msg}")
        sys.exit(1)

    order_type_enum = _resolve_order_type(order_type)
    tif_enum = _resolve_time_in_force(time_in_force)

    try:
        if float(quantity) <= 0:
            raise ValueError
    except (ValueError, TypeError):
        msg = "quantity 必须为正数"
        if output_json:
            print(json.dumps({"error": msg}, ensure_ascii=False))
        else:
            print(f"错误: {msg}")
        sys.exit(1)

    if format_enum(trd_env) == "REAL" and not confirmed:
        preview = {
            "action": "place_combo_order_preview",
            "legs": json.loads(legs_json),
            "price": float(price),
            "quantity": float(quantity),
            "order_type": str(order_type).upper(),
            "time_in_force": str(time_in_force).upper(),
            "expire_time": expire_time,
            "trd_env": "REAL",
            "acc_id": acc_id,
            "message": "实盘组合下单需要确认。请核实后加 --confirmed 重新执行。",
        }
        if output_json:
            print(json.dumps(preview, ensure_ascii=False))
        else:
            print("=" * 60)
            print("实盘组合下单预览（未执行）")
            print("=" * 60)
            print(f"  价格:       {price}")
            print(f"  数量:       {quantity}")
            print(f"  订单类型:   {order_type}")
            print(f"  有效期:     {time_in_force}")
            if expire_time:
                print(f"  过期时间:   {expire_time}")
            print(f"  账户:       {acc_id}")
            print(f"  组合腿数:   {len(combo_legs)}")
            print("=" * 60)
            print("请确认后加 --confirmed 参数重新执行。")
        sys.exit(2)

    ctx = None
    try:
        ctx = create_trade_context(market, security_firm=parse_security_firm(security_firm))
        ret, data = ctx.place_combo_order(
            combo_leg_list=combo_legs,
            price=float(price),
            qty=float(quantity),
            order_type=order_type_enum,
            trd_env=trd_env,
            acc_id=acc_id,
            remark=remark,
            time_in_force=tif_enum,
            expire_time=expire_time,
        )
        check_ret(ret, data, ctx, "组合下单")

        if is_empty(data):
            result = {
                "status": "submitted",
                "message": "下单成功，但未返回订单详情",
            }
        else:
            row = data.iloc[0] if hasattr(data, "iloc") else data[0]
            result = {
                "order_id": str(safe_get(row, "order_id", default="")),
                "code": str(safe_get(row, "code", default="")),
                "strategy_type": str(safe_get(row, "strategy_type", default="")),
                "trd_side": str(safe_get(row, "trd_side", default="")),
                "order_type": str(safe_get(row, "order_type", default="")),
                "order_status": str(safe_get(row, "order_status", default="")),
                "qty": safe_float(safe_get(row, "qty", default=0.0)),
                "price": safe_float(safe_get(row, "price", default=0.0)),
                "amount": safe_float(safe_get(row, "amount", default=0.0)),
                "time_in_force": str(safe_get(row, "time_in_force", default="")),
                "expire_time": str(safe_get(row, "expire_time", default="")),
                "dealt_qty": safe_float(safe_get(row, "dealt_qty", default=0.0)),
                "dealt_avg_price": safe_float(safe_get(row, "dealt_avg_price", default=0.0)),
                "create_time": str(safe_get(row, "create_time", default="")),
                "updated_time": str(safe_get(row, "updated_time", default="")),
                "last_err_msg": str(safe_get(row, "last_err_msg", default="")),
                "remark": str(safe_get(row, "remark", default="")),
            }

        _audit_log({"action": "place_combo_order", "result": "success", **result})

        if output_json:
            print(json.dumps(result, ensure_ascii=False))
        else:
            print("=" * 70)
            print("组合下单成功")
            print("=" * 70)
            print(f"  订单 ID:       {result.get('order_id', '')}")
            print(f"  组合代码:       {result.get('code', '')}")
            print(f"  策略类型:       {result.get('strategy_type', '')}")
            print(f"  方向:           {result.get('trd_side', '')}")
            print(f"  数量:           {result.get('qty', '')}")
            print(f"  价格:           {result.get('price', '')}")
            print(f"  状态:           {result.get('order_status', '')}")
            print("=" * 70)

    except Exception as e:
        _audit_log({
            "action": "place_combo_order",
            "result": "error",
            "legs": json.loads(legs_json) if legs_json else [],
            "price": price,
            "quantity": quantity,
            "error": str(e),
        })
        if output_json:
            print(json.dumps({"error": str(e)}, ensure_ascii=False))
        else:
            print(f"错误: {e}")
        sys.exit(1)
    finally:
        safe_close(ctx)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="组合下单（组合期权/组合策略）")
    parser.add_argument(
        "legs",
        help='组合腿 JSON，如 \'[{"code":"US.AAPL260529C302500","trd_side":"BUY","qty_ratio":1},{"code":"US.AAPL","trd_side":"SELL","qty_ratio":100}]\'',
    )
    parser.add_argument("--price", type=float, required=True, help="订单价格")
    parser.add_argument("--quantity", type=float, required=True, help="组合数量")
    parser.add_argument("--order-type", default="NORMAL", help="订单类型（默认 NORMAL）")
    parser.add_argument("--acc-id", type=int, default=None, help="账户 ID")
    parser.add_argument("--trd-env", choices=["REAL", "SIMULATE"], default=None, help="交易环境")
    parser.add_argument(
        "--security-firm",
        choices=["FUTUSECURITIES", "FUTUINC", "FUTUSG", "FUTUAU", "FUTUCA", "FUTUJP", "FUTUMY"],
        default=None,
        help="券商标识",
    )
    parser.add_argument("--remark", default="", help="备注（UTF-8 最长 64 字节）")
    parser.add_argument("--time-in-force", default="DAY", help="有效期限（默认 DAY）")
    parser.add_argument("--expire-time", default=None, help="过期时间（yyyy-MM-dd，仅 GTD 时有效）")
    parser.add_argument("--confirmed", action="store_true", help="实盘下单确认标志（不传则只预览不执行）")
    parser.add_argument("--json", action="store_true", dest="output_json", help="输出 JSON 格式")
    args = parser.parse_args()

    place_combo_order(
        legs_json=args.legs,
        price=args.price,
        quantity=args.quantity,
        order_type=args.order_type,
        acc_id=args.acc_id,
        trd_env=args.trd_env,
        security_firm=args.security_firm,
        remark=args.remark,
        time_in_force=args.time_in_force,
        expire_time=args.expire_time,
        confirmed=args.confirmed,
        output_json=args.output_json,
    )
