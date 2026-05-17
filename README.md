# LinkedIn Intelligence System

LinkedIn Intelligence System is a small Python workspace for turning LinkedIn MCP output into durable research artifacts.

It normalizes raw profile and feed data, stores generated dossiers and briefs, and keeps the workflow logic in a repeatable package layout.

## Attribution

This project is built around output from the external MCP server [`stickerdaniel/linkedin-mcp-server`](https://github.com/stickerdaniel/linkedin-mcp-server).

## Public Repo Policy

This repository is prepared for public use:

- generated artifacts are not meant to be committed
- local environment folders are ignored
- only one sample dossier output is kept in source control: `data/dossiers/active/people/satya_nadella.md`
- example prompts and templates remain in `config/` and `src/liis/`

## What It Does

- turns LinkedIn MCP output into reusable intelligence artifacts
- synthesizes people, company, and job research into dossiers
- generates feed insight briefs from raw feed JSON
- builds post drafts from raw idea markdown
- prepares outreach briefs for a specific target
- maintains a catalog index for later retrieval
- archives stale data on startup via `lifecycle.py`

## Project Layout

- `src/liis/` - package code for the CLI, storage, normalization, and workflows
- `config/` - prompt templates and watchlists
- `data/` - runtime workspace for generated artifacts and the retained sample dossier
- `archived/` - archived artifacts created by lifecycle maintenance
- `tests/` - unit and integration tests
- `Tools.md` - MCP tool reference

## Installation

### From source
Clone the repository and install in development mode:

```bash
git clone https://github.com/ajaaysrinivaas/linkedin-intelligence-system.git
cd linkedin-intelligence-system
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .[dev]
```

### Requirements
- Python 3.8+
- The external MCP server: [`stickerdaniel/linkedin-mcp-server`](https://github.com/stickerdaniel/linkedin-mcp-server)

## Testing

Run the test suite:

```bash
pytest
```

## CLI Reference

Install the CLI and view available commands:

```bash
liis --help
```

## Typical CLI Usage

```bash
liis --root <repo-root> ingest jobs --source-name jobs-watchlist --input path/to/raw-jobs.json
liis --root <repo-root> ingest companies --source-name company-search --input path/to/raw-companies.json
liis --root <repo-root> ingest people --source-name people-search --input path/to/raw-people.json
liis --root <repo-root> feed-insights --input path/to/feed.json
liis --root <repo-root> post --input path/to/raw-idea.md
liis --root <repo-root> outreach --people-config config/dossier-gather/people.md --target <username> --message "..."
```

## Notes

- The CLI expects an explicit workspace root so it can create or locate `data/`, `config/`, and archive paths.
- Generated dossiers, feed briefs, and post drafts should stay out of version control.
- `lifecycle.py` is a maintenance helper for archiving stale artifacts, not a required part of normal development.

## License

MIT License © 2026 Ajaay Srinivaas R. See [LICENSE](LICENSE) for details.
