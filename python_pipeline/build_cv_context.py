from __future__ import annotations


def build_cv_context(profile: dict, job: dict, decision: dict) -> dict:
    matched = decision.get("matched_skills", [])
    return {
        "name": profile["name"],
        "headline": profile["headline"],
        "location": profile["location"],
        "company": job["company"],
        "role": job["role"],
        "matched_strengths": matched,
        "experience": profile.get("experience_highlights", []),
    }
