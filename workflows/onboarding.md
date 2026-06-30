# Onboarding — connect this repo to the Meta Ads account

**Goal:** end with the MCP connected, the account verified, billing status known,
[`../account/defaults.md`](../account/defaults.md) filled in with the user's goals, and the
durable memory store seeded — reached through a **browser-driven, near-zero-typing** flow.

**Good news up front:** the official Meta Ads MCP uses a browser OAuth login — **there are no API
keys or secrets to paste.** Onboarding collects *goals*, not credentials.

This whole flow is 🟢 read/connect only — nothing here spends money.

**Narrate every phase as it happens** (requirement: live, observable onboarding). Say what you're
about to do, then do it: `bootstrapping local memory → opening browser → waiting for callback →
callback received ✓ → completing authentication → verifying account → connected ✓ → account
summary`. Keep the user oriented at all times.

---

## Step 0 — Prerequisite

The user must have Claude Code open **inside the `gaucho-ads` directory** (so `.mcp.json` and
`.claude/settings.json` apply). If not, ask them to `cd` there and restart. This flow is **local**
(the controlled browser runs on the user's machine) — it is not for a remote/cloud session.

## Step 0.5 — Bootstrap local memory (one time)

Narrate: *"Bootstrapping local memory…"*

1. **git LFS** — the memory store is committed via git LFS. Check `git lfs version`; if missing,
   tell the user and (with approval) run `brew install git-lfs && git lfs install`. Then
   **materialize the store**: `git lfs pull`. (A fresh clone made before git-lfs was installed leaves
   `memory/agent.sqlite` as a small text *pointer*; `db.py` detects that and tells you to run
   `git lfs pull`.) The repo ships `.gitattributes` (tracks `memory/agent.sqlite` +
   `memory/audit-log.jsonl`) and `.gitignore` (ignores the WAL sidecars).
2. **Initialize the store** — run `python3 memory/db.py init` (idempotent; creates the schema + the
   JSONL audit mirror if absent, or confirms the pulled one). See [`memory.md`](memory.md).
3. Record an audit row marking onboarding start:
   `python3 memory/db.py record-audit --json '{"actor":"claude","action_type":"onboard","note":"onboarding started"}'`
4. **(Optional) Enable the session-start digest.** Add this to `.claude/settings.json` (after the
   `permissions` block) so every new/resumed session greets you with last-known state from the DB —
   `/watch` works without it; this only adds the automatic digest:
   ```json
   "hooks": {
     "SessionStart": [
       { "matcher": "startup", "hooks": [ { "type": "command", "command": "python3 ${CLAUDE_PROJECT_DIR}/memory/db.py digest --session-start", "timeout": 15 } ] },
       { "matcher": "resume",  "hooks": [ { "type": "command", "command": "python3 ${CLAUDE_PROJECT_DIR}/memory/db.py digest --session-start", "timeout": 15 } ] }
     ]
   }
   ```

## Step 1 — Approve the `meta-ads` MCP server

`.mcp.json` ships in the repo, so on the first launch here Claude Code shows a one-time prompt to
approve the `meta-ads` server. Ask the user to **approve it**. If they missed the prompt, have them
run `/mcp` and approve `meta-ads` there. After approval it auto-connects every future session.

## Step 2 — Authenticate (browser-driven, auto-captured — no URL pasting)

> **Why this design:** Claude Code's native loopback OAuth is blocked server-side by Meta
> (`mcp.facebook.com/ads` only registered the claude.ai-web and Claude *Desktop* redirect URIs, not
> the CLI's localhost loopback — Anthropic issues #57191/#59924, closed "not planned"). A local
> `127.0.0.1` helper can't catch a redirect Meta never sends there. So we drive the working
> `authenticate`/`complete_authentication` tools and **auto-capture the redirect from a controlled
> browser** — eliminating the manual paste. The user's personal Meta login is **never automated**;
> we only open the page and read the post-Authorize URL.

1. Call `mcp__meta-ads__authenticate`. It returns a Meta OAuth URL (scopes `ads_management`,
   `ads_read`, `catalog_management`, `business_management`, `pages_show_list`, `instagram_basic`)
   and, typically, a `state` value. Keep both.
2. **Open the controlled browser** (prefer **chrome-devtools** MCP; **playwright** MCP is the
   drop-in alternative if chrome-devtools isn't connected):
   - chrome-devtools: `new_page` (or `navigate_page`) → the OAuth URL. This opens a **headed** window
     using the MCP's own persistent profile. *(Recent Chrome blocks debug-attaching to your default
     profile, so a dedicated profile is the robust path — you log into Facebook once here, and it's
     remembered afterward.)*
   - playwright equivalent: `browser_navigate` → the OAuth URL.
3. Narrate: *"Browser open — please log into Facebook (first time only) and click **Authorize**.
   I'll capture the rest automatically."* **Wait for the human.** Do not type their credentials.
4. **Auto-capture the callback.** Poll until the browser navigates to the redirect carrying the
   auth code (narrate *"waiting for callback…"* between polls, ~every few seconds, up to ~3 min):
   - chrome-devtools: read the current tab URL via `list_pages`; also scan `list_network_requests`
     for the redirect request. The target is a URL containing **`code=` and `state=`** (its host is
     a Meta/claude.ai host, not localhost). `list_network_requests` captures it **even if the
     landing page shows a connection error** — the URL still carries the code, which neutralizes the
     documented redirect quirk.
   - playwright: `browser_wait_for` the redirect, then `browser_network_requests` / current tab URL.
5. **Validate** the captured `state` matches the one from Step 1 (CSRF check). Narrate
   *"callback received ✓ → completing authentication…"*
6. Call `mcp__meta-ads__complete_authentication` with the **full captured URL**, on the **same MCP
   session** that called `authenticate` (the server keys PKCE state to that session). → Connected,
   **no paste**.
7. **Fallback (built in).** If no redirect is detected within the timeout, or the controlled browser
   is unavailable: open the URL in the default browser (`open "<url>"`), ask the user to authorize,
   then **paste the single address-bar URL** back, and call `mcp__meta-ads__complete_authentication`
   with it. This is the original flow — "near-zero" instead of "zero" paste — and always works.

See [`../Documentation/meta-mcp-setup.md`](../Documentation/meta-mcp-setup.md) for the original
walk-through of this flow and the Argentine billing notes.

## Step 3 — Verify the connection

Narrate: *"Verifying account…"*

1. Have the user run `/mcp` — expect **"Connected to meta-ads"**.
2. Call `ads_get_ad_accounts`. Confirm:
   - `ad_account_id` = `1930186940607840`
   - `is_ads_mcp_enabled` = `true`  ← if `false`, the MCP tools won't return live data; stop and
     surface this.
   - `currency` = `ARS`
3. Persist the verified facts to memory:
   `python3 memory/db.py set-profile --json '{"ad_account_id":"1930186940607840","currency":"ARS","business":"Mattress sales, Argentina","time_zone":"<tz once known>"}'`

## Step 4 — Billing check

From `ads_get_ad_accounts` (and account tools), check `has_payment_method` and current funds.
- If a payment method / funds are missing, point the user to Ads Manager → Billing, or the direct
  path documented in `Documentation/meta-mcp-setup.md`.
- **Argentina specifics** (from the setup doc): only Visa cards from Argentine banks are accepted;
  the first charge often needs the user to authorize "Meta Platforms Ireland" with their bank;
  there's a Meta-set daily spend limit. Surface these only if billing isn't already set.
- Campaigns can be built without funds — they just can't be **activated** until billing works.

## Step 5 — Capture goals → `account/defaults.md` **and** memory

Narrate: *"Connected ✓ — a few quick goals and you're set."* Interview the user (one topic at a
time) and write answers into **both** places (defaults.md stays the human-editable source of truth;
the DB keeps a durable, versioned snapshot — see [`memory.md`](memory.md)):

- **Primary objective** — Traffic / Sales / Awareness?
- **Landing destination** — website URL / WhatsApp / Instagram?
- **Target CPA** — cost per result they'll accept (ARS).
- **ROAS floor** — minimum acceptable return (if Sales objective).
- **Monthly budget** — total planned spend (ARS).
- **Time zone** — for pacing and dayparting.

Write the placeholders in `account/defaults.md`, then mirror to memory:
`python3 memory/db.py record-goals --json '{"objective":"…","landing_destination":"…","target_cpa":…,"roas_floor":…,"monthly_budget":…}'`

Leave the optimization thresholds at their defaults unless the user wants to tune them.

## Step 6 — Seed the first awareness snapshot + confirm safety posture

Narrate: *"Here's your account right now…"* — do a read-only summary pull and store it as the first
snapshot so future `/watch` runs have a baseline to diff against:

1. `ads_get_ad_entities` (existing campaigns/ad sets/ads), a quick `ads_insights_*` pull (spend,
   results), and `ads_account_get_activity_logs` (recent server-side changes). Present a short
   summary.
2. Seed the baseline: `python3 memory/db.py snapshot --json '[…per-entity rows with metrics…]'`
   (see [`awareness.md`](awareness.md) for the row shape).
3. Restate the safety posture plainly: **approve money moves** — the agent monitors, analyzes, and
   drafts freely, but any create / budget-up / activate needs an explicit "yes", and new campaigns
   are created **PAUSED**. Point to [`guardrails.md`](guardrails.md).

---

## Done when

- [ ] `meta-ads` shows **Connected** in `/mcp` (callback auto-captured, no paste)
- [ ] `ads_get_ad_accounts` returns account `1930186940607840`, `is_ads_mcp_enabled: true`, `ARS`
- [ ] Billing status known (set, or the user knows what's needed)
- [ ] `account/defaults.md` placeholders filled in **and** mirrored to `memory/agent.sqlite`
- [ ] First awareness snapshot seeded; safety posture confirmed with the user

Then suggest **`/watch`** (live read-only awareness) and **`/menu`** (pick a workflow).
