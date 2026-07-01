from __future__ import annotations

import re


KNOWN_SKILLS = [
    "angular",
    "react",
    "next.js",
    "typescript",
    "javascript",
    "html",
    "css",
    "scss",
    "ui/ux",
    "c#",
    ".net",
    ".net 8",
    "java",
    "spring boot",
    "node.js",
    "nestjs",
    "prisma",
    "graphql",
    "sql",
    "postgresql",
    "sql server",
    "api",
    "rest",
    "azure devops",
    "kusto",
    "docker",
    "aws",
    "ci/cd",
    "keycloak",
    "strapi",
    "tableau",
]

SENIORITY_TERMS = ["intern", "junior", "mid", "senior", "lead", "principal", "staff"]
WORK_MODES = ["remote", "hybrid", "onsite"]


def extract_job(text: str) -> dict:
    lower = text.lower()
    company = _field_or_default(text, "Company", "Unknown Company")
    role = _field_or_default(text, "Role", "Unknown Role")
    location = _field_or_default(text, "Location", "Unknown")

    required_skills = [skill for skill in KNOWN_SKILLS if skill in lower]
    seniority = [term for term in SENIORITY_TERMS if re.search(rf"\b{re.escape(term)}\b", lower)]
    work_mode = [mode for mode in WORK_MODES if re.search(rf"\b{mode}\b", lower)]
    years = _extract_years(lower)
    requirement_lines = _requirement_lines(text)

    return {
        "company": company,
        "role": role,
        "location": location,
        "raw_text": text,
        "required_skills": sorted(set(required_skills)),
        "seniority": sorted(set(seniority)),
        "work_mode": sorted(set(work_mode)),
        "years_experience": years,
        "requirements": requirement_lines,
    }


def _field_or_default(text: str, field: str, default: str) -> str:
    match = re.search(rf"^{field}:\s*(.+)$", text, flags=re.IGNORECASE | re.MULTILINE)
    return match.group(1).strip() if match else default


def _extract_years(text: str) -> int:
    matches = [int(value) for value in re.findall(r"(\d+)\+?\s+years?", text)]
    return max(matches) if matches else 0


def _requirement_lines(text: str) -> list[str]:
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("-"):
            lines.append(stripped.lstrip("- ").strip())
    return lines
