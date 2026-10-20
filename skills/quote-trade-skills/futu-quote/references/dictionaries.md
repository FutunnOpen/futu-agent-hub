# Quote naming dictionary

This file maps a user's natural-language intent to the markets, security types, K-line types, adjustments, trading sessions, plates, and option parameters accepted by `futu` CLI quote commands. The official Futu quote naming dictionary is the source of truth for the full enums:

`https://open.futunn.com/zh-cn/api/quote/naming-dictionary`

## Usage rules

- When building CLI commands, prefer the CLI string parameters listed in `references/cli-parameters.md`. Do not pass OpenAPI SDK enum names or numeric values to the CLI unless the flag explicitly requires a number.
- When the user asks what a field or enum means, or asks about a quote enum that the CLI parameter table does not cover, look up the official quote naming dictionary.
- If the official dictionary conflicts with the local CLI parameter notes, generate commands using the parameters the local CLI supports. When explaining a concept, describe the mapping between the official dictionary name and the CLI argument.
- If the market or instrument is uncertain, ask first. Do not use a bare code, a legacy code, or a guessed market in a command.

## Common mapping hints

### Markets and symbols

- CLI symbols use `MARKET.CODE`: `HK.00700`, `US.AAPL`, `SH.600519`, `SZ.000001`, `CC.BTCUSD`.
- Left-pad Hong Kong codes to 5 digits. Usually uppercase the market prefix and the stock code.
- "Hong Kong stocks" usually maps to `HK`. "US stocks" usually maps to `US`. "Shanghai" maps to `SH`. "Shenzhen" maps to `SZ`. Use `CN` for overall A-share rankings or IPOs.
- Code examples: `HK.00700` is a Hong Kong stock, `US.AAPL` is a US stock, `SH.600519` is Shanghai, `SZ.000001` is Shenzhen, `HK.LIST1045` is a plate, and `HK.800000` is an index.
- Common market values: `HK/US/CN/SH/SZ/BJ/SG/JP/AU/CA/MY/KR/CC/HKCC/BMD/BMS`. The supported range for a specific command is defined in `cli-parameters.md`.

### K-lines and adjustments

- `--ktype` for `futu kline` and `futu history-kline` uses CLI numeric values: `2=daily`, `3=weekly`, `4=monthly`, `5=yearly`, `11=quarterly`. Common minute K-lines: `1=1m`, `10=3m`, `6=5m`, `26=10m`, `7=15m`, `8=30m`, `9=60m`, `14=120m`, `29=180m`, `15=240m`. Second-level K-lines: `101=1s`, `105=5s`, `110=10s`, `115=15s`, `130=30s`, `145=45s`.
- Common `--autype` values: `0=none`, `1=forward`, `2=backward`. `kline` also supports `3=forward with dividends` and `4=backward with dividends`. `history-kline` uses only `0/1/2`.
- `--extended-time`: `0=regular`, `1=pre/post`, `2=overnight`.
- `--pred-side`: `0=keep`, `1=YES`, `2=NO`, used for event-contract direction.

### Ticks, intraday data, and trading sessions

- `futu ticker --period` can be repeated with `NORMAL`, `BEFORE`, `AFTER`, and `OVERNIGHT`.
- `futu rt-data --section` uses `NORMAL`, `FULL`, `PREMARKET`, `AFTERHOURS`, `HK_DARK`, and `OVERNIGHT`.
- Map "pre-market" to `PREMARKET` or `BEFORE`, depending on the command. Map "after-hours" to `AFTERHOURS` or `AFTER`. Map "overnight" to `OVERNIGHT`.
- `capital --view intraday --section` supports `NORMAL/FULL/PREMARKET/AFTERHOURS`.

### Plates, IPOs, and calendars

- `--market` for `futu plate --view list` uses `HK/US/SH/SZ/SG/JP/AU/CA/MY/KR`.
- `--plate-class` uses `ALL/INDUSTRY/REGION/CONCEPT/OTHER`.
- `--price-type` for plate constituent price sessions uses `NORMAL/BEFORE/AFTER/OVERNIGHT`.
- `futu trading-days --market` supports more markets, such as `HK/US/SH/SZ/BJ/SG/JP/CA/AU/KR/JP_FUTURE/SG_FUTURE`.
- Historical capital-flow `--period-type` uses `DAY/WEEK/MONTH`.
- Adjustment-factor `--divi-mode` uses `compat/exclude_divi/include_divi`.

### Options

- Prefer `futu option chain <symbol>` for the option chain. Use `futu option-data <symbol> --view ...` for advanced data such as expirations, strategies, and volatility.
- `--filter-standard` uses `ALL/STANDARD/NON_STANDARD`.
- Common `--index-option-type` values: `1=HSI`, `2=HSCEI`, `3=Mini-HSI`, `4=Mini-HSCEI`, `5=HSTECH`, `1001=VIX`, `2001=N225`. The CLI derives some values automatically from `HK.800000`, `HK.800100`, `HK.800700`, `US.VIX`, `US.VIXW`, `JP.N225`, and `JP.NI225`.
- For complex JSON in strategy parameters such as `--strategy`, `--strategy-param`, `--field-filter`, and `--sort-obj`, check the official dictionary and API docs before generating valid JSON.

### Field names

- Common real-time quote and snapshot fields: `code`, `name`, `sc_name`, `tc_name`, `data_time`, `data_date`, `last_price`, `open_price`, `high_price`, `low_price`, `prev_close_price`, `volume`, `turnover`, `turnover_rate`, `amplitude`, `sec_status`, `suspension`, `dark_status`, `listing_date`.
- US extended-hours fields: `pre_market`, `after_market`, `overnight`. Common subfields: `price`, `high_price`, `low_price`, `volume`, `turnover`, `change_val`, `change_rate`, `amplitude`.
- K-line list field: `kline_list`. Current K-lines commonly use `time_key/open_price/high_price/low_price/close_price/volume`. Historical K-lines commonly use `time/open/high/low/close/volume`.
- Tick fields: `ticker_list.time`, `ticker_list.price`, `ticker_list.volume`, `ticker_list.ticker_direction` or `direction`.
- Intraday fields: `section_list.trade_section`, `section_list.point_list.time`, `cur_price`, `high`, `low`, `volume`.
- Order-book fields: `books.exchange`, `bid_list.price/volume`, `ask_list.price/volume`.

### Watchlist and content language

- Watchlist `--group-type` uses `ALL/CUSTOM/SYSTEM`.
- Watchlist mutations `--action add/delete/move-out` automatically map to `op=ADD/DEL/MOVE_OUT`. Execute them only when the user explicitly asks to modify the watchlist.
- News and community `--lang` uses `zh-CN/zh-HK/en/ja`.

## When to read the official dictionary

- The user asks what an enum or field means.
- The user gives a market, security category, trading session, adjustment method, or filter condition that must be converted into a CLI parameter.
- `cli-parameters.md` lists the flag name but not the allowed values or their meanings.
- A numeric enum, English enum, or SDK enum name in a server response needs to be explained.
