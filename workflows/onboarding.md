# Onboarding — connect this repo to the Meta Ads account

**Goal:** end with the MCP connected, the account verified, billing status known, and
[`../account/defaults.md`](../account/defaults.md) filled in with the user's goals.

**Good news up front:** the official Meta Ads MCP uses a browser OAuth login — **there are no API
keys or secrets to paste.** Onboarding collects *goals*, not credentials.

This whole flow is 🟢 read/connect only — nothing here spends money.

---

## Step 0 — Prerequisite

The user must have Claude Code open **inside the `gaucho-ads` directory** (so `.mcp.json` and
`.claude/settings.json` apply). If not, ask them to `cd` there and restart.

## Step 1 — Approve the `meta-ads` MCP server

`.mcp.json` ships in the repo, so on the first launch here Claude Code shows a one-time prompt to
approve the `meta-ads` server. Ask the user to **approve it**. If they missed the prompt, have them
run `/mcp` and approve `meta-ads` there. After approval it auto-connects every future session.

## Step 2 — Authenticate (browser OAuth)

1. Call `mcp__meta-ads__authenticate`. It returns a Meta OAuth URL requesting scopes:
   `ads_management`, `ads_read`, `catalog_management`, `business_management`, `pages_show_list`,
   `instagram_basic`.
2. The user opens the URL in a browser, logs into the Meta account that owns the ad account, and
   authorizes.
3. **If the browser shows a connection error on redirect** (a known Claude Code quirk), ask the
   user to copy the full URL from the address bar and paste it back, then call
   `mcp__meta-ads__complete_authentication` with it.

See [`../Documentation/meta-mcp-setup.md`](../Documentation/meta-mcp-setup.md) for the original
walk-through and screenshots-in-prose of this flow.

## Step 3 — Verify the connection

1. Have the user run `/mcp` — expect **"Connected to meta-ads"**.
2. Call `ads_get_ad_accounts`. Confirm:
   - `ad_account_id` = `1930186940607840`
   - `is_ads_mcp_enabled` = `true`  ← if `false`, the MCP tools won't return live data; stop and
     surface this.
   - `currency` = `ARS`

## Step 4 — Billing check

From `ads_get_ad_accounts` (and account tools), check `has_payment_method` and current funds.
- If a payment method / funds are missing, point the user to Ads Manager → Billing, or the direct
  path documented in `Documentation/meta-mcp-setup.md`.
- **Argentina specifics** (from the setup doc): only Visa cards from Argentine banks are accepted;
  the first charge often needs the user to authorize "Meta Platforms Ireland" with their bank;
  there's a Meta-set daily spend limit. Surface these only if billing isn't already set.
- Campaigns can be built without funds — they just can't be **activated** until billing works.

## Step 5 — Capture goals → `account/defaults.md`

Interview the user (one topic at a time) and write answers into `account/defaults.md`, replacing the
`‹set during onboarding›` placeholders:

- **Primary objective** — Traffic / Sales / Awareness?
- **Landing destination** — website URL / WhatsApp / Instagram?
- **Target CPA** — cost per result they'll accept (ARS).
- **ROAS floor** — minimum acceptable return (if Sales objective).
- **Monthly budget** — total planned spend (ARS).
- **Time zone** — for pacing and dayparting.

Leave the optimization thresholds at their defaults unless the user wants to tune them.

## Step 6 — Confirm the safety posture

Restate it plainly: **approve money moves** — the agent monitors, analyzes, and drafts freely, but
any create / budget-up / activate needs an explicit "yes", and new campaigns are created **PAUSED**.
Point to [`guardrails.md`](guardrails.md).

---

## Done when

- [ ] `meta-ads` shows **Connected** in `/mcp`
- [ ] `ads_get_ad_accounts` returns account `1930186940607840`, `is_ads_mcp_enabled: true`, `ARS`
- [ ] Billing status known (set, or the user knows what's needed)
- [ ] `account/defaults.md` placeholders filled in
- [ ] Safety posture confirmed with the user

Then suggest **`/menu`** to pick a workflow.
