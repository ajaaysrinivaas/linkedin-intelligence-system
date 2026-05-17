---
name: outreach
description: "Prepare, review, and manage LinkedIn outreach and inbox workflows."
---

# Outreach

Use this skill for:

- preparing a message draft for a specific person
- preparing a connection note
- reviewing inbox conversations
- searching conversations by keyword
- sending a message only after explicit confirmation

## Workflow

1. Load the target person from `config/dossier-gather/people.md`, or from a prior dossier only when the dossier file path is supplied explicitly.
2. Prepare the outreach brief locally.
3. Show recipient, context, and message before any send action.
4. Use the MCP tool only after explicit approval.
5. Fail immediately if the target cannot be resolved from the supplied inputs.

## Output

- prepared outreach briefs in `data/outreach/`
- inbox and conversation context used as source material
- indexed artifacts in `data/index/catalog.json`
- no implicit target lookup beyond the provided inputs
