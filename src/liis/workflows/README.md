# workflows

High-level workflow entrypoints that convert normalized LinkedIn data into stored output artifacts.

This package orchestrates the full end-to-end steps for each intelligence flow:
- normalize input
- render a markdown or JSON artifact
- persist the output
- update the catalog index

## Modules

- `dossiers.py`: ingests raw dossier JSON for people, companies, and jobs; normalizes it; renders markdown dossiers; saves artifacts and indexes them.
- `feed_insights.py`: ingests raw feed JSON; normalizes posts; extracts signal data; builds prompt context; renders a feed insight report; saves the result.
- `posts.py`: ingests raw idea markdown with YAML frontmatter; builds a draft post body using configured templates; saves curated markdown and indexes the draft.
- `outreach/`: loads people targets, finds recipient matches, and prepares outreach messages with structured metadata.
