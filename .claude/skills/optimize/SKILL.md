---
name: optimize
description: Analyze the Meta Ads account and PROPOSE optimization changes — pause losers, scale winners, reallocate budget, adjust bids, refresh creative/audience, dayparting. Always proposes a diff and waits for explicit approval; never writes on its own.
argument-hint: "[all | opt-1..opt-9 | a goal like 'scale winners']"
disable-model-invocation: true
---

Run the optimization workflow for the Meta Ads account.

Paths below are relative to the repo root.

1. Read `workflows/optimization.md` (the plays), `workflows/guardrails.md` (the safety floors), and
   `account/defaults.md` (the thresholds).
2. Analyze the account read-only. If the arguments (`$ARGUMENTS`) name a specific play or goal, focus
   there; otherwise review across OPT-1..OPT-9 and surface the highest-value moves.
3. For each recommended change, **in order**:
   a. Check the relevant safety floor — if it blocks the action, say so and skip it.
   b. Present a precise diff: **entity · field · old → new · expected effect**, and note any
      learning-phase reset.
   c. Wait for the user's explicit "yes" for that specific change.
   d. Only then apply it with `ads_update_entity` / `ads_activate_entity` — one change at a time.

🟡 This is propose-then-approve. Never batch-apply, never write without showing the diff and getting
approval first. New entities (e.g. duplicated ad sets) are created **PAUSED**; going live is `/activate`.
