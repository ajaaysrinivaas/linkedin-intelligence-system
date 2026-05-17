from __future__ import annotations

from typing import Any


def _compact_text(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return " ".join(value.split()).strip()


def _excerpt(text: str, max_length: int = 180) -> str:
    compact = " ".join(text.split())
    return compact if len(compact) <= max_length else compact[: max_length - 1].rstrip() + "…"


def _extract_items(node: Any) -> list[dict[str, Any]]:
    if isinstance(node, list):
        return [item for item in node if isinstance(item, dict)]  # type: ignore[misc]
    if not isinstance(node, dict):
        return []
    for key in ("posts", "feed", "items", "results", "updates"):
        nested: Any = node.get(key)  # type: ignore[assignment]
        items = _extract_items(nested)
        if items:
            return items
    return []


def _coerce_post(post: dict[str, Any]) -> dict[str, Any]:
    text = _compact_text(
        next(
            (value for value in (post.get(key) for key in ("content", "text", "body", "summary", "title", "headline")) if isinstance(value, str) and value.strip()),
            "",
        )
    )
    author = next((str(post.get(key)).strip() for key in ("author", "name", "username", "creator", "actor_name") if isinstance(post.get(key), str) and str(post.get(key)).strip()), "")
    company = next((str(post.get(key)).strip() for key in ("company", "author_company", "organization", "org", "employer") if isinstance(post.get(key), str) and str(post.get(key)).strip()), "")
    url = next((str(post.get(key)).strip() for key in ("url", "link", "permalink", "post_url") if isinstance(post.get(key), str) and str(post.get(key)).strip()), "")
    timestamp = next((str(post.get(key)).strip() for key in ("timestamp", "created_at", "published_at", "posted_at", "date") if isinstance(post.get(key), str) and str(post.get(key)).strip()), "")
    return {
        "author": author,
        "company": company,
        "text": text,
        "excerpt": _excerpt(text),
        "url": url,
        "timestamp": timestamp,
        "title": next((str(post.get(key)).strip() for key in ("title", "headline") if isinstance(post.get(key), str) and str(post.get(key)).strip()), ""),
    }


def normalize_feed_payload(raw: dict[str, Any]) -> dict[str, Any]:
    raw_items = _extract_items(raw)

    posts: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    author_counts: dict[str, int] = {}
    company_counts: dict[str, int] = {}

    for raw_post in raw_items:
        post = _coerce_post(raw_post)
        text_key = post["text"].lower()
        author_key = post["author"].lower()
        company_key = post["company"].lower()
        if not text_key and not author_key and not company_key:
            continue
        identity = (text_key, author_key, company_key)
        if identity in seen:
            continue
        seen.add(identity)
        posts.append(post)

        if post["author"]:
            author_counts[post["author"]] = author_counts.get(post["author"], 0) + 1
        if post["company"]:
            company_counts[post["company"]] = company_counts.get(post["company"], 0) + 1

    authors: list[dict[str, Any]] = sorted(
        [{"name": name, "count": count} for name, count in author_counts.items()],  # type: ignore[misc]
        key=lambda item: (-int(item["count"]), str(item["name"])),  # type: ignore[arg-type]
    )  # type: ignore[assignment]
    companies: list[dict[str, Any]] = sorted(
        [{"company": name, "count": count} for name, count in company_counts.items()],  # type: ignore[misc]
        key=lambda item: (-int(item["count"]), str(item["company"])),  # type: ignore[arg-type]
    )  # type: ignore[assignment]

    return {
        "total_posts": len(posts),
        "unique_authors": len(authors),  # type: ignore[arg-type]
        "unique_companies": len(companies),  # type: ignore[arg-type]
        "authors": authors,
        "companies": companies,
        "posts": posts,
    }
