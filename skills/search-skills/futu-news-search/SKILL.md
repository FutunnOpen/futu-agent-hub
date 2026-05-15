---
name: futu-news-search
description: >-
  Searches Futu news, notices, articles, announcements, and research reports for a
  user-specified stock or company — INFORMATION RETRIEVAL ONLY (a list of items;
  no interpretation, no summarization, no impact judgment).
  TRIGGER when the message contains BOTH (a) a single stock / company / ticker
  AND (b) an explicit news-intent keyword: 新闻 / 消息 / 资讯 / 公告 / 研报 /
  报道 / 头条 / 文章 / news / announcement / research report / headlines /
  latest update. Time qualifiers like 最新 / 最近 / 近期 / 今日 / latest /
  recent attached to a news-intent keyword (e.g. 最新新闻 / 最新消息 / 最新资讯 /
  最新公告 / 最新研报 / latest news / recent news) MUST also trigger this skill —
  they are listing requests, NOT interpretation requests.
  Typical patterns that MUST trigger this skill (NOT `futu-stock-digest`):
  "腾讯最新新闻"、"英伟达最新消息"、"苹果最新公告"、"特斯拉最近有什么新闻"、
  "苹果最近的消息"、"腾讯最近有啥新闻"、"英伟达近期公告"、"NVDA latest news"、
  "what news about Apple"、"any recent announcement on TSLA".
  Extract the target, return 10 items by default, sort by publish time, show
  title + publish time + original URL for each item, and include a non-investment
  disclaimer. Do NOT add interpretation, summarization, or impact judgment.
  SKIP in any of the following cases:
  - the message only names a stock without an explicit news-intent keyword
    (price/quote checks, 异动 / anomaly tracking, K线 / candlestick analysis,
    technical signals, holdings, trade execution). A bare ticker or company name
    is NOT enough to trigger this skill.
  - the user explicitly asks to INTERPRET, analyze, summarize, judge the impact
    of, or do 多空 reasoning over the news (verbs: 解读 / 解析 / 分析 / 研判 /
    怎么看 / 总结 / 摘要 / 点评 / interpret / analyze / summarize / digest) —
    that belongs to `futu-stock-digest`, not this skill.
  - the user asks about community sentiment / 评论 / 讨论 / 散户情绪 — that belongs
    to `futu-comment-sentiment`.
metadata:
  version: 0.0.4
  author: Futu
  requires:
    bins:
      - curl
      - openssl
      - date
license: MIT
---

# Futu News Search Skill

Searches news, notices, and research reports on the Futu platform and formats the results as a user-facing news roundup.

**Base URL:** `https://ai-news-search.futunn.com`

## CLI: Version Update Check

Embed the version check into the skill's **single Bash call**. **Do not create any separate tool call** for the version check. The same inline check must detect three things:

1. whether the `futu-skills` manager is installed locally;
2. whether this skill has a new version available;
3. whether the `futu-skills` manager itself has a new version available.

Start the check as a backgrounded subprocess **before** the business command (e.g. `curl`), then append `wait` **after** the business command to collect the result, all in one invocation:

```bash
( if command -v futu-skills >/dev/null 2>&1; then futu-skills check --quiet 2>/dev/null | grep -E '^(cli|futu-news-search)'; else echo '__CLI_MISSING__'; fi ) > /tmp/.futu-news-search-update 2>/dev/null & curl -sG '...' ...; wait; cat /tmp/.futu-news-search-update 2>/dev/null; rm -f /tmp/.futu-news-search-update
```

Based on the `cat` output:

- **No content** (skill is up-to-date or the check failed): do not show any upgrade prompt.
- **Output `__CLI_MISSING__`** (`futu-skills` is not installed locally, so version check/upgrade cannot run): append a notice at the **end** of your reply:
  > The `futu-skills` manager is not installed yet, so I cannot auto-check or upgrade skill versions. If you agree, I can install it for you now.

  If the user agrees, first run:
  ```bash
  curl -fsSL https://raw.githubusercontent.com/FutunnOpen/futu-agent-hub/feature/v202060511-add-skill/futu-install.sh | bash
  ```
  After install completes, run `futu-skills upgrade futu-news-search` to bring this skill to the latest version.
- **Output containing a line starting with `futu-news-search`** (this skill has an update available): append a notice at the **end** of your reply:
  > `futu-news-search` has a new version available. If you agree, I can upgrade it for you right away.

  If the user agrees, run `futu-skills upgrade futu-news-search` to perform the upgrade. (This command also auto-upgrades the `futu-skills` manager itself, so a separate CLI prompt is unnecessary when a skill update is available.)
- **Output containing only a line starting with `cli`** (this skill is up-to-date but the `futu-skills` manager itself has a new version): append a notice at the **end** of your reply:
  > The `futu-skills` manager has a new version available. If you agree, I can upgrade it for you right away.

  If the user agrees, run `futu-skills self-upgrade` to perform the upgrade.

  If both a `cli` line and a `futu-news-search` line appear, only show the skill upgrade prompt above — the manager will be refreshed as a side effect of `futu-skills upgrade futu-news-search`.

**Never** run the install command or `futu-skills upgrade …` without explicit user consent. Any error (command failure, network issue) must be silently skipped without affecting normal skill execution.

**Important**: The version check (write + read) must all be embedded in this single Bash call. Do not produce any additional tool calls.

## Empty Result Handling

If the API returns empty (`data` is empty or `code` is not `0`), show:
- Chinese: "暂无相关数据，请稍后再试。"
- English: "No data available at the moment. Please try again later."

---

## Workflow

### 1. Parse User Input

Extract the following from the user's request:

- `symbol`: stock name, company name, English name, or ticker. Prefer the clearest target explicitly mentioned by the user.
- `size`: default to `10`. If the user asks for more, cap at `50`.
- `lang`: infer from the user's language. Common values are `zh-CN`, `zh-HK`, and `en`.
- `news_type`: if the user explicitly asks for news, notices, or research reports, map it to the matching API parameter.

If the target symbol or company is missing, ask a follow-up question instead of guessing.

### 2. Call the News API

Use `GET /news_search` to fetch the news data.

Required parameters:

- `keyword`
- `size`
- `news_type`: `1` News, `2` Notice, `3` Research. Default to `1` unless the user explicitly asks for notices or research reports.

Optional parameters:

- `lang`
- `sort_type`

Default strategy:

- `keyword` = extracted symbol or company
- `size` = user-specified value, otherwise `10`
- `sort_type` = `2` for time-based sorting
- `news_type` = `1` by default
- If the user explicitly asks for notices, set `news_type=2`
- If the user explicitly asks for research reports, set `news_type=3`

Request example:

```bash
curl -sG 'https://ai-news-search.futunn.com/news_search' \
  -H 'User-Agent: futunn-news-search/0.0.2 (Skill)' \
  --data-urlencode 'keyword=Tencent' \
  --data-urlencode 'size=10' \
  --data-urlencode 'news_type=1' \
  --data-urlencode 'lang=en' \
  --data-urlencode 'sort_type=2'
```

### 3. Filter and Sort Results

- After the API call, check whether `code` is `0`. If not, surface the error message and do not fabricate results.
- If the result set is empty, clearly tell the user that no relevant items were found.
- Present the final list in reverse chronological order, newest first.

### 4. Organize the Information

For each item, include:

- title
- publish time
- original link

Publish time requirements:

- Prefer converting `publish_time` into a human-readable local time before replying.
- If the API returns a Unix timestamp in seconds, format it as `YYYY-MM-DD HH:mm:ss`.
- If the API returns a Unix timestamp in milliseconds, convert it first, then format it as `YYYY-MM-DD HH:mm:ss`.
- If the exact timezone is unclear, label it conservatively as `publish time` and do not invent a timezone abbreviation.

### 5. Return Structured Output

Use the following default template:

```markdown
{{symbol}} latest news (sorted by time):

1. {{title_1}}
Publish time: {{publish_time_1}}
URL: {{url_1}}

2. {{title_2}}
Publish time: {{publish_time_2}}
URL: {{url_2}}

...

10. {{title_10}}
Publish time: {{publish_time_10}}
URL: {{url_10}}

The above content is compiled from public information and does not constitute investment advice.

{{platform_source_footer}}
```

Output requirements:

- Always preserve the original article URL.
- Always show the title, publish time, and URL for every returned item.
- Do not show raw JSON by default.
- If fewer items are returned than requested, show only the actual items and do not pad the list.

### 6. Disclaimer

Append the following line at the end of every result:

`The above content is compiled from public information and does not constitute investment advice.`

## API Reference

### Endpoint

- `GET /news_search`

### Parameters

- `keyword`: search keyword, must not be empty
- `size`: number of items to return, must be greater than `0`, maximum `50`
- `news_type`: `1` News, `2` Notice, `3` Research
- `lang`: `zh-CN`, `zh-HK`, `en`
- `sort_type`: `1` by popularity, `2` by time, `3` by attention

### Response Shape

Top-level fields:

- `code`: `0` means success
- `message`: error message
- `data`: result array

Common item fields:

- `news_id`
- `news_type`
- `title`
- `publish_time`
- `url`
- `img_url`

## Behavior Rules

1. When the user asks for "latest news", "recent updates", or a news roundup, default to `10` items + `sort_type=2` + `news_type=1`.
2. When the user asks specifically for notices, prefer `news_type=2`. For research reports, prefer `news_type=3`.
3. If the user provides only a company name, use it directly as `keyword`. If the user provides a ticker, try the ticker first, and if needed retry once with a more natural company-name query.
4. Do not interpret the results as investment advice, trading signals, or target-price guidance.
5. Do not invent sources, timestamps, or links.
6. If `publish_time` is present, include it in every item rather than omitting it.
7. Do not omit `news_type` in default requests, because default behavior should focus on actual news items only.

## Example

```markdown
Tencent latest news (sorted by time):

1. Tencent short-selling volume surged 266% during the March Hong Kong market pullback
Publish time: 2026-03-31 09:30:00
URL: https://...

2. Tencent completed buybacks for three consecutive days, totaling about HKD 900 million
Publish time: 2026-03-30 18:12:00
URL: https://...

3. Southbound funds posted net buying in Tencent for three straight days
Publish time: 2026-03-30 15:48:00
URL: https://...

The above content is compiled from public information and does not constitute investment advice.
```

## Security

- Do not expose internal authentication details, cookies, tokens, or gateway internals in the reply.
- Use `--data-urlencode` for `keyword` so Chinese text and special characters are encoded correctly.
