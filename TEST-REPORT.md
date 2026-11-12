# muse-reach — Test Report

Date: 2026-11-12 (IST). Version: 0.1.0. Tester: Muse (subagent build).

## What passed

- `python3 muse-reach.py channels --json` — lists all 16 channels (14 Agent Reach channels + amazon + flipkart) with Muse-first route, fallback, login note and status.
- `python3 muse-reach.py doctor` — exit 0, all 5 local checks ok: agent-reach binary (`~/.local/bin/agent-reach`), google-chrome `--no-sandbox` wrapper, yt-dlp no-certifi config, yt-dlp binary (uv tool dir), gh CLI. Doctor is local-only, no network.
  - Found and fixed during testing: the first doctor run reported `ok: false` because agent-reach and yt-dlp are not on PATH in a plain shell; they live under `~/.local/bin` and `~/.local/share/uv/tools/agent-reach/bin/`. Doctor now checks those locations too.
- `python3 muse-reach.py amazon search "boAt Airdopes Plus 223"` — routing-only, no scraping. Returns the Shopping route (Meta Catalog + live browser) plus the explicit rule that a stale crawl or curl 200 is not a live price.
- `python3 muse-reach.py route reddit search "boAt Airdopes"` — routing-only, no fetch. Correctly reports RATE_LIMITED and routes to browser.search / social.search.
- `python3 muse-reach.py exec amazon search ...` — correctly REFUSED (exit 3) with the Shopping-route message.
- `python3 muse-reach.py exec youtube search "Voxy Minecraft" --limit 2` — LIVE, passed. Returned 2 real results via yt-dlp (Voxy videos by flowstate and Stackleyy), `ok: true`.
- Skill discoverability: `muse.skill_search` for "muse-reach search reddit youtube amazon" returns `muse_reach` (`~/workspace/custom-skills/muse-reach/SKILL.md`). YAML frontmatter parses (`name: muse-reach`, description present). For a pure "open amazon product search" query the shopping skill ranks first, which is correct — it owns product search, and muse-reach routes Amazon through it.
- Repo hygiene: no secrets, keys, passwords, cookies or personal data in the repo. `.gitignore` excludes profiles, cookies, credentials, keys, `.env`, `__pycache__`.

## What failed / was not re-tested (carried over, verified earlier 2026-11-12)

- Reddit via agent-reach public-web: RATE_LIMITED, HTTP 429. Not re-run. Use browser.search / social.search.
- Agent Reach web read (Exa/Jina): RATE_LIMITED, wait hint 3586s. Not re-run. Use browser.search / browser.open.
- Amazon direct fetch: `browser.open` on an amazon.in product page returned a 344-day-old cached crawl with no price; `curl` returned HTTP 200 but 3793 bytes, a bot-check shell. Direct scraping does not work. Live price needs a live browser task or Meta Catalog.
- X/Twitter, LinkedIn jobs, Instagram: login-gated or broken (verified 2026-10-27). Not re-tested today. Do not claim they work until a live test passes.

## Honest limits

- muse-reach cannot unblock a site that bot-blocks automation or requires login. It changes the route, not the site's defences. Amazon live price still needs the live browser; Instagram/X/LinkedIn still need the user's own login.
- bilibili, v2ex, xueqiu, github, facebook, instagram and flipkart were all live-tested in the evening retest of 2026-11-12 (see "Retest 2026-11-12 evening" below). xiaohongshu and boss are broken via the dedicated browser; xiaoyuzhou needs a Groq key.
- `exec` only runs youtube, github, bilibili and v2ex through agent-reach. Everything else is routing-only by design.

## Not done

- Repo live at https://github.com/JSxtrme/Muse-Reach (public, main). Pushed 2026-11-12, head 9b8753d before this expansion.
- Flipkart live test: done in the evening retest of 2026-11-12 (Meta Catalog verified).

## Retest 2026-11-12 evening (~21:00-21:15 IST) — every untested / unverified channel

All 16 channels now have a live verdict. Nothing is "not tested" any more.

### Now verified working

- **bilibili** — `agent-reach bilibili hot --limit 3`: ok via bili-cli. Live trending videos, e.g. BV1hrW367Emp ("辽阔的土地生不出狭隘的爱", 3.0M views) and BV1kZWX62ENY (影视飓风 18M-subscriber Q&A). Slow/flaky: a later `muse-reach.py exec bilibili hot` run hit agent-reach's 30s backend timeout on both bili-cli and bilibili-api. Working, but slow — not blocked.
- **v2ex** — `agent-reach v2ex hot --limit 3`: ok via v2ex-api. Today's topics, e.g. t/1256329 (2026-11-12T01:12:46Z). Also works via the router now: `muse-reach.py exec v2ex hot --limit 1` returns the same live topic.
- **xueqiu** — `agent-reach xueqiu quote AAPL`: ok via tencent backend, no login. Apple (AAPL) 357.62, +0.63%, time 2026-11-12 10:40:59. hot_posts/hot_stocks need login and were not tested.
- **github** — `agent-reach github search "muse-reach" --limit 2`: ok via github-api. Live results, including JSxtrme/Muse-Reach itself (created 2026-11-12T15:08:46Z, description matches).
- **facebook (Muse-first)** — social.search, platform facebook: ok, 28 posts kept.
- **instagram (Muse-first)** — social.search, platform instagram: ok, 49 posts kept.
- **flipkart** — Meta Catalog search for "boAt Airdopes Plus 223 earbuds" with flipkart.com/amazon.in domain preference: ok, 3 products. Rank 1 is the real Flipkart listing: sale ₹1,199, MRP ₹3,499, 3.9 stars, 55,374 reviews, flipkart.com URL. browser.search also returns real Flipkart listings (₹999, crawled 2-5 days ago — not live). Live price still needs a live browser check.

### Partially working (Muse-first only)

- **linkedin** — browser.search "LinkedIn jobs software engineer India": real LinkedIn job listings, but via SmartRecruiters/Simplify mirrors, not linkedin.com direct. Site search still login-gated.
- **twitter / X** — browser.search finds public X posts via the search index (e.g. an X post about the Voxy Minecraft seed, reposted on Instagram). Direct x.com feed still login-gated.
- **reddit** — Muse browser.search is patchy: `site:reddit.com` query for a specific product review returned no results; a general query returned review roundups that mention Reddit, not direct posts. Agent-reach public-web still rate-limited (pause to ~21:24 IST, not retested). User screenshots remain the fallback.

### Broken — the big finding

- **Agent Reach's dedicated browser will not open at all (2026-11-12).** `agent-reach check` for twitter, facebook, instagram, linkedin, boss and xiaohongshu all fail identically with `UPSTREAM_BROKEN: the Agent Reach browser did not open: browser closed` (opencli backend; boss also fails on boss-agent-cli). This is NOT per-site login gating — the browser dies before reaching any site.
- Root cause, verified: a direct headless Chromium launch (`google-chrome --headless=new --dump-dom about:blank`) exits with `Hatch WebGL domain policy is required for browser startup`. `~/.agent-reach/browser/watcher.log` shows `Extensions.loadUnpacked failed: {'message': 'browser closed'}`. Muse's own browser is unaffected (it runs through Muse's harness, not a direct launch).
- Consequence: for facebook and instagram, Muse's own social search is now the *only* working path, not just the preferred one. For xiaohongshu and boss, there is no working path for direct notes/jobs — Muse search returns guides/background about the platforms only.
- `doctor` now includes a dedicated-browser launch check that reports this (it fails, so `doctor` currently exits 1 — that is the honest signal, not a bug).

### Not verified (could not be tested)

- **xiaoyuzhou** — `agent-reach check xiaoyuzhou` returned 0/0 actions. Transcribe needs a Groq key; none was supplied, and none will be invented. No test is possible without one.

### Router bug found and fixed in this pass

- `muse-reach.py exec bilibili hot` / `exec v2ex hot` returned BAD_INPUT: exec required a query argument, but `hot` takes none. Fixed: `NO_QUERY_ACTIONS = {"hot"}`, exec and `route` accept 2-arg calls for it, and exec no longer passes an empty `""` query to the agent-reach CLI (that broke the CLI with `unrecognized arguments`). Verified: `exec v2ex hot --limit 1` now returns a live topic.

### Not re-tested in this pass (deliberately)

- Reddit / web agent-reach backends: rate-limit pause expires ~21:24 IST; retesting before that would violate the stop rules. The Muse-first routes were tested instead.

## Expansion 2026-11-12 evening (~22:30-22:45 IST) — 14 new Muse-first-only channels

Owner asked for more social media platforms and more international shopping sites. All 14 are Muse-first-only: Agent Reach never had them, so there is no agent-reach backend to test — the router refuses `exec` for all of them (exit 3, with a Muse-tools hint). Router bumped to v0.2.0, 30 channels total. The route output key for shopping channels changed from `amazon_rule` to `shopping_rule`, now covering all 8 shopping channels.

### Now verified working

- **telegram** — browser.search `site:t.me anime download channel`: real public channel posts with full text (AniDL, AnimeTm Official, Dark Anime Hindi, crawled 2-4 days ago, t.me/s/ web view). Public channels only.
- **pinterest** — browser.search `site:pinterest.com anime wallpaper aesthetic`: real pin and idea pages with titles and topics (uk/in/ca/br/au Pinterest, freshest crawled 1-3 days ago). Public content only.
- **bluesky** — browser.search `site:bsky.app Minecraft post`: real public posts with full text, dates and likes (@gamingonlinux.com, @modrinth.com, @nineverything.bsky.social, crawled 8-66 days ago); per-profile RSS feeds exist. Direct public API (`public.api.bsky.app` searchPosts) returned HTTP 403 from this VM's curl — do NOT call the API from here; use the search index.
- **ebay** — browser.search `site:ebay.com wireless earbuds Bluetooth price`: real listings with USD prices, seller feedback and stock (JBL Vibe Beam $29.90, Sony WF-1000XM6 $177.99, Denon PerL $139.99, crawled 3-15 days ago). Note: a boAt Plus 223 query returned no results — India brand, not on eBay US. Prices are crawled, not live.
- **aliexpress** — browser.search `site:aliexpress.com wireless earbuds Bluetooth price`: real listings with USD prices (Soundcore Life P2 Mini $26.83, Lenovo GM2 Pro $7.80, ERAZER XT66PRO $5.71, crawled 2-8 days ago). Prices are crawled, not live.
- **etsy** — browser.search `site:etsy.com handmade anime keychain price`: real handmade listings with prices in USD/EUR/AUD and stock (JJK cat keychain $11.99, Kacchan phone charm $12.00, custom anime keychain $75.00+, crawled 4-25 days ago). Prices are crawled, not live.
- **shopee** — browser.search `Shopee wireless earbuds price Singapore`: real Shopee SG listings with SGD prices (Baseus BP1 Pro $28.24 SGD, UGREEN Dots $15.69 SGD, Skullcandy Rail ANC $99.80 SGD, crawled 2-10 days ago). Note: `site:shopee.sg` returned no results — use a plain query. Prices are crawled, not live.
- **temu** — browser.search `site:temu.com wireless earbuds price`: real listings with USD prices (TWS earbuds $5.97, AI translation earbuds $8.40, ear-clip earbuds $12.47, crawled 4-27 days ago). Prices are crawled, not live.

### Partially working (Muse-first only)

- **tiktok** — browser.search `site:tiktok.com Minecraft Voxy mod video`: real public TikTok videos found (@voxy.us, video 7704557589287144734, crawled 2-11 days ago). Cannot play or read a full video / feed without the app or login.
- **discord** — browser.search `discord server Minecraft Bedwars community invite`: real public server listings with member counts and invite links (Hypixel Bedwars 74,927 members, Rinaorc 76,083, Tier Tests 26,833) via discodus.com / discordbotlist.com, not discord.com direct. Messages need a Discord login.
- **mastodon** — browser.search `site:mastodon.social anime OR site:fosstodon.org Minecraft post`: real public posts via mastodon.social profiles and RSS feeds (e.g. @sleepychels, @RetroescentGaming), but crawls were stale (28-84 days) and search is instance-by-instance, not global. Public timeline API requires an authenticated user (`{"error":"This method requires an authenticated user"}`).
- **snapchat** — browser.search `Snapchat Spotlight Minecraft video`: real public Spotlight posts on snapchat.com profiles (@ecosmp Minecraft builds, posted Aug 2026; @onlyaboutgage Spotlight video). Stories, lenses and friends need the app/login.
- **mercadolibre** — browser.search `site:mercadolibre.com ...` returned no results; a plain query (`Mercado Libre audífonos inalámbricos precio`) returned listings only via resellers/aggregators (Latinafy, Karma) with USD prices, not mercadolibre.com direct. Direct site is JS/login-walled in the index.

### Not verified

- **threads** — social.search, platform threads, 3 queries (Minecraft Bedwars tips, anime edits AMV, tech gadgets India): returned 0 posts (stood_down, no_post_blocks). Not conclusively broken — may be query-dependent — but no result obtained yet.

### Considered, not added

- **wechat** (~1.4B users) — login-walled, China infrastructure, no public web path.
- **whatsapp** (~3B users) — messaging, not searchable.
- **taobao / jd** — China-only, login-walled, no public index path.

### Router changes in this pass

- 14 new entries in CHANNELS, all with `fallback: "none - Agent Reach has no <channel> channel"` and `exec` refused via EXEC_REFUSE (verified: `exec temu search "earbuds"` exits 3 with a Shopping-skill hint).
- Two `},,` typos introduced by the edit script (CHANNELS and EXEC_REFUSE) — caught by `py_compile`, fixed, recompiled clean. `channels --json` now lists 30 channels; `route bluesky search "Minecraft"` returns the correct Muse-first route.
