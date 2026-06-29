# Campaign creation (🔴 assemble → PAUSED → `/activate`)

Assemble a complete campaign and create it **PAUSED**. The agent builds everything; it does **not**
go live. Activation is a separate, deliberate `/activate` (a second, explicit yes). Naming follows
[`../account/defaults.md`](../account/defaults.md); safety from [`guardrails.md`](guardrails.md).

**Tool sequence:** `ads_create_campaign` → `ads_create_ad_set` → `ads_create_creative` →
`ads_create_ad` → `ads_get_ad_preview`. **Every create call sets `status: PAUSED`.**

> Before any create call, present the full assembled spec (objective · audience · budget · creative ·
> names) as one summary and get the user's approval to create it — paused.

## CRT-1 · Objective

Match objective to funnel stage (Awareness/Traffic = cold; Engagement/Leads = warm; Sales/App = hot).
Don't point Sales at a cold audience with no purchase data — expensive and slow to exit learning. For
mattresses with a website/WhatsApp destination, Traffic or Sales are the usual picks (see `defaults.md`).

## CRT-2 · Audience / targeting

For ecommerce with conversion history and >~$50/day, default to **Advantage+ Audience (broad)** and
treat inputs as suggestions. Add exclusions (e.g. recent purchasers) when prospecting. Need ~50
conv/week for stable delivery. Geo and minimum age are the only hard constraints under Advantage+.

## CRT-3 · Budget & schedule

Size the weekly budget ≈ 50× target CPA so the ad set can clear learning. Choose **daily** (always-on)
or **lifetime** (required if you'll daypart). Pick CBO vs ABO per OPT-5. Amounts in ARS — sanity-check
the magnitude against the monthly budget in `defaults.md`.

## CRT-4 · Creative

Load diverse creative — multiple concepts / formats / aspect ratios (9:16 Reels/Stories, 1:1 or 4:5
feed), distinct hooks, within text/policy limits. **The human supplies the actual image/video** (the
agent can't see assets); the agent handles copy, structure, and upload via `ads_create_creative`.
Verify the landing page is live and compliant.

## CRT-5 · Naming

Apply the convention from `defaults.md` (underscores): Campaign = `funnel_objective_budget_bid`; Ad set
= `audience_placement_geo`; Ad = `concept_format_date`. Validate before creating.

## CRT-6 · A/B test structure (if testing)

One variable at a time; one ad per ad set (avoid overlap). Budget ~50 conversions per variation;
allocate 10–20% of campaign budget to testing. Declare a winner only at ≥90% confidence and ≥1,000
impressions per variant.

## CRT-7 · Pre-launch QA (must pass before creating)

- [ ] Pixel / CAPI firing + event match quality OK
- [ ] Correct optimization event
- [ ] Budget & any cap sane (ARS magnitude checked)
- [ ] Naming valid
- [ ] Targeting + exclusions correct
- [ ] Placements set
- [ ] Tracking / UTMs in place
- [ ] Landing page live & compliant

---

## Handoff

After creating, show `ads_get_ad_preview` and confirm every entity is **PAUSED**. Tell the user the
campaign is built but **not spending**, and that going live is a separate **`/activate`**. Never call
`ads_activate_entity` from this workflow.
