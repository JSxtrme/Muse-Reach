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
- bilibili, v2ex, xiaohongshu, xueqiu, boss, xiaoyuzhou were not live-tested 2026-11-12. Their status says so in `channels`.
- `exec` only runs youtube, github, bilibili and v2ex through agent-reach. Everything else is routing-only by design.

## Not done

- No GitHub repo created, nothing pushed. That is the user's next step when he is ready.
- No Flipkart live test (same honest route as Amazon, untested).
