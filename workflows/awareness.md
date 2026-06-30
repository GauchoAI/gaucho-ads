# Awareness — in-session, read-only live state

**Zone: 🟢 green (read-only).** This is how the agent keeps an ongoing eye on the account and
surfaces *what's happening server-side* without you asking each time. It **never writes or spends** —
it calls only `ads_get_*`, `ads_insights_*`, `ads_account_get_*` (all in the harness `allow` list).
All write/activate paths stay gated by [`guardrails.md`](guardrails.md); campaigns stay paused.

Awareness is **in-session only** — it runs while you have Claude Code open. There is **no unattended
scheduler** (that's a deliberate guardrail choice, see `guardrails.md`).

## Two cooperating pieces

### 1. `SessionStart` digest (instant, offline — optional)
An **optional** `SessionStart` hook (enable it during onboarding — see
[`onboarding.md`](onboarding.md) Step 0.5) runs `python3 memory/db.py digest --session-start`,
printing the **last-known state + recent deltas from the DB** — no network, no spend. It ends with a
nudge to run a live refresh. Without the hook, just run `/watch` (or `db.py digest`) yourself. When you see it, **proactively offer/run a live `/watch`** early in the session (unless the
user is mid-task) so they get current state "without asking."

### 2. `/watch` sweep (live, read-only)
On `/watch`, run a full read-only sweep, persist it, and surface only what changed:

1. **Pull** (read-only):
   - `ads_get_ad_entities` — current campaigns / ad sets / ads + status.
   - `ads_insights_performance_trend` (or the relevant `ads_insights_*`) — spend, results, CPA/ROAS,
     frequency per entity.
   - `ads_account_get_activity_logs` — **server-side changes** (edits made in Ads Manager by the
     user or Meta) since the last sweep.
   - `ads_insights_anomaly_signal` — flagged anomalies.
2. **Snapshot** — write one row per entity:
   ```
   python3 memory/db.py snapshot --json '[
     {"scope":"campaign","entity_id":"<id>","entity_name":"<name>","status":"ACTIVE",
      "metrics":{"spend":<n>,"results":<n>,"cpa":<n>,"roas":<n>,"frequency":<n>},
      "source_tool":"ads_insights_performance_trend"}
   ]'
   ```
   (Pass `--json -` and pipe a large array via stdin if needed.)
3. **Diff** — `python3 memory/db.py compute-deltas` computes per-metric changes vs the previous sweep
   and stores narratives.
4. **Surface** — report a tight summary of what changed, drawing on:
   - **Deltas** from `compute-deltas` (spend up/down, CPA drift, frequency climbing…).
   - **Server-side changes** from the activity log (what the user/Meta changed).
   - **Claude's own past actions** from the audit log:
     `python3 memory/db.py query --sql "SELECT ts,action_type,entity_id,field,old_value,new_value FROM audit_log ORDER BY id DESC LIMIT 10"`.
   - **Anomalies** worth attention. For anything actionable, **propose** under the yellow/red rules in
     `optimization.md`/`creation.md` — never act without approval.

## Periodic awareness while you work
Use the built-in `/loop` to repeat the sweep on an interval (it inherits this session's `meta-ads`
MCP and stays read-only): e.g. `/loop 15m /watch`. The default cadence is in
[`../account/defaults.md`](../account/defaults.md) (Awareness cadence). Stop it any time with `Esc`.

## Logging awareness runs
Record each sweep so the audit trail is complete:
`python3 memory/db.py record-audit --json '{"actor":"claude","action_type":"monitor","note":"watch sweep — <n> entities, <n> deltas"}'`

## Relationship to `monitoring.md`
`monitoring.md` defines the monitoring **rules/thresholds** (MON-1..6: pacing, anomalies, learning
phase, frequency, policy, delivery). `awareness.md` is the **persistent, diffing loop** that applies
them against the DB-backed history and surfaces changes. Use `monitoring.md` for the "what counts as
a problem" thresholds; use this file for the "keep me aware over time" mechanics.
