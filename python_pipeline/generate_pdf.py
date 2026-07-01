from __future__ import annotations

from html import escape
from pathlib import Path


def render_cv_html(template_path: Path, output_path: Path, context: dict) -> None:
    template = template_path.read_text(encoding="utf-8")
    rendered = template
    rendered = rendered.replace("{{ name }}", escape(context["name"]))
    rendered = rendered.replace("{{ headline }}", escape(context["headline"]))
    rendered = rendered.replace("{{ location }}", escape(context["location"]))
    rendered = rendered.replace("{{ company }}", escape(context["company"]))
    rendered = rendered.replace("{{ role }}", escape(context["role"]))
    rendered = rendered.replace("{{ matched_strengths }}", _li(context["matched_strengths"]))
    rendered = rendered.replace("{{ experience }}", _li(context["experience"]))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered, encoding="utf-8")


def _li(items: list[str]) -> str:
    return "\n".join(f"<li>{escape(item)}</li>" for item in items)
