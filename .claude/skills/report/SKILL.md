---
name: report
description: Generate a read-only Meta Ads report — daily pacing, weekly performance, creative, audience breakdown, or executive. No spend, no changes.
argument-hint: "[daily | weekly | creative | audience | exec]"
disable-model-invocation: true
---

Generate a Meta Ads report.

Paths below are relative to the repo root.

1. Read `workflows/reporting.md` as the source of truth, and `account/defaults.md` for the action-
   flag thresholds.
2. Build the report type given in the arguments (`$ARGUMENTS`); default to `weekly` if none given.
   Valid types: `daily`, `weekly`, `creative`, `audience`, `exec`.
3. Pull data with the insights tools, format the report as specified, and include the auto-derived
   action flags (PAUSE / SCALE / MONITOR) where relevant. Amounts in ARS.

This is 🟢 read-only. Flags are recommendations only — acting on one goes through `/optimize`.
