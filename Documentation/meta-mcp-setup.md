# Meta Ads MCP Setup — Full Journey

## What We Were Trying To Do

Connect Claude Code to Meta Ads so we can create, manage, and analyze ad campaigns directly from the terminal using natural language.

---

## Phase 1: Is There an Official Meta MCP Server?

### Initial confusion

The question started simple: install the official Meta MCP server. Turned out not to be simple at all — initial deep research (98 agents, 1.3M tokens) concluded that **no official Meta MCP server existed**, and the best available option was a third-party hosted server by Pipeboard at `https://meta-ads.mcp.pipeboard.co/`.

### The Reddit find that changed everything

A Google search result from `facebook.com/business/news/meta-ads-ai-connectors` revealed that **Meta did release an official MCP connector**, announced on April 29, 2026 as open beta. It was called **Meta Ads AI Connectors**.

Key details from the official announcement:
- Official Meta Ads MCP server URL: `https://mcp.facebook.com/ads`
- Built and maintained by Meta — no third-party risk
- Full read-and-write access to ad accounts
- No developer credentials or API setup required
- Setup takes "minutes, not days"
- Capabilities: reporting, campaign management, catalog management, signal diagnostics

Reddit users also confirmed:
- Claude Desktop supports it natively via "Add Custom Connector"
- Claude Code (terminal) requires a workaround — the OAuth browser flow doesn't launch automatically
- Google's official MCP is read-only; Meta's is read-and-write
- Accounts need `is_ads_mcp_enabled: true` to work

---

## Phase 2: Installing the Meta Ads MCP in Claude Code

### Add the MCP server

```bash
claude mcp add --transport http meta-ads "https://mcp.facebook.com/ads"
```

Output:
```
Added HTTP MCP server meta-ads with URL: https://mcp.facebook.com/ads to local config
File modified: /Users/miguel_lemos/.claude-eg/.claude.json
```

### Restart Claude Code

After adding the server, restart Claude Code. On restart, two auth tools appeared:
- `mcp__meta-ads__authenticate`
- `mcp__meta-ads__complete_authentication`

### Authenticate via OAuth

Calling `mcp__meta-ads__authenticate` returned a Facebook OAuth URL with these scopes:
```
ads_management
ads_read
catalog_management
business_management
pages_show_list
instagram_basic
```

The user opens the URL in their browser, logs into Facebook, and authorizes their ad accounts.

**If the browser shows a connection error on redirect:** paste the full URL from the address bar back into Claude and call `mcp__meta-ads__complete_authentication` with it.

### Verify connection

After completing the browser flow, restart Claude Code and run `/mcp`. Expected output:
```
Authentication successful. Connected to meta-ads.
```

---

## Phase 3: Tools Available After Authentication

The full Meta Ads MCP toolset becomes available — 70+ tools covering:

**Account & Reporting**
- `ads_get_ad_accounts` — list all ad accounts
- `ads_get_ad_entities` — get campaigns, ad sets, ads
- `ads_insights_performance_trend` — performance trends
- `ads_insights_anomaly_signal` — anomaly detection
- `ads_insights_advertiser_context` — account-level context
- `ads_get_opportunity_score` — optimization score
- `ads_account_get_activity_logs` — audit log

**Campaign Management**
- `ads_create_campaign` — create campaigns
- `ads_create_ad_set` — create ad sets
- `ads_create_ad` — create ads
- `ads_create_creative` — create creatives
- `ads_update_entity` — edit any entity
- `ads_activate_entity` — pause/activate
- `ads_get_ad_preview` — preview an ad

**Audiences**
- `ads_create_custom_audience`
- `ads_get_ad_account_custom_audiences`
- `ads_update_custom_audience_users`

**Catalogs**
- `ads_catalog_create`, `ads_catalog_get_catalogs`, `ads_catalog_search_product`, etc.

**Pixels & Signals**
- `ads_get_datasets`, `ads_get_dataset_quality`, `ads_pixel_event_*`

**Experiments**
- `ads_experiment_abtest_create_test`, `ads_experiment_lift_create_test`, etc.

**Instagram & Pages**
- `ads_get_ig_accounts`, `ads_get_ig_media`, `ads_boost_ig_post`

---

## Phase 4: Ad Account Discovery

```
ads_get_ad_accounts
```

Result:
```json
{
  "ad_account_id": "1930186940607840",
  "ad_account_name": "",
  "business_id": "",
  "business_name": "",
  "is_ads_mcp_enabled": true,
  "account_status": "ACTIVE",
  "currency": "ARS",
  "has_payment_method": false
}
```

One account found. `is_ads_mcp_enabled: true` — confirmed working. Currency is ARS (Argentine pesos).

---

## Phase 5: Setting Up Billing

### Finding the billing page

- `business.facebook.com/billing` — blocked (requires Business Manager)
- `facebook.com/billing` — access denied
- **Working path:** Ads Manager → top menu → Billing, or direct URL:
  `business.facebook.com/billing_hub/payment_settings/?placement=ads_manager&asset_id=1930186940607840`

### Argentine billing restrictions

Meta warning: **Only Visa cards issued by Argentine banks are accepted** as of February 10. Foreign Visa cards are blocked.

### Adding funds

- Payment method added: Visa ···6067
- Initial top-up attempts failed (bank blocked the charge)
- Fix: call your bank to authorize charges from "Meta Platforms Ireland"
- Successfully loaded: **$20,000 ARS**
- Daily spend limit set by Meta: $72,770 ARS
- Billing threshold: charges when balance reaches $2,856 ARS, approximately once per day

---

## Current Status

| Step | Status |
|------|--------|
| MCP server installed | ✅ |
| OAuth authentication | ✅ |
| Ad account found & MCP-enabled | ✅ |
| Payment method added | ✅ |
| Funds loaded ($20,000 ARS) | ✅ |
| Ready to create campaigns | ✅ |

---

## What's Next

Building the first campaign: a single-image ad for selling mattresses.

Required inputs before creating:
1. Campaign objective (Traffic / Sales / Awareness)
2. Daily budget in ARS
3. Target location (city/region in Argentina)
4. Landing page URL (website, WhatsApp, or Instagram)
5. Mattress image file

---

## Key Lessons Learned

1. **Meta's official MCP was announced April 29, 2026** — it didn't exist in earlier knowledge cutoffs, which caused initial confusion.
2. **Claude Desktop vs Claude Code**: Desktop has a native connector UI. In Code (terminal), you add it manually with `claude mcp add --transport http` and authenticate via a browser OAuth URL.
3. **New Argentine ad accounts have billing restrictions**: foreign cards blocked, bank authorization often needed for first charge, initial fund limits apply.
4. **`is_ads_mcp_enabled` must be `true`** on the account — if false, the MCP tools won't return live data.
5. **You don't need pre-loaded funds to build campaigns** — campaigns created in paused state won't spend until activated.

---

## References

- Meta Ads AI Connectors announcement: `facebook.com/business/news/meta-ads-ai-connectors`
- Official setup guide (requires Facebook login): `facebook.com/business/help/1456422242197840`
- Ads CLI developer blog: `developers.facebook.com/blog/post/2026/04/29/introducing-ads-cli`
- MCP server URL: `https://mcp.facebook.com/ads`
