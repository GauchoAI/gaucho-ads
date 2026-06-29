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
- The four categories (full decision rules + which `ads_*` tools to call live in the playbooks):

  | Category | Playbook | Zone |
  |---|---|---|
  | Monitor | [`workflows/monitoring.md`](workflows/monitoring.md) | 🟢 read-only |
  | Optimize | [`workflows/optimization.md`](workflows/optimization.md) | 🟡 propose → approve |
  | Create | [`workflows/creation.md`](workflows/creation.md) | 🔴 assemble → PAUSED |
  | Report | [`workflows/reporting.md`](workflows/reporting.md) | 🟢 read-only |

- **Not connected yet?** Run **`/onboard`** ([`workflows/onboarding.md`](workflows/onboarding.md)).
- **Free-form requests** ("how are my ads doing?", "scale the winners") are welcome — map them to
  the relevant playbook and honor the guardrails. The `workflows/*.md` files are the source of
  truth; the `/slash` skills are just shortcuts into them.

## Conventions

- Use the naming convention in `account/defaults.md` for any entity you create.
- Thresholds are **editable defaults** in `account/defaults.md` — read them there, never hardcode.
  Meta-official rules (≈50 conversions / 7 days to exit learning) are fixed.
- Currency is **ARS** — always state amounts with the currency and sanity-check the magnitude.

## Setup reference

[`Documentation/meta-mcp-setup.md`](Documentation/meta-mcp-setup.md) is the canonical MCP setup +
troubleshooting journey (OAuth flow, Argentine billing notes). Onboarding links to it.
