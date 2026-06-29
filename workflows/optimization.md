# Optimization workflows (🟡 propose → approve → write)

Analyze, then **propose** a concrete change and wait for an explicit "yes" before writing. Every
write here goes through `ads_update_entity` or `ads_activate_entity` and is gated both by the harness
(`ask`) and by you (show the diff). Honor the safety floors in [`guardrails.md`](guardrails.md).
Thresholds come from [`../account/defaults.md`](../account/defaults.md).

**How every OPT runs:**

1. Pull the data (read-only).
2. Check the relevant **safety floor** — if it blocks the action, say so and stop.
3. Present a precise **diff**: entity · field · old → new · expected effect.
4. On explicit approval, apply with `ads_update_entity` / `ads_activate_entity` — one change at a time.
5. Note when a significant edit will **reset the learning phase**.

## OPT-1 · Kill / pause underperformers

- **Inputs:** spend, conversions, target CPA, frequency, impressions, learning status, days running.
- **Rule:** pause if spend > 1.5× target CPA with 0 conversions over 3 days (or the conservative
  variant in `defaults.md`). **Exclude** anything still in learning or under ~5,000–10,000
  impressions — too little signal.
- **Write:** `ads_activate_entity` → PAUSED. **Output:** pause proposals + evidence.

## OPT-2 · Scale winners (the 20% rule)

- **Inputs:** ad-set CPA/ROAS vs target, consecutive days at target, learning status.
- **Rule:** a "winner" is out of learning **and** at/above target for 5–7 consecutive days. Raise
  budget ≤20% every 24–72 h. **Safety floor:** no increase if 7-day CPA > target ×1.2; cap +15%/day.
- **Write:** `ads_update_entity` (budget). **Output:** scaling plan (ad sets · new budgets · cadence).

## OPT-3 · Horizontal scaling / audience expansion

- **Inputs:** saturation signals (rising freq + CPA), winning creative/post ID, new audience ideas.
- **Rule:** when vertical scaling shows rising CPA + creeping frequency, duplicate the winning
  creative into new audiences (new LAL %s, interest stacks, geos). New entities created **PAUSED**.
- **Write:** create flow (→ [`creation.md`](creation.md)), PAUSED. **Output:** proposed new ad sets.

## OPT-4 · Budget reallocation

- **Inputs:** per-ad-set 7-day ROAS/CPA, current spend share.
- **Rule:** shift toward ROAS > floor / CPA < target; trim those above target. Cap any single change
  to +15%/day. In CBO, let the algorithm allocate — don't impose ad-set caps without a real reason.
- **Write:** `ads_update_entity`. **Output:** reallocation proposal.

## OPT-5 · CBO vs ABO

- **Per-campaign routing**, not an account-wide rule. **ABO** for testing / new offers / small
  budgets / guaranteed per-ad-set data; **CBO** to scale proven winners (size weekly budget ≈ 50×
  target CPA so each ad set can reach ~50 conv/week). Avoid ad-set spend caps inside CBO.
- **Output:** structure recommendation per campaign (apply via create/edit, with approval).

## OPT-6 · Bid strategy

- **Lowest Cost** = default for most campaigns. **Cost Cap** only with a real CPA ceiling **and** ≥50
  conv/wk per ad set **and** 60+ days history (set the cap at the trailing-14-day avg CPA, raise
  ≤5–10%/wk). **Bid Cap** — avoid without auction-level margin data. **ROAS goal** — only at scale
  with clean value data (set at 80% of trailing-28-day ROAS).
- **Principle:** constrain based on where the account *is* (current data), not where you want it.
- **Write:** `ads_update_entity`. **Output:** bid strategy + cap value.

## OPT-7 · Creative refresh

- **Inputs:** fatigue flags from MON-4 (frequency, CTR decay), creative-level performance.
- **Rule:** refresh on CTR decay >25% or a frequency breach; cadence ≈ feed 14–28 d, Reels 7–14 d,
  Stories 10–18 d. Keep winners live; queue the next test.
- **Output:** rotation plan + briefs for net-new creative. **Asset selection stays with the human** —
  the agent can't see the actual image/video.

## OPT-8 · Audience refresh

- **Inputs:** frequency, audience overlap, lookalike performance.
- **Rule:** rebuild lookalikes (test 1% → larger %s); refresh exclusions (recent purchasers). With
  Advantage+ Audience, feed LAL/custom audiences as *suggestions*. Typical split: 70–80% broad /
  Advantage+, 10–20% retargeting, 5–10% interest/LAL tests.
- **Write:** audience tools + `ads_update_entity` (with approval). **Output:** refreshed config.

## OPT-9 · Dayparting / ad scheduling

- **Inputs:** hour-of-day / day-of-week CPC/CTR/CPA breakdown, budget type.
- **Rule:** requires a **lifetime** budget. Test in ~3-hour blocks; keep a schedule only if it lowers
  cost/conversion without killing volume; revert to 24/7 if conversions drop. Don't over-restrict.
- **Write:** `ads_update_entity` (schedule). **Output:** schedule config, or a "not worth it" verdict.

---

**Reminder:** nothing here writes without an explicit, per-change approval. Present one clear diff at
a time, state the expected effect and any learning-phase reset, then apply. When in doubt, recommend
and stop.
