"""LegalEase - Plain Text (.TXT) Document Generator.

Provides clean plain text formatting with structured headers, metadata
separators, and standardized legal spacing.
"""

from typing import Optional
from document_utils.formatter import sanitize_text


def format_txt(
    text: str,
    doc_type: str = "LEGAL AGREEMENT",
    parties: Optional[str] = None,
    dates: Optional[str] = None,
) -> str:
    """Format the legal document into a clean, well-spaced plain text representation.

    Args:
        text: The generated or edited document content.
        doc_type: Title or category of the legal document.
        parties: Optional parties descriptor.
        dates: Optional effective date.

    Returns:
        Formatted plain text string.
    """
    clean_body = sanitize_text(text).strip()
    border = "=" * 76
    sub_border = "-" * 76

    header_lines = [
        border,
        f"{doc_type.upper():^76}",
        border,
    ]

    metadata_lines = []
    if dates:
        metadata_lines.append(f"Effective Date: {dates}")
    if parties:
        metadata_lines.append(f"Parties: {parties}")

    if metadata_lines:
        header_lines.extend(metadata_lines)
        header_lines.append(sub_border)

    header_lines.append("")  # Empty line before content

    footer_lines = [
        "",
        sub_border,
        "LegalEase - AI-Powered Legal Document Generator",
        "Notice: Generated for informational & drafting purposes.",
        border,
    ]

    full_txt = "\n".join(header_lines) + clean_body + "\n" + "\n".join(footer_lines)
    return full_txt
