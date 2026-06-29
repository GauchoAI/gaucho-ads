---
name: monitor
description: Run read-only Meta Ads health checks — spend pacing, CPA/ROAS anomalies, learning-phase status, frequency/fatigue, disapproved ads, and delivery issues. Safe; never spends or changes anything.
argument-hint: "[all | mon-1..mon-6 | a topic like 'fatigue']"
disable-model-invocation: true
---

Run the monitoring suite for the Meta Ads account.

Paths below are relative to the repo root.

1. Read `workflows/monitoring.md` and use it as the source of truth.
2. Read thresholds from `account/defaults.md`; pull the account baseline first
   (`ads_insights_advertiser_context`).
3. Run the checks. If the user named a specific one in the arguments (`$ARGUMENTS`), run just that
   one; otherwise run all of MON-1..MON-6.
4. Output: a one-line health verdict, a compact table (entity · metric · value · status), then the
   flagged items with the suggested next workflow.

This is 🟢 read-only. Never call a write tool here — if a fix is warranted, recommend `/optimize`
(and let the user decide).
