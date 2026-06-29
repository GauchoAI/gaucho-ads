# Monitoring workflows (🟢 read-only)

Health checks that run freely — no approval, no spend. Thresholds come from
[`../account/defaults.md`](../account/defaults.md). Run all six with `/monitor`, or ask for one by name.

**Primary tools:** `ads_insights_performance_trend`, `ads_insights_anomaly_signal`,
`ads_insights_advertiser_context`, `ads_get_opportunity_score`, `ads_get_ad_entities`,
`ads_account_get_activity_logs`.

> Pull the account's own baseline first (`ads_insights_advertiser_context`) and judge against it,
> not just the universal defaults — an account's normal CTR/CPA is the better yardstick.

## MON-1 · Spend pacing

- **Purpose:** ensure spend tracks the plan; catch over/underspend before the budget runs out.
- **Inputs:** spend today + month-to-date, monthly budget (`defaults.md`), days elapsed/remaining.
- **Tools:** `ads_insights_performance_trend` (spend by day) + the planned budget.
- **Logic:** `pacing% = actual ÷ planned × 100`. Band 90–110% = on track; >110% over (130%/day
  exhausts a monthly budget ~day 23, then goes dark at month-end); <90% under (lost opportunity).
- **Output:** pacing status + projected end-of-month spend + any breach.

## MON-2 · CPA/ROAS anomaly

- **Purpose:** catch performance degradation early.
- **Inputs:** 7-day trailing CPA/ROAS per campaign & ad set; target CPA + ROAS floor.
- **Tools:** `ads_insights_anomaly_signal` (Meta's built-in), `ads_insights_performance_trend`.
- **Logic:** flag if CPA > 20% above target over 7 days, or above target 3+ days running. Diagnose:
  rising CPM + flat CTR = auction competition; declining CTR + stable CPM = creative fatigue.
- **Output:** ranked anomaly list with a likely-cause tag.

## MON-3 · Learning-phase status

- **Purpose:** find ad sets stuck in Learning / Learning Limited.
- **Inputs:** learning status, 7-day conversions, optimization event, budget, avg cost/conversion.
- **Tools:** `ads_get_ad_entities` (ad sets + status), `ads_insights_performance_trend`.
- **Logic (Meta-official):** ~50 optimization events / 7-day rolling window to exit learning.
  Feasibility test: `weekly_budget ÷ avg_cost_per_conversion ≥ 50`? If not, the root cause is usually
  budget too low, event too rare, or too many ad sets splitting conversions. Significant edits reset
  learning to day 1 — flag this before recommending any edit.
- **Output:** stuck ad sets + reason + suggested fix (consolidate, broaden, raise budget, change event).

## MON-4 · Frequency / fatigue

- **Purpose:** detect creative wear-out before it tanks performance.
- **Inputs:** 7-day frequency, CTR & CPM trends, audience type (cold vs warm).
- **Tools:** `ads_insights_performance_trend` (frequency + CTR by day).
- **Logic:** cold/prospecting frequency >3.0 = monitor, >4.0 = strong fatigue; warm/retargeting
  tolerates 5–7. Earliest signal = declining CTR while impressions hold (leads a frequency breach by
  ~3–5 days).
- **Output:** fatigue flags + refresh / expand-audience suggestion (→ OPT-7 / OPT-8).

## MON-5 · Disapproved / policy

- **Purpose:** catch rejected ads and account-quality issues fast.
- **Inputs:** ad review status, account-quality issues.
- **Tools:** `ads_get_ad_entities` (ad `effective_status`), `ads_account_get_activity_logs`.
- **Logic:** "Disapproved" = a policy issue in creative or landing page; surface the reason and the
  remediation path (edit & resubmit, or request review). A failed payment method pauses *all*
  campaigns — check billing if everything stalls at once.
- **Output:** disapproved-ad list + reason + fix path.

## MON-6 · Delivery / zero-spend

- **Purpose:** detect ad sets not spending or under-delivering.
- **Inputs:** spend vs budget, status, bid/cost cap, payment status, audience size.
- **Tools:** `ads_get_ad_entities`, `ads_insights_performance_trend`, `ads_get_opportunity_score`.
- **Logic:** common causes — cost/bid cap too low vs market CPM, payment failure, audience too
  narrow, still in review, or overlapping ad sets cannibalizing delivery.
- **Output:** under-delivery list with the diagnosed cause.

---

**Output style:** lead with a one-line account-health verdict, then a compact table
(entity · metric · value · status), then the flagged items with the suggested next workflow.
Everything here is read-only — if a fix is warranted, hand off to `/optimize`; never auto-apply.
