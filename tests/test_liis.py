from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from liis.config import load_dossier_prompt_template, load_feed_prompt_template, load_prompt_template, load_watchlist
from liis.storage import RepositoryStore
from liis.normalize import normalize_dossier_payload
from liis.workflows.dossiers import ingest_dossier_file
from liis.workflows.feed_insights import build_feed_insights_from_file
from liis.workflows.outreach import build_outreach_brief, find_target, load_targets
from liis.workflows.posts import build_post_draft


def _write_minimal_config(root: Path) -> None:
    (root / "config" / "dossier-gather").mkdir(parents=True, exist_ok=True)
    (root / "config" / "content-draft").mkdir(parents=True, exist_ok=True)
    (root / "config" / "feed-insights").mkdir(parents=True, exist_ok=True)

    (root / "config" / "dossier-gather" / "jobs.md").write_text(
        """# Jobs\n\n```yaml\njobs:\n  - title: \"AI Engineer\"\n    keywords: \"ai engineer\"\n    location: \"Remote\"\n```\n""",
        encoding="utf-8",
    )
    (root / "config" / "content-draft" / "quick_take.md").write_text(
        """# quick_take\n\n**Name:** Quick Take (1 paragraph)\n\n**Prompt Template:**\n```\nQuick take.\nRaw: {raw_content}\nUse hashtags: {tags}\n```\n\n**Tags:** [\"#one\", \"#two\"]\n\n**Tone:** direct\n\n**Length:** short\n""",
        encoding="utf-8",
    )
    (root / "config" / "dossier-gather" / "default.md").write_text(
        """# dossier_gather_prompt\n\n**Name:** Grounded Dossier Brief\n\n**Prompt Template:**\n```text\nUse only the supplied dossier bundle.\nDossier type: {dossier_type}\nInput:\n{profile_data}\n\nWrite markdown with:\n## Executive Summary\n## Verified Facts\n## Evidence\n## Grounded Inferences\n## Outreach Readiness\n## Source Data\n```\n\n**Tags:** [\"#dossier\", \"#grounded\", \"#intelligence\"]\n\n**Tone:** grounded\n\n**Length:** medium\n""",
        encoding="utf-8",
    )
    (root / "config" / "feed-insights" / "default.md").write_text(
        """# feed_insights\n\n**Name:** Feed Intelligence Brief\n\n**Prompt Template:**\n```text\nYou are writing a feed intelligence brief from a preprocessed feed bundle.\nFeed summary:\n{feed_summary}\n\nTop posts:\n{top_posts}\n\nObserved signals:\n{signals}\n\nWrite markdown with:\n## Executive Summary\n## What Changed\n## Key Themes\n## Actionable Signals\n## People to Watch\n## Companies to Watch\n## Next Actions\n```\n\n**Tags:** [\"#feed\", \"#intelligence\"]\n\n**Tone:** analytical\n\n**Length:** medium\n""",
        encoding="utf-8",
    )


def test_load_watchlist_and_prompt_template(tmp_path: Path) -> None:
    _write_minimal_config(tmp_path)

    watchlist = load_watchlist("jobs", root=tmp_path)
    assert len(watchlist) == 1
    assert watchlist[0].name == "AI Engineer"
    assert watchlist[0].query == "ai engineer"
    assert watchlist[0].location == "Remote"

    template = load_prompt_template("quick_take", root=tmp_path)
    assert template.name == "Quick Take (1 paragraph)"
    assert "Quick take." in template.prompt
    assert template.tags == ["#one", "#two"]
    assert template.tone == "direct"

    dossier_template = load_dossier_prompt_template(root=tmp_path)
    assert dossier_template.name == "Grounded Dossier Brief"
    assert "{dossier_type}" in dossier_template.prompt
    assert "## Grounded Inferences" in dossier_template.prompt


def test_ingest_dossier_file_creates_normalized_artifact(tmp_path: Path) -> None:
    _write_minimal_config(tmp_path)
    store = RepositoryStore(root=tmp_path)
    payload: dict[str, Any] = {
        "skill": "dossier-gather",
        "type": "jobs",
        "timestamp": "2026-05-15T18:15:00Z",
        "results": [
            {
                "title": "Healthcare AI Engineer",
                "keywords": "healthcare AI engineer",
                "location": "Remote",
                "total_results": 2,
                "job_postings": [
                    {"job_id": "1", "title": "AI Engineer", "company": "Acme", "location": "Remote"}
                ],
            }
        ],
    }
    input_file: Path = tmp_path / "raw.json"
    input_file.write_text(json.dumps(payload), encoding="utf-8")

    path, normalized = ingest_dossier_file(store, kind="jobs", path=input_file, source_name="raw")

    assert path.exists()
    saved = path.read_text(encoding="utf-8")
    assert path.suffix == ".md"
    assert "# Healthcare AI Engineer" in saved
    assert "## Normalized Data" in saved
    assert normalized["summary"]["query_count"] == 1
    catalog = json.loads((tmp_path / "data" / "index" / "catalog.json").read_text(encoding="utf-8"))
    assert catalog[0]["kind"] == "dossier:jobs"


def test_build_feed_insights_from_file(tmp_path: Path) -> None:
    _write_minimal_config(tmp_path)
    store = RepositoryStore(root=tmp_path)
    payload: dict[str, Any] = {
        "tool": "get_feed",
        "posts": [
            {"author": "A", "company": "Acme", "content": "We are hiring two ML engineers for our clinical AI team."},
            {"author": "B", "company": "Acme", "content": "Launched a new healthcare workflow product today."},
            {"author": "C", "company": "Beta", "content": "Open to partnerships and integrations."},
        ],
    }
    input_file: Path = tmp_path / "feed.json"
    input_file.write_text(json.dumps(payload), encoding="utf-8")

    path, normalized = build_feed_insights_from_file(store, path=input_file, title="Weekly Feed")

    assert path.exists()
    assert "feed_insights" in path.parts
    text = path.read_text(encoding="utf-8")
    assert "# Weekly Feed" in text
    assert "## What Changed" in text
    assert "## Actionable Signals" in text
    assert "## Hot Keywords" in text
    assert "## People to Watch" in text
    assert "## Companies to Watch" in text
    assert "Hiring signals found" in text
    assert "Product launch" in text
    assert "Partnership / integration signals" in text
    assert "prompt" in normalized
    assert normalized["total_posts"] == 3
    assert normalized["unique_authors"] == 3


def test_load_feed_prompt_template_uses_repo_default(tmp_path: Path) -> None:
    _write_minimal_config(tmp_path)
    template = load_feed_prompt_template(root=tmp_path)
    assert template.name == "Feed Intelligence Brief"
    assert "{feed_summary}" in template.prompt
    assert "{top_posts}" in template.prompt
    assert "{signals}" in template.prompt


def test_build_post_draft_uses_template_and_frontmatter(tmp_path: Path) -> None:
    _write_minimal_config(tmp_path)

    store = RepositoryStore(root=tmp_path)
    raw = """---\ntitle: \"Clinical AI\"\ntags: [\"#healthtech\", \"#AI\"]\ntemplate: \"quick_take\"\n---\n\nThis should become a draft.\n"""
    raw_path: Path = tmp_path / "idea.md"
    raw_path.write_text(raw, encoding="utf-8")

    path, result = build_post_draft(store, raw_path=raw_path, raw_text=raw)

    assert path.exists()
    content = path.read_text(encoding="utf-8")
    assert "status: draft" in content
    assert "This should become a draft." in result["prompt"]
    assert "Quick take." in result["prompt"]


def test_prepare_outreach_brief(tmp_path: Path) -> None:
    people_config: Path = tmp_path / "people.md"
    people_config.write_text(
        """# People\n\n```yaml\npeople:\n  - name: \"Alex Chen\"\n    username: \"alex-chen-healthtech\"\n    role: \"VP of AI\"\n```\n""",
        encoding="utf-8",
    )

    targets = load_targets(people_config)
    target = find_target(targets, "alex-chen-healthtech")
    store = RepositoryStore(root=tmp_path)
    path, payload = build_outreach_brief(store, target=target, message="Hello there")

    assert path.exists()
    assert payload["confirm_required"] is True
    assert payload["recipient"]["username"] == "alex-chen-healthtech"
    assert "Hello there" in path.read_text(encoding="utf-8")


def test_normalize_people_search_result_extracts_match() -> None:
    raw: dict[str, Any] = {
        "query": "Vijay Saayi R Microsoft",
        "results": {
            "search_results": (
                "Did you mean vijay sanayi r microsoft?\n\n"
                "Vijay Saayi R \n • 3rd+\n\n"
                "Senior Software Engineer for Azure App Services at Microsoft\n\n"
                "Chennai, Tamil Nadu, India\n\n"
                "Message\n\n"
                "Current: Senior Software Engineer at Microsoft\n\n"
                "Are these results helpful?"
            ),
            "references": {
                "search_results": [
                    {
                        "kind": "person",
                        "url": "/in/vijaysaayi/",
                        "text": "Vijay Saayi R",
                        "context": "search result",
                    }
                ]
            },
        },
    }

    normalized = normalize_dossier_payload("people", raw)
    assert normalized["summary"]["name"] == "Vijay Saayi R"
    assert normalized["summary"]["profile_url"] == "/in/vijaysaayi/"
    assert normalized["summary"]["match_found"] is True
    assert normalized["entities"][0]["profile_url"] == "/in/vijaysaayi/"


def test_people_search_ingest_writes_markdown_brief(tmp_path: Path) -> None:
    _write_minimal_config(tmp_path)
    store = RepositoryStore(root=tmp_path)
    payload: dict[str, Any] = {
        "query": "Ajaay Srinivaas R Curaj",
        "results": {
            "search_results": "r i • 3rd+\n\nStudent at curaj\n\nRajasthan, India\n\nMessage\n\nEducation: curaj",
            "references": {
                "search_results": [
                    {
                        "kind": "person",
                        "url": "/in/r-i-52b809117/",
                        "text": "r i",
                        "context": "search result",
                    }
                ]
            },
        },
    }
    input_file = tmp_path / "search.json"
    input_file.write_text(json.dumps(payload), encoding="utf-8")

    path, normalized = ingest_dossier_file(store, kind="people", path=input_file, source_name="search")

    assert path.suffix == ".md"
    text = path.read_text(encoding="utf-8")
    assert "## Best Match" in text
    assert "## Possible Matches" in text
    assert "get_person_profile" in text
    assert "\"search_results\"" not in text
    assert normalized["summary"]["match_found"] is True


def test_people_profile_ingest_uses_grounded_sections(tmp_path: Path) -> None:
    _write_minimal_config(tmp_path)
    store = RepositoryStore(root=tmp_path)
    payload: dict[str, Any] = {
        "url": "https://www.linkedin.com/in/jane-doe/",
        "sections": {
            "main_profile": (
                "Jane Doe\n\n"
                "· 500 connections\n\n"
                "Chief Product Officer at Acme\n\n"
                "Seattle, Washington, United States\n\n"
                "About\n"
            ),
            "experience": "Acme\nChief Product Officer\n",
            "education": "MBA\n",
            "certifications": "",
            "skills": "Product Strategy\n",
            "projects": "",
        },
    }
    input_file = tmp_path / "profile.json"
    input_file.write_text(json.dumps(payload), encoding="utf-8")

    path, normalized = ingest_dossier_file(store, kind="people", path=input_file, source_name="profile")

    assert path.suffix == ".md"
    text = path.read_text(encoding="utf-8")
    assert "## Verified Facts" in text
    assert "## Grounded Inferences" in text
    assert "healthcare" not in text.lower()
    assert normalized["summary"]["current_company"] == "Acme"
    assert "prompt" in normalized


def test_normalize_people_profile_becomes_intelligence() -> None:
    raw: dict[str, Any] = {
        "url": "https://www.linkedin.com/in/vijaysaayi/",
        "sections": {
            "main_profile": (
                "Vijay Saayi R\n\n"
                "· 3rd\n\n"
                "Senior Software Engineer for Azure App Services at Microsoft\n\n"
                "Chennai, Tamil Nadu, India\n\n"
                "498 connections\n\n"
                "509 followers"
            ),
            "experience": (
                "Experience\n\nMicrosoft\n\nFull-time · 7 yrs 10 mos\n\n"
                "Senior Software Engineer\n\nDec 2025 - Present · 6 mos\n\n"
                "Software Engineer II\n\nJun 2022 - Mar 2026 · 3 yrs 10 mos"
            ),
            "education": "Education\n\nShanmugha Arts, Science, Technology and Research Academy\n\nBachelor of Technology (B.Tech.), Electronics and Communications Engineering",
            "certifications": "Licenses & certifications\n\nMicrosoft Certified: Azure Fundamentals\n\nMicrosoft",
            "skills": "Skills\n\nPython\n\n1 endorsement\n\nC++\n\nLabVIEW\n\nEmbedded C",
            "projects": "Projects\n\nQuick Tools\n\nGroup Tabs and Share Browser-Extension\n\nUI for Dynamic IP Restrictions for Azure App Services",
        },
        "profile_urn": "ACoAABhWOc4BWz-g3D0R4SxVtRJzL3BjKEtvego",
    }

    normalized = normalize_dossier_payload("people", raw)
    assert normalized["summary"]["name"] == "Vijay Saayi R"
    assert normalized["summary"]["current_company"] == "Microsoft"
    assert "why_it_matters" in normalized["intelligence"]
    assert normalized["evidence"]["projects"]
