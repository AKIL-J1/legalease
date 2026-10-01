"""LegalEase - Document Text Formatter & Sanitizer.

Provides utilities to sanitize text for cross-platform compatibility,
parse semicolon-separated terms, and format text for rich HTML preview.
"""

import html
import re
from typing import List


def sanitize_text(text: str) -> str:
    """Sanitize raw text by normalizing special unicode characters, quotes,

    and non-breaking spaces while keeping legitimate legal formatting.
    """
    if not text:
        return ""

    replacements = {
        "\u2018": "'",  # Left single quote
        "\u2019": "'",  # Right single quote
        "\u201c": '"',  # Left double quote
        "\u201d": '"',  # Right double quote
        "\u2014": " -- ",  # Em dash
        "\u2013": "-",  # En dash
        "\u2026": "...",  # Ellipsis
        "\u00a0": " ",  # Non-breaking space
        "\u2022": "*",  # Bullet
        "\ufeff": "",  # Byte order mark
        "\u200b": "",  # Zero width space
        "\t": "    ",  # Replace tabs with 4 spaces
    }

    sanitized = text
    for orig, repl in replacements.items():
        sanitized = sanitized.replace(orig, repl)

    # Normalize carriage returns
    sanitized = sanitized.replace("\r\n", "\n").replace("\r", "\n")

    return sanitized


def parse_terms(terms_string: str) -> List[str]:
    """Parse a semicolon-separated string of terms into a list of clean, non-empty terms.

    Example: "Salary: $50,000; Hours: 9-5; 15 days notice"
    -> ["Salary: $50,000", "Hours: 9-5", "15 days notice"]
    """
    if not terms_string:
        return []

    # Split on semicolon or newline
    items = re.split(r"[;\n]+", terms_string)
    parsed = []
    for item in items:
        cleaned = item.strip()
        # Remove leading bullet points or numbers if user entered them
        cleaned = re.sub(r"^[-*•\d+.)]\s*", "", cleaned).strip()
        if cleaned:
            parsed.append(cleaned)
    return parsed


def format_html_preview(text: str) -> str:
    """Convert raw legal text into semantic, styled HTML blocks for inline

    rendering in the Streamlit preview card.
    """
    if not text:
        return "<p class='italic text-gray-400'>No document content generated yet.</p>"

    lines = sanitize_text(text).split("\n")
    html_parts: List[str] = []

    in_signature_block = False

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            html_parts.append("<div style='height: 12px;'></div>")
            continue

        escaped = html.escape(line)

        # Detect Document Main Title (starts with # or ALL CAPS short title)
        if line.startswith("# ") or (line.isupper() and len(line) < 80 and not line.startswith("SECTION")):
            title_text = line.lstrip("#").strip()
            html_parts.append(
                f"<div style='text-align: center; margin-bottom: 24px; padding-bottom: 12px; "
                f"border-bottom: 2px solid #3b82f6;'>"
                f"<h1 style='font-size: 20px; font-weight: 800; letter-spacing: 0.05em; "
                f"color: #f8fafc; margin: 0;'>{html.escape(title_text)}</h1>"
                f"</div>"
            )
        # Detect Major Section Heading (## or SECTION X or 1. TITLE)
        elif line.startswith("## ") or re.match(r"^(SECTION\s+\d+|[0-9]{1,2}\.\s+[A-Z])", line):
            heading_text = line.lstrip("#").strip()
            html_parts.append(
                f"<div style='margin-top: 20px; margin-bottom: 8px;'>"
                f"<h2 style='font-size: 15px; font-weight: 700; color: #93c5fd; "
                f"letter-spacing: 0.02em; border-left: 3px solid #3b82f6; padding-left: 8px; "
                f"margin: 0;'>{html.escape(heading_text)}</h2>"
                f"</div>"
            )
        # Detect Subsection or Clause (### or 1.1 / (a))
        elif line.startswith("### ") or re.match(r"^(\d+\.\d+|[a-z]\))\s+", line):
            sub_text = line.lstrip("#").strip()
            html_parts.append(
                f"<div style='margin-top: 10px; margin-bottom: 6px; padding-left: 14px;'>"
                f"<span style='font-size: 14px; font-weight: 600; color: #cbd5e1;'>{html.escape(sub_text)}</span>"
                f"</div>"
            )
        # Detect Recitals / WHEREAS clauses
        elif line.startswith("WHEREAS") or line.startswith("WITNESSETH") or line.startswith("NOW, THEREFORE"):
            html_parts.append(
                f"<p style='margin: 8px 0; font-size: 13.5px; line-height: 1.6; color: #e2e8f0; "
                f"font-style: italic; background: rgba(59, 130, 246, 0.08); padding: 8px 12px; "
                f"border-radius: 4px; border-left: 2px solid #60a5fa;'>{escaped}</p>"
            )
        # Detect Signature lines or Attestation
        elif "IN WITNESS WHEREOF" in line.upper():
            in_signature_block = True
            html_parts.append(
                f"<div style='margin-top: 28px; margin-bottom: 16px; padding-top: 16px; "
                f"border-top: 1px dashed #475569;'>"
                f"<p style='font-size: 13.5px; font-weight: 600; color: #e2e8f0; text-align: center; "
                f"margin: 0;'>{escaped}</p>"
                f"</div>"
            )
        elif in_signature_block and ("By:" in line or "Name:" in line or "Title:" in line or "Date:" in line or "Signature:" in line):
            html_parts.append(
                f"<div style='font-family: monospace; font-size: 13px; color: #cbd5e1; "
                f"padding: 2px 0 2px 16px;'>{escaped}</div>"
            )
        # Standard Legal Body Paragraph
        else:
            html_parts.append(
                f"<p style='margin: 8px 0; font-size: 13.5px; line-height: 1.65; color: #e2e8f0; "
                f"text-align: justify;'>{escaped}</p>"
            )

    return "\n".join(html_parts)
