# liis

Core implementation for the LinkedIn Intelligence System.

This package contains the backend logic that converts raw LinkedIn MCP output into durable artifacts under `data/`.

## What it contains

- `cli.py`: command-line helper and test harness for ingesting raw JSON, building feed insights, drafting posts, and preparing outreach objects.
- `config.py`: prompt template loader and shared configuration access.
- `normalize.py`: top-level normalization entrypoint that dispatches raw payloads to dossier or feed normalizers.
- `storage.py`: repository storage support for saving markdown, JSON, and run records, and for enforcing the workspace file layout.
- `index.py`: artifact cataloging and metadata management using `Catalog` and `IndexEntry`.
- `models.py`: shared dataclasses such as `Artifact` and `RunRecord`.
- `utils.py`: common helpers for timestamps, JSON/YAML parsing, slug generation, and frontmatter handling.
- `normalization/`: raw mapper modules for dossiers and feed payloads.
- `workflows/`: high-level workflow orchestrators for dossier ingestion, feed insights, post drafting, and outreach preparation.

## How it fits

The `src/liis/` package is the engine used by Copilot skills to process, normalize, render, and store LinkedIn intelligence workflows.
