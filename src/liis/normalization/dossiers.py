from __future__ import annotations

from collections.abc import Iterable
import re
from typing import Any

Payload = dict[str, Any]


def _first_string(payload: Payload, keys: Iterable[str], default: str = "") -> str:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return default


def _first_list_length(payload: Payload, keys: Iterable[str]) -> int:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, list):
            return len(value)  # type: ignore[arg-type]
    return 0


def _summarize_job_search(entry: Payload) -> Payload:
    jobs = entry.get("job_postings")
    jobs_list: list[Payload] = [
        job for job in (jobs if isinstance(jobs, list) else [])  # type: ignore[misc]
        if isinstance(job, dict)
    ]  # type: ignore[misc]
    return {
        "title": entry.get("title", "Job search"),
        "summary": f"{entry.get('total_results', 0)} results for {entry.get('keywords', '')} in {entry.get('location', '')}".strip(),
        "metrics": {
            "total_results": entry.get("total_results", 0),
            "jobs_returned": len(jobs_list),
        },
        "entities": [
            {
                "id": str(job.get("job_id", "")),
                "title": job.get("title", ""),
                "company": job.get("company", ""),
                "location": job.get("location", ""),
                "salary": job.get("salary"),
                "posted": job.get("posted"),
            }
            for job in jobs_list
        ],
    }


def _first_reference(raw: Payload) -> Payload | None:
    results = raw.get("results")
    if not isinstance(results, dict):
        return None
    references: dict[str, Any] | None = results.get("references")  # type: ignore[assignment]
    if not isinstance(references, dict):
        return None
    search_refs: list[Any] | None = references.get("search_results")  # type: ignore[assignment]
    if not isinstance(search_refs, list):
        return None
    refs_gen: Any = (ref for ref in search_refs if isinstance(ref, dict))  # type: ignore[assignment]
    result: dict[str, Any] | None = next(refs_gen, None)  # type: ignore[assignment]
    return result


def _parse_people_search_excerpt(raw: Payload) -> str:
    results = raw.get("results")
    if not isinstance(results, dict):
        return ""
    text: Any | None = results.get("search_results")  # type: ignore[assignment]
    if not isinstance(text, str):
        return ""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return ""
    return " | ".join(lines[:4])


def _normalize_people_search(raw: Payload) -> Payload:
    reference = _first_reference(raw)
    results_value = raw.get("results")
    results: dict[str, Any] = results_value if isinstance(results_value, dict) else {}  # type: ignore[assignment]
    search_text: Any = results.get("search_results") if results else ""
    if not isinstance(search_text, str):
        search_text = ""

    result_name = ""
    profile_url = ""
    if isinstance(reference, dict):
        result_name = str(reference.get("text") or "").strip()
        profile_url = str(reference.get("url") or "").strip()

    if not result_name and search_text:
        first_line = next((line.strip() for line in search_text.splitlines() if line.strip()), "")
        if first_line:
            result_name = first_line.replace("• 3rd+", "").strip()

    excerpt = _parse_people_search_excerpt(raw)
    return {
        "kind": "people",
        "summary": {
            "query": _first_string(raw, ["query"], ""),
            "name": result_name or _first_string(raw, ["name", "full_name"], "Person"),
            "headline": excerpt,
            "profile_url": profile_url,
            "match_found": bool(result_name or profile_url or search_text),
        },
        "entities": [
            {
                "name": result_name,
                "profile_url": profile_url,
                "excerpt": excerpt,
            }
        ]
        if (result_name or profile_url or excerpt)
        else [],
        "payload": raw,
    }


def _clean_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def _is_noise_line(line: str) -> bool:
    lowered = line.lower()
    if lowered in {
        "show project",
        "show credential",
        "more",
        "about",
        "featured",
        "media",
        "activity",
        "experience",
        "education",
        "licenses & certifications",
        "skills",
        "projects",
        "contact info",
        "current",
        "all",
        "industry knowledge",
        "tools & technologies",
        "interpersonal skills",
    }:
        return True
    if re.match(r"^\d+\s*(endorsement|endorsements|connections|followers?)$", lowered):
        return True
    if re.match(r"^(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b", lowered):
        return True
    if "reposted this" in lowered:
        return True
    if lowered.startswith("https://"):
        return True
    return False


def _collect_signal_lines(text: str, max_items: int = 5) -> list[str]:
    candidates: list[str] = []
    for line in _clean_lines(text):
        if _is_noise_line(line):
            continue
        if len(line) < 3:
            continue
        if line not in candidates:
            candidates.append(line)
        if len(candidates) >= max_items:
            break
    return candidates


def _extract_section_titles(text: str, max_items: int = 6) -> list[str]:
    titles: list[str] = []
    lines = _clean_lines(text)
    for index, line in enumerate(lines):
        if _is_noise_line(line):
            continue
        if index + 1 < len(lines) and re.match(r"^(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b", lines[index + 1].lower()):
            if line not in titles:
                titles.append(line)
        elif line and line[0].isupper() and len(line) > 3 and line not in titles:
            titles.append(line)
        if len(titles) >= max_items:
            break
    return titles


def _parse_people_profile(raw: Payload) -> Payload:
    sections_value = raw.get("sections")
    sections: dict[str, Any] = sections_value if isinstance(sections_value, dict) else {}  # type: ignore[assignment]

    main_profile = str(sections.get("main_profile") or "")
    experience = str(sections.get("experience") or "")
    education = str(sections.get("education") or "")
    certifications = str(sections.get("certifications") or "")
    skills = str(sections.get("skills") or "")
    projects = str(sections.get("projects") or "")

    main_lines = _clean_lines(main_profile)
    name = main_lines[0] if main_lines else _first_string(raw, ["name", "full_name"], "Person")
    headline = next((line for line in main_lines if " at " in line and "•" not in line), "")
    degree = next((line for line in main_lines if re.search(r"•\s*\d+(st|nd|rd|th)\+?", line)), "")
    location = next((line for line in main_lines if "," in line and any(token in line for token in ["India", "USA", "United", "Remote"])), "")
    connection_match = re.search(r"(\d+)\s+connections", main_profile, re.IGNORECASE)
    followers_match = re.search(r"(\d+)\s+followers", main_profile, re.IGNORECASE)
    profile_url = str(raw.get("url") or "").strip()
    current_company = ""
    if " at " in headline:
        current_company = headline.split(" at ", 1)[1].strip()
    current_title = headline.split(" at ", 1)[0].strip() if " at " in headline else headline

    experience_signals = _extract_section_titles(experience, max_items=6)
    education_signals = _extract_section_titles(education, max_items=4)
    certification_signals = _extract_section_titles(certifications, max_items=4)
    skill_signals = _extract_section_titles(skills, max_items=8)
    project_signals = _extract_section_titles(projects, max_items=8)
    activity_signals = _collect_signal_lines(main_profile.split("Activity", 1)[-1] if "Activity" in main_profile else main_profile, max_items=4)

    outreach_angles: list[str] = []
    if current_company:
        outreach_angles.append(f"Leads a current role at {current_company}")
    if current_title and any(term in current_title.lower() for term in ["ceo", "founder", "chair", "vp", "vp of", "head of"]):
        outreach_angles.append("Senior leadership and strategy perspective")
    if any(skill in skill_signals for skill in ["Python", "C++", "Embedded C", "Java", "C#"]):
        outreach_angles.append("Technical builder with hands-on engineering background")
    if any("open-source" in item.lower() or "github" in item.lower() for item in project_signals):
        outreach_angles.append("Open-source or developer tooling contributor")
    if any("board" in item.lower() or "trustee" in item.lower() for item in experience_signals + education_signals):
        outreach_angles.append("Governance and cross-institution perspective")

    fit_signals_list: list[str] = [
        f"Seniority: {degree or 'not stated'}",
        f"Location: {location or 'not stated'}",
        f"Connections: {connection_match.group(1) if connection_match else 'not stated'}",
        f"Followers: {followers_match.group(1) if followers_match else 'not stated'}",
    ]
    intelligence: dict[str, Any] = {
        "one_liner": f"{current_title or name} at {current_company or 'unknown company'}",
        "why_it_matters": "Profile shows seniority, current company context, and evidence-backed experience signals that can guide outreach or follow-up.",
        "fit_signals": list(dict.fromkeys(fit_signals_list)),
        "outreach_angles": list(dict.fromkeys(outreach_angles))[:4],
    }

    evidence = {
        "experience": experience_signals,
        "education": education_signals,
        "certifications": certification_signals,
        "skills": skill_signals,
        "projects": project_signals,
        "activity": activity_signals,
    }

    return {
        "kind": "people",
        "summary": {
            "name": name,
            "headline": headline or _first_string(raw, ["headline", "title", "position"], ""),
            "location": location,
            "current_company": current_company,
            "current_title": current_title,
            "degree": degree,
            "connections": int(connection_match.group(1)) if connection_match else None,
            "followers": int(followers_match.group(1)) if followers_match else None,
            "profile_url": profile_url,
            "profile_urn": str(raw.get("profile_urn") or "").strip(),
        },
        "intelligence": intelligence,
        "evidence": evidence,
        "payload": {
            "source_sections": list(sections.keys()),
        },
    }


def normalize_dossier_payload(kind: str, raw: Payload) -> Payload:
    if kind == "jobs" and isinstance(raw.get("results"), list):
        results: list[Payload] = [entry for entry in raw["results"] if isinstance(entry, dict)]
        return {
            "kind": "jobs",
            "summary": {
                "query_count": len(results),
                "total_results": sum(int(entry.get("total_results", 0)) for entry in results),
            },
            "entries": [_summarize_job_search(entry) for entry in results],
        }

    if kind == "companies":
        return {
            "kind": "companies",
            "summary": {
                "name": _first_string(raw, ["name", "company_name", "title"], "Company"),
                "description": _first_string(raw, ["description", "headline", "about"], ""),
                "post_count": _first_list_length(raw, ["posts", "company_posts"]),
                "job_count": _first_list_length(raw, ["jobs", "open_jobs"]),
                "employee_count": _first_list_length(raw, ["employees", "company_employees"]),
            },
            "payload": raw,
        }

    if kind == "people":
        if isinstance(raw.get("results"), dict) and "search_results" in raw["results"]:
            return _normalize_people_search(raw)
        if isinstance(raw.get("sections"), dict):
            return _parse_people_profile(raw)
        return {
            "kind": "people",
            "summary": {
                "name": _first_string(raw, ["name", "full_name"], "Person"),
                "headline": _first_string(raw, ["headline", "title", "position"], ""),
                "company": _first_string(raw, ["company", "current_company"], ""),
                "skills_count": _first_list_length(raw, ["skills"]),
            },
            "payload": raw,
        }

    return {"kind": kind, "payload": raw}
