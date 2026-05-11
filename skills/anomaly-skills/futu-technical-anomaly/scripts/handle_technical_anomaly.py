#!/usr/bin/env python3
import argparse
import json
import os
import sys
from pathlib import Path


def configure_utf8_stdio():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")


def bootstrap_repo_path():
    script_path = Path(__file__).resolve()
    for parent in script_path.parents:
        package_dir = parent / "futu"
        if package_dir.is_dir() and (package_dir / "__init__.py").exists():
            parent_str = str(parent)
            if parent_str not in sys.path:
                sys.path.insert(0, parent_str)
            return


def load_futu():
    bootstrap_repo_path()
    from futu import OpenQuoteContext, RET_OK

    return OpenQuoteContext, RET_OK


def parse_list_args(values):
    if not values:
        return None

    items = []
    for value in values:
        for part in str(value).split(","):
            part = part.strip()
            if part:
                items.append(part)
    return items or None


def normalize_data(value):
    if hasattr(value, "to_dict"):
        try:
            return value.to_dict(orient="records")
        except TypeError:
            return value.to_dict()
    if isinstance(value, dict):
        return {key: normalize_data(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [normalize_data(item) for item in value]
    return value


def build_parser():
    parser = argparse.ArgumentParser(
        description="Call the technical anomaly skill backend.",
    )
    parser.add_argument("stock_symbol", help="Stock symbol, such as US.NVDA or HK.00700")
    parser.add_argument("--time-range", type=int, default=7, help="Natural day window, default 7")
    parser.add_argument(
        "--indicator-filters",
        nargs="*",
        help="Indicator filters, supports space-separated or comma-separated values",
    )
    parser.add_argument(
        "--language-id",
        type=int,
        default=0,
        choices=[0, 1, 2, 4, 5],
        help="0=zh-CN, 1=zh-TW, 2=en, 4=th, 5=ja",
    )
    parser.add_argument("--host", default=os.getenv("FUTU_OPEND_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("FUTU_OPEND_PORT", "11111")))
    parser.add_argument("--json", action="store_true", help="Print JSON only")
    return parser


def main():
    configure_utf8_stdio()
    args = build_parser().parse_args()
    indicator_filters = parse_list_args(args.indicator_filters)
    OpenQuoteContext, RET_OK = load_futu()

    quote_ctx = OpenQuoteContext(host=args.host, port=args.port)
    try:
        ret, data = quote_ctx.get_technical_unusual(
            args.stock_symbol,
            time_range=args.time_range,
            indicator_filters=indicator_filters,
            language_id=args.language_id,
        )
    finally:
        quote_ctx.close()

    if ret != RET_OK:
        print(f"get_technical_unusual error: {data}", file=sys.stderr)
        return 1

    payload = {
        "method": "get_technical_unusual",
        "stock_symbol": args.stock_symbol,
        "time_range": args.time_range,
        "indicator_filters": indicator_filters or [],
        "language_id": args.language_id,
        "data": normalize_data(data),
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print("get_technical_unusual")
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
