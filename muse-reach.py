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

VERSION = "0.1.0"

# channel -> {muse_first, fallback, login, status, actions}
CHANNELS = {
    "github": {
        "muse_first": "GitHub connector / `gh` CLI",
        "fallback": "agent-reach github search|read",
        "login": "none for public repos",
        "status": "working via GitHub connector; CLI not re-tested 2026-11-12",
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
        "status": "not tested 2026-11-12",
        "actions": ["search", "read", "hot", "subtitle"],
    },
    "v2ex": {
        "muse_first": "browser.search / browser.open",
        "fallback": "agent-reach v2ex hot|node|read|user (v2ex-api)",
        "login": "none",
        "status": "not tested 2026-11-12",
        "actions": ["hot", "node", "read", "user"],
    },
    "web": {
        "muse_first": "browser.search, then browser.open",
        "fallback": "agent-reach web search|read (Exa/Jina) - USE ONLY IF Muse tools fail",
        "login": "none",
        "status": "RATE_LIMITED 2026-11-12 (agent-reach backend, wait 3586s hint). Do not retry that backend today; use browser.search/browser.open.",
        "actions": ["search", "read"],
    },
    "xiaohongshu": {
        "muse_first": "browser.search",
        "fallback": "agent-reach xiaohongshu search|read|comments (opencli)",
        "login": "login required for full access; user logs in themselves",
        "status": "not added / not verified",
        "actions": ["search", "read", "comments"],
    },
    "xueqiu": {
        "muse_first": "browser.search for quotes; finance vertical for stocks",
        "fallback": "agent-reach xueqiu quote|search|hot_posts|hot_stocks",
        "login": "quotes need no login; hot posts/stocks need login",
        "status": "not added / not verified",
        "actions": ["quote", "search", "hot_posts", "hot_stocks"],
    },
    "boss": {
        "muse_first": "browser.search",
        "fallback": "agent-reach boss search|read",
        "login": "login required; user logs in themselves",
        "status": "not added / not verified",
        "actions": ["search", "read"],
    },
    "xiaoyuzhou": {
        "muse_first": "browser.search",
        "fallback": "agent-reach xiaoyuzhou transcribe (Groq Whisper)",
        "login": "none; transcribe needs a Groq key",
        "status": "not added / not verified",
        "actions": ["transcribe"],
    },
    "linkedin": {
        "muse_first": "browser.search (public job pages only)",
        "fallback": "agent-reach linkedin jobs|read (opencli)",
        "login": "LOGIN-GATED for site search; public job pages readable without login",
        "status": "login-gated, verified 2026-10-27",
        "actions": ["jobs", "read"],
    },
    "reddit": {
        "muse_first": "browser.search, then social.search; screenshots from the user as last resort",
        "fallback": "agent-reach reddit search|read|subreddit --backend public-web",
        "login": "public posts need no login; site search may need login",
        "status": "RATE_LIMITED 2026-11-12 (HTTP 429, public-web/exa). Do not retry today; use browser.search/social.search.",
        "actions": ["search", "read", "subreddit"],
    },
    "twitter": {
        "muse_first": "social.search, then browser.search",
        "fallback": "agent-reach twitter search|profile|tweets|thread (opencli)",
        "login": "LOGIN-GATED (no x.com session, no ct0 cookie); profile header only via web reader",
        "status": "login-gated, verified 2026-10-27",
        "actions": ["search", "profile", "tweets", "thread"],
    },
    "facebook": {
        "muse_first": "Facebook connector (facebook-cli)",
        "fallback": "agent-reach facebook search|profile --backend public-web",
        "login": "login required for full access; user logs in themselves",
        "status": "public-web search worked 2026-10-27; not re-tested 2026-11-12",
        "actions": ["search", "profile"],
    },
    "instagram": {
        "muse_first": "Instagram connector (instagram-cli)",
        "fallback": "agent-reach instagram search|profile|posts (opencli)",
        "login": "LOGIN-GATED",
        "status": "broken on test 2026-10-27 (Failed to fetch); not re-tested 2026-11-12",
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
        "status": "NEW channel (Agent Reach never had one). Same honest route as amazon; live price/stock ONLY from a live browser task or Meta Catalog. Not live-tested 2026-11-12.",
        "actions": ["search", "read"],
    },
}

# Channels `exec` is allowed to run, and the agent-reach action it maps to.
EXEC_ALLOW = {"youtube", "github", "bilibili", "v2ex"}
# Channels that must never be fetched by this script.
EXEC_REFUSE = {
    "amazon": "use the Shopping skill: Meta Catalog + live browser product search. Direct fetching is bot-blocked.",
    "flipkart": "use the Shopping skill: Meta Catalog + live browser product search. Direct fetching is bot-blocked.",
    "reddit": "rate-limited 2026-11-12 (HTTP 429). Use browser.search / social.search; do not retry the agent-reach backend today.",
    "web": "rate-limited 2026-11-12. Use browser.search / browser.open; do not retry the agent-reach backend today.",
}

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
    if not query:
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
    if channel in ("amazon", "flipkart"):
        result["amazon_rule"] = ("Live price/stock ONLY from a live browser task or "
                                 "Meta Catalog. A stale browser.open crawl or a curl "
                                 "HTTP 200 is NOT a live price. Never construct a "
                                 "product URL; use only URLs returned by search/tools "
                                 "or supplied by the user.")
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
    if len(args) < 3:
        print(json.dumps({"ok": False, "error": {"code": "BAD_INPUT",
                         "message": "usage: muse-reach.py exec <channel> <action> <query-or-url> [--limit N]"}}))
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
    cmd = [agent_reach, channel, action, query, "--limit", str(limit)]
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
