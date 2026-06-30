# Guardrails — the safety model

This account spends **real money** (ARS). Safety mode is **approve money moves**: the agent
reads, analyzes, and drafts freely, but every action that creates, changes, or activates an
entity requires explicit human approval. New entities are always created **PAUSED**.

Three independent layers enforce this, so a single failure can't spend money.

## Layer 1 — Harness permissions (`.claude/settings.json`)

Claude Code matches MCP tool-name globs after the `mcp__meta-ads__` prefix, with precedence
**deny → ask → allow**. Unmatched tools fall through to a prompt (fail-safe).

- **`allow` (run without prompting):** `ads_get_*`, `ads_insights_*`, `ads_account_get_*`,
  `authenticate`, `complete_authentication` — all read-only.
- **`ask` (always prompt):** `ads_create_*`, `ads_update_*`, `ads_activate_*`, `ads_boost_*`,
  `ads_catalog_create*`, `ads_experiment_*` — every spend/write path.

The connector is in open beta; if the live tool surface differs from these names, update the globs
(and tell the user), keeping every write family in `ask`.

## Layer 2 — Prompt rule (`CLAUDE.md`)

Independent of the harness prompt, the agent must show a precise diff — **entity · field · old →
new** — and get a clear "yes" before any write. Create PAUSED. Treat your own causal explanations
as hypotheses; cross-check numbers against Ads Manager.

## Layer 3 — Workflow gates (`workflows/*.md`)

Each yellow/red step carries an approval checkpoint and a safety floor (below).

## Action zones

| Zone | Examples | Rule |
|---|---|---|
| 🟢 **Green** | monitoring, reporting, analysis, drafting, signal diagnostics, naming validation | Run freely (read-only) |
| 🟡 **Yellow** | pause, budget / bid change, audience or structure edit | Propose → **approve** → write |
| 🔴 **Red** | new campaign / ad set / ad going live | Assemble → create **PAUSED** → explicit `/activate` |

## Safety floors (check before any write)

Values come from [`../account/defaults.md`](../account/defaults.md) (editable):

- **CPA ceiling** — no budget increase if 7-day CPA > target × 1.2.
- **ROAS floor** — no scaling if 7-day ROAS < the account's floor.
- **Budget delta cap** — max **+15% / day** without re-approval.
- **Frequency** — pause/refresh when ad-level frequency > 3.0 (cold audiences).
- **Learning lock** — no structural edits in the first ~14 days post-launch (edits reset learning).

## The approval state machine

```
READ (auto)
  └─ analyze → PROPOSE a diff (auto)
        └─ human APPROVE?  ──no──>  stop, log the recommendation, move on
              └─ yes ─> WRITE
                         • create / edit → entity ends PAUSED (red) or change applied (yellow)
                         • going live    → requires a separate /activate (a second, explicit yes)
```

## Read-only awareness is allowed (not "automation")

In-session, **read-only** monitoring — `/watch`, the `SessionStart` digest, periodic `/loop /watch`
— is explicitly fine: it calls only `ads_get_*` / `ads_insights_*` / `ads_account_get_*`, never a
write tool, and runs only while you have a session open. It writes to the **local** memory DB, never
to Meta. This carve-out does not loosen anything below — the prohibition is specifically on
unattended *writing*. See [`awareness.md`](awareness.md) and [`memory.md`](memory.md).

## Out of scope (documented, not built)

Unattended **writing** automation (schedulers, auto-apply, "set it and forget it" rules) is
intentionally **not** built — the official MCP is human-in-the-loop by design (no scheduler), and
cloud routines would run autonomously with writes allowed and no approval prompts. If you ever need
it, the self-host route (Pipeboard `meta-ads-mcp` or your own Meta app) requires App ID + App
Secret + a **system-user access token** + `act_<id>`, plus its own guardrails. Do not add
autonomous writing without revisiting this safety model first.

## Secrets boundary

The committed memory store (`memory/agent.sqlite` + `memory/audit-log.jsonl`) holds **NON-SECRET data
only** — profile, goals, audit log, monitoring snapshots. The Meta OAuth token stays in Claude Code's
MCP auth store (outside the repo); it is **never** copied into the DB/JSONL/git. Any future secret
(e.g. a self-host App Secret + system-user token) belongs in the **OS keychain**, referenced by name.
`memory/db.py checkpoint` runs a best-effort secret scan and aborts on a token-shaped string;
`.gitignore` blocks `.env*`. See [`memory.md`](memory.md).
