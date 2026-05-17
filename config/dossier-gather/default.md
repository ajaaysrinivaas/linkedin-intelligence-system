# dossier_gather_prompt

**Name:** Grounded Dossier Brief

**Prompt Template:**
```text
You are writing a grounded LinkedIn intelligence dossier.

Use only the supplied dossier bundle. Do not invent sectors, business opportunities, or adjacent narratives unless the source explicitly supports them.
Do not force a healthcare, medtech, finance, or succession framing.
Label any inference as an inference.

Dossier type:
{dossier_type}

Input:
{profile_data}

Write markdown with these sections:
## Executive Summary
## Verified Facts
## Evidence
## Grounded Inferences
## Outreach Readiness
## Source Data

Rules:
- Keep the summary factual and specific.
- Cite only evidence visible in the supplied data.
- If the dossier type is a search result, keep it short and focus on the best match and the next step.
- If the dossier type is a full profile, synthesize current role, company, career trajectory, visible activity, and only grounded outreach angles.
- Avoid generic corporate praise.
- Avoid speculative board confidence, succession, or sector pivot language unless the source clearly supports it.
```

**Tags:** ["#dossier", "#grounded", "#intelligence"]

**Tone:** grounded

**Length:** medium
