from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from python_pipeline.build_cv_context import build_cv_context
from python_pipeline.extract_requirements import extract_job
from python_pipeline.generate_pdf import render_cv_html, render_cv_pdf
from python_pipeline.ingest import read_job_description
from python_pipeline.normalize import slugify
from python_pipeline.schemas import require_keys


ROOT = Path(__file__).resolve().parent


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Resume Pipeline OS against a raw job description.")
    parser.add_argument("--job", required=True, type=Path, help="Path to a raw .txt job description.")
    parser.add_argument("--skip-rust-build", action="store_true", help="Use an already built decision_engine binary.")
    args = parser.parse_args()

    profile_path = ROOT / "data/profile/erni_profile.json"
    preferences_path = ROOT / "data/profile/preferences.json"
    profile = _read_json(profile_path)
    preferences = _read_json(preferences_path)
    require_keys(profile, ["name", "headline", "location", "skills", "experience_highlights"], "profile")
    require_keys(preferences, ["preferred_roles", "preferred_work_modes", "preferred_seniority", "avoid"], "preferences")

    raw_text = read_job_description(_resolve(args.job))
    job = extract_job(raw_text)
    stem = slugify(f"{job['company']}-{job['role']}")

    normalized_path = ROOT / "data/jobs/normalized" / f"{stem}.json"
    analyzed_path = ROOT / "data/jobs/analyzed" / f"{stem}.json"
    decision_path = ROOT / "data/output/reports" / f"{stem}_decision.json"
    summary_path = ROOT / "data/output/reports" / f"{stem}_summary.md"
    cv_html_path = ROOT / "data/output/cvs" / f"Erni_Tabash_{slugify(job['role'])}_{slugify(job['company'])}.html"
    cv_pdf_path = ROOT / "data/output/cvs" / f"Erni_Tabash_{slugify(job['role'])}_{slugify(job['company'])}.pdf"

    _write_json(normalized_path, job)
    _write_json(analyzed_path, {"job": job, "profile_name": profile["name"]})

    _run_engine(profile_path, preferences_path, normalized_path, decision_path, args.skip_rust_build)
    decision = _read_json(decision_path)
    _write_summary(summary_path, job, decision)

    if decision["decision"] == "APPLY":
        context = build_cv_context(profile, job, decision)
        render_cv_html(ROOT / "templates/cv.html", cv_html_path, context)
        render_cv_pdf(cv_pdf_path, context)
        print(f"Decision: APPLY")
        print(f"Decision report: {decision_path}")
        print(f"Summary: {summary_path}")
        print(f"CV HTML: {cv_html_path}")
        print(f"CV PDF: {cv_pdf_path}")
    else:
        print(f"Decision: SKIP")
        print(f"Decision report: {decision_path}")
        print(f"Summary: {summary_path}")
        print("CV was not generated because the job did not pass the decision rules.")

    return 0


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _run_engine(profile: Path, preferences: Path, job: Path, output: Path, skip_build: bool) -> None:
    engine_dir = ROOT / "rust_engine"
    if not skip_build:
        subprocess.run(["cargo", "build", "--release"], cwd=engine_dir, check=True)
    exe = engine_dir / "target/release/decision_engine.exe"
    if not exe.exists():
        exe = engine_dir / "target/release/decision_engine"
    subprocess.run(
        [
            str(exe),
            "--profile",
            str(profile),
            "--preferences",
            str(preferences),
            "--job",
            str(job),
            "--output",
            str(output),
        ],
        cwd=engine_dir,
        check=True,
    )


def _write_summary(path: Path, job: dict, decision: dict) -> None:
    lines = [
        f"# {job['company']} - {job['role']} Decision",
        "",
        f"Decision: **{decision['decision']}**",
        f"Profile score: {decision['profile_score']}",
        f"Preference score: {decision['preference_score']}",
        f"Hard requirements pass: {decision['hard_requirements_pass']}",
        f"Red flags: {len(decision['red_flags'])}",
        "",
        "## Matched Skills",
        *(f"- {skill}" for skill in decision.get("matched_skills", [])),
        "",
        "## Missing Skills",
        *(f"- {skill}" for skill in decision.get("missing_skills", [])),
        "",
        "## Reasons",
        *(f"- {reason}" for reason in decision.get("reasons", [])),
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
