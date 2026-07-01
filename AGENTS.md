# AGENTS.md

## Project Name

Resume Pipeline OS

## Mission

Build a local-first job resume pipeline that receives a raw job description in `.txt` format, analyzes whether the job matches Erni Tabash Sequeira's professional profile, experience, and preferences, and only generates a tailored ATS-friendly resume artifact when the job is worth applying to.

This is a decision engine for job applications, not just a resume generator.

The system should:

1. Read a raw job description.
2. Extract role requirements.
3. Compare the role against the profile.
4. Decide whether the job is worth applying to.
5. Generate a tailored CV only when the match is strong enough.
6. Produce a clear report explaining the decision.

## Core Product Rule

Never generate a CV automatically unless the job passes the decision rules.

Default decision logic:

```text
IF hard_requirements_pass == true
AND profile_score >= 75
AND preference_score >= 70
AND red_flags == 0
THEN generate tailored CV PDF
ELSE generate decision report only
```

For the MVP, the generated CV is an HTML file. The pipeline has a PDF-ready boundary and keeps generated resume artifacts out of git by default.

## Target User Profile

The system is built around a professional sample profile for Erni Tabash Sequeira:

- Full-stack engineer.
- Frontend: Angular, React, Next.js, HTML, CSS, SCSS, UI/UX execution.
- Backend: C#/.NET, Java Spring Boot, Node/NestJS, Prisma, GraphQL, SQL, PostgreSQL, SQL Server, APIs.
- Microsoft/Xbox vendor experience through Hanson Consulting Group.
- Experience with Game Hosting UX, Microsoft ecosystem, Azure DevOps, Kusto, React, .NET 8, and cloud platform workflows.
- Previous CINDE/Future Up experience with Angular, Spring Boot, Strapi, Keycloak, PostgreSQL, Docker, AWS, CI/CD, and Tableau integrations.
- Interested in full-stack, .NET, React, Angular, product engineer, platform engineer, technical lead, and technical product manager roles.
- Prefers remote roles.
- Avoids junior roles, unpaid roles, pure sales roles, onsite-only jobs outside Costa Rica, and jobs unrelated to software/product/platform work.

## Tech Direction

Use Python for local orchestration, text cleanup, requirement extraction, JSON generation, report generation, and CV context rendering.

Use Rust for typed data models, hard requirement checks, skill matching, preference scoring, red flag detection, and final decision output.

## Expected Commands

```powershell
python pipeline.py --job data/jobs/raw/sample-fullstack-platform.txt
cd rust_engine
cargo test
cargo run --release -- --profile ../data/profile/erni_profile.json --preferences ../data/profile/preferences.json --job ../data/jobs/normalized/sample-fullstack-platform.json --output ../data/output/reports/manual_decision.json
```

## Safety and Privacy Rules

- Do not add real phone numbers, exact addresses, IDs, banking data, secrets, or sensitive personal information.
- Do not commit generated CVs unless explicitly requested.
- Keep generated outputs under `data/output/`.
- Prefer local-first execution.
- Do not call external APIs for job analysis unless explicitly requested.

## Definition of Done

- The code runs locally.
- The main command is documented.
- The expected output is generated.
- Errors are handled clearly.
- Tests cover meaningful behavior.
- The implementation respects the core rule: no CV artifact unless the job passes.
- Code comments are in English.
