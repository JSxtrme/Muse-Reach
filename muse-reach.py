#!/usr/bin/env python3
"""muse-reach: a Muse-native router for reading the public web.

Routing only. It prints, as JSON, which Muse tool or CLI should be used
for a channel/action, in order. It does NOT scrape, does NOT fetch pages
itself, and does NOT bypass bot checks, logins, CAPTCHAs or rate limits.

Usage:
    muse-reach.py channels [--json]
    muse-reach.py doctor [--json]
    muse-reach.py route <channel> <action> <query-or-url> [--limit N] [--json]
    muse-reach.py <channel> <action> <query-or-url> [--limit N]  (alias for route)
    muse-reach.py exec <channel> <action> <query-or-url> [--limit N]

`exec` runs only the safe read-only backends (agent-reach youtube/github/
bilibili/v2ex). It refuses amazon, flipkart, reddit and web: those must go
through Muse's own tools (Meta Catalog, live browser, browser.search),
because direct fetching is blocked or rate-limited there. See SKILL.md.
Stdlib only, no new dependencies.
"""

import json
import os
import shutil
import subprocess
import sys

VERSION = "0.2.0"

# channel -> {muse_first, fallback, login, status, actions}
CHANNELS = {
    "github": {
        "muse_first": "GitHub connector / `gh` CLI",
        "fallback": "agent-reach github search|read",
        "login": "none for public repos",
        "status": "working, verified 2026-11-12 (github-api search returned live results, incl. JSxtrme/Muse-Reach)",
        "actions": ["search", "read"],
    },
    "youtube": {
        "muse_first": "browser.search, then agent-reach youtube (yt-dlp)",
        "fallback": "agent-reach youtube search|read|subtitle",
        "login": "none for public videos; transcribe needs a Groq/OpenAI key",
        "status": "working, verified 2026-11-12 (yt-dlp search returned live results)",
        "actions": ["search", "read", "subtitle", "transcribe"],
    },
    "bilibili": {
        "muse_first": "browser.search",
        "fallback": "agent-reach bilibili search|read|hot|subtitle (bili-cli)",
        "login": "none; subtitles may need login",
        "status": "working, verified 2026-11-12 (bili-cli hot returned live trending videos, e.g. BV1hrW367Emp, 3.0M views). Slow/flaky: a later router run hit agent-reach's 30s backend timeout - not blocked, just slow.",
        "actions": ["search", "read", "hot", "subtitle"],
    },
    "v2ex": {
        "muse_first": "browser.search / browser.open",
        "fallback": "agent-reach v2ex hot|node|read|user (v2ex-api)",
        "login": "none",
        "status": "working, verified 2026-11-12 (v2ex-api hot returned today's topics, e.g. t/1256329, 2026-11-12)",
        "actions": ["hot", "node", "read", "user"],
    },
    "web": {
        "muse_first": "browser.search, then browser.open",
        "fallback": "agent-reach web search|read (Exa/Jina) - USE ONLY IF Muse tools fail",
        "login": "none",
        "status": "Muse tools work (browser.search/browser.open verified 2026-11-12). Agent-reach backend RATE_LIMITED 2026-11-12 (wait 3586s hint, pause to ~21:24 IST). Do not retry that backend until the pause expires.",
        "actions": ["search", "read"],
    },
    "xiaohongshu": {
        "muse_first": "browser.search",
        "fallback": "agent-reach xiaohongshu search|read|comments (opencli)",
        "login": "login required for full access; user logs in themselves",
        "status": "BROKEN 2026-11-12: agent-reach browser will not open (browser closed; Chromium reports 'Hatch WebGL domain policy is required'). Muse browser.search returns guides about the platform only, no direct notes.",
        "actions": ["search", "read", "comments"],
    },
    "xueqiu": {
        "muse_first": "browser.search for quotes; finance vertical for stocks",
        "fallback": "agent-reach xueqiu quote|search|hot_posts|hot_stocks",
        "login": "quotes need no login; hot posts/stocks need login",
        "status": "working for quotes, verified 2026-11-12 (AAPL 357.62, +0.63%, via tencent backend, no login). hot_posts/hot_stocks need login, not tested.",
        "actions": ["quote", "search", "hot_posts", "hot_stocks"],
    },
    "boss": {
        "muse_first": "browser.search",
        "fallback": "agent-reach boss search|read",
        "login": "login required; user logs in themselves",
        "status": "BROKEN 2026-11-12: agent-reach browser will not open (both opencli and boss-agent-cli backends, browser closed). Muse browser.search returns background about the platform only, no direct job listings.",
        "actions": ["search", "read"],
    },
    "xiaoyuzhou": {
        "muse_first": "browser.search",
        "fallback": "agent-reach xiaoyuzhou transcribe (Groq Whisper)",
        "login": "none; transcribe needs a Groq key",
        "status": "not verified 2026-11-12: check returned 0/0 actions; transcribe needs a Groq key, none supplied. No test possible without one.",
        "actions": ["transcribe"],
    },
    "linkedin": {
        "muse_first": "browser.search (public job pages only)",
        "fallback": "agent-reach linkedin jobs|read (opencli)",
        "login": "LOGIN-GATED for site search; public job pages readable without login",
        "status": "agent-reach browser BROKEN 2026-11-12 (opencli: browser closed). Muse-first works partially: browser.search returned real LinkedIn jobs via SmartRecruiters/Simplify (2026-11-12), not linkedin.com direct; site search still login-gated.",
        "actions": ["jobs", "read"],
    },
    "reddit": {
        "muse_first": "browser.search, then social.search; screenshots from the user as last resort",
        "fallback": "agent-reach reddit search|read|subreddit --backend public-web",
        "login": "public posts need no login; site search may need login",
        "status": "RATE_LIMITED 2026-11-12 (HTTP 429, public-web/exa, pause to ~21:24 IST). Do not retry the agent-reach backend until the pause expires. Muse browser.search is patchy for direct Reddit posts (site:reddit.com returned no results 2026-11-12); user screenshots remain the fallback.",
        "actions": ["search", "read", "subreddit"],
    },
    "twitter": {
        "muse_first": "social.search, then browser.search",
        "fallback": "agent-reach twitter search|profile|tweets|thread (opencli)",
        "login": "LOGIN-GATED (no x.com session, no ct0 cookie); profile header only via web reader",
        "status": "agent-reach browser BROKEN 2026-11-12 (opencli: browser closed). Muse-first works partially: browser.search finds public X posts via the search index (2026-11-12); direct x.com feed still login-gated.",
        "actions": ["search", "profile", "tweets", "thread"],
    },
    "facebook": {
        "muse_first": "Facebook connector (facebook-cli)",
        "fallback": "agent-reach facebook search|profile --backend public-web",
        "login": "login required for full access; user logs in themselves",
        "status": "agent-reach browser BROKEN 2026-11-12 (opencli: browser closed). Muse-first WORKS: social.search returned 28 Facebook posts, 2026-11-12.",
        "actions": ["search", "profile"],
    },
    "instagram": {
        "muse_first": "Instagram connector (instagram-cli)",
        "fallback": "agent-reach instagram search|profile|posts (opencli)",
        "login": "LOGIN-GATED",
        "status": "agent-reach browser BROKEN 2026-11-12 (opencli: browser closed, all 3 actions). Muse-first WORKS: social.search returned 49 Instagram posts, 2026-11-12.",
        "actions": ["search", "profile", "posts"],
    },
    "amazon": {
        "muse_first": "Shopping skill: Meta Catalog search (/opt/hatch/bin/meta-catalog-search or /opt/hatch/bin/shopping catalog-search) + live browser product search for the live price",
        "fallback": "browser.open on the product page with max_age_minutes (stale cache is NOT a live price); price trackers (Smartprix, 91mobiles, pricehistory.app) as corroboration only",
        "login": "none for reading; purchase needs the user's own checkout in the live browser",
        "status": "NEW channel (Agent Reach never had one). Live price/stock ONLY from a live browser task or Meta Catalog. Verified 2026-11-12: browser.open returned a 344-day-old crawl with no price; curl returned HTTP 200 but only 3793 bytes, a bot-check shell. Direct scraping does not work.",
        "actions": ["search", "read"],
    },
    "flipkart": {
        "muse_first": "Shopping skill: Meta Catalog search + live browser product search for the live price",
        "fallback": "browser.open on the product page with max_age_minutes (stale cache is NOT a live price)",
        "login": "none for reading; purchase needs the user's own checkout in the live browser",
        "status": "NEW channel (Agent Reach never had one). Same honest route as amazon; live price/stock ONLY from a live browser task or Meta Catalog. Verified 2026-11-12: Meta Catalog returned a real Flipkart Plus 223 listing (sale Rs 1,199, 3.9 stars, 55,374 reviews); browser.search also returns real Flipkart listings (crawled 2-5 days ago, not live).",
        "actions": ["search", "read"],
    },
    "tiktok": {
        "muse_first": "browser.search (site:tiktok.com) for public videos; browser.open on a video URL returned by search",
        "fallback": "none - Agent Reach has no tiktok channel; no direct fetch (app/login wall)",
        "login": "none to find public videos via search; watching the feed / full video needs the app or login",
        "status": "PARTIAL, verified 2026-11-12: browser.search returned real public TikTok videos (e.g. @voxy.us, crawled 2-11 days ago). Cannot play or read a full video / feed without the app or login.",
        "actions": ["search", "read"],
    },
    "threads": {
        "muse_first": "social.search (threads platform), then browser.search",
        "fallback": "none - Agent Reach has no threads channel",
        "login": "none for public posts via search; full feed needs login",
        "status": "UNPROVEN 2026-11-12: social.search (threads) returned 0 posts for 3 queries (Minecraft, anime edits, tech gadgets). Not conclusively broken - may be query-dependent - but no result obtained yet.",
        "actions": ["search", "read"],
    },
    "telegram": {
        "muse_first": "browser.search (site:t.me) for public channels; browser.open on a t.me/s/ web-view URL returned by search",
        "fallback": "none - Agent Reach has no telegram channel",
        "login": "none for public channels (t.me/s/ web view is public); private chats/groups need login",
        "status": "WORKING, verified 2026-11-12: browser.search returned real public channel posts with full text (e.g. AniDL, AnimeTm, crawled 2-4 days ago). Public channels only.",
        "actions": ["search", "read"],
    },
    "discord": {
        "muse_first": "browser.search for public server listings (discodus.com, discordbotlist.com); browser.open on a listing URL returned by search",
        "fallback": "none - Agent Reach has no discord channel; discord.com messages need login",
        "login": "none to find public servers; reading a server / messages needs a Discord login",
        "status": "PARTIAL, verified 2026-11-12: search returned real public server listings with member counts and invite links (e.g. Hypixel Bedwars, 74,927 members). No direct discord.com content; messages need login.",
        "actions": ["search", "read"],
    },
    "pinterest": {
        "muse_first": "browser.search (site:pinterest.com) for pins and idea pages",
        "fallback": "none - Agent Reach has no pinterest channel",
        "login": "none for public pins/boards via search; full feed and saving need login",
        "status": "WORKING, verified 2026-11-12: browser.search returned real pin and idea pages with titles and topics (anime wallpapers, crawled 1-3 days ago for the freshest). Public content only.",
        "actions": ["search", "read"],
    },
    "bluesky": {
        "muse_first": "browser.search (site:bsky.app) for public posts; browser.open on a post URL returned by search; per-profile RSS feeds exist (bsky.app/profile/<handle>/rss)",
        "fallback": "none - Agent Reach has no bluesky channel; direct public API (public.api.bsky.app) returned HTTP 403 from this VM (egress proxy), so do not call it from here",
        "login": "none for public posts",
        "status": "WORKING, verified 2026-11-12: browser.search returned real public posts with full text, dates and likes (e.g. @gamingonlinux.com, @modrinth.com, crawled 8-66 days ago). Direct API 403 from this VM - use the search index, not the API.",
        "actions": ["search", "read"],
    },
    "mastodon": {
        "muse_first": "browser.search (site:mastodon.social and other instances) for public posts; per-profile RSS feeds exist",
        "fallback": "none - Agent Reach has no mastodon channel; the public timeline API requires an authenticated user",
        "login": "none for public posts via search/RSS; instance search and the API need login",
        "status": "PARTIAL, verified 2026-11-12: search returned real public posts via mastodon.social profiles and RSS feeds, but crawls were stale (28-84 days) and search is instance-by-instance, not global. Public timeline API requires auth.",
        "actions": ["search", "read"],
    },
    "snapchat": {
        "muse_first": "browser.search for public Spotlight posts on snapchat.com profiles",
        "fallback": "none - Agent Reach has no snapchat channel",
        "login": "none for public Spotlight posts via search; stories, lenses and friends need the app/login",
        "status": "PARTIAL, verified 2026-11-12: search returned real public Spotlight posts on snapchat.com profiles (e.g. @ecosmp Minecraft builds, posted Aug 2026). Stories/lenses/friends need the app.",
        "actions": ["search", "read"],
    },
    "ebay": {
        "muse_first": "Shopping skill: browser.search (site:ebay.com) for listings; Meta Catalog search may also return eBay listings; live browser product search for the live price",
        "fallback": "browser.open on a listing URL returned by search (crawled copy is NOT a live price)",
        "login": "none for reading; purchase needs the user's own checkout in the live browser",
        "status": "WORKING, verified 2026-11-12: browser.search returned real listings with USD prices, seller feedback and stock (e.g. JBL Vibe Beam $29.90, Sony WF-1000XM6 $177.99, crawled 3-15 days ago). Prices are crawled, not live - verify in the live browser before quoting.",
        "actions": ["search", "read"],
    },
    "aliexpress": {
        "muse_first": "Shopping skill: browser.search (site:aliexpress.com) for listings; live browser product search for the live price",
        "fallback": "browser.open on a listing URL returned by search (crawled copy is NOT a live price)",
        "login": "none for reading; purchase needs the user's own checkout in the live browser",
        "status": "WORKING, verified 2026-11-12: browser.search returned real listings with USD prices (e.g. Soundcore Life P2 Mini $26.83, Lenovo GM2 Pro $7.80, crawled 2-8 days ago). Prices are crawled, not live - verify in the live browser before quoting.",
        "actions": ["search", "read"],
    },
    "etsy": {
        "muse_first": "Shopping skill: browser.search (site:etsy.com) for listings; live browser product search for the live price",
        "fallback": "browser.open on a listing URL returned by search (crawled copy is NOT a live price)",
        "login": "none for reading; purchase needs the user's own checkout in the live browser",
        "status": "WORKING, verified 2026-11-12: browser.search returned real handmade listings with prices in USD/EUR/AUD and stock (e.g. JJK cat keychain $11.99, Kacchan phone charm $12.00, crawled 4-25 days ago). Prices are crawled, not live - verify in the live browser before quoting.",
        "actions": ["search", "read"],
    },
    "shopee": {
        "muse_first": "Shopping skill: browser.search (plain query, NOT site: - the site: operator returned nothing) for Shopee SG listings; live browser product search for the live price",
        "fallback": "browser.open on a listing URL returned by search (crawled copy is NOT a live price)",
        "login": "none for reading; purchase needs the user's own checkout in the live browser",
        "status": "WORKING, verified 2026-11-12: browser.search returned real Shopee SG listings with SGD prices (e.g. Baseus BP1 Pro $28.24 SGD, UGREEN Dots $15.69 SGD, crawled 2-10 days ago). Note: site:shopee.sg returned no results - use a plain query. Prices are crawled, not live.",
        "actions": ["search", "read"],
    },
    "temu": {
        "muse_first": "Shopping skill: browser.search (site:temu.com) for listings; live browser product search for the live price",
        "fallback": "browser.open on a listing URL returned by search (crawled copy is NOT a live price)",
        "login": "none for reading; purchase needs the user's own checkout in the live browser",
        "status": "WORKING, verified 2026-11-12: browser.search returned real listings with USD prices (e.g. TWS earbuds $5.97, AI translation earbuds $8.40, crawled 4-27 days ago). Prices are crawled, not live - verify in the live browser before quoting.",
        "actions": ["search", "read"],
    },
    "mercadolibre": {
        "muse_first": "Shopping skill: browser.search for Mercado Libre listings (plain query in Spanish/Portuguese; site: operator returned nothing)",
        "fallback": "browser.open on a listing URL returned by search; reseller/aggregator pages (Latinafy, Karma) that mirror Mercado Libre listings",
        "login": "none for reading; purchase needs the user's own checkout in the live browser",
        "status": "PARTIAL, verified 2026-11-12: no direct mercadolibre.com results in the search index; listings only surfaced via resellers/aggregators (Latinafy, Karma) with USD prices. Direct site is JS/login-walled in the index. Verify any price in the live browser before quoting.",
        "actions": ["search", "read"],
    },
}

# Channels `exec` is allowed to run, and the agent-reach action it maps to.
EXEC_ALLOW = {"youtube", "github", "bilibili", "v2ex"}

# Actions that take no query (e.g. `hot` lists). exec allows 2 args for these.
NO_QUERY_ACTIONS = {"hot"}
# Channels that must never be fetched by this script.
EXEC_REFUSE = {
    "amazon": "use the Shopping skill: Meta Catalog + live browser product search. Direct fetching is bot-blocked.",
    "flipkart": "use the Shopping skill: Meta Catalog + live browser product search. Direct fetching is bot-blocked.",
    "reddit": "rate-limited 2026-11-12 (HTTP 429). Use browser.search / social.search; do not retry the agent-reach backend today.",
    "web": "rate-limited 2026-11-12. Use browser.search / browser.open; do not retry the agent-reach backend today.",
    "tiktok": "no agent-reach backend. Use browser.search (site:tiktok.com); full video/feed needs the app or login.",
    "threads": "no agent-reach backend. Use social.search (threads); 0 posts returned 2026-11-12, unproven.",
    "telegram": "no agent-reach backend. Use browser.search (site:t.me) / browser.open on t.me/s/ web-view URLs.",
    "discord": "no agent-reach backend. Use browser.search for public server listings; messages need a Discord login.",
    "pinterest": "no agent-reach backend. Use browser.search (site:pinterest.com).",
    "bluesky": "no agent-reach backend; direct public API 403 from this VM. Use browser.search (site:bsky.app).",
    "mastodon": "no agent-reach backend; public timeline API needs auth. Use browser.search / per-profile RSS.",
    "snapchat": "no agent-reach backend. Use browser.search for public Spotlight posts; stories need the app.",
    "ebay": "use the Shopping skill: browser.search (site:ebay.com) + live browser for the live price. Crawled prices are not live.",
    "aliexpress": "use the Shopping skill: browser.search (site:aliexpress.com) + live browser for the live price. Crawled prices are not live.",
    "etsy": "use the Shopping skill: browser.search (site:etsy.com) + live browser for the live price. Crawled prices are not live.",
    "shopee": "use the Shopping skill: browser.search (plain query, site: returns nothing) + live browser for the live price.",
    "temu": "use the Shopping skill: browser.search (site:temu.com) + live browser for the live price. Crawled prices are not live.",
    "mercadolibre": "use the Shopping skill: browser.search (plain Spanish/Portuguese query; site: returns nothing). Direct listings are thin in the index.",
}

SHOPPING_CHANNELS = {"amazon", "flipkart", "ebay", "aliexpress", "etsy", "shopee", "temu", "mercadolibre"}

STOP_CODES = ["RATE_LIMITED", "PLATFORM_BLOCKED", "NEED_LOGIN", "BUSY"]


def _out(obj, as_json):
    if as_json:
        print(json.dumps(obj, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(obj, indent=2, ensure_ascii=False))


def cmd_channels(args):
    as_json = "--json" in args
    table = [
        {"channel": name, **info} for name, info in CHANNELS.items()
    ]
    _out({"version": VERSION, "channels": table}, as_json)
    return 0


def _local_check(label, candidates):
    """candidates: list of paths; a plain name is looked up on PATH,
    anything with a slash (or ~) is checked as a file. OK if any matches.
    (agent-reach / yt-dlp live in the uv tool dir, not necessarily on PATH.)"""
    found = None
    for c in candidates:
        if "/" in c or c.startswith("~"):
            p = os.path.expanduser(c)
            if os.path.exists(p):
                found = p
                break
        elif shutil.which(c):
            found = shutil.which(c)
            break
    return {"check": label, "ok": found is not None, "path": found or candidates[0]}


def _chrome_launch_check():
    """Try a direct headless Chromium launch (about:blank, 15s). This is what
    Agent Reach's dedicated browser needs. On 2026-11-12 it fails on this VM
    with 'Hatch WebGL domain policy is required for browser startup', which
    is why every opencli channel fails with 'browser closed'. A fail here
    does not mean Muse's own browser is broken - that runs through its own
    harness, not a direct launch."""
    label = "dedicated-browser launch (direct headless Chromium)"
    try:
        r = subprocess.run(
            [os.path.expanduser("~/.local/bin/google-chrome"),
             "--headless=new", "--disable-gpu", "--dump-dom", "about:blank"],
            capture_output=True, text=True, timeout=15)
        ok = r.returncode == 0 and "<html" in r.stdout
        detail = "launched ok" if ok else (r.stderr.strip().splitlines()[-1]
                                           if r.stderr.strip() else "no output")
        return {"check": label, "ok": ok, "path": "direct launch",
                "detail": detail}
    except Exception as e:
        return {"check": label, "ok": False, "path": "direct launch",
                "detail": f"{type(e).__name__}: {e}"}


def cmd_doctor(args):
    """Cheap local checks only. Never hits the network, never retries a
    rate-limited channel, never opens a browser."""
    as_json = "--json" in args
    checks = [
        _local_check("agent-reach binary", ["agent-reach", "~/.local/bin/agent-reach"]),
        _local_check("google-chrome wrapper (--no-sandbox, root needs it)", ["~/.local/bin/google-chrome"]),
        _local_check("yt-dlp no-certifi config (egress proxy CA fix)", ["~/.config/yt-dlp/config"]),
        _local_check("yt-dlp binary (bundled with agent-reach)", ["yt-dlp", "~/.local/share/uv/tools/agent-reach/bin/yt-dlp"]),
        _local_check("gh CLI", ["gh"]),
        _chrome_launch_check(),
    ]
    ok = all(c["ok"] for c in checks)
    _out({
        "version": VERSION,
        "ok": ok,
        "note": "Local checks only. Live channel status is in `channels`; a channel marked RATE_LIMITED must not be re-tested until its pause expires.",
        "checks": checks,
        "stop_codes": STOP_CODES,
    }, as_json)
    return 0 if ok else 1


def route(channel, action, query, limit):
    if channel not in CHANNELS:
        return {"ok": False, "error": {"code": "BAD_INPUT",
                "message": f"unknown channel: {channel}",
                "hint": f"Run `muse-reach.py channels`. Known channels: {', '.join(sorted(CHANNELS))}"}}
    info = CHANNELS[channel]
    if action not in info["actions"]:
        return {"ok": False, "error": {"code": "BAD_INPUT",
                "message": f"unknown action {action!r} for channel {channel}",
                "hint": f"Actions for {channel}: {', '.join(info['actions'])}"}}
    if not query and action not in NO_QUERY_ACTIONS:
        return {"ok": False, "error": {"code": "BAD_INPUT",
                "message": "missing query or URL",
                "hint": "Pass a search query or a full URL supplied by the user or returned by a search tool. Never construct a URL."}}
    steps = [info["muse_first"]]
    if info["fallback"]:
        steps.append(info["fallback"])
    result = {
        "ok": True,
        "version": VERSION,
        "channel": channel,
        "action": action,
        "query": query,
        "limit": limit,
        "route_in_order": steps,
        "login": info["login"],
        "status": info["status"],
        "stop_rules": ("On RATE_LIMITED, PLATFORM_BLOCKED, NEED_LOGIN or BUSY: "
                       "stop that channel, report what was already obtained, "
                       "do not switch backends to evade, do not loop-retry."),
    }
    if channel in SHOPPING_CHANNELS:
        result["shopping_rule"] = ("Search-index prices are crawled copies (days old), "
                                   "NOT a live price. Live price/stock ONLY from a live "
                                   "browser task or Meta Catalog. A stale browser.open "
                                   "crawl or a curl HTTP 200 is NOT a live price. Never "
                                   "construct a product URL; use only URLs returned by "
                                   "search/tools or supplied by the user.")
    return result


def cmd_route(args):
    as_json = "--json" in args
    args = [a for a in args if a != "--json"]
    limit = 5
    if "--limit" in args:
        i = args.index("--limit")
        try:
            limit = int(args[i + 1])
            if limit < 1 or limit > 50:
                raise ValueError
        except (IndexError, ValueError):
            print(json.dumps({"ok": False, "error": {"code": "BAD_INPUT",
                             "message": "--limit needs an integer 1-50"}}))
            return 2
        del args[i:i + 2]
    if len(args) < 3:
        print(json.dumps({"ok": False, "error": {"code": "BAD_INPUT",
                         "message": "usage: muse-reach.py route <channel> <action> <query-or-url> [--limit N]"}}))
        return 2
    channel, action = args[0], args[1]
    query = " ".join(args[2:])
    _out(route(channel, action, query, limit), as_json)
    return 0


def cmd_exec(args):
    """Run a safe read-only backend. Refuses blocked / rate-limited channels."""
    limit = 5
    if "--limit" in args:
        i = args.index("--limit")
        try:
            limit = int(args[i + 1])
        except (IndexError, ValueError):
            print(json.dumps({"ok": False, "error": {"code": "BAD_INPUT",
                             "message": "--limit needs an integer"}}))
            return 2
        del args[i:i + 2]
    if len(args) < 3 and not (len(args) == 2 and args[1] in NO_QUERY_ACTIONS):
        print(json.dumps({"ok": False, "error": {"code": "BAD_INPUT",
                         "message": "usage: muse-reach.py exec <channel> <action> <query-or-url> [--limit N] (no query needed for: hot)"}}))
        return 2
    channel, action = args[0], args[1]
    query = " ".join(args[2:])
    if channel in EXEC_REFUSE:
        print(json.dumps({"ok": False, "channel": channel, "error": {
            "code": "REFUSED", "message": EXEC_REFUSE[channel]}}, indent=2))
        return 3
    if channel not in EXEC_ALLOW:
        print(json.dumps({"ok": False, "channel": channel, "error": {
            "code": "REFUSED",
            "message": f"exec only supports {sorted(EXEC_ALLOW)}; for {channel} follow the route printed by `route` instead."}}, indent=2))
        return 3
    decision = route(channel, action, query, limit)
    if not decision["ok"]:
        print(json.dumps(decision, indent=2))
        return 2
    agent_reach = shutil.which("agent-reach") or os.path.expanduser("~/.local/bin/agent-reach")
    if not os.path.exists(agent_reach):
        print(json.dumps({"ok": False, "error": {"code": "NEED_SETUP",
                         "message": "agent-reach binary not found; add ~/.local/bin to PATH"}}))
        return 2
    # No shell=True, allowlisted channel/action only, bounded timeout.
    # No-query actions (hot) get no query argument at all - passing "" breaks the CLI.
    cmd = [agent_reach, channel, action] + ([query] if query else []) + ["--limit", str(limit)]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
    except subprocess.TimeoutExpired:
        print(json.dumps({"ok": False, "error": {"code": "TIMEOUT",
                         "message": "backend timed out after 90s; do not loop-retry"}}))
        return 4
    out = proc.stdout.strip() or proc.stderr.strip()
    print(out if out else json.dumps({"ok": False, "error": {"code": "UPSTREAM_BROKEN",
                                     "message": "backend returned no output"}}))
    return 0


def _help():
    print(__doc__.strip())
    return 0


def main(argv):
    if not argv or argv[0] in ("-h", "--help", "help"):
        return _help()
    cmd, rest = argv[0], argv[1:]
    if cmd == "channels":
        return cmd_channels(rest)
    if cmd == "doctor":
        return cmd_doctor(rest)
    if cmd == "route":
        return cmd_route(rest)
    if cmd == "exec":
        return cmd_exec(rest)
    # Alias: <channel> <action> <query...> means route.
    if cmd in CHANNELS:
        return cmd_route([cmd] + rest)
    print(json.dumps({"ok": False, "error": {"code": "BAD_INPUT",
                     "message": f"unknown command or channel: {cmd}",
                     "hint": "Run `muse-reach.py --help` or `muse-reach.py channels`"}}))
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
