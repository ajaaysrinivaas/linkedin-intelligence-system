from __future__ import annotations

import re
from collections import Counter, defaultdict
from typing import Any

_STOPWORDS = {
    "the",
    "and",
    "with",
    "this",
    "that",
    "from",
    "your",
    "have",
    "will",
    "for",
    "you",
    "are",
    "our",
    "was",
    "about",
}

_HIRING_PHRASES = (
    "we're hiring",
    "we are hiring",
    "now hiring",
    "hiring",
    "open role",
    "open roles",
    "join our team",
    "looking for",
    "we are looking for",
    "seeking",
)

_THEMES: dict[str, tuple[str, ...]] = {
    "hiring": ("hiring", "open role", "open roles", "join our team", "looking for", "recruiting"),
    "launches": ("launch", "launched", "releases", "available", "shipping", "shipped"),
    "partnerships": ("partner", "partnership", "collaboration", "integrat"),
    "funding": ("funding", "raised", "seed", "series a", "series b", "investor"),
    "community": ("community", "event", "webinar", "conference", "talk", "session"),
    "open_source": ("github", "open source", "repo", "released", "code"),
    "customer_signal": ("customer", "client", "adopted", "deployed", "rolled out", "production"),
}


def post_text(post: dict[str, Any]) -> str:
    value = post.get("text")
    if isinstance(value, str) and value.strip():
        return value.strip()
    return " ".join(
        value.strip()
        for key in ("content", "body", "summary", "title", "headline")
        if isinstance((value := post.get(key)), str) and value.strip()
    )


def score_post(post: dict[str, Any]) -> int:
    text = post_text(post)
    if not text:
        return 0
    lower = text.lower()
    score = 1
    if any(phrase in lower for phrase in _HIRING_PHRASES):
        score += 4
    if any(word in lower for word in ("launch", "launched", "available", "shipping", "shipped")):
        score += 4
    if any(word in lower for word in ("partner", "partnership", "collaboration", "integrat")):
        score += 4
    if len(text) > 120:
        score += 1
    if post.get("author"):
        score += 1
    if post.get("company"):
        score += 1
    if post.get("url"):
        score += 1
    return score


def rank_posts(posts: list[dict[str, Any]], limit: int = 8) -> list[dict[str, Any]]:
    ranked = sorted(
        posts,
        key=lambda post: (
            -score_post(post),
            str(post.get("timestamp") or ""),
            str(post.get("author") or ""),
            str(post.get("company") or ""),
        ),
    )
    return ranked[:limit]


def collect_signals(posts: list[dict[str, Any]]) -> dict[str, Any]:
    theme_counter: Counter[str] = Counter()
    keyword_counter: Counter[str] = Counter()
    person_counter: Counter[str] = Counter()
    company_counter: Counter[str] = Counter()
    hiring_posts: list[dict[str, Any]] = []
    launch_posts: list[dict[str, Any]] = []
    partnership_posts: list[dict[str, Any]] = []
    follow_up_people: dict[str, list[str]] = defaultdict(list)
    follow_up_companies: dict[str, list[str]] = defaultdict(list)

    for post in posts:
        text = post_text(post)
        if not text:
            continue

        lower = text.lower()
        author = str(post.get("author") or post.get("name") or post.get("username") or "").strip()
        company = str(post.get("company") or post.get("author_company") or "").strip()

        if author:
            person_counter[author] += 1
        if company:
            company_counter[company] += 1

        for theme, phrases in _THEMES.items():
            if any(phrase in lower for phrase in phrases):
                theme_counter[theme] += 1

        keyword_counter.update(
            token for token in re.findall(r"[A-Za-z][A-Za-z0-9+#-]{2,}", text.lower()) if token not in _STOPWORDS
        )

        hiring = any(phrase in lower for phrase in _HIRING_PHRASES)
        launch = any(word in lower for word in ("launch", "launched", "available", "shipping", "shipped"))
        partnership = any(word in lower for word in ("partner", "partnership", "collaboration", "integrat"))

        if hiring:
            hiring_posts.append(post)
            if author:
                follow_up_people[author].append("Potential hiring contact")
            if company:
                follow_up_companies[company].append("Hiring signal")

        if launch:
            launch_posts.append(post)
        if partnership:
            partnership_posts.append(post)
        if author and ("dm" in lower or "reach out" in lower or "contact" in lower):
            follow_up_people[author].append("Open to outreach")

    return {
        "themes": [{"theme": theme, "count": count} for theme, count in theme_counter.most_common(8)],
        "top_keywords": [{"keyword": token, "count": count} for token, count in keyword_counter.most_common(12)],
        "top_people": [{"name": name, "count": count} for name, count in person_counter.most_common(8)],
        "top_companies": [{"company": name, "count": count} for name, count in company_counter.most_common(8)],
        "hiring_posts": hiring_posts[:8],
        "launch_posts": launch_posts[:8],
        "partnership_posts": partnership_posts[:8],
        "follow_up_people": [{"name": name, "signals": signals} for name, signals in list(follow_up_people.items())[:8]],
        "follow_up_companies": [{"company": name, "signals": signals} for name, signals in list(follow_up_companies.items())[:8]],
    }
