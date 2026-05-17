---
name: dossier-gather
description: "Collect research on people, companies, or jobs and store it as an intelligence dossier."
---

# Dossier Gather

Use this single skill for all research-heavy LinkedIn workflows:

- people search and profile research
- company deep dives
- job searches and job detail capture

## Workflow

1. Start with the smallest query that matches the request.
2. Call LinkedIn MCP tools sequentially.
3. Save the captured result as a markdown dossier artifact.
4. Normalize the raw material into an intelligence brief, not a raw scrape dump.
5. Keep every claim grounded in the source profile or search result.
6. Use `config/dossier-gather/default.md` as the grounding prompt when synthesizing the brief.
7. Fail immediately if the required config file or source artifact is missing.

## Research Modes

### People

Use when the user asks:

- find a person
- profile overview
- who is this person
- research this contact
- people search

MCP tools:

- `search_people`
- `get_person_profile`

Grounding rules:

- Verify spelling and company context before writing the dossier.
- If the name looks misspelled, search the company plus the likely person first, then confirm via the profile URL.
- Do not invent sector angles such as healthcare, medtech, or finance unless the source explicitly supports them.
- Do not force an “adjacent opportunity” section if the profile does not justify it.
- Prefer factual role, company, career arc, education, and visible activity.
- Do not infer filenames, guessed repo roots, or prior dossier paths unless the user explicitly supplied them.

### Companies

Use when the user asks:

- research a company
- company deep dive
- should I join this company
- what is this company doing

MCP tools:

- `search_companies`
- `get_company_profile`
- `get_company_posts`
- `get_company_employees`

### Jobs

Use when the user asks:

- find jobs
- compare roles
- job details
- salary or hiring signals

MCP tools:

- `search_jobs`
- `get_job_details`

## Storage

Store normalized output under:

- `data/dossiers/active/people/`
- `data/dossiers/active/companies/`
- `data/dossiers/active/jobs/`

Avoid saving raw MCP payloads as the main artifact. Raw payloads are only source material.
Do not use hidden alternate paths or default locations.

## Output Quality Bar

The dossier should read like a grounded intelligence brief:

- concise summary
- evidence-backed signals
- relevant outreach angle only when justified
- no speculative industry framing
- no recycled generic language
