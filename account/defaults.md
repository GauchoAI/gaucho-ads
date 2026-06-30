# Account Defaults & Strategy Config

Single source of truth for account facts and the thresholds every workflow uses.
**Edit these freely** — they are starting points, not laws. Workflows read this file; change a
value here and every workflow respects it. Values flagged **(Meta-official)** are platform rules,
not heuristics — don't loosen them.

> Items marked `‹set during onboarding›` are captured by `/onboard`. Until a value is set,
> workflows will ask before acting on anything that depends on it.

## Account facts

| Field | Value |
|---|---|
| Ad account ID | `1930186940607840` |
| Currency | ARS (Argentine peso) |
| Business | Mattress sales, Argentina |
| Primary objective | ‹set during onboarding› — Traffic / Sales / Awareness |
| Landing destination | ‹set during onboarding› — website / WhatsApp / Instagram |
| Time zone | ‹set during onboarding› |

## Performance targets (editable)

| Target | Value | Notes |
|---|---|---|
| Target CPA | ‹set during onboarding› | Cost per result you'll accept (ARS) |
| ROAS floor | ‹set during onboarding› | Minimum acceptable return on ad spend |
| Monthly budget | ‹set during onboarding› | Total planned spend (ARS) |

## Optimization thresholds (editable heuristics)

Practitioner consensus, **not** Meta rules — tune to how this account actually behaves.

| Rule | Default | Used by |
|---|---|---|
| Kill underperformer | spend > 1.5× target CPA with 0 conversions over 3 days | OPT-1 |
| Conservative kill | CPA > 2× target **and** spend > 1× target CPA **and** impressions > 2,000 | OPT-1 |
| Min impressions before judging rate metrics | 5,000–10,000 | OPT-1, reporting |
| Scale step (winners) | ≤ 20% budget increase every 24–72 h | OPT-2 |
| Budget delta cap (per change) | +15% / day without re-approval | OPT-4, guardrails |
| Frequency — cold / prospecting | 3.0 monitor · 4.0 fatigue | MON-4, OPT-7 |
| Frequency — warm / retargeting | 5–7 | MON-4 |
| Creative refresh cadence | feed 14–28 d · Reels 7–14 d · Stories 10–18 d | OPT-7 |
| Pacing on-track band | 90–110% of planned | MON-1, REP-1 |
| Anomaly trigger | CPA > 20% above target over 7 d, or above target 3 days running | MON-2 |
| Awareness sweep cadence | 15 min (in-session `/loop /watch`) | awareness.md |

## Platform rules (fixed — Meta-official)

| Rule | Value |
|---|---|
| Exit learning phase | ~50 optimization events per 7-day rolling window |
| Learning reset | significant edits (budget / targeting / bid / event) reset learning to day 1 |
| Learning lock (our policy) | no structural edits in the first ~14 days post-launch |
| Dayparting | requires a **lifetime** budget (unavailable on daily budgets) |

## Naming convention

Three levels, **underscores** (not hyphens) for clean parsing:

- **Campaign:** `‹funnel›_‹objective›_‹budget-type›_‹bid-strategy›` — e.g. `TOF_Traffic_CBO_LowestCost`
- **Ad set:** `‹audience›_‹placement›_‹geo›` — e.g. `Broad_AdvantagePlus_AR-CABA`
- **Ad:** `‹concept›_‹format›_‹date›` — e.g. `MemoryFoam_1x1_2026-07-01`

## Safety posture

- Mode: **Approve money moves** — reads run free; create / update / activate require explicit approval.
- New campaigns / ad sets / ads are always created **PAUSED**; going live is a separate `/activate`.
- **Memory:** this file stays the human-editable source of truth for goals & thresholds; the durable
  store (`memory/agent.sqlite`, git LFS, **non-secret only**) mirrors goals and snapshots these
  thresholds over time, and holds the audit log + monitoring history. See
  [`../workflows/memory.md`](../workflows/memory.md).
- Full model: [`../workflows/guardrails.md`](../workflows/guardrails.md).
