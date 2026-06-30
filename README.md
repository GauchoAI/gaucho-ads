# gaucho-ads

Agentic Meta Ads management via Claude Code and the **official Meta Ads MCP** — monitor, optimize,
create, and report on real Facebook/Instagram campaigns in natural language, with money-spending
actions gated behind your explicit approval.

Mattress sales, Argentina · ad account `1930186940607840` · ARS.

## Quickstart

1. Open Claude Code **inside this directory** (`gaucho-ads`).
2. Approve the `meta-ads` MCP server when prompted (it's defined in `.mcp.json`).
3. Run **`/onboard`** — a browser opens, you log in + click **Authorize**, and the callback is
   **captured automatically** (no URL pasting; **no API keys**). It then verifies the account, checks
   billing, captures your goals, and bootstraps the local memory store.
4. Run **`/watch`** anytime for a read-only pulse on what changed, or **`/menu`** to pick a workflow.

A fresh session in this repo has everything it needs.

## What's inside

| Path | Purpose |
|---|---|
| `CLAUDE.md` | Always-on context + the guardrails (read first) |
| `.mcp.json` | Registers the official `meta-ads` MCP (`https://mcp.facebook.com/ads`) |
| `.claude/settings.json` | Enables the MCP + enforces read-allow / write-prompt permissions |
| `.claude/skills/` | The `/slash` menu — `onboard`, `watch`, `menu`, `monitor`, `optimize`, `create-campaign`, `report`, `activate`, `checkpoint` |
| `workflows/` | The playbooks (decision rules + which `ads_*` tools to call) + `guardrails.md`, `awareness.md`, `memory.md` |
| `account/defaults.md` | Editable account facts + strategy thresholds (single source of truth) |
| `memory/` | Durable cross-session memory — SQLite (`agent.sqlite`) + audit JSONL via git LFS, **non-secret only**; helper `db.py`. See [`workflows/memory.md`](workflows/memory.md) |
| `Documentation/meta-mcp-setup.md` | The original MCP setup + troubleshooting journey |

## The workflows

🟢 **Monitor** & **Report** run freely (read-only). 🟡 **Optimize** proposes changes and waits for
your approval. 🔴 **Create** assembles a campaign and leaves it **PAUSED** — going live is a separate,
deliberate **`/activate`**. See [`workflows/README.md`](workflows/README.md) for the full menu.

## Safety

**Approve money moves.** Reads are free; every create / budget-up / activate requires explicit
approval, enforced in three layers (harness permissions, prompt rules, workflow gates). New campaigns
never spend until you activate them. Details in [`workflows/guardrails.md`](workflows/guardrails.md).

## Status

- Ad account `1930186940607840` — active, ARS, funded (~$20,000 ARS loaded).
- Agentic scaffold (workflows, skills, guardrails) — in place.
- Browser-driven onboarding (auto-captured OAuth) + in-session read-only awareness (`/watch`).
- Durable memory in `memory/agent.sqlite` (git LFS) — profile, goals, audit log, monitoring history.
- Each new machine/session connects with **`/onboard`** (MCP auth is per-environment).
