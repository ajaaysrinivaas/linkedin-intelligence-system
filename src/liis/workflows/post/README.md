# post

Helpers for building and saving LinkedIn post drafts.

This package turns raw idea markdown into curated draft posts suitable for publishing.

## Modules

- `prompt.py`: renders a post prompt by combining raw idea content with a configured template.
- `workflow.py`: parses raw idea markdown frontmatter, generates a post draft body, creates draft metadata, saves curated markdown, and indexes the draft artifact.
