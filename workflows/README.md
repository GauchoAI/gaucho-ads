# Workflow menu

The agentic Meta Ads playbooks for this account. Each workflow names the exact `ads_*` MCP tools
and the decision rules it uses. Thresholds come from [`../account/defaults.md`](../account/defaults.md);
safety rules from [`guardrails.md`](guardrails.md).

**Zones:** 🟢 read-only (runs freely) · 🟡 propose → approve → write · 🔴 assemble → PAUSED → `/activate`

## First time here → `/onboard`

Connect the MCP, authenticate, verify the account, check billing, capture goals.
See [`onboarding.md`](onboarding.md).

## 🟢 Monitor — `/monitor` → [`monitoring.md`](monitoring.md)

Read-only health checks. Run anytime.

- **MON-1 Spend pacing** — actual vs planned; project end-of-month.
- **MON-2 CPA/ROAS anomaly** — flag degradation (uses `ads_insights_anomaly_signal`).
- **MON-3 Learning-phase status** — find ad sets stuck / Learning Limited.
- **MON-4 Frequency / fatigue** — frequency + CTR decay.
- **MON-5 Disapproved / policy** — rejected ads & account quality.
- **MON-6 Delivery / zero-spend** — ad sets not delivering, and why.

## 🟡 Optimize — `/optimize` → [`optimization.md`](optimization.md)

Analyze and **propose** changes; apply only after you approve.

- **OPT-1 Kill underperformers** · **OPT-2 Scale winners** · **OPT-3 Horizontal expansion**
- **OPT-4 Budget reallocation** · **OPT-5 CBO vs ABO** · **OPT-6 Bid strategy**
- **OPT-7 Creative refresh** · **OPT-8 Audience refresh** · **OPT-9 Dayparting**

## 🔴 Create — `/create-campaign` → [`creation.md`](creation.md)

Assemble a campaign end-to-end; create it **PAUSED**. Going live is a separate **`/activate`**.

- **CRT-1 Objective** → **CRT-2 Audience** → **CRT-3 Budget/schedule** → **CRT-4 Creative**
  → **CRT-5 Naming** → **CRT-6 A/B structure** → **CRT-7 Pre-launch QA**.

## 🟢 Report — `/report [daily|weekly|creative|audience|exec]` → [`reporting.md`](reporting.md)

Read-only reports with an auto-derived action flag (PAUSE / SCALE / MONITOR) per row.

- **REP-1 Daily pacing** · **REP-2 Weekly performance** · **REP-3 Creative**
  · **REP-4 Audience / breakdown** · **REP-5 Executive**

---

Free-form is fine too — describe what you want and it maps to the right playbook, under the guardrails.
