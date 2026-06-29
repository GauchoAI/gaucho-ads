# Reporting workflows (🟢 read-only)

Formatted reports built from insights. No approval, no spend.
`/report [daily|weekly|creative|audience|exec]` (default `weekly`).
Action-flag thresholds come from [`../account/defaults.md`](../account/defaults.md).

**Primary tools:** `ads_insights_performance_trend`, `ads_insights_advertiser_context`,
`ads_get_ad_entities`, `ads_get_opportunity_score`.

## REP-1 · Daily pacing

Spend today, MTD vs target, pacing%, projected end-of-month. Rolled up account → campaign.
(Shares logic with MON-1.)

## REP-2 · Weekly performance

One row per campaign / ad set: 7-day spend, ROAS, CPA, CPM, CTR, frequency, status, and an
**auto-derived action flag**:

- `PAUSE` — CPA > 2× target for 3 consecutive days
- `SCALE` — ROAS > 1.5× floor for 5 consecutive days
- `MONITOR` — frequency > 3.0

Flags are recommendations only — acting on one goes through `/optimize`.

## REP-3 · Creative performance

Ad-level CTR, CPA/ROAS, thumb-stop / hold rate, video-view rate, frequency, top hooks, fatigue
indicators. Present as a **CTR × CPA/ROAS quadrant** (high-CTR + good-CPA = scale candidates;
low-CTR + poor-CPA = retire).

## REP-4 · Audience / breakdown

Breakdowns by age/gender, placement, geo, device, and time-of-day to find efficient vs wasteful
segments. Use insights breakdowns.

## REP-5 · Executive

Exec scorecard (spend, CPA/ROAS, revenue or leads, CTR, CPC, CPM) + a full-funnel view
(impressions → clicks → landing-page views → add-to-cart → checkout → purchase) + a plain-English
narrative. Amounts in ARS.

---

**Cross-report signals to auto-surface:** rising CPM + flat CTR (auction competition); declining CTR
+ stable CPM (creative fatigue); frequency >3.0 + declining results (saturation); CPA up >20% over
7 days (investigate). Reports never write — they point to `/optimize` for any action.
