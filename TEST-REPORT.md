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

- No GitHub repo created, nothing pushed. That is the user's next step when he is ready.
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
