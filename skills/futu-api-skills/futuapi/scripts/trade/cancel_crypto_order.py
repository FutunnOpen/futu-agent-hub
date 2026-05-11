#!/usr/bin/env python3
"""
撤销加密货币订单

说明：
- 加密货币订单仅支持撤单，不支持改单/失效/生效/删单
- 支持 cancel_all_order() 一键全撤
"""
import argparse
import json
import sys
import os as _os
sys.path.insert(0, _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..")))
from common import (
    create_crypto_trade_context,
    parse_security_firm,
    get_default_acc_id,
    check_ret,
    safe_close,
    TrdEnv,
    ModifyOrderOp,
)


def cancel_crypto_order(order_id=None, cancel_all=False, acc_id=None,
                        security_firm=None, output_json=False):
    acc_id = acc_id or get_default_acc_id()
    firm_enum = parse_security_firm(security_firm)

    if not cancel_all and not order_id:
        msg = "请传入 --order-id 或 --all"
        if output_json:
            print(json.dumps({"error": msg}, ensure_ascii=False))
        else:
            print(f"错误: {msg}")
        sys.exit(1)

    ctx = None
    try:
        ctx = create_crypto_trade_context(security_firm=firm_enum)
        if cancel_all:
            ret, data = ctx.cancel_all_order(trd_env=TrdEnv.REAL, acc_id=acc_id)
            check_ret(ret, data, ctx, "加密货币全部撤单")
            result = {"action": "cancel_all", "status": "submitted"}
        else:
            ret, data = ctx.modify_order(ModifyOrderOp.CANCEL, order_id, 0, 0,
                                         trd_env=TrdEnv.REAL, acc_id=acc_id)
            check_ret(ret, data, ctx, f"加密货币撤单(order_id={order_id})")
            result = {"action": "cancel", "order_id": str(order_id), "status": "submitted"}

        if output_json:
            print(json.dumps(result, ensure_ascii=False))
        else:
            print(f"撤单请求已提交: {result}")
    finally:
        safe_close(ctx)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="撤销加密货币订单")
    parser.add_argument("--order-id", default=None, help="订单 ID")
    parser.add_argument("--all", action="store_true", dest="cancel_all", help="撤销所有加密货币订单")
    parser.add_argument("--acc-id", type=int, default=None, help="加密货币账户 ID")
    parser.add_argument("--security-firm",
                        choices=["FUTUSECURITIES", "FUTUINC", "FUTUSG"],
                        default=None, help="券商标识")
    parser.add_argument("--json", action="store_true", dest="output_json", help="输出 JSON 格式")
    args = parser.parse_args()
    cancel_crypto_order(order_id=args.order_id, cancel_all=args.cancel_all,
                        acc_id=args.acc_id, security_firm=args.security_firm,
                        output_json=args.output_json)
