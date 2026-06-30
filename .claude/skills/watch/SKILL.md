---
name: watch
description: Read-only live awareness sweep of the Meta Ads account — pulls current entities/insights/activity-logs, diffs against the last snapshot in the memory DB, and surfaces what changed server-side (changes, spend, anomalies, and Claude's own past actions). Never writes or spends. Use /loop 15m /watch to keep it running while you work.
argument-hint: ""
disable-model-invocation: true
---

Run a **read-only** awareness sweep. Follow [`workflows/awareness.md`](../../../workflows/awareness.md).

This is 🟢 green / read-only — call only `ads_get_*`, `ads_insights_*`, `ads_account_get_*`. Do
**not** call any write/activate tool; if something looks actionable, *propose* it under the
guardrails, don't do it.

Steps:
1. Pull current state: `ads_get_ad_entities`, the relevant `ads_insights_*` (spend/results/CPA/ROAS/
   frequency), `ads_account_get_activity_logs` (server-side changes), `ads_insights_anomaly_signal`.
2. Persist: `python3 memory/db.py snapshot --json '[…per-entity rows…]'`, then
   `python3 memory/db.py compute-deltas`.
3. Surface a tight summary of **what changed** since the last sweep: deltas, server-side activity,
   anomalies, and recent entries from the audit log (`db.py query …`).
4. Log the sweep: `python3 memory/db.py record-audit --json '{"actor":"claude","action_type":"monitor","note":"watch sweep"}'`.

Periodic mode: suggest `/loop 15m /watch` (or the cadence in `account/defaults.md`) to keep awareness
live while the user works. Reads are free, so this runs without approval prompts.
