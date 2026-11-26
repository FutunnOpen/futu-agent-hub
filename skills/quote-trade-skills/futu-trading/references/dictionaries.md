# Futu Trading Dictionary

The sections below reproduce the official English trading naming dictionary as checked on 2026-11-26: https://open.futunn.com/api/trading/naming-dictionary. Values describe the API; market, security and account restrictions still apply. Read [CLI parameters](cli-parameters.md) for CLI-specific flags, output mappings and preview/confirmation behavior.
Enumeration and data structure reference for all trading APIs. All enum fields and response structures in the API documentation can be found here.


## trd_side (Trading Direction)

| Value | Description |
| --- | --- |
| BUY | Buy |
| SELL | Sell |
| SELL_SHORT | Sell short |
| BUY_BACK | Buy back |


## order_type (Order Type)

| Value | Description |
| --- | --- |
| LIMIT | Limit orders |
| MARKET | Market orders |
| AUCTION | At-auction market orders |
| AUCTION_LIMIT | At-auction limit orders |
| STOP | Stop orders |
| STOP_LIMIT | Stop Limit orders |
| MARKET_IF_TOUCHED | Market if Touched orders |
| LIMIT_IF_TOUCHED | Limit if Touched orders |
| TRAILING_STOP | Trailing Stop Market |
| TRAILING_STOP_LIMIT | Trailing Stop Limit |
| TWAP | TWAP Market Algo |
| TWAP_LIMIT | TWAP Limit Algo |
| VWAP | VWAP Market Algo |
| VWAP_LIMIT | VWAP Limit Algo |
| POV | POV Market Algo (Volume participation) |
| POV_LIMIT | POV Limit Algo |
| SLICER | Slicer Market Algo (Slicing) |
| SLICER_LIMIT | Slicer Limit Algo |
| PEG | PEG Market Algo |
| PEG_LIMIT | PEG Limit Algo |
| ICEBERG_LIMIT | Iceberg Limit Algo |


## order_status (Order Status)

| Value | Description |
| --- | --- |
| WAITING_SUBMIT | Waiting to submit |
| SUBMITTING | Submitting |
| SUBMITTED | Pending |
| FILLED_PART | Partially filled, unfilled part not cancelled |
| FILLED_ALL | All filled |
| CANCELLED_PART | Partially filled, remaining cancelled |
| CANCELLED_ALL | All cancelled, no transactions |
| FAILED | Order failed, refused by server |
| DISABLED | Order disabled |
| DELETED | Deleted, only unfilled orders can be deleted |


## trd_market (Trading Market)

| Value | Description |
| --- | --- |
| HK | Hong Kong market |
| US | US market |
| SG | Singapore market |
| HKCC | China stock market |
| CA | Canada market |
| FUTURES | Futures market |
| JP | Japan market |
| KR | Korea market |
| MY | Malaysia market |
| AU | Australia market |
| FOREX | Forex market |
| PREDICTION | Prediction market (event contracts) |


## exchange (Exchange)

| Value | Description |
| --- | --- |
| US | US Exchange |
| SEHK | Hong Kong Stock Exchange |
| SGX | Singapore Exchange |
| SSE | Shanghai Stock Exchange (Shanghai-Hong Kong Stock Connect) |
| SZSE | Shenzhen Stock Exchange (Shenzhen-Hong Kong Stock Connect) |
| JP | Japan Exchange |
| CA | Canada Exchange |
| CME | Chicago Mercantile Exchange |
| CBOT | Chicago Board of Trade |
| NYMEX | New York Mercantile Exchange |
| COMEX | Commodity Exchange |
| CBOE | Chicago Board Options Exchange |
| HKFE | Hong Kong Futures Exchange |
| KR | Korea Exchange |
| BMS | Bursa Malaysia Securities |
| BMD | Bursa Malaysia Derivatives |
| ASX | Australian Securities Exchange |
| FX | Forex exchange |
| KALSHI | Kalshi event contract exchange |


## trading_session (Trading Session)

| Value | Description |
| --- | --- |
| RTH | Regular trading hours |
| RTH+Pre/Post-Mkt | RTH + Pre/Post-Market |
| OVERNIGHT | Only night trading |
| ALL_DAY | All-day trading |

Only applicable to US stocks. Market orders only support RTH.


## time_in_force (Time in Force)

| Value | Description |
| --- | --- |
| DAY | Day order |
| GTC | Good till cancelled |
| GTD | Good till date |
| IOC | Immediate or cancel |
| FOK | Fill or kill. Client-set FOK is forex only. |


## order_class (Order Class)

| Value | Description |
| --- | --- |
| MLEG | Multi-leg order |


## lot_type (Lot Type)

| Value | Description |
| --- | --- |
| ODD | Odd lot |
| ROUND | Round lot (default) |

Applicable to Hong Kong and Japanese stocks.


## currency (Currency)

| Value | Description |
| --- | --- |
| HKD | Hong Kong Dollar |
| USD | US Dollar |
| CNH | Offshore RMB |
| JPY | Japanese Yen |
| SGD | Singapore Dollar |
| KRW | Korean Won |
| MYR | Malaysian Ringgit |
| AUD | Australian Dollar |


## trail_type (Trailing Type)

| Value | Description |
| --- | --- |
| RATIO | Trailing ratio |
| AMOUNT | Trailing amount |


## position_open_type (Position Open Type)

Trailing stop orders only. Controls whether opening new positions is allowed.

| Value | Description |
| --- | --- |
| DISABLE_POSITION_OPEN | Disable (close only) |
| ENABLE_POSITION_OPEN | Enable |


## pricing_strategy (Algo Sub-order Pricing Strategy)

Common optional field for algo orders. Controls sub-order pricing strategy. Defaults to ADAPTIVE (neutral).

| Value | Description |
| --- | --- |
| ADAPTIVE | Neutral |
| GHOST | Aggressive |
| PASSIVE | Conservative |


## layering (Algo Sub-order Layering)

Common optional field for algo orders. Controls sub-order placement layer count. Defaults to 3 layers.

| Value | Description |
| --- | --- |
| AUTO | Auto |
| 1 - 10 | Explicit layer count |


## peg_offset (PEG Sub-order Price Tracking Rule)

Required field for PEG algo orders. Controls how the sub-order price tracks the market quote.

| Value | Description |
| --- | --- |
| MID_PRICE | Mid price |
| AGGRESSIVE_ONE_TICK | Aggressive 1 tick |
| NEAR_PRICE | Quote 1 tick |
| PASSIVE_ONE_TICK | Quote 2 ticks |
| PASSIVE_TWO_TICKS | Quote 3 ticks |
| PASSIVE_THREE_TICKS | Quote 4 ticks |
| PASSIVE_FOUR_TICKS | Quote 5 ticks |
| PASSIVE_FIVE_TICKS | Quote 6 ticks |
| PASSIVE_SIX_TICKS | Quote 7 ticks |
| PASSIVE_SEVEN_TICKS | Quote 8 ticks |
| PASSIVE_EIGHT_TICKS | Quote 9 ticks |
| PASSIVE_NINE_TICKS | Quote 10 ticks |


## deal_status (Deal Status)

| Value | Description |
| --- | --- |
| OK | Normal |
| CANCELLED | Transaction cancelled |
| CHANGED | Transaction changed |


## security_type (Security Type)

| Value | Description |
| --- | --- |
| STOCK | Stock |
| OPTION | Option |
| FUTURES | Future |
| FUND | Fund |
| MULTILEG_OPTION | Multi-leg option |
| FOREX | Forex |
| EVENT_CONTRACT | Event contract |


## position_side (Position Side)

| Value | Description |
| --- | --- |
| LONG | Long position (default) |
| SHORT | Short position |


## clt_risk_status (Risk Status)

| Value | Description |
| --- | --- |
| LEVEL1 | Very Safe |
| LEVEL2 | Safe |
| LEVEL3 | Safe |
| LEVEL4 | Low Risk |
| LEVEL5 | Medium Risk |
| LEVEL6 | High Risk |
| LEVEL7 | Warning |
| LEVEL8 | Margin Call |
| LEVEL9 | Margin Call |


## enable_market (Supported Trading Market)

Used in the Get Authorized Trading Accounts response.

| Value | Description |
| --- | --- |
| 1 | Hong Kong Market |
| 2 | US Market |
| 4 | China Stock Market |
| 5 | Futures |
| 6 | Singapore Market |
| 7 | Crypto |
| 8 | Australia Market |
| 9 | Forex |
| 10 | Bond |
| 11 | Malaysia Market |
| 12 | Canada Market |
| 14 | Fund |
| 15 | Japan Market |
| 16 | Structured Notes |
| 17 | Event Contracts |
| 18 | Korea Market |


## security_firm (Security Firm)

Used in the Get Authorized Trading Accounts response.

| Value | Description |
| --- | --- |
| FUTUSECURITIES | Futu Securities (Hong Kong) |
| FUTUSG | Moomoo (Singapore) |
| FUTUINC | Moomoo (US) |
| FUTUCA | Moomoo (Canada) |
| FUTUMY | Moomoo (Malaysia) |
| FUTUAU | Moomoo (Australia) |
| FUTUJP | Moomoo (Japan) |


## acc_type (Account Type)

Account type. Used in the acc_type field of the Get Authorized Trading Accounts response.

| Value | Description |
| --- | --- |
| cash | Cash account |
| margin | Margin account |
| derivative | Derivative account (JP only) |


## asset_category (Asset Category)

JP only. Used in the asset_category request parameter of the Get Account Funds and Get Positions APIs.

| Value | Description |
| --- | --- |
| DOMESTIC | Domestic (Japan) |
| FOREIGN | Foreign |


## sub_acc_type (Sub-Account Type)

JP only. Sub-account type under a JP account. See sub_account.

| Value | Description |
| --- | --- |
| General | General |
| Specified | Specified |
| NISA | NISA |


## margin_trading_type (Margin Trading Type)

JP margin account only. Margin (credit) trading type.

| Value | Description |
| --- | --- |
| GENERAL | Negotiable type |
| STANDARDIZED | Standardized type |


## margin_period_type (Margin Period Type)

JP margin account only. Margin (credit) period type.

| Value | Description |
| --- | --- |
| INDEFINITE | Indefinite type |


## option_strategy (Option Strategy)

Used in the multi_leg_info.option_strategy field for multi-leg orders.

| Value | Description |
| --- | --- |
| Covered | Covered |
| VerticalSpread | Vertical Spread |
| Straddle | Straddle |
| Strangle | Strangle |
| Collar | Collar |
| Butterfly | Butterfly |
| Condor | Condor |
| IronButterfly | Iron Butterfly |
| IronCondor | Iron Condor |
| CalenderSpread | Calendar Spread |
| DiagonalSpread | Diagonal Spread |
| Customize | Customize |


## account (Account Structure)

Account object returned by the Get Authorized Trading Accounts endpoint.

| Field | Type | Description |
| --- | --- | --- |
| account_id | uint64 | Trading business account ID. JSON number; do not parse with JavaScript Number when it exceeds MAX_SAFE_INTEGER. |
| security_firm | security_firm | Security firm info |
| enable_market | list[int] | Supported trading markets. See enable_market |
| univs_account_card_number | string | Universal account card number (16 digits) |
| acc_type | acc_type | Account type |
| account_card_number | string | Business account card number (16 digits) |
| sub_accounts | list[sub_account] | JP only. Selectable sub-accounts under this account (one record per sub-account type). Only tradable sub-accounts are returned. Empty / omitted for non-JP brokers. |


## sub_account (Sub-Account Structure)

Sub-account object under a JP account, returned in the sub_accounts list of the account object.

| Field | Type | Description |
| --- | --- | --- |
| sub_acc_type | sub_acc_type | JP only. Sub-account type. |
| sub_acc_id | string | Sub-account id. Pass this value as sub_acc_id when placing an order. |


## order (Order Structure)

Order object returned by order query APIs.

| Field | Type | Description |
| --- | --- | --- |
| side | trd_side | Trading direction |
| order_type | order_type | Order type |
| order_status | order_status | Order status |
| order_id | string | Order ID |
| code | string | Security code |
| stock_name | string | Security name |
| security_type | security_type | Instrument type |
| qty | string | Order quantity |
| price | string | Order price |
| currency | currency | Transaction currency |
| create_time | uint64 | Create time, Unix microsecond timestamp |
| updated_time | uint64 | Last update time, Unix microsecond timestamp |
| dealt_qty | string | Deal quantity |
| dealt_avg_price | string | Average deal price |
| last_err_msg | string | Last error description |
| remark | string | Remark set when placing order |
| time_in_force | time_in_force | Time in force |
| session | trading_session | Trading session |
| aux_price | string | Trigger price |
| trail_type | trail_type | Trailing type |
| trail_value | string | Trailing amount/ratio. |
| trail_spread | string | Specify spread. |
| multi_leg_info | multi_leg_info | Multi-leg order info |
| position_open_type | position_open_type | Open type, only for trailing stop orders |
| algo_info | algo_info | Algo info, only for algo orders |
| expire_time | uint64 | Unix timestamp in microseconds. |
| sub_acc_id | string | JP only. Sub-account id of the order. (Returned by the Get Authorized Trading Accounts interface) |
| sub_acc_type | sub_acc_type | JP only. Sub-account type. |
| margin_trading_type | margin_trading_type | JP margin account only. Margin trading type. |
| margin_period_type | margin_period_type | JP margin account only. Margin period type. |
| exchange | string | Exchange |


## order_fill (Fill Structure)

Fill object returned by deal query APIs.

| Field | Type | Description |
| --- | --- | --- |
| trd_side | trd_side | Trade direction |
| deal_id | string | Fill identifier. Base58-encoded, up to 32 characters. Case-sensitive. |
| order_id | string | Order identifier |
| code | string | Stock code |
| stock_name | string | Stock name |
| qty | string | Fill quantity |
| price | string | Fill price |
| create_time | uint64 | Creation time, Unix microsecond timestamp |
| update_time | uint64 | Last update time, Unix microsecond timestamp |
| counter_broker_id | string | Counterparty broker number |
| counter_broker_name | string | Counterparty broker name |
| status | deal_status | Fill status |
| sub_acc_id | string | JP only. Sub-account id of the order. (Returned by the Get Authorized Trading Accounts interface) |
| sub_acc_type | sub_acc_type | JP only. Sub-account type. |


## multi_leg_info (Multi-Leg Order Info)

Multi-leg order details used in place order requests and order responses.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| option_strategy | option_strategy | Yes | Multi-leg option strategy type. Required when placing a multi-leg order; optional for combo trading-info queries. |
| underlying_symbol | string | Yes | Underlying stock symbol, e.g. AAPL |
| underlying_stock_name | string | No | Underlying stock name (response only) |
| leg_infos | list[order_leg_info] | Yes | Information of each leg |


## order_leg_info (Order Leg Info)

Detailed information for each leg in a multi-leg order.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| leg_code | string | Yes | Leg security code. Format: market.symbol, e.g. US.AAPL |
| leg_ratio_qty | string | Yes | Ratio quantity determined by greatest common factor |
| leg_side | trd_side | Yes | Direction of each leg |
| leg_stock_name | string | No | Leg stock name (response only) |
| leg_hp_multiplier | string | No | Leg contract multiplier (response only) |
| leg_avg_fill_price | string | No | Average fill price of each leg (response only) |
| leg_security_type | security_type | No | Leg security type (response only) |
| leg_symbol | string | No | Leg symbol (response only) |
| leg_exchange | string | No | Leg exchange (response only) |


## direction (Cash Flow Direction)

Used in the direction request parameter of Get Cash Logs.

| Value | Meaning |
| --- | --- |
| IN | Cash inflow |
| OUT | Cash outflow |


## cash_log (Cash Flow)

Cash flow record object returned by the Get Cash Logs API.

| Field | Type | Description |
| --- | --- | --- |
| transaction_name | string | Description of the cash change event (e.g., "Stock Sell Executed", "Fund Subscription") |
| created_time | string | Record creation time in MM/DD/YYYY HH:MM:SS format, e.g., 09/29/2026 05:53:16 |
| cash_change | string | Cash change amount. Positive for inflow, negative for outflow |
| balance | string | Account balance after the change |
| symbol | string | Associated symbol without market prefix, e.g. AAPL, 00700. Use code (market.symbol, e.g. US.AAPL) when filtering requests. Empty if no associated symbol |
| stock_name | string | Associated symbol code and name, e.g. "AAPL Apple Inc.", not the name alone. Empty if no associated symbol |


## order_fee (Fee Item)

Fee detail object returned by the Get Order Fees API.

| Field | Type | Description |
| --- | --- | --- |
| type | string | Fee item type name (e.g., "Commission", "Platform Fee") |
| amount | string | Fee item amount |


## margin_preview (Margin Preview)

Margin preview object returned by the Get Combo Trading Info API.

| Field | Type | Description |
| --- | --- | --- |
| name | string | Margin item name |
| inc_value | string | Margin change amount |


## margin_ratio (Margin Ratio Data)

Margin ratio object returned by the Get Margin Ratio API.

| Field | Type | Description |
| --- | --- | --- |
| code | string | Symbol code. Format: market.symbol |
| is_long_permit | bool | Whether margin buying is allowed |
| is_short_permit | bool | Whether short selling is allowed |
| short_pool_remain | string | Remaining short pool |
| short_fee_rate | string | Short selling reference rate, e.g. "0.003%" |
| alert_long_ratio | string | Margin buying alert ratio, e.g. "130.00%" |
| alert_short_ratio | string | Short selling alert ratio |
| im_long_ratio | string | Initial margin ratio for long positions |
| im_short_ratio | string | Initial margin ratio for short positions |
| mcm_long_ratio | string | Margin call margin ratio for long positions |
| mcm_short_ratio | string | Margin call margin ratio for short positions |
| mm_long_ratio | string | Maintenance margin ratio for long positions |
| mm_short_ratio | string | Maintenance margin ratio for short positions |


## algo_info (Algo Order Info)

Algo execution info in order query responses, only for algo orders. pricing_strategy and layering are common fields; sub-structures for each algo type are returned based on order type.

| Field | Type | Description |
| --- | --- | --- |
| start_time | int64 | Algo execution start time, Unix timestamp in microseconds |
| end_time | int64 | Algo execution end time, Unix timestamp in microseconds |
| pricing_strategy | pricing_strategy | Sub-order pricing strategy |
| layering | layering | Sub-order placement layer count |
| twap | twap_info | TWAP execution params |
| vwap | vwap_info | VWAP execution params |
| pov | pov_info | POV execution params |
| slicer | slicer_info | Slicer execution params |
| peg | peg_info | PEG execution params |
| iceberg | iceberg_info | Iceberg execution params |


## twap_info (TWAP Execution Info)

| Field | Type | Description |
| --- | --- | --- |
| participation_rate | string | Maximum participation rate, range 1%–99%, minimum increment 1%. String type indicates the value is a percentage; do not pass % itself, e.g. "20" means 20% |


## vwap_info (VWAP Execution Info)

| Field | Type | Description |
| --- | --- | --- |
| participation_rate | string | Maximum participation rate, range 1%–99%, minimum increment 1%. String type indicates the value is a percentage; do not pass % itself, e.g. "20" means 20% |


## pov_info (POV Execution Info)

| Field | Type | Description |
| --- | --- | --- |
| participation_rate | string | Maximum participation rate, range 1%–80% (HK / A-share Connect / futures) or 1%–99% (US stocks), minimum increment 1%. String type indicates the value is a percentage; do not pass % itself, e.g. "20" means 20% |


## slicer_info (Slicer Execution Info)

| Field | Type | Description |
| --- | --- | --- |
| slice_interval | int | Sub-order placement interval, in seconds; must be ≥10 and ≤(end_time − start_time) in seconds. Mutually exclusive with display_qty; one of the two is required |
| display_qty | int | Sub-order one-time qty, positive integer lots. Mutually exclusive with slice_interval; one of the two is required |
| display_qty_var | int | Sub-order qty randomization, integer 0–99, default 0 |


## peg_info (PEG Execution Info)

| Field | Type | Description |
| --- | --- | --- |
| display_qty | int | Sub-order one-time qty, positive integer lots |
| peg_offset | peg_offset | Peg position; defaults to NEAR_PRICE |
| display_qty_var | int | Sub-order qty randomization, integer 0–99, default 0 |


## iceberg_info (Iceberg Execution Info)

| Field | Type | Description |
| --- | --- | --- |
| display_qty | int | Sub-order one-time qty, positive integer lots, range 1–parent order lots |
| display_qty_var | int | Sub-order qty randomization, integer 0–99, default 0 |
