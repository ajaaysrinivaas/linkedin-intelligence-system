from __future__ import annotations

import argparse
from pathlib import Path

from .storage import RepositoryStore
from .workflows.dossiers import ingest_dossier_file
from .workflows.feed_insights import build_feed_insights_from_file
from .workflows.outreach import build_outreach_brief, find_target, load_targets
from .workflows.posts import build_post_draft


def _add_common_root(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--root",
        type=Path,
        required=True,
        help="Workspace root",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="liis", description="LinkedIn Intelligence System")
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest = subparsers.add_parser("ingest", help="Ingest raw MCP output into data/")
    _add_common_root(ingest)
    ingest_sub = ingest.add_subparsers(dest="kind", required=True)

    for kind in ("companies", "jobs", "people"):
        kind_parser = ingest_sub.add_parser(kind, help=f"Ingest {kind} dossier output")
        kind_parser.add_argument("--input", type=Path, required=True, help="Raw MCP JSON file")
        kind_parser.add_argument("--source-name", type=str, required=True, help="Source label")

    feed_insights = subparsers.add_parser(
        "feed-insights",
        help="Build feed insights from feed JSON",
    )
    _add_common_root(feed_insights)
    feed_insights.add_argument("--input", type=Path, required=True, help="Raw feed JSON file")
    feed_insights.add_argument("--title", type=str, help="Insight report title")

    post = subparsers.add_parser("post", help="Build a post draft from raw idea markdown")
    _add_common_root(post)
    post.add_argument("--input", type=Path, required=True, help="Raw markdown idea file")
    post.add_argument("--body", type=str, help="Optional final post body")

    outreach = subparsers.add_parser("outreach", help="Prepare an outreach brief for a person")
    _add_common_root(outreach)
    outreach.add_argument("--people-config", type=Path, required=True, help="People config markdown file")
    outreach.add_argument("--target", type=str, required=True, help="Username or name to target")
    outreach.add_argument("--message", type=str, required=True, help="Message text to prepare")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    store = RepositoryStore(root=args.root)
    store.ensure_layout()

    if args.command == "ingest":
        path, _normalized = ingest_dossier_file(
            store,
            kind=args.kind,
            path=args.input,
            source_name=args.source_name,
        )
        print(path)
        return 0

    if args.command == "feed-insights":
        path, _normalized = build_feed_insights_from_file(store, path=args.input, title=args.title)
        print(path)
        return 0

    if args.command == "post":
        raw_text = args.input.read_text(encoding="utf-8")
        path, _result = build_post_draft(store, raw_path=args.input, raw_text=raw_text, body=args.body)
        print(path)
        return 0

    if args.command == "outreach":
        people_config = args.people_config if args.people_config.is_absolute() else args.root / args.people_config
        targets = load_targets(people_config)
        target = find_target(targets, args.target)
        path, _payload = build_outreach_brief(store, target=target, message=args.message)
        print(path)
        return 0

    parser.error("Unknown command")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
