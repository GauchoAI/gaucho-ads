---
name: onboard
description: Connect this repo to the Meta Ads account — browser-driven OAuth with automatic callback capture (no URL pasting), verify the account, check billing, bootstrap the local memory store, and capture goals. Run this first, before any other workflow.
argument-hint: ""
disable-model-invocation: true
---

Run the browser-driven onboarding workflow for the Meta Ads agent.

Paths below are relative to the repo root (where Claude Code is running).

1. Read `workflows/onboarding.md` and follow it **step by step**, in order.
2. **Narrate every phase as it happens** — this is meant to be live and observable. Announce each
   transition: bootstrapping local memory → opening browser → waiting for callback → callback
   received ✓ → completing authentication → verifying account → connected ✓ → account summary.
3. **OAuth is zero-paste:** call `mcp__meta-ads__authenticate`, open the returned URL in a controlled
   browser (chrome-devtools MCP `new_page`/`navigate_page`; playwright as fallback), let the user log
   in + click Authorize themselves (**never automate their credentials**), then **auto-capture** the
   redirect URL (`list_pages` / `list_network_requests`, watching for `code=`+`state=`), validate
   `state`, and call `mcp__meta-ads__complete_authentication` with it on the same session. If capture
   times out or the browser is unavailable, fall back to the auto-open + single-paste path.
4. Honor `workflows/guardrails.md` throughout — this is a read/connect flow, so nothing here spends
   money, but keep the posture.
5. Bootstrap memory early (`python3 memory/db.py init`) and, as you learn the user's goals
   (objective, landing destination, target CPA, ROAS floor, monthly budget, time zone), write them
   into **both** `account/defaults.md` (replacing the `‹set during onboarding›` placeholders) **and**
   the SQLite store (`db.py set-profile`, `db.py record-goals`). See `workflows/memory.md`.
6. Seed the first awareness snapshot (`db.py snapshot`) from a read-only summary pull so `/watch` has
   a baseline.

End state: the `meta-ads` MCP is connected (callback auto-captured, no paste), the account is
verified (`is_ads_mcp_enabled: true`, currency `ARS`), billing status is known, `account/defaults.md`
is filled in and mirrored to `memory/agent.sqlite`, and the safety posture is confirmed. Then point
the user to `/watch` (live awareness) and `/menu`.
