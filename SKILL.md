---
name: muse-reach
description: "Muse-native read-only search and reading across GitHub, YouTube, Reddit, X/Twitter, Facebook, Instagram, Bilibili, V2EX, Xiaohongshu, LinkedIn, and the web, plus Amazon and Flipkart product search. Use when the user asks to search or read a link on any of those sites, open Amazon or Flipkart, find a product price, or asks what Agent Reach can do. Routes Muse's own browser.search, browser.open, social.search and connectors first, Agent Reach only as fallback. Never logs in for the user, never posts or buys."
---

# Muse Reach

Read-only search and reading for Muse. One router for every site Agent Reach covers, plus Amazon and Flipkart, built for Muse instead of ported from another agent.

## How to use

- Run `python3 ~/workspace/muse-reach/muse-reach.py route <channel> <action> <query-or-url>` before fetching anything. It prints the route in order as JSON. Follow that order.
- Run `python3 ~/workspace/muse-reach/muse-reach.py channels` to list every channel, its actions and its honest status. Run `doctor` for cheap local checks only. Doctor never hits the network and never re-tests a rate-limited channel.
- The router itself never scrapes and never fetches pages. It only tells you which Muse tool or CLI to use. Fetch with that tool.
- `exec` runs only the safe read-only backends (youtube, github, bilibili, v2ex) through `agent-reach`. It refuses amazon, flipkart, reddit and web. For those, follow the printed route with Muse tools instead.

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
- amazon: Shopping skill first. Meta Catalog search plus a live browser product search for the live price. See the Amazon section below. Agent Reach never had this channel.
- flipkart: same route as amazon. Agent Reach never had this channel.

## Amazon and Flipkart, the honest route

- Live price and stock come ONLY from a live browser task or Meta Catalog. Nothing else counts as live.
- A `browser.open` result can be a stale cached crawl, sometimes hundreds of days old, with no price. That is not a live price. Say so, do not quote it as current.
- A `curl` HTTP 200 can be a bot-check shell of a few kilobytes, not a product page. That is not a live price either.
- Price trackers such as Smartprix, 91mobiles and pricehistory.app are corroboration only, never the live price.
- Never construct a product URL. Use only URLs returned by search or tools, or supplied by the user.
- For a purchase, follow the Shopping skill. The live browser owns checkout. Never buy, add to cart for real, or enter payment details through a script.
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

## Status, verified 2026-11-12

- youtube works (yt-dlp search returned live results).
- reddit search via public-web failed with HTTP 429 rate limit. web read via Agent Reach failed rate-limited with a 3586 second wait hint. Do not retry either backend that day.
- browser.open on an amazon.in product page returned a 344-day-old crawl with no price. curl to amazon.in returned HTTP 200 but 3793 bytes, a bot-check shell.
- X/Twitter, LinkedIn jobs and Instagram are login-gated or broken. Do not claim they work until a live test passes.
- bilibili, v2ex, xiaohongshu, xueqiu, boss and xiaoyuzhou were not live-tested 2026-11-12. Their status in `channels` says so.
