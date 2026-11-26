# futu Quote Naming Dictionary

Source: the official English quote naming dictionary: https://open.futunn.com/api/quote/naming-dictionary. Enum values describe API fields and may differ from the CLI flags; use CLI help and the CLI parameter reference for accepted inputs.
Enumeration value lookup table for all quote APIs. Fields referencing enums in API docs link back here.


## sec_status (Security Status)

| Value | Description |
| --- | --- |
| NORMAL | Normal |
| LISTING | Pending listing |
| PURCHASING | IPO subscription in progress |
| SUBSCRIBING | Subscribing |
| BEFORE_DARK_TRADE_OPEING | Before dark pool opening |
| DARK_TRADING | Dark pool trading |
| DARK_TRAD_END | Dark pool closed |
| TO_BE_OPEN | Awaiting market open |
| SUSPENDED | Suspended |
| CALLED | Called back (CBBC) |
| EXPIRED_LAST_TRADING_DATE | Past last trading date |
| EXPIRED | Expired |
| DELISTED | Delisted |
| CHANGE_TO_TEMPORARY_CODE | Changed to temporary code |
| TEMPORARY_CODE_TRADE_END | Temporary code trading ended |
| CHANGED_PLATE_TRADE_END | Board changed, old code trading ended |
| CHANGED_CODE_TRAD_END | Code changed, old code trading ended |
| RECOVERABLE_CIRCUIT_BREAKER | Recoverable circuit breaker |
| UNRECOVERABLE_CIRCUIT_BREAKER | Unrecoverable circuit breaker |
| AFTER_COMBINATION | After-hours matching |
| AFTER_TRANSACTION | After-hours trading |
| DARK_TRADE_SUSPEND | Dark pool suspended |
| EXPIRED_LAST_TRADING_TIME | Past last trading time |
| N/A | Unknown / No mapping |


## dark_status (Dark Pool Status)

| Value | Description |
| --- | --- |
| TRADING | Dark pool trading |
| END | Dark pool closed |
| N/A | Not in dark pool |


## option_type (Option Direction)

| Value | Description |
| --- | --- |
| CALL | Call |
| PUT | Put |
| "" | Not an option |


## option_area_type (Option Exercise Type)

| Value | Description |
| --- | --- |
| AMERICAN | American option |
| EUROPEAN | European option |
| BERMUDA | Bermuda option |
| "" | Not an option |


## trust_assetClass (Trust Fund Asset Class)

| Value | Description |
| --- | --- |
| STOCK | Equity |
| BOND | Bond |
| COMMODITY | Commodity |
| CURRENCY_MARKET | Money market |
| FUTURE | Futures |
| SWAP | Swap |


## ktype (K-line Type)

| Value | Description |
| --- | --- |
| 1 | 1 minute |
| 2 | Day |
| 3 | Week |
| 4 | Month |
| 5 | Year |
| 6 | 5 minutes |
| 7 | 15 minutes |
| 8 | 30 minutes |
| 9 | 60 minutes |
| 10 | 3 minutes |
| 11 | Quarter |
| 14 | 120 minutes |
| 15 | 240 minutes |
| 26 | 10 minutes |
| 29 | 180 minutes |


## autype (Adjustment Type)

| Value | Description |
| --- | --- |
| 0 | No adjustment |
| 1 | Forward adjusted (excluding dividends) |
| 2 | Backward adjusted (excluding dividends) |
| 3 | Forward adjusted (including dividends) |
| 4 | Backward adjusted (including dividends) |


## extended_time (Pre/Post Market Switch, US 1-min K-line only)

| Value | Description |
| --- | --- |
| 0 | Default (exclude pre/post market) |
| 1 | Include pre/post market |
| 2 | Include overnight session |


## request_section (rt-data Trading Session, get_rt_data only)

| Value | Description |
| --- | --- |
| NORMAL | Regular session (default; HK includes dark pool) |
| FULL | Full session including pre/post market (US only, excludes overnight) |
| PREMARKET | US pre-market |
| AFTERHOURS | US after-hours |
| HK_DARK | HK dark pool |
| OVERNIGHT | US overnight |


## capital_flow_section (capital_flow Trading Session, request param; get_capital_flow only)

| Value | Description |
| --- | --- |
| NORMAL | Regular session (default; HK includes dark pool) |
| FULL | Full session including pre/post market |
| PREMARKET | Pre-market only |
| AFTERHOURS | After-hours only |


## capital_flow_history_period_type (capital_flow_history Period Type, request param)

| Value | Description |
| --- | --- |
| DAY | Daily aggregation (default) |
| WEEK | Weekly aggregation |
| MONTH | Monthly aggregation |


## trade_section (Trading Session Type, response; by market)

| Value | Description |
| --- | --- |
| AUCTION | HK auction session |
| MORNING | HK morning session |
| AFTERNOON | HK afternoon session |
| NIGHT | Night session |
| US_PREMARKET | US pre-market |
| US_AFTERHOURS | US after-hours |
| HK_DARK | HK dark pool |
| FUT_PART1 | Futures session 1 |
| FUT_PART2 | Futures session 2 |
| STIB_AFTERHOURS | STAR Market after-hours |
| US_OVERNIGHT | US overnight |
| US_REGULAR | US regular session |
| DEFAULT | Default (general markets) |
| REGULAR | Regular session |
| US_INDEX_OPT_REGULAR | US index option regular |
| US_INDEX_OPT_GLOBAL | US index option global |
| US_INDEX_OPT_CURB | US index option CURB |
| JP_INDEX_OPT_NIGHT | JP index option night |
| JP_INDEX_OPT_REGULAR | JP index option regular |


## trade_date_type (Trading Day Type, response)

| Value | Description |
| --- | --- |
| WHOLE | Full-day trading |
| MORNING | Morning only |
| AFTERNOON | Afternoon only |


## ticker_direction (Tick Direction)

| Value | Description |
| --- | --- |
| BUY | Buy |
| SELL | Sell |
| NEUTRAL | Neutral (direction undetermined) |


## tick_type (Tick Trade Type)

The table lists 32 trade types by market usage frequency. Less common types may appear for specific products or historical data.

| Value | Description |
| --- | --- |
| UNKNOWN | Unknown |
| AUTO_MATCH | Automatch (most common in HK) |
| LATE | Late trade |
| NON_AUTO_MATCH | Non-automatch |
| ODD_LOT | Odd lot |
| AUCTION | Auction |
| BULK | Block trade |
| OVERSEAS | Overseas trade |
| UNAUTO_MATCH_OFF | Non-automatch off-exchange |
| NON_DIRECT_OFF | Non-direct off-exchange |
| OVERSEAS_OFF | Overseas off-exchange |
| AUTO_MATCH_OFF | Automatch off-exchange |
| BULK_OFF | Block trade off-exchange |
| LATE_OFF | Late trade off-exchange |
| AUCTION_OFF | Auction off-exchange |
| ODD_LOT_OFF | Odd lot off-exchange |
| EVENING | Evening session trade |
| ACCEPT_ELECTRONIC | Electronic accepted |
| OUT_HOUR_CONTRACT | After-hours contract |
| BANK_CHARGE | CCASS charge |
| ELECTRONIC | Electronic trade |
| HIGH_DENSITY | High-density trade |
| INTERMEDIATE_PRICE | Intermediate price trade |
| AT_AUCTION | At-auction |
| AUCTION_LIMIT | Auction limit |
| AT_AUCTION_LIMIT | At-auction limit |
| ENHANCE_LIMIT | Enhanced limit |
| HOT_QUOTE | Hot quote |
| MARKET | Market order |
| ROUND_LOT | Round lot |
| SPECIAL_LOT | Special lot |
| ODD_AND_SPECIAL_LOT | Odd and special lot |


## period_type (Tick Period Type)

| Value | Description |
| --- | --- |
| NORMAL | Regular session |
| BEFORE | Pre-market |
| AFTER | After-hours |
| OVERNIGHT | Overnight |


## stock_type (Security Type)

| Value | Description |
| --- | --- |
| BOND | Exchange-traded bond |
| WEALTH_MANAGE | Wealth management fund |
| STOCK | Equity |
| ETF | ETF / REIT / Trust |
| WARRANT | Warrant (CBBC / Inline warrant) |
| IDX | Index |
| PLATE | Sector / Plate |
| DRVT | Option |
| FUTURE | Futures |
| FOREX | Forex |
| CRYPTO | Cryptocurrency |
| OTC_STRUCT_NOTES | Wealth management structured notes |
| PLATESET | Plate set |
| SECURITY_PORTFOLIO | Security portfolio |
| EC | Macro data |
| OPPORTUNITY_PORTFOLIO | Opportunity portfolio |
| OLD_OTC_STRUCT_NOTES | Legacy structured notes |
| PREDICTION | Event contract |
| TOKENIZED_FUND | Tokenized fund |


## state (Security Lifecycle State)

| Value | Description |
| --- | --- |
| NORMAL | Normal |
| PENDING_LISTING | Pending listing |
| IPO_PURCHASING_CN | A-share IPO subscription |
| IPO_PURCHASING_OTHER | Other market IPO subscription |
| DARK_TRADE_PENDING | Dark pool pending open |
| DARK_TRADE_HAPPENING | Dark pool trading |
| DARK_TRADE_END | Dark pool closed |
| TO_BE_OPEN | Awaiting open |
| SUSPENDED | Suspended |
| CALLED | Called back (CBBC) |
| EXPIRED_LAST_TRADING_DATE | Last trading date |
| EXPIRED | Expired |
| DELISTED | Delisted |
| CHANGE_TO_TEMPORARY_CODE | Changed to temporary code |
| TEMPORARY_CODE_END_TRADING | Temporary code trading ended |
| CHANGED_PLATE_END_TRADING | Board changed, trading ended |
| CHANGED_CODE_END_TRADING | Code changed, trading ended |
| CIRCUIT_BREAKER_RECOVERABLE | Recoverable circuit breaker |
| CIRCUIT_BREAKER_UNRECOVERABLE | Unrecoverable circuit breaker |
| AFTER_COMBINATION | After-hours matching |
| AFTER_TRANSACTION | After-hours trading |
| DARK_TRADE_SUSPEND | Dark pool suspended |
| EXPIRED_LAST_TRADING_TIME | Past last trading time |


## stock_child_type (Warrant Sub-type)

| Value | Description |
| --- | --- |
| N/A | Not a warrant or unknown |
| CALL | Call warrant |
| PUT | Put warrant |
| BULL | Bull CBBC |
| BEAR | Bear CBBC |
| INLINE | Inline warrant |


## action_type (Corporate Action Type, get_rehab)

| Value | Description |
| --- | --- |
| SPLIT | Stock split |
| JOIN | Reverse split |
| BONUS_STK | Bonus shares |
| INTOSHARES | Share conversion (capital reserve) |
| ALLOT | Rights issue |
| ADD | Additional issue |
| DIVIDEND | Dividend |
| SPECIALDIVIDEND | Special dividend |
| SPINOFF | Spin-off |


## divi_mode (Dividend Adjustment Mode, get_rehab request param)

| Value | Description |
| --- | --- |
| compat | Legacy compatibility (not recommended) |
| exclude_divi | Exclude dividends (Yahoo / Bloomberg convention) |
| include_divi | Include dividends (default; A-share / Futu convention) |


## plate_type (Plate Type, response)

| Value | Description |
| --- | --- |
| INDUSTRY | Industry sector (GICS / SW classification) |
| CONCEPT | Concept / Theme sector |
| REGION | Regional sector (SH/SZ A-share only) |
| OTHER | Other sectors |


## market_state (Market Trading State, get_market_state response)

The following table lists all 38 market states. The API returns their enum names as strings.

| Value | Description |
| --- | --- |
| NONE (0) | No trading / Unsupported market / Not open |
| AUCTION (1) | Auction |
| WAITING_OPEN (2) | Waiting for open |
| MORNING (3) | Morning session |
| REST (4) | Lunch break |
| AFTERNOON (5) | Afternoon session |
| CLOSED (6) | Closed |
| MAAUCTION (7) | Matching Auction |
| PRE_MARKET_BEGIN (8) | US pre-market begin |
| PRE_MARKET_END (9) | US pre-market end |
| AFTER_HOURS_BEGIN (10) | US after-hours begin |
| AFTER_HOURS_END (11) | US after-hours end |
| FUTU_SWITCH_DATE (12) | Futu date switch |
| NIGHT_OPEN (13) | Derivatives night session open |
| NIGHT_END (14) | Derivatives night session close |
| FUTURE_DAY_OPEN (15) | Futures day session open |
| FUTURE_DAY_BREAK (16) | Futures day session break |
| FUTURE_DAY_CLOSE (17) | Futures day session close |
| FUTURE_DAY_WAIT_OPEN (18) | Futures day session waiting |
| HK_CAS (19) | HK Closing Auction Session |
| FUTURE_NIGHT_WAIT (20) | Futures night session waiting |
| FUTURE_AFTERNOON (21) | Futures afternoon open (deprecated) |
| FUTURE_SWITCH_DATE (22) | Derivatives date switch |
| FUTURE_OPEN (23) | Derivatives open |
| FUTURE_BREAK (24) | Derivatives break |
| FUTURE_BREAK_OVER (25) | Derivatives break over |
| FUTURE_CLOSE (26) | Derivatives close |
| STIB_AFTER_HOURS_WAIT (27) | STAR Market after-hours matching wait |
| STIB_AFTER_HOURS_BEGIN (28) | STAR Market after-hours begin |
| STIB_AFTER_HOURS_END (29) | STAR Market after-hours end |
| CLOSE_AUCTION (30) | Closing auction |
| AFTERNOON_END (31) | Closed |
| NIGHT (32) | Night session trading |
| OVERNIGHT_BEGIN (33) | US overnight begin |
| OVERNIGHT_END (34) | US overnight end |
| TRADE_AT_LAST (35) | Trade at last |
| TRADE_AUCTION (36) | Trade auction |
| OVERNIGHT (37) | US overnight session |


## trade_section_type (Trading Session Type Numeric, get_market_state response)

The API returns the integer trading-session codes listed below.

| Value | Description |
| --- | --- |
| US_PREMARKET (5) | US pre-market |
| US_AFTERHOURS (6) | US after-hours |
| US_OVERNIGHT (11) | US overnight |
| US_REGULAR (12) | US regular |
| DEFAULT (20) | Default (HK / SH / SZ / Crypto / Forex) |
| REGULAR (21) | Single session (US option regular) |
| US_INDEX_OPTION_REGULAR (22) | US index option regular |
| US_INDEX_OPTION_GLOBAL (23) | US index option global |
| US_INDEX_OPTION_CURB (24) | US index option CURB |
| JP_INDEX_OPTION_NIGHT (25) | JP index option night |
| JP_INDEX_OPTION_REGULAR (26) | JP index option regular |


## market (Market Prefix)

The market request parameter used in plate and market screening APIs.

| Value | Description |
| --- | --- |
| HK | Hong Kong |
| US | United States |
| SH | Shanghai A-share |
| SZ | Shenzhen A-share |
| SG | Singapore |
| JP | Japan |
| AU | Australia |
| CA | Canada |
| MY | Malaysia |
| KR | South Korea |

SH and SZ share the same A-share plate set (calling SH or SZ is equivalent).


## plate_class (Plate Classification)

| Value | Description |
| --- | --- |
| ALL | All plates |
| INDUSTRY | Industry plate |
| REGION | Regional plate (SH / SZ only) |
| CONCEPT | Concept plate |
| OTHER | Other plates |


## sort_field (Plate Stock Sort Field, get_plate_stock request param)

| Value | Description |
| --- | --- |
| NONE | No sort (default, server order) |
| CODE | Stock code |
| CHANGE_RATE | Change rate |
| NAME | Stock name |
| MARKET_VAL | Total market cap |
| PRICE_CHANGE_VAL | Price change value |
| CUR_PRICE | Current price |
| PRICE_CHANGE_SPEED | Price change speed |
| TURNOVER | Turnover |
| VOLUME | Volume |
| PRICE_HIGHEST | Highest price |
| PRICE_LOWEST | Lowest price |
| PRICE_OPEN | Opening price |
| PRICE_LAST | Previous close |
| PE | P/E ratio |
| ASK_PRICE | Ask price |
| BID_PRICE | Bid price |
| ASK_VOL | Ask volume |
| BID_VOL | Bid volume |
| TURNOVER_RATIO | Turnover ratio |
| BUYSELL_RATIO | Buy/sell ratio |
| VOLUME_RATIO | Volume ratio |
| AMPLITUDE | Amplitude |
| TOTAL_SHARES | Total shares |
| CIRC_TOTAL_SHARES | Circulating shares |
| CIRC_MARKET_VALUE | Circulating market cap |
| DIVIDEND_RATIO_TTM | Dividend yield TTM |
| DIVIDEND_RATIO_LFY | Dividend yield LFY (last fiscal year) |
| PREMIUM | Premium (warrants/CBBCs) |
| PRICE_RISE_COUNT | Consecutive rise days |
| MARGINABLE | Marginable |
| MORTGAGE_RATE | Margin ratio |
| SHORT_SELLING | Short sellable |
| SHORT_REF_RATE | Short selling reference rate |
| LONG_MARGIN_INITIAL_RATIO | Long initial margin ratio |
| SHORT_MARGIN_INITIAL_RATIO | Short initial margin ratio |
| IPO_PRICE | IPO price |
| LIST_TIME | Listing time |
| IPO_PE | IPO P/E |
| IPO_PRICE_CHANGE_RATIO | IPO cumulative change rate |
| CONTINUOUS_RISE_DAY_CNT | IPO consecutive rise days |
| FIRST_DAY_PCR | First day change rate |
| FIRST_DAY_REAL_PCR | First day actual change rate |
| ISSUE_SIZE | Issue size |
| PRE_CUR_PRICE | Pre-market current price |
| PRE_PRICE_CHANGE_VAL | Pre-market price change value |
| PRE_CHANGE_RATE | Pre-market change rate |
| AFTER_CUR_PRICE | After-hours current price |
| AFTER_PRICE_CHANGE_VAL | After-hours price change value |
| AFTER_CHANGE_RATE | After-hours change rate |
| PRE_AMPLITUDE | Pre-market amplitude |
| AFTER_AMPLITUDE | After-hours amplitude |
| PRE_TURNOVER | Pre-market turnover |
| AFTER_TURNOVER | After-hours turnover |
| PRE_VOLUME | Pre-market volume |
| AFTER_VOLUME | After-hours volume |
| HSG_HOLD_NUM | Stock Connect holdings |
| HSG_HOLD_RATIO | Stock Connect holdings ratio |
| CHANGE_RATIO_5_DAYS | 5-day change rate |
| CHANGE_RATIO_10_DAYS | 10-day change rate |
| CHANGE_RATIO_20_DAYS | 20-day change rate |
| CHANGE_RATIO_60_DAYS | 60-day change rate |
| CHANGE_RATIO_120_DAYS | 120-day change rate |
| CHANGE_RATIO_250_DAYS | 250-day change rate |
| CHANGE_RATIO_YEAR | YTD change rate |
| CHANGE_RATIO_5_MIN | 5-minute change rate |
| ADR_CODE | ADR related code |
| ADR_PRICE | ADR price |
| ADR_DIFF_PRICE | ADR premium/discount amount |
| ADR_DIFF_PER | ADR premium/discount percentage |
| ADR_CONVERTION_RATIO | ADR conversion ratio |
| ADR_RATIO | ADR ratio |
| ADR_TRAD_VOL | ADR trading volume |
| HSG_HOLD_AMOUNT | Stock Connect holdings amount |
| ADR_PRICE_HK | ADR HK related price |
| HSG_DAY_FLOW | Stock Connect daily flow |
| HSG_WEEK_FLOW | Stock Connect weekly flow |
| HSG_MONTH_FLOW | Stock Connect monthly flow |
| HSG_QUATER_FLOW | Stock Connect quarterly flow |
| TTM_PE | TTM P/E |
| ANNUAL_PE | Static P/E |
| BMP_PRICE | Dark pool price |
| BMP_PRICE_CHANGE_VAL | Dark pool price change value |
| BMP_PRICE_CHANGE_RATE | Dark pool change rate |
| WEIGHT | Plate weight |
| EFFECT_DOT | Impact points |
| US_FUTURE_DEFAULT | US futures default sort |
| LAST_SETTLE_PRICE | Last settlement price (futures) |
| POSITION | Open interest (futures) |
| POSITION_CHANGE | Daily position change (futures) |
| LAST_TRADE_TIME | Last trade time (futures) |
| EN_NAME | English name |
| DARK_CHANGE_RATIO | Dark pool change rate (legacy) |
| DARK_CHANGE_VAL | Dark pool change value (legacy) |
| PB | P/B ratio |
| TRUST_AUM | Trust fund AUM |
| TRADE_INFO | Trade info |
| CURRENCY_CODE | Currency code |
| MATURITY_DATE | Maturity date (warrants/convertible bonds) |
| RELATION_WEIGHT | Related weight |
| CONVERT_PREMINUM_RATIO | Convertible bond premium rate |
| STRB_PREMIUM_RATIO | Straddle warrant premium rate |
| PUT_LEVER_PRICE | Put warrant leverage price |
| CALL_LEVER_PRICE | Call warrant leverage price |
| STRB_VALUE | Straddle warrant value |
| CONVERT_STOCK_PRICE | Convertible bond conversion price |
| WRNT_LAST_TRADE_DATE | Warrant last trade date |
| CHANGE_RATIO_3_YEAR | 3-year change rate |
| JA_NAME | Japanese name |
| OVERNIGHT_PRICE | Overnight price |
| OVERNIGHT_TURNOVER | Overnight turnover |
| OVERNIGHT_VOLUME | Overnight volume |
| OVERNIGHT_AMPLITUDE | Overnight amplitude |
| OVERNIGHT_PRICE_CHANGE_VAL | Overnight price change value |
| OVERNIGHT_CHANGE_RATE | Overnight change rate |
| HOT | Popularity |
| ETF_LEVERAGE | ETF leverage |
| DIVIDEND_TTM | TTM dividend |
| PAYOUT_RATIO_LFY | Payout ratio LFY |
| DISTRIBUTION_FREQUENCY | Distribution frequency |
| MAX_DIVIDEND_GROW_YEAR | Max consecutive dividend growth years |
| DIVIDEND_INCREASE_RATE_1YEAR | 1-year dividend growth rate |
| AVERAGE_DIVIDEND_YIELD_5YEAR | 5-year average dividend yield |
| CHANGE_RATIO_24H | 24-hour change rate |
| DEBT_ASSET_RATIO | Debt-to-asset ratio |
| TH_NAME | Thai name |


## price_type (Price Sort Basis, get_plate_stock request param)

| Value | Description |
| --- | --- |
| NORMAL | Regular price (default) |
| BEFORE | Pre-market price |
| AFTER | After-hours price |
| OVERNIGHT | Overnight price |


## statement_type (Financial Statement Type, request param)

| Value | Description |
| --- | --- |
| 1 | Income statement |
| 2 | Balance sheet |
| 3 | Cash flow statement |
| 4 | Key indicators |


## financial_type (Financial Period Type, request/response parameter)

The English source omits entries and differs for some labels; this section is translated from the Chinese official dictionary. Whether an endpoint accepts a value depends on that endpoint.

| Value | Description |
| --- | --- |
| 0 | Automatic period matching by date; request only, for revenue breakdown. |
| 1 | Q1, single quarter. |
| 2 | Q2, single quarter. |
| 3 | Q3, single quarter. |
| 4 | Q4, single quarter. |
| 5 | Q6, cumulative first-half report. |
| 6 | Q9, cumulative first three quarters. |
| 7 | Annual report. |
| 8 | Aggregated quarterly, US stocks only, for revenue breakdown. |
| 9 | All single-quarter reports (Q1–Q4); multi-period selector, request only. |
| 10 | Single-quarter reports and annual report (Q1–Q4 plus annual); request-only multi-period selector and financial statements default. |
| 11 | All cumulative reports (Q1, Q6, Q9 and annual); multi-period selector, request only. |
| 102 | All cumulative reports (Q1, Q6, Q9 and annual); request-only multi-period selector for company operational efficiency. |
| 70 | Malaysia Other single-quarter report (`period_text` suffix `SQ`). |
| 71 | Malaysia Other cumulative report (`period_text` suffix `CQ`). |

## financial_structure (Financial Structure ID, response)

Different statement_type values map to different structure sets; the same statement_type may map to different structures across markets (e.g., HK income statement → 5, US income statement → 8). Agents typically don't need to parse structure directly — each item_list element in the response already includes an inline display_name.

| Value | Description | statement_type |
| --- | --- | --- |
| 1 | Income Statement (US GAAP, Banking) | 1 Income |
| 2 | Income Statement (US GAAP, Insurance) | 1 Income |
| 3 | Income Statement (US GAAP, Industrial) | 1 Income |
| 4 | Balance Sheet (US GAAP, Banking) | 2 Balance |
| 5 | Income Statement (HK / IAS, General) | 1 Income |
| 6 | Balance Sheet (HK / IAS, General) | 2 Balance |
| 7 | Cash Flow Statement (US GAAP) | 3 Cash Flow |
| 8 | Income Statement (US GAAP, General) | 1 Income |
| 9 | Balance Sheet (US GAAP, General) | 2 Balance |
| 10 | Income Statement (CN / CAS, Industrial) | 1 Income |
| 11 | Balance Sheet (HK / IAS, Banking) | 2 Balance |
| 12 | Income Statement (HK / IAS, Banking) | 1 Income |
| 13 | Cash Flow Statement (HK / IAS) | 3 Cash Flow |
| 14 | Key Indicators – Per Share | 4 Key Indicators |
| 15 | Key Indicators – Profitability | 4 Key Indicators |
| 16 | Key Indicators – Solvency | 4 Key Indicators |
| 17 | Key Indicators – Growth | 4 Key Indicators |
| 18 | Key Indicators – Operating Efficiency | 4 Key Indicators |
| 19 | Key Indicators – Cash Flow | 4 Key Indicators |


## expiration_cycle (Option Expiration Cycle)

| Value | Description |
| --- | --- |
| MONTH | Monthly |
| WEEK | Weekly |
| END_OF_MONTH | End of month |
| QUARTERLY | Quarterly |
| WEEKMON | Monday expiry |
| WEEKTUE | Tuesday expiry |
| WEEKWED | Wednesday expiry |
| WEEKTHU | Thursday expiry |
| WEEKFRI | Friday expiry |
| N/A | Unknown |


## index_option_type (Index Option Type, request param)

| Value | Market | Description |
| --- | --- | --- |
| 1 | HK | Hang Seng Index (HSI) |
| 2 | HK | H-shares Index (HSCEI) |
| 3 | HK | Mini-HSI |
| 4 | HK | Mini-HSCEI |
| 5 | HK | Hang Seng TECH Index (HSTECH) |
| 1000 | US | Fallback index option |
| 1001 | US | VIX |
| 1002 | US | SPX |
| 1003 | US | XSP |
| 1004 | US | NDX |
| 1005 | US | EFS |
| 1006 | US | MXS |
| 1007 | US | DJX |
| 1008 | US | OEX |
| 1009 | US | SIXB |
| 1010 | US | SIXI |
| 1011 | US | SIXM |
| 1012 | US | SIXU |
| 1013 | US | SIXV |
| 1014 | US | XEO |
| 1015 | US | BKX |
| 1016 | US | XAU |
| 1017 | US | OSX |
| 1018 | US | SOX |
| 1019 | US | UTY |
| 1020 | US | RUT |
| 1021 | US | SIXRE |
| 1022 | US | XND |
| 1023 | US | CBTX |
| 1024 | US | MBTX |
| 2001 | JP | N225 |
| 2002 | JP | N225M |
| 2003 | JP | TOPIX |


## filter_standard (Standard/Non-standard Option Filter, request param)

| Value | Description |
| --- | --- |
| ALL | All (default) |
| STANDARD | Standard options only |
| NON_STANDARD | Non-standard options only (FLEX / adjusted contracts) |


## combo_strategy (Combo Option Strategy Type, request/response)

Integer strategy for Combo Option Strategy and Combo Option Spread. This is not the trading-order string enum option_strategy; do not mix them. Values not listed (e.g. 3 / 5 / 10 / 12) are outside the supported enum and return ret_code=-3.

Strategies marked as requiring spread: omitting spread causes a business error (ret_code=-5). Call the spread API first, then pass default_spread or a value from spread_list.

| Value | Name | Description | Requires spread | Requires far_expire_time |
| --- | --- | --- | --- | --- |
| 1 | SingleOption | Single-leg option | no | no |
| 2 | Covered | Covered | no | no |
| 4 | Spread | Vertical spread | yes | no |
| 6 | Straddle | Straddle | no | no |
| 7 | Strangle | Strangle | yes | no |
| 8 | Collar | Collar | yes | no |
| 9 | Butterfly | Butterfly | yes | no |
| 11 | Condor | Condor | yes | no |
| 13 | IronButterfly | Iron butterfly | yes | no |
| 14 | IronCondor | Iron condor | yes | no |
| 15 | CalendarSpread | Calendar spread | no | yes |
| 16 | DiagonalSpread | Diagonal spread | yes | yes |
| 100 | Customize | Custom | no | no |

Each combo_list item from quote.option_strategy is one combo, with legs in legs[]. Covered(2) / Collar(8) prepend the path underlying as a STOCK leg and do not return side / quantity; the caller supplies those when quoting. HK does not support 2/8.


## option_standard_type (Option Specification, response)

Used as option_standard_type on option-chain rows and combo legs. Request-side filter is filter_standard (adds ALL).

| Value | Description |
| --- | --- |
| STANDARD | Standard option |
| NON_STANDARD | Non-standard option (FLEX / adjusted contracts) |
| N/A | Unknown / unmapped |


## combo_leg_instrument (Combo Leg Instrument, response)

Used as legs[].instrument in Combo Option Strategy. The quote API does not send this field; it distinguishes option vs stock by code.

| Value | Description |
| --- | --- |
| OPTION | Option contract |
| STOCK | Underlying stock (included for Covered / Collar only) |


## combo_side (Combo Quote Leg Side, request/echo)

Used as legs[].side in Combo Option Quote. The value is not inferred from strategy type; the caller must send it. This is not the same as tick ticker_direction BUY/SELL.

| Value | Description |
| --- | --- |
| BUY | Buy this leg |
| SELL | Sell this leg |


## holder_type (Holder Type, request/response param)

Used in get_shareholders_holding_changes as holder_type (English text) / holder_type_id (numeric). Also used in get_shareholders_holder_detail as request_type (additionally includes 1000=All, default 1000).

| holder_type_id | holder_type | Description |
| --- | --- | --- |
| 1 | Other Institution | Other institution |
| 2 | Traditional Investment Manager | Traditional investment manager |
| 3 | Hedge Fund Manager / CTA | Hedge fund |
| 4 | VC / PE Firm | Venture capital / Private equity |
| 5 | Corporate Pension Plan Sponsor | Corporate pension |
| 6 | Foundation Fund Sponsor | Foundation fund |
| 7 | Insurance Company | Insurance company |
| 8 | Bank / Investment Bank | Bank / Investment bank |
| 9 | Family Office / Trust | Family office / Trust |
| 10 | Sovereign Wealth Fund | Sovereign wealth fund |
| 11 | REIT / Real Estate Investment Manager | REIT |
| 12 | Structured Finance Pool Manager | Structured finance manager |
| 13 | Union Pension Plan Sponsor | Union pension |
| 14 | Government Pension Plan Sponsor | Government pension |
| 15 | Endowment Fund Sponsor | Endowment fund |
| 100 | Individual Insider | Individual |
| 200 | ADR Issuer | ADS |
| 300 | Public Corporation | Public corporation |
| 400 | Private Corporation | Private corporation |
| 500 | State-Owned Shares | State-owned shares |


## pub_type (Financial Report Disclosure Timing, response)

| Value | Description |
| --- | --- |
| 0 | Same day (unspecified pre/post market) |
| 1 | Pre-market |
| 2 | Post-market |


## delivery_type (Delivery Type, get_future_info)

| Value | Description |
| --- | --- |
| UNKNOWN | Unknown / Unspecified |
| PHYSICAL | Physical delivery |
| CASH | Cash settlement |


## query_time_period (Option Volatility Query Period, request param)

| Value | Description |
| --- | --- |
| 1 | 1 week |
| 2 | 1 month (default) |
| 3 | 3 months |
| 4 | 6 months |
| 5 | 1 year |


## impvol_status (Implied Volatility Analysis Status, response)

| Value | Description |
| --- | --- |
| FLUCTUATING | Fluctuating |
| OVERVALUED | Overvalued |
| UNDERVALUED | Undervalued |


## Prosperity band (prosperity_band)

Chains, nodes and stocks share these values:

| Value | Meaning |
| --- | --- |
| UNSPECIFIED | Unrated |
| BOOMING | Booming |
| EXPANDING | Expanding |
| STABLE | Stable |
| SUBDUED | Subdued |


## History quota pool (pool)

standard: ordinary targets; option: option chains. Both pools have the same total and independent usage. Subscription quota does not use this parameter.


## Index-option differences by endpoint

Gamma exposure accepts all values in the index-option table, including 1002 (SPX) and 1004 (NDX). Trade/open-interest distribution excludes 1002 and 1004; see its endpoint enum for accepted values. Omit index_option_type for equity-option underlyings.


## indicator_filters（Technical indicators）

| Value | Description |
| --- | --- |
| CCI | CCI |
| KDJ | KDJ |
| BIAS | BIAS |
| AR | AR |
| BR | BR |
| VR | VR |
| PSY | PSY |
| OSC | OSC |
| WMSR | WMSR |
| MACD | MACD |
| BOLL | BOLL |
| MA | MA |
| RSI6 | RSI6 |
| RSI12 | RSI12 |
| RSI24 | RSI24 |


## analysis_dimensions（Capital analysis dimensions）

| Value | Description |
| --- | --- |
| funds_distribution | Fund distribution |
| funds_broker | Brokers |
| funds_flow | Fund flow |
| short_sell_number | Short-selling volume |
| short_sell_ratio | Short-selling ratio |
| short_sell_number_and_ratio | Short-selling volume and ratio |


## analysis_dimensions（Derivatives analysis dimensions）

| Value | Description |
| --- | --- |
| warrant_ratio | CBBC outstanding ratio |
| warrant_price_distribution | CBBC distribution |
| option_unusual | Options block trades / unusual activity |
| option_volatility | Options volatility |
| option_volume_price | Options volume and price |
| option_sentiment | Options sentiment |
| option_comprehensive | Combined options signals |


## language_id（Response language）

| Value | Description |
| --- | --- |
| 0 | Simplified Chinese (default) |
| 1 | Traditional Chinese |
| 2 | English |
| 4 | Thai |
| 5 | Japanese |
