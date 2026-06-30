# gaucho-ads — Meta Ads agent

Manage a real Meta (Facebook/Instagram) ad account through the **official Meta Ads MCP**
(server `meta-ads` → `https://mcp.facebook.com/ads`), entirely in natural language.

**Business:** mattress sales, Argentina · **Ad account:** `1930186940607840` · **Currency:** ARS
All account facts and every tunable threshold live in [`account/defaults.md`](account/defaults.md).

## ⛔ Guardrails — the money is real (read first)

Safety mode: **approve money moves**. The harness enforces it (`.claude/settings.json`), and so
must you:

1. **Never call a write tool without explicit approval.** Before any `ads_create_*`,
   `ads_update_*`, `ads_activate_*` (or other write), show *exactly* what will change —
   **entity · field · old → new** — and wait for a clear "yes". The harness will also prompt;
   that prompt is **not** a substitute for showing the diff first.
2. **New campaigns / ad sets / ads are always created `PAUSED`.** They never spend until the user
   runs `/activate` on them deliberately.
3. **Reads are free.** Pulling insights, listing entities, building reports, and drafting proposed
   changes need no approval — do them liberally.
4. **Respect the safety floors** in [`workflows/guardrails.md`](workflows/guardrails.md) (no budget
   increase if 7-day CPA > target × 1.2; max +15%/day; no structural edits during learning).
5. **Verify, don't assert.** Cross-check against what the MCP returns; treat your own "why did X
   happen" explanations as hypotheses, not facts.

## How to work here

- **`/menu`** lists every workflow — route the user there if they're unsure.
- The categories (full decision rules + which `ads_*` tools to call live in the playbooks):

  | Category | Playbook | Zone |
  |---|---|---|
  | Awareness | [`workflows/awareness.md`](workflows/awareness.md) | 🟢 read-only |
  | Monitor | [`workflows/monitoring.md`](workflows/monitoring.md) | 🟢 read-only |
  | Optimize | [`workflows/optimization.md`](workflows/optimization.md) | 🟡 propose → approve |
  | Create | [`workflows/creation.md`](workflows/creation.md) | 🔴 assemble → PAUSED |
  | Report | [`workflows/reporting.md`](workflows/reporting.md) | 🟢 read-only |

- **Not connected yet?** Run **`/onboard`** ([`workflows/onboarding.md`](workflows/onboarding.md)).
- **Free-form requests** ("how are my ads doing?", "scale the winners") are welcome — map them to
  the relevant playbook and honor the guardrails. The `workflows/*.md` files are the source of
  truth; the `/slash` skills are just shortcuts into them.

## Memory & awareness

This project has a **durable memory store** — `memory/agent.sqlite` (git LFS) + an append-only
`memory/audit-log.jsonl` mirror — holding the account profile, goals, an **audit log of every action
you take**, and **monitoring snapshots/deltas**. It is the project's cross-session memory. Touch it
only through the helper: `python3 memory/db.py …` (see [`workflows/memory.md`](workflows/memory.md)).

- **Log what you do.** After any proposal, approved write, or `/activate`, record it
  (`db.py record-audit`). After a `/watch` sweep, `snapshot` then `compute-deltas`.
- **Stay aware.** `/watch` is in-session, **read-only** live awareness (diffs vs the last snapshot,
  surfaces what changed server-side — see [`workflows/awareness.md`](workflows/awareness.md)). An
  optional `SessionStart` digest (enabled during onboarding) greets you with last-known state; when
  you see it, proactively offer a live `/watch`. There is **no unattended scheduler** — by design
  (see `guardrails.md`).
- **Commit via `/checkpoint`** — never `git add` the DB directly; `/checkpoint` folds the WAL, scans
  for secrets, and stages the LFS files. Never auto-commit mid-sweep.

## ⛔ Secrets boundary

The committed memory store holds **NON-SECRET data only**. The Meta OAuth token is managed by Claude
Code's MCP auth store (outside the repo) — **never** copy it into the DB, the JSONL, or git. The
schema has no credential columns. Any future secret → the **OS keychain**, never the repo. `db.py
checkpoint` aborts if a token-shaped string is found in the committed files.

## Conventions

- Use the naming convention in `account/defaults.md` for any entity you create.
- Thresholds are **editable defaults** in `account/defaults.md` — read them there, never hardcode.
  Meta-official rules (≈50 conversions / 7 days to exit learning) are fixed.
- Currency is **ARS** — always state amounts with the currency and sanity-check the magnitude.

## Setup reference

[`Documentation/meta-mcp-setup.md`](Documentation/meta-mcp-setup.md) is the canonical MCP setup +
troubleshooting journey (OAuth flow, Argentine billing notes). Onboarding links to it.
