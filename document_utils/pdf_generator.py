"""LegalEase - PDF Document Generator.

Generates clean, branded PDF legal documents with logos, headers,
footers, and page numbers using FPDF.
"""

import io
import os
import re
from typing import Optional
from fpdf import FPDF

from document_utils.formatter import sanitize_text, parse_terms


class LegalDocumentPDF(FPDF):
    """Custom FPDF class that adds automated running headers and footers."""

    def __init__(self, doc_type: str = "Legal Agreement", logo_path: Optional[str] = None):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.doc_type = doc_type
        self.logo_path = logo_path
        self.set_auto_page_break(auto=True, margin=20)
        self.set_margins(left=20, top=20, right=20)

    def header(self):
        """Page Header with optional Logo."""
        if self.page_no() == 1 and self.logo_path and os.path.exists(self.logo_path):
            try:
                # Center logo on first page
                page_width = self.w - 40
                logo_width = 32
                x_pos = (self.w - logo_width) / 2
                self.image(self.logo_path, x=x_pos, y=10, w=logo_width)
                self.set_y(32)
                return
            except Exception:
                pass

        if self.page_no() > 1:
            self.set_font("Times", "I", 8)
            self.set_text_color(128, 128, 128)
            # Running header on subsequent pages
            safe_title = self.doc_type.encode("latin-1", "replace").decode("latin-1")
            self.cell(0, 8, safe_title.upper(), border="B", align="R")
            self.ln(10)

    def footer(self):
        """Page Footer with Branding and Page Numbering."""
        self.set_y(-15)
        self.set_font("Times", "I", 8.5)
        self.set_text_color(128, 128, 128)
        footer_text = f"LegalEase Inc. | contact@legalease.com | Page {self.page_no()}"
        self.cell(0, 10, footer_text, align="C")


def _latin_safe(text: str) -> str:
    """Ensure text is encodable in standard FPDF Latin-1 font,

    replacing unsupported characters safely.
    """
    clean = sanitize_text(text)
    # Currency symbol normalization for Latin-1
    clean = clean.replace("₹", "INR ").replace("€", "EUR ").replace("£", "GBP ")
    return clean.encode("latin-1", "replace").decode("latin-1")


def format_pdf(
    text: str,
    doc_type: str = "Legal Document",
    logo_path: Optional[str] = None,
    terms: Optional[str] = None,
) -> bytes:
    """Create a formatted PDF document as in-memory bytes.

    Args:
        text: Legal agreement body text.
        doc_type: Agreement type/title.
        logo_path: Path to logo image if available.
        terms: Optional semicolon-separated terms string.

    Returns:
        bytes representing the generated PDF file.
    """
    pdf = LegalDocumentPDF(doc_type=doc_type, logo_path=logo_path)
    pdf.add_page()

    # Document Main Title
    pdf.set_font("Times", "B", 15)
    pdf.set_text_color(15, 23, 42)
    safe_title = _latin_safe(doc_type.upper())
    pdf.cell(0, 10, safe_title, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    # Subtitle decorative line
    pdf.set_draw_color(59, 130, 246)
    pdf.set_line_width(0.4)
    line_y = pdf.get_y()
    pdf.line(pdf.l_margin + 30, line_y, pdf.w - pdf.r_margin - 30, line_y)
    pdf.ln(6)

    # Key Terms Summary Box if terms supplied
    if terms:
        terms_list = parse_terms(terms)
        if terms_list:
            pdf.set_font("Times", "B", 10.5)
            pdf.set_text_color(30, 58, 138)
            pdf.cell(0, 7, _latin_safe("KEY STIPULATED TERMS"), new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Times", "", 9.5)
            pdf.set_text_color(40, 50, 70)

            for idx, item in enumerate(terms_list, start=1):
                clean_item = _latin_safe(f"{idx}. {item}")
                pdf.multi_cell(0, 5.5, clean_item)
                pdf.ln(1)
            pdf.ln(4)

    # Document Body Lines
    lines = text.split("\n")
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            pdf.ln(2.5)
            continue

        # Skip duplicate main title
        if line.upper() == doc_type.upper() or line == f"# {doc_type}":
            continue

        safe_line = _latin_safe(line)

        # Detect Section Heading
        is_heading = (
            line.startswith("## ")
            or line.startswith("# ")
            or re.match(r"^(SECTION\s+\d+|[0-9]{1,2}\.\s+[A-Z])", line)
        )
        if is_heading:
            clean_head = _latin_safe(line.lstrip("#").strip())
            pdf.ln(4)
            pdf.set_font("Times", "B", 11.5)
            pdf.set_text_color(15, 23, 42)
            pdf.multi_cell(0, 6, clean_head)
            pdf.ln(1)
            continue

        # Detect Subclause
        is_sub = line.startswith("### ") or re.match(r"^(\d+\.\d+|[a-z]\))\s+", line)
        if is_sub:
            clean_sub = _latin_safe(line.lstrip("#").strip())
            pdf.set_font("Times", "B", 10)
            pdf.set_text_color(30, 41, 59)
            pdf.set_x(pdf.l_margin + 5)
            pdf.multi_cell(pdf.w - pdf.l_margin - pdf.r_margin - 5, 5.5, clean_sub)
            continue

        # Detect Recital (WHEREAS, WITNESSETH)
        if line.startswith("WHEREAS") or line.startswith("WITNESSETH") or line.startswith("NOW, THEREFORE"):
            pdf.set_font("Times", "I", 10)
            pdf.set_text_color(30, 41, 59)
            pdf.multi_cell(0, 5.5, safe_line)
            pdf.ln(2)
            continue

        # Signature or Attestation Lines
        if "IN WITNESS WHEREOF" in line.upper():
            pdf.ln(6)
            pdf.set_font("Times", "B", 10)
            pdf.set_text_color(15, 23, 42)
            pdf.cell(0, 7, safe_line, align="C", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(3)
            continue

        # Standard Legal Body Text
        pdf.set_font("Times", "", 10)
        pdf.set_text_color(30, 41, 59)
        pdf.multi_cell(0, 5.2, safe_line)

    # Return bytes buffer
    buffer = io.BytesIO()
    # Output to bytearray / bytes
    pdf_bytes = pdf.output()
    if isinstance(pdf_bytes, str):
        return pdf_bytes.encode("latin-1")
    return bytes(pdf_bytes)
