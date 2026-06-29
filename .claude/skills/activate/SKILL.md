---
name: activate
description: Take a PAUSED Meta Ads entity live. This STARTS REAL SPENDING (ARS). Deliberate and money-gated — requires a billing check and an explicit, unambiguous confirmation before it activates anything.
argument-hint: "[campaign / ad set / ad name or id]"
disable-model-invocation: true
---

Take a PAUSED entity live. **This is the one workflow that starts real spending.** Be maximally careful.

Paths below are relative to the repo root.

1. Identify the target entity from the arguments (`$ARGUMENTS`) using `ads_get_ad_entities`. If it's
   ambiguous or names more than one entity, stop and ask — never guess what to activate.
2. Show its current state: status, daily/lifetime budget (ARS), schedule, and a one-line targeting
   summary.
3. **Pre-flight checks:**
   - Billing is set (`has_payment_method`, funds available) — if not, stop; it can't spend anyway.
   - The CRT-7 pre-launch QA (see `workflows/creation.md`) passed.
   - The budget magnitude in ARS is sane against `account/defaults.md`.
4. State plainly what will go live and the **daily/lifetime budget at risk**, then require an
   explicit, unambiguous confirmation (e.g. the user says "yes, activate"). A vague reply is not
   approval.
5. Only then call `ads_activate_entity` → ACTIVE, for exactly the entity named — nothing more.
6. Confirm the new status and suggest running `/monitor` after a few hours.

🔴 Never activate more than the user explicitly named. Never infer activation from another workflow.
Honor `workflows/guardrails.md`.
