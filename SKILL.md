---
name: muse-reach
description: "Muse-native read-only search and reading across GitHub, YouTube, Reddit, X/Twitter, Facebook, Instagram, Bilibili, V2EX, Xiaohongshu, LinkedIn, TikTok, Threads, Telegram, Discord, Pinterest, Bluesky, Mastodon, Snapchat, and the web, plus Amazon, Flipkart, eBay, AliExpress, Etsy, Shopee, Temu and Mercado Libre product search. Use when the user asks to search or read a link on any of those sites, open Amazon or Flipkart, find a product price, or asks what Agent Reach can do. Routes Muse's own browser.search, browser.open, social.search and connectors first, Agent Reach only as fallback. Never logs in for the user, never posts or buys."
---

# Muse Reach

Read-only search and reading for Muse. One router for every site Agent Reach covers, plus Amazon, Flipkart and 12 more channels Agent Reach never had, built for Muse instead of ported from another agent.

## How to use

- Run `python3 ~/workspace/muse-reach/muse-reach.py route <channel> <action> <query-or-url>` before fetching anything. It prints the route in order as JSON. Follow that order.
- Run `python3 ~/workspace/muse-reach/muse-reach.py channels` to list every channel, its actions and its honest status. Run `doctor` for cheap local checks only. Doctor never hits the network and never re-tests a rate-limited channel.
- The router itself never scrapes and never fetches pages. It only tells you which Muse tool or CLI to use. Fetch with that tool.
- `exec` runs only the safe read-only backends (youtube, github, bilibili, v2ex) through `agent-reach`. It refuses amazon, flipkart, reddit, web, and all 14 Muse-first-only channels (tiktok, threads, telegram, discord, pinterest, bluesky, mastodon, snapchat, ebay, aliexpress, etsy, shopee, temu, mercadolibre) — those have no agent-reach backend. For those, follow the printed route with Muse tools instead.

## Route order, every channel

Muse-native first, Agent Reach only as fallback. Public content first with Muse's own search and read tools. Use Reach only when those fail or miss the post body, comments or subtitles.

- github: GitHub connector or `gh` CLI first, then `agent-reach github search|read`. No login for public repos.
- youtube: `browser.search` first, then `agent-reach youtube search|read|subtitle` (yt-dlp). No login for public videos. Transcribe needs a Groq or OpenAI key, supplied by the user in their own terminal, never in chat.
- bilibili: `browser.search` first, then `agent-reach bilibili search|read|hot|subtitle` (bili-cli). No login, subtitles may need login.
- v2ex: `browser.search` or `browser.open` first, then `agent-reach v2ex hot|node|read|user`. No login.
- web: `browser.search`, then `browser.open`. Use `agent-reach web search|read` (Exa/Jina) only if Muse tools fail.
- xiaohongshu: `browser.search` first, then `agent-reach xiaohongshu search|read|comments`. Login required for full access.
- xueqiu: `browser.search` or the finance vertical for quotes first, then `agent-reach xueqiu quote|search|hot_posts|hot_stocks`. Quotes need no login, hot posts and hot stocks need login.
- boss: `browser.search` first, then `agent-reach boss search|read`. Login required.
- xiaoyuzhou: `browser.search` first, then `agent-reach xiaoyuzhou transcribe`. Transcribe needs a Groq key.
- linkedin: `browser.search` for public job pages first, then `agent-reach linkedin jobs|read`. Site search is login-gated.
- reddit: `browser.search`, then `social.search`, then screenshots the user sends. Fallback is `agent-reach reddit search|read|subreddit --backend public-web`. Public posts need no login.
- twitter: `social.search`, then `browser.search`. Fallback is `agent-reach twitter search|profile|tweets|thread`. Site search is login-gated, no x.com session means no tweet feed. A specific x.com link through the web reader returns the profile header only.
- facebook: Facebook connector (`facebook-cli`) first, then `agent-reach facebook search|profile --backend public-web`. Login required for full access.
- instagram: Instagram connector (`instagram-cli`) first, then `agent-reach instagram search|profile|posts`. Login-gated, and broken on test 2026-10-27.
- amazon: Shopping skill first. Meta Catalog search plus a live browser product search for the live price. See the shopping section below. Agent Reach never had this channel.
- flipkart: same route as amazon. Agent Reach never had this channel.
- tiktok: `browser.search` (site:tiktok.com) for public videos. No agent-reach backend; full video/feed needs the app or login.
- threads: `social.search` (threads), then `browser.search`. No agent-reach backend.
- telegram: `browser.search` (site:t.me) for public channels; `browser.open` on a t.me/s/ web-view URL. No agent-reach backend; private chats need login.
- discord: `browser.search` for public server listings (discodus.com, discordbotlist.com). No agent-reach backend; messages need a Discord login.
- pinterest: `browser.search` (site:pinterest.com) for pins and idea pages. No agent-reach backend.
- bluesky: `browser.search` (site:bsky.app) for public posts; per-profile RSS feeds exist. No agent-reach backend; the direct public API returns HTTP 403 from this VM, do not call it from here.
- mastodon: `browser.search` across instances (site:mastodon.social and others) for public posts; per-profile RSS feeds exist. No agent-reach backend; the public timeline API needs auth.
- snapchat: `browser.search` for public Spotlight posts on snapchat.com profiles. No agent-reach backend; stories/lenses need the app.
- ebay: Shopping skill first — `browser.search` (site:ebay.com) for listings, live browser for the live price. Same honest route as amazon. No agent-reach backend.
- aliexpress: same route as ebay, `browser.search` (site:aliexpress.com). No agent-reach backend.
- etsy: same route as ebay, `browser.search` (site:etsy.com). No agent-reach backend.
- shopee: same route as ebay, but use a plain `browser.search` query — the site: operator returned nothing for Shopee. No agent-reach backend.
- temu: same route as ebay, `browser.search` (site:temu.com). No agent-reach backend.
- mercadolibre: `browser.search` with a plain Spanish/Portuguese query — the site: operator returned nothing, and direct listings are thin in the index (reseller/aggregator mirrors only). No agent-reach backend.

## Amazon, Flipkart and the other shops — the honest route

- Live price and stock come ONLY from a live browser task or Meta Catalog. Nothing else counts as live.
- A `browser.open` result can be a stale cached crawl, sometimes hundreds of days old, with no price. That is not a live price. Say so, do not quote it as current.
- A `curl` HTTP 200 can be a bot-check shell of a few kilobytes, not a product page. That is not a live price either.
- Price trackers such as Smartprix, 91mobiles and pricehistory.app are corroboration only, never the live price.
- Never construct a product URL. Use only URLs returned by search or tools, or supplied by the user.
- For a purchase, follow the Shopping skill. The live browser owns checkout. Never buy, add to cart for real, or enter payment details through a script.
- The same rules apply to ebay, aliexpress, etsy, shopee, temu and mercadolibre: search-index prices are crawled copies (days old), not live. Verify in the live browser before quoting a price.
- Prefer the India store (amazon.in, flipkart.com) and INR when the user is in India.

## Stop rules

- On `RATE_LIMITED`, `PLATFORM_BLOCKED`, `NEED_LOGIN` or `BUSY`, stop that channel. Report what was already obtained. Do not switch backends to evade the block, do not solve CAPTCHAs by bypass, do not loop-retry, and do not open a second browser to get around it.
- A rate limit has a pause. Respect the `retry_after_seconds` or the wait hint the backend gave. A failed or empty result is still a result, report it.
- Never log in for the user, never ask for passwords or cookies, never copy a login from the user's browser yourself. If a channel needs login, say so and let the user log in themselves in the live browser.
- Read-only. Never post, comment, like, DM, or buy through this skill.

## Known setup quirks, this VM

- `agent-reach` lives in `~/.local/bin` (uv tool). Add that to PATH or the binary is not found.
- `~/.local/bin/google-chrome` is a wrapper running `/opt/meta-chromium/chrome --no-sandbox`. Chrome refuses to run as root without it. Do not replace it with a plain symlink.
- yt-dlp defaults to its certifi bundle, which misses this VM's egress proxy CA. The fix is `~/.config/yt-dlp/config` containing `--compat-options no-certifi`, so it uses system certs. Never use `--no-check-certificates`.
- CloakBrowser download fails on this VM, so Agent Reach falls back to Muse's Chromium with a dedicated profile.

## Status, verified 2026-11-12 (retest evening, ~21:00-21:15 IST)

- youtube works (yt-dlp search returned live results).
- github works (github-api search returned live results, incl. JSxtrme/Muse-Reach).
- bilibili works (bili-cli hot returned live trending videos; slow — one router run hit the 30s backend timeout).
- v2ex works (v2ex-api hot returned today's topics).
- xueqiu quotes work (AAPL 357.62, +0.63%, tencent backend, no login). hot_posts/hot_stocks need login, not tested.
- reddit search via public-web failed with HTTP 429 rate limit. web read via Agent Reach failed rate-limited with a 3586 second wait hint. Do not retry either backend until the pause expires (~21:24 IST). Muse browser.search is patchy for direct Reddit posts.
- browser.open on an amazon.in product page returned a 344-day-old crawl with no price. curl to amazon.in returned HTTP 200 but 3793 bytes, a bot-check shell.
- flipkart works via Meta Catalog (real Flipkart Plus 223 listing, sale Rs 1,199, 3.9 stars, 55,374 reviews). Browser.search also returns real Flipkart listings, crawled 2-5 days ago, not live.
- **Agent Reach's dedicated browser is broken 2026-11-12**: every opencli channel (twitter, facebook, instagram, linkedin, boss, xiaohongshu) fails with `the Agent Reach browser did not open: browser closed`. Root cause: a direct Chromium launch now exits with `Hatch WebGL domain policy is required for browser startup`. `doctor` now checks this and reports it. Muse's own browser is unaffected.
- facebook and instagram work Muse-first: social.search returned 28 Facebook and 49 Instagram posts on 2026-11-12.
- linkedin works partially Muse-first: browser.search returns real LinkedIn jobs via SmartRecruiters/Simplify, not linkedin.com direct.
- twitter/X works partially Muse-first: browser.search finds public X posts via the search index; the direct feed is still login-gated.
- xiaohongshu and boss do not work for direct notes/jobs: browser broken, and Muse search returns background about the platforms only.
- xiaoyuzhou not verified: transcribe needs a Groq key, none supplied (check returned 0/0 actions).
- Router fix: `exec` now accepts no-query actions (`hot`) — it previously required a query and returned BAD_INPUT. `route` matches.

## Expansion, verified 2026-11-12 evening (~22:30-22:45 IST) — 14 new Muse-first-only channels

Agent Reach never had any of these. All of them route through Muse tools only; `exec` refuses them (no agent-reach backend).

- telegram works: browser.search returned real public channel posts with full text (AniDL, AnimeTm, crawled 2-4 days ago). Public channels only.
- pinterest works: browser.search returned real pin and idea pages (anime wallpapers, freshest crawled 1-3 days ago). Public content only.
- bluesky works: browser.search returned real public posts with full text, dates and likes (@gamingonlinux.com, @modrinth.com). Direct public API returns HTTP 403 from this VM — use the search index, not the API.
- ebay works: browser.search returned real listings with USD prices, seller feedback and stock (JBL Vibe Beam $29.90, Sony WF-1000XM6 $177.99, crawled 3-15 days ago). Prices are crawled, not live.
- aliexpress works: browser.search returned real listings with USD prices (Soundcore Life P2 Mini $26.83, Lenovo GM2 Pro $7.80, crawled 2-8 days ago). Prices are crawled, not live.
- etsy works: browser.search returned real handmade listings with prices in USD/EUR/AUD and stock (JJK cat keychain $11.99, Kacchan phone charm $12.00, crawled 4-25 days ago). Prices are crawled, not live.
- shopee works: browser.search returned real Shopee SG listings with SGD prices (Baseus BP1 Pro $28.24 SGD, UGREEN Dots $15.69 SGD, crawled 2-10 days ago). Use a plain query — the site: operator returned nothing. Prices are crawled, not live.
- temu works: browser.search returned real listings with USD prices (TWS earbuds $5.97, AI translation earbuds $8.40, crawled 4-27 days ago). Prices are crawled, not live.
- tiktok partial: browser.search finds real public TikTok videos (@voxy.us, crawled 2-11 days ago); playing or reading a full video/feed needs the app or login.
- discord partial: search finds public server listings with member counts and invite links (Hypixel Bedwars, 74,927 members) via discodus/discordbotlist, not discord.com direct; messages need login.
- mastodon partial: search finds real public posts via mastodon.social profiles and RSS feeds, but crawls were stale (28-84 days) and search is instance-by-instance; the public timeline API needs auth.
- snapchat partial: search finds real public Spotlight posts on snapchat.com profiles (@ecosmp Minecraft builds, posted Aug 2026); stories/lenses/friends need the app.
- mercadolibre partial: no direct mercadolibre.com results in the index; listings only surfaced via resellers/aggregators (Latinafy, Karma). Direct site is JS/login-walled in the index.
- threads unproven: social.search (threads) returned 0 posts for 3 queries on 2026-11-12. Not conclusively broken — may be query-dependent — but no result obtained yet.
- Not added, on purpose: wechat (~1.4B users) is login-walled with no public web path; whatsapp (~3B) is messaging, not searchable; taobao/jd are China-only and login-walled.
- Router is now v0.2.0 with 30 channels. The route output key for shopping channels is now `shopping_rule` (was `amazon_rule`), covering all 8 shopping channels.
