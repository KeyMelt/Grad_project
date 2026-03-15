from __future__ import annotations

import os
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Preformatted,
)


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="TitleCenter",
            parent=styles["Title"],
            alignment=TA_CENTER,
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            spaceAfter=10,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SectionHeading",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            spaceBefore=10,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SubHeading",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            spaceBefore=8,
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Body",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13,
            spaceAfter=5,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BulletBody",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13,
            leftIndent=14,
            firstLineIndent=0,
            spaceAfter=2,
        )
    )
    return styles


def escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def parse_markdown(md_text: str):
    lines = md_text.splitlines()
    i = 0
    blocks: list[tuple[str, str]] = []
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            i += 1
            continue
        if stripped.startswith("```"):
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            blocks.append(("code", "\n".join(code_lines).rstrip()))
            i += 1
            continue
        if stripped.startswith("### "):
            blocks.append(("h3", stripped[4:].strip()))
            i += 1
            continue
        if stripped.startswith("## "):
            blocks.append(("h2", stripped[3:].strip()))
            i += 1
            continue
        if stripped.startswith("# "):
            blocks.append(("h1", stripped[2:].strip()))
            i += 1
            continue
        if stripped.startswith("- "):
            blocks.append(("bullet", stripped[2:].strip()))
            i += 1
            continue

        paragraph_lines = [stripped]
        i += 1
        while i < len(lines):
            nxt = lines[i].strip()
            if not nxt:
                break
            if nxt.startswith(("```", "# ", "## ", "### ", "- ")):
                break
            paragraph_lines.append(nxt)
            i += 1
        blocks.append(("p", " ".join(paragraph_lines)))
    return blocks


def render(markdown_path: Path, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    styles = build_styles()
    story = []
    blocks = parse_markdown(markdown_path.read_text(encoding="utf-8"))

    title_used = False
    subtitle_used = False
    for kind, text in blocks:
        if kind == "h1" and not title_used:
            story.append(Paragraph(escape(text), styles["TitleCenter"]))
            title_used = True
            continue
        if kind == "h2" and title_used and not subtitle_used:
            story.append(Paragraph(escape(text), styles["SubHeading"]))
            story.append(Spacer(1, 4))
            subtitle_used = True
            continue
        if kind == "h1":
            story.append(Paragraph(escape(text), styles["SectionHeading"]))
        elif kind == "h2":
            story.append(Paragraph(escape(text), styles["SectionHeading"]))
        elif kind == "h3":
            story.append(Paragraph(escape(text), styles["SubHeading"]))
        elif kind == "p":
            story.append(Paragraph(escape(text), styles["Body"]))
        elif kind == "bullet":
            story.append(Paragraph(escape(text), styles["BulletBody"], bulletText="•"))
        elif kind == "code":
            story.append(
                Preformatted(
                    text,
                    ParagraphStyle(
                        "Code",
                        fontName="Courier",
                        fontSize=7.8,
                        leading=9.2,
                        leftIndent=8,
                        rightIndent=8,
                        borderWidth=0.5,
                        borderColor=colors.HexColor("#c9c9c9"),
                        borderPadding=6,
                        backColor=colors.HexColor("#f6f6f6"),
                        spaceBefore=4,
                        spaceAfter=6,
                    ),
                )
            )
        story.append(Spacer(1, 1.5))

    def draw_page(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#666666"))
        canvas.drawString(doc.leftMargin, 10 * mm, "Interactive Reinforcement Learning Platform")
        canvas.drawRightString(A4[0] - doc.rightMargin, 10 * mm, f"Page {doc.page}")
        canvas.restoreState()

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=16 * mm,
        title="Implementation and Testing Report",
        author="OpenAI Codex",
    )
    doc.build(story, onFirstPage=draw_page, onLaterPages=draw_page)


def main():
    if len(sys.argv) != 3:
        raise SystemExit("Usage: render_report_pdf.py <input.md> <output.pdf>")
    markdown_path = Path(sys.argv[1]).resolve()
    output_path = Path(sys.argv[2]).resolve()
    render(markdown_path, output_path)


if __name__ == "__main__":
    main()
