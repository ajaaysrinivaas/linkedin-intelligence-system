# dossier

Rendering helpers for dossier research workflows.

This package converts normalized dossier payloads into final markdown research artifacts.

## Modules

- `renderers.py`: renders dossier markdown for different kinds of output.
  - `render_people_dossier()`: creates a people intelligence dossier with frontmatter, a one-liner, outreach angles, and evidence sections.
  - `render_people_search()`: renders a people search result summary with best match details and recommended next steps.
  - `render_generic_dossier()`: renders generic markdown for company and job dossiers, including a JSON dump of normalized payloads.
