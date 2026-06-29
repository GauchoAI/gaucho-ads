---
name: create-campaign
description: Assemble a new Meta Ads campaign end-to-end (objective, audience, budget, creative, naming, QA) and create it PAUSED for review. Never goes live — activation is the separate /activate.
argument-hint: "[a short brief, e.g. 'memory foam sale, Buenos Aires, WhatsApp']"
disable-model-invocation: true
---

Assemble a new Meta Ads campaign.

Paths below are relative to the repo root.

1. Read `workflows/creation.md` (the steps), `workflows/guardrails.md` (safety), and
   `account/defaults.md` (objective, target CPA, budget, naming convention).
2. Use the arguments (`$ARGUMENTS`) as the campaign brief. Walk CRT-1..CRT-7, gathering any missing
   inputs from the user — especially the **creative asset**, which the human must supply (the agent
   can't see images/video).
3. Run the CRT-7 pre-launch QA checklist. Fix anything that fails before proceeding.
4. Present the **full assembled spec** (objective · audience · budget in ARS · creative · names) as
   one summary, and get approval to create it — paused.
5. On approval, create the entities **PAUSED** in order: `ads_create_campaign` →
   `ads_create_ad_set` → `ads_create_creative` → `ads_create_ad`. Then show `ads_get_ad_preview`.
6. Confirm every entity is **PAUSED** and tell the user it is **not spending**. Going live is a
   separate **`/activate`**.

🔴 Never call `ads_activate_entity` here. Build it, pause it, hand it off.
