# feed

Helpers for the feed insights workflow.

This package turns normalized feed data into actionable insight artifacts.

## Modules

- `prompt.py`: builds the prompt payload used to summarize feed data using configured prompt templates.
- `render.py`: renders the finalized feed insights markdown document from artifact metadata, normalized posts, and extracted signals.
- `signals.py`: extracts signal-level data from normalized feed posts, such as notable authors, companies, and post-level cues.
