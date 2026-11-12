<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/banner-white.png">
    <img src="assets/banner.png" alt="Muse Reach" width="480">
  </picture>
</p>

<p align="center"><strong>Give Muse by Meta eyes for the parts of the internet it can't reach on its own.</strong></p>

<p align="center">Read and search YouTube, Reddit, X, GitHub, Bilibili, Instagram, Facebook — and check real Amazon / Flipkart prices — with one router, zero API fees, and no pretending a blocked page is a real result.</p>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/tagline.png">
    <img src="assets/tagline-black.png" alt="Give Muse its own eyes" width="600">
  </picture>
</p>

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-green.svg)](muse-reach.py)
[![Read-only](https://img.shields.io/badge/Read--only-no%20posting%2C%20no%20buying-lightgrey.svg)](#safety)
[![Built for Muse by Meta](https://img.shields.io/badge/Built%20for-Muse%20by%20Meta-purple.svg)](#quick-start)

> **Muse here means Muse by Meta** — Meta's personal AI agent ([muse.ai](https://muse.ai)). Not any other product called Muse. Inspired by [Agent Reach](https://github.com/Panniantong/Agent-Reach) — the idea of one command for every platform, rebuilt from scratch for Muse instead of ported to it. Agent Reach is made for generic CLI agents. Muse Reach is made for Muse by Meta: it uses what Muse already has first, and only reaches for Agent Reach when Muse's own tools can't get there.

---

## Why Muse Reach exists

Muse already has web search, page reading, social search, and connectors. What it doesn't have is a single place that decides *which* of those to use for each site — and what to do when that site says no.

That's the gap this fills. Without it, every platform is a fresh guess: try the search, try a fetch, try Agent Reach, hope something sticks. With it, every site has a written route, in order, with an honest status next to it.

Muse Reach is for the cases Muse's built-in tools struggle with on their own:

- **Sites that need a login to search properly** — X, LinkedIn, Instagram, Xiaohongshu. It tells you plainly when that's the wall, instead of failing quietly.
- **Video content** — YouTube and Bilibili subtitles, and YouTube transcripts, where a normal page read only gives you a title and a description.
- **Posts and comments, not just headlines** — Reddit threads, Facebook pages, V2EX topics, with the body and the replies, not a summary of the page shell.
- **Shopping, worldwide** — Amazon.in and Flipkart, which Agent Reach never covered at all, plus eBay, AliExpress, Etsy, Shopee, Temu and Mercado Libre. Muse Reach adds them all, through the shopping route that actually works, not through scraping that doesn't.
- **Clean, structured answers** — GitHub repos and issues, stock quotes, job posts, returned as tidy results instead of raw HTML.

### ✅ Before you start, good to know

- **Which agent?** Muse by Meta. The skill (`SKILL.md`) and the router (`muse-reach.py`) are written for it. The router is plain Python, so anyone can read it, but the routes assume Muse's tools.
- **Does it touch your browser or accounts?** Only in the ways you approve. Logins happen in a browser window you control, never by Muse typing your password. It never reads your password store, and it never copies a login on its own.
- **Does it cost anything?** No. No API keys, no paid proxy, no subscription. The optional fallback is the free, open-source Agent Reach CLI.
- **Is it read-only?** Yes, always. It searches and reads. It never posts, comments, likes, DMs, adds to cart, or buys.

---

## Supported platforms

This is the current picture — 30 channels, checked 2026-11-12. Statuses change — platforms change their anti-bot rules, backends get rate-limited — so run `python3 muse-reach.py channels` for the live table, and check `TEST-REPORT.md` for the last verified run.

| Channel | What you can do | Needs | Status |
| --- | --- | --- | --- |
| github | Search repos, read a repo / README, read an issue or PR with comments | Nothing for public repos | ✔&#xFE0E; Working, verified 2026-11-12 |
| youtube | Search videos, read a video, get subtitles, transcribe audio | Nothing for public videos; transcription needs a Groq / OpenAI key | ✔&#xFE0E; Working, verified 2026-11-12 |
| bilibili | Search videos, read a video, trending, subtitles | Nothing; subtitles may need login | ✔&#xFE0E; Working, verified 2026-11-12 (slow — one router run hit the 30s backend timeout) |
| v2ex | Trending topics, a node, a topic with replies, a user | Nothing | ✔&#xFE0E; Working, verified 2026-11-12 |
| web | Search the web, read a page as clean text | Nothing | ✔&#xFE0E; Muse tools work; Agent Reach backend rate-limited (pause to ~21:24 IST, 2026-11-12) |
| xiaohongshu | Search notes, read a note, read comments | Login | ✘&#xFE0E; Agent Reach browser broken 2026-11-12 — Muse search gives background only, no direct notes |
| xueqiu | Live stock quotes, search stocks, trending posts / stocks | Quotes need no login; trending needs login | ✔&#xFE0E; Quotes working, verified 2026-11-12 (AAPL 357.62); trending needs login, not tested |
| boss | Search jobs, read a job description | Login | ✘&#xFE0E; Agent Reach browser broken 2026-11-12 (both backends) — no direct job listings |
| xiaoyuzhou | Transcribe a podcast episode | Groq key | ⏸&#xFE0E; Not verified — transcribe needs a Groq key, none supplied |
| linkedin | Search jobs, read a job description | Public jobs need no login; site search needs login | ⚠&#xFE0E; Agent Reach browser broken 2026-11-12; Muse search returns real LinkedIn jobs via SmartRecruiters / Simplify |
| reddit | Search posts, read a post with top comments, latest in a subreddit | Nothing for public posts | ⚠&#xFE0E; Rate-limited 2026-11-12 (HTTP 429, pause to ~21:24 IST); Muse search patchy for direct posts — user screenshots remain the fallback |
| twitter / X | Search tweets, a profile, a user's tweets, a thread with replies | Login | ⚠&#xFE0E; Agent Reach browser broken 2026-11-12; Muse search finds public X posts via the search index |
| facebook | Search, a page / profile | Login for full access | ✔&#xFE0E; Muse-first works — social.search returned 28 posts, 2026-11-12 (Agent Reach browser broken) |
| instagram | Search users, a profile, a user's posts | Login | ✔&#xFE0E; Muse-first works — social.search returned 49 posts, 2026-11-12 (Agent Reach browser broken) |
| amazon | Search products, read a product page | Nothing to read; buying needs your own checkout | **New** — live price only from live browser / catalog |
| flipkart | Search products, read a product page | Nothing to read; buying needs your own checkout | **New** — ✔&#xFE0E; catalog verified 2026-11-12 (real Flipkart listing, sale ₹1,199) |
| tiktok | Search public videos, read a video page | Nothing to find via search; watching needs the app / login | ⚠&#xFE0E; Partial — search finds real public videos (e.g. @voxy.us, 2026-11-12); full video / feed needs the app |
| threads | Search posts, read a post | Nothing for public posts via search | ⚠&#xFE0E; Unproven — social.search returned 0 posts on 2026-11-12; not conclusively broken |
| telegram | Search public channels, read channel posts | Nothing for public channels | ✔&#xFE0E; Working, verified 2026-11-12 — real public channel posts with full text (AniDL, AnimeTm) |
| discord | Find public servers, read a server listing | Nothing to find servers; reading messages needs login | ⚠&#xFE0E; Partial — search finds real server listings with member counts and invite links; messages need login |
| pinterest | Search pins and boards, read a pin page | Nothing for public pins via search | ✔&#xFE0E; Working, verified 2026-11-12 — real pin and idea pages (anime wallpapers) |
| bluesky | Search posts, read a post, read a profile feed | Nothing for public posts | ✔&#xFE0E; Working, verified 2026-11-12 — real public posts with full text and dates; direct API 403 from this VM, use search |
| mastodon | Search public posts across instances, read a profile feed | Nothing for public posts via search / RSS | ⚠&#xFE0E; Partial — real public posts found, but crawls were stale (28-84 days) and search is instance-by-instance |
| snapchat | Search public Spotlight posts, read a profile | Nothing for public Spotlight via search; stories need the app | ⚠&#xFE0E; Partial — real public Spotlight posts on snapchat.com profiles; stories / lenses need the app |
| ebay | Search listings, read a listing | Nothing to read; buying needs your own checkout | **New** — ✔&#xFE0E; verified 2026-11-12 (real listings, USD prices, crawled 3-15 days ago, not live) |
| aliexpress | Search listings, read a listing | Nothing to read; buying needs your own checkout | **New** — ✔&#xFE0E; verified 2026-11-12 (real listings, USD prices, crawled 2-8 days ago, not live) |
| etsy | Search handmade listings, read a listing | Nothing to read; buying needs your own checkout | **New** — ✔&#xFE0E; verified 2026-11-12 (real listings, USD/EUR/AUD prices, crawled 4-25 days ago, not live) |
| shopee | Search listings, read a listing | Nothing to read; buying needs your own checkout | **New** — ✔&#xFE0E; verified 2026-11-12 (real Shopee SG listings, SGD prices, crawled 2-10 days ago, not live) |
| temu | Search listings, read a listing | Nothing to read; buying needs your own checkout | **New** — ✔&#xFE0E; verified 2026-11-12 (real listings, USD prices, crawled 4-27 days ago, not live) |
| mercadolibre | Search listings, read a listing | Nothing to read; buying needs your own checkout | **New** — ⚠&#xFE0E; partial, 2026-11-12 — no direct listings in the index, only reseller / aggregator mirrors |

- **Working** means a live test passed. **Not tested** means the route exists but no live test was run that day — don't assume it works until one passes. **Login-gated** means the site itself demands a session Muse doesn't have. **Rate-limited** means the backend asked us to wait, and we do.

> **2026-11-12, big finding:** every Agent Reach channel that needs its dedicated browser (twitter, facebook, instagram, linkedin, boss, xiaohongshu — all via opencli) now fails before it even reaches the site: `the Agent Reach browser did not open: browser closed`. The cause is one level down — a direct Chromium launch on this machine now exits with `Hatch WebGL domain policy is required for browser startup` (see the `watcher.log`, and the new `doctor` check). Muse's own browser still works, because it runs through Muse's harness, not a direct launch. That is exactly why this project routes Muse-first: for facebook and instagram, Muse's own social search is now the *only* working path, not just the preferred one. If the dedicated browser starts working again, `doctor` will say so.

---

## Quick start

### The one-line way (in Muse)

Just say it in plain words:

```
Set up Muse Reach from https://github.com/JSxtrme/Muse-Reach
```

Muse will clone it, copy the skill into place, run `doctor`, and tell you which channels are actually working on your machine.

### The manual way

```bash
git clone https://github.com/JSxtrme/Muse-Reach.git
cd Muse-Reach

# Use it as a Muse skill:
mkdir -p ~/workspace/custom-skills/muse-reach
cp SKILL.md ~/workspace/custom-skills/muse-reach/SKILL.md

# Agent Reach is an optional fallback, not a requirement:
# https://github.com/Panniantong/Agent-Reach
```

No dependencies beyond Python 3.10+ — the router is standard library only. No keys, no accounts, no cookies to configure.

### First commands

```bash
python3 muse-reach.py channels
python3 muse-reach.py doctor            # cheap local checks only, no network
python3 muse-reach.py route youtube search "Voxy Minecraft" --limit 5
python3 muse-reach.py route reddit search "boAt Airdopes" --limit 5
python3 muse-reach.py route amazon search "boAt Airdopes Plus 223"
python3 muse-reach.py exec youtube search "Voxy Minecraft" --limit 2
```

In Muse itself, just ask normally — *"search Reddit for…"*, *"read this YouTube link"*, *"open this Amazon product"* — and the `muse-reach` skill picks the route.

---

## After it's set up

| You say | What happens |
| --- | --- |
| "Check Muse Reach status" | `doctor` for local setup, `channels` for every platform's status and route |
| "Add Xiaohongshu / Boss / Xueqiu" | That channel's fallback is enabled and its tools are checked; you'll be told only what *you* still need to do (log in, or supply a key yourself) |
| "My X login expired" / "Switch account" / "Log out" | The login window opens for *you* to sign in, or the stored session for that site is cleared |
| "Update Muse Reach" | The router and skill are updated, then `doctor` runs again and reports what changed |
| "Uninstall Muse Reach" | You'll see exactly what will be removed first, and nothing is deleted until you confirm |

---

## How it picks a route

Every channel is an ordered list, not a single tool. The router prints that list; Muse follows it from the top.

```
youtube search "…" 
  1. browser.search            <- Muse's own search first
  2. agent-reach youtube       <- yt-dlp, only if the first step missed the body / subtitles
```

That order is the whole design. Agent Reach on its own always starts at step 2 — Exa, Jina, OpenCLI — even when Muse's own search would have worked. Those shared backends are also the ones that get rate-limited first. Starting with Muse's tools means a Reddit or web search still works on a day Agent Reach's backend is paused, because Muse isn't sharing that backend's quota.

A platform changing its layout or blocking a tool is normal. When it happens, only that channel's list changes. How you ask doesn't change.

### What the router will and won't do

- `route <channel> <action> <query>` prints the route as JSON and fetches nothing. Safe to run any time.
- `exec` runs only the safe read-only backends — YouTube, GitHub, Bilibili, V2EX — through Agent Reach.
- `exec` **refuses** Amazon, Flipkart, Reddit, and web. Those must go through Muse's own tools, because direct fetching there is bot-blocked or rate-limited. Refusing is a feature, not a missing feature.
- `doctor` runs local checks only. It never hits the network and never re-tests a rate-limited channel.

---

## Amazon, honestly

This is the part most "open Amazon" tools are dishonest about, so here's the exact evidence, from 2026-11-12:

- Reading an amazon.in product page with a plain page reader returned a **344-day-old cached copy with no price on it**.
- Fetching the same page with `curl` returned HTTP 200 — but only **3,793 bytes, a bot-check shell**, not a product page.

A tool that quotes either of those as the current price is lying to you. Muse Reach doesn't.

So Amazon and Flipkart work like this, and only like this:

1. **Meta Catalog search** for the product across merchants.
2. **A live browser product search** for the live Amazon / Flipkart price, stock, seller, and delivery.
3. Price trackers (Smartprix, 91mobiles, pricehistory.app) as **corroboration only** — never as the live price.

A live price comes only from step 1 or 2. If neither runs, the answer is *"I couldn't verify the live price"*, not a stale number. Product URLs are never guessed or built from a product name — only URLs returned by a search, or supplied by you, are used. And buying is never done by a script: checkout happens in the live browser, by you.

---

## Safety

- **Read-only.** Searching and reading only. No posting, commenting, liking, DMing, or buying.
- **Never logs in for you.** It never asks for, stores, or types a password or a cookie. When a site needs a login, you log in yourself in your own browser window.
- **Keys stay with you.** If transcription needs a Groq or OpenAI key, you enter it in your own terminal. Never paste a key into chat.
- **Stop means stop.** On `RATE_LIMITED`, `PLATFORM_BLOCKED`, `NEED_LOGIN`, or `BUSY`, that channel stops. What was already found is still handed over, but there is no switching backends to dodge the block, no CAPTCHA bypass, no loop of retries, and no second browser opened to get around it. A rate limit comes with a pause — the pause is respected.
- **Nothing personal in the repo.** No profiles, sessions, cookies, credentials, or keys are ever committed. See `.gitignore`.

### 🗑️ Uninstall

Say "uninstall Muse Reach". You'll be shown what will be removed — the skill, the router, and any per-site sessions — and nothing is deleted until you confirm. Your other files and your browser are untouched.

---

## Acknowledgements

- [Agent Reach](https://github.com/Panniantong/Agent-Reach) for the original idea: one command, every platform, free. Muse Reach borrows that shape and rebuilds the inside for Muse by Meta.
- [yt-dlp](https://github.com/yt-dlp/yt-dlp), bili-cli, OpenCLI, Jina Reader, and Exa — the backends Agent Reach assembles, which Muse Reach falls back to where they still work.
- Muse's own search, page reader, social search, and connectors — the first step of every route here.

## License

MIT. See [LICENSE](LICENSE).
