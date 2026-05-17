# normalization

Normalization helpers for raw LinkedIn MCP output.

This package standardizes incoming JSON payloads into canonical structures that workflows can render consistently.

## Modules

- `dossiers.py`: normalizes people, company, and job dossier payloads.
  - extracts candidate names, headlines, company details, search results, and smart profile signals.
  - builds people intelligence payloads with outreach angles, fit signals, evidence, and profile metadata.
  - summarizes job search results into entries with title, company, location, and posting metrics.
  - normalizes company payloads with description, post counts, job counts, and employee counts.
- `feed.py`: normalizes feed payloads.
  - extracts posts, authors, companies, timestamps, and URLs from nested feed structures.
  - deduplicates duplicate items and computes author/company frequency metrics.
  - creates normalized `posts`, `authors`, `companies`, and summary counts for insight generation.
