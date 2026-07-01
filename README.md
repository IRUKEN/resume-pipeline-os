# Resume Pipeline OS

Resume Pipeline OS is a local-first job application decision engine. It reads a raw job description, extracts role requirements, compares them against a professional profile and preferences, and only creates a tailored resume artifact when the job passes the rules.

The core rule is strict: no CV is generated unless the Rust decision engine returns `APPLY`.

## What the MVP Includes

- Python pipeline for raw `.txt` ingestion, normalization, requirement extraction, report writing, and CV HTML rendering.
- Rust decision engine for typed scoring, hard requirement checks, preference matching, red flag detection, and final `APPLY` or `SKIP`.
- Sample profile, preferences, experience bank, and job description fixture.
- JSON and Markdown decision reports.
- Tests for Python text extraction and Rust decision logic.

## Repository Layout

```text
resume-pipeline-os/
  AGENTS.md
  README.md
  pipeline.py
  data/
    profile/
    jobs/
    output/
  python_pipeline/
  rust_engine/
  templates/
  tests/
```

## Requirements

- Python 3.10+
- Rust 1.70+ with Cargo

The MVP intentionally avoids Python package dependencies. Rust dependencies are managed by Cargo.

## Run the Pipeline

From the repository root:

```powershell
python pipeline.py --job data/jobs/raw/sample-fullstack-platform.txt
```

Expected output:

- `data/jobs/normalized/contoso-cloud-platforms-senior-full-stack-platform-engineer.json`
- `data/jobs/analyzed/contoso-cloud-platforms-senior-full-stack-platform-engineer.json`
- `data/output/reports/contoso-cloud-platforms-senior-full-stack-platform-engineer_decision.json`
- `data/output/reports/contoso-cloud-platforms-senior-full-stack-platform-engineer_summary.md`
- `data/output/cvs/Erni_Tabash_senior-full-stack-platform-engineer_contoso-cloud-platforms.html` only if the decision is `APPLY`

## Run the Rust Engine Directly

```powershell
cd rust_engine
cargo run --release -- --profile ../data/profile/erni_profile.json --preferences ../data/profile/preferences.json --job ../data/jobs/normalized/contoso-cloud-platforms-senior-full-stack-platform-engineer.json --output ../data/output/reports/manual_decision.json
```

## Run Tests

Python unit tests:

```powershell
python -m unittest discover -s tests/python -p "test_*.py"
```

Rust tests:

```powershell
cd rust_engine
cargo test
```

## Decision Rules

A job receives `APPLY` only when:

- Hard requirements pass.
- Profile score is at least `75`.
- Preference score is at least `70`.
- No red flags are detected.

Otherwise, the system writes reports only and does not generate a CV artifact.

## Privacy Notes

The checked-in profile is professional sample data. Do not add real phone numbers, exact addresses, private IDs, credentials, tokens, or generated CVs to the repository.
