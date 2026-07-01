from __future__ import annotations

from html import escape
from pathlib import Path
from textwrap import wrap


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


def render_cv_pdf(output_path: Path, context: dict) -> None:
    """Write a simple dependency-free PDF resume for the MVP."""
    lines = [
        context["name"],
        f"{context['headline']} | {context['location']}",
        "",
        "Target Role",
        f"{context['role']} at {context['company']}",
        "",
        "Matched Strengths",
    ]
    lines.extend(f"- {item}" for item in context["matched_strengths"])
    lines.extend(["", "Selected Experience"])
    lines.extend(f"- {item}" for item in context["experience"])

    content_lines: list[str] = []
    for line in lines:
        if not line:
            content_lines.append("")
            continue
        content_lines.extend(wrap(line, width=92) or [""])

    stream = _pdf_text_stream(content_lines)
    pdf = _build_pdf(stream)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(pdf)


def _pdf_text_stream(lines: list[str]) -> str:
    commands = ["BT", "/F1 11 Tf", "50 770 Td", "14 TL"]
    for index, line in enumerate(lines):
        if index:
            commands.append("T*")
        commands.append(f"({_escape_pdf_text(line)}) Tj")
    commands.append("ET")
    return "\n".join(commands)


def _escape_pdf_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _build_pdf(stream: str) -> bytes:
    objects = [
        "1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
        "2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
        "3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\nendobj\n",
        "4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n",
        f"5 0 obj\n<< /Length {len(stream.encode('latin-1', errors='replace'))} >>\nstream\n{stream}\nendstream\nendobj\n",
    ]
    output = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for obj in objects:
        offsets.append(len(output))
        output.extend(obj.encode("latin-1", errors="replace"))
    xref_offset = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    output.extend(
        (
            "trailer\n"
            f"<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            "startxref\n"
            f"{xref_offset}\n"
            "%%EOF\n"
        ).encode("ascii")
    )
    return bytes(output)
