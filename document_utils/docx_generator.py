"""LegalEase - DOCX Document Generator.

Builds formatted Microsoft Word (.docx) documents with Times New Roman
typography, logo embedding, terms table, footers, and signature sections.
"""

import io
import os
import re
from typing import Optional
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

from document_utils.formatter import sanitize_text, parse_terms


def _set_cell_background(cell, color_hex: str):
    """Set the background color of a table cell."""
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)


def _set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Set padding for a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement("w:tcMar")
    for margin_name, val in [("top", top), ("bottom", bottom), ("left", left), ("right", right)]:
        node = OxmlElement(f"w:{margin_name}")
        node.set(qn("w:w"), str(val))
        node.set(qn("w:type"), "dxa")
        tcMar.append(node)
    tcPr.append(tcMar)


def format_docx(
    text: str,
    doc_type: str = "Legal Document",
    logo_path: Optional[str] = None,
    terms: Optional[str] = None,
) -> bytes:
    """Generate a formatted Microsoft Word document (.docx) as in-memory bytes.

    Args:
        text: The AI-generated or edited legal document text.
        doc_type: Title or type of legal agreement.
        logo_path: Optional path to logo image.
        terms: Semicolon-separated terms to include in a summary table.

    Returns:
        Bytes of the generated .docx file.
    """
    doc = Document()
    clean_text = sanitize_text(text)

    # Configure Margins: 1 inch on all sides (Standard Legal layout)
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        section.page_width = Inches(8.27)  # A4 width
        section.page_height = Inches(11.69)  # A4 height

        # Footer configuration
        footer = section.footer
        footer_p = footer.paragraphs[0]
        footer_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        footer_run = footer_p.add_run(
            "LegalEase | contact@legalease.com | Prepared for drafting & informational purposes"
        )
        footer_run.font.name = "Times New Roman"
        footer_run.font.size = Pt(8.5)
        footer_run.font.italic = True
        footer_run.font.color.rgb = RGBColor(128, 128, 128)

    # Normal Style configuration
    normal_style = doc.styles["Normal"]
    normal_style.font.name = "Times New Roman"
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = RGBColor(30, 41, 59)

    # Optional Logo (Center aligned on first page)
    if logo_path and os.path.exists(logo_path):
        try:
            logo_p = doc.add_paragraph()
            logo_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            logo_p.paragraph_format.space_after = Pt(12)
            logo_run = logo_p.add_run()
            logo_run.add_picture(logo_path, width=Inches(1.8))
        except Exception:
            pass  # Fall back gracefully if image format unsupported

    # Document Title
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_p.paragraph_format.space_before = Pt(6)
    title_p.paragraph_format.space_after = Pt(18)
    title_run = title_p.add_run(doc_type.upper())
    title_run.bold = True
    title_run.font.name = "Times New Roman"
    title_run.font.size = Pt(16)
    title_run.font.color.rgb = RGBColor(15, 23, 42)

    # Optional Terms Table
    if terms:
        parsed_terms_list = parse_terms(terms)
        if parsed_terms_list:
            table_intro = doc.add_paragraph()
            table_intro.paragraph_format.space_before = Pt(10)
            table_intro.paragraph_format.space_after = Pt(4)
            table_intro_run = table_intro.add_run("Schedule of Incorporated Key Terms")
            table_intro_run.bold = True
            table_intro_run.font.size = Pt(11.5)

            table = doc.add_table(rows=1, cols=2)
            table.alignment = WD_TABLE_ALIGNMENT.CENTER
            table.autofit = False

            # Column widths
            col_widths = [Inches(0.8), Inches(5.4)]
            hdr_cells = table.rows[0].cells
            hdr_cells[0].text = "No."
            hdr_cells[1].text = "Agreed Term / Specification"

            for i, cell in enumerate(hdr_cells):
                cell.width = col_widths[i]
                _set_cell_background(cell, "1E3A8A")  # Dark Blue
                _set_cell_margins(cell, top=120, bottom=120, left=140, right=140)
                p = cell.paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER if i == 0 else WD_ALIGN_PARAGRAPH.LEFT
                for run in p.runs:
                    run.font.name = "Times New Roman"
                    run.font.bold = True
                    run.font.size = Pt(10)
                    run.font.color.rgb = RGBColor(255, 255, 255)

            for idx, term_item in enumerate(parsed_terms_list, start=1):
                row_cells = table.add_row().cells
                row_cells[0].width = col_widths[0]
                row_cells[1].width = col_widths[1]

                row_cells[0].text = str(idx)
                row_cells[1].text = term_item

                bg_color = "F8FAFC" if idx % 2 == 0 else "FFFFFF"
                for i, cell in enumerate(row_cells):
                    _set_cell_background(cell, bg_color)
                    _set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
                    p = cell.paragraphs[0]
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER if i == 0 else WD_ALIGN_PARAGRAPH.LEFT
                    for run in p.runs:
                        run.font.name = "Times New Roman"
                        run.font.size = Pt(9.5)
                        run.font.color.rgb = RGBColor(30, 41, 59)

            spacer = doc.add_paragraph()
            spacer.paragraph_format.space_after = Pt(14)

    # Process Document Body Lines
    lines = clean_text.split("\n")
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue

        # Skip duplicate title line if it matches document_type
        if line.upper() == doc_type.upper() or line == f"# {doc_type}":
            continue

        # Section Heading
        is_heading = (
            line.startswith("## ")
            or line.startswith("# ")
            or re.match(r"^(SECTION\s+\d+|[0-9]{1,2}\.\s+[A-Z])", line)
        )
        if is_heading:
            clean_heading = line.lstrip("#").strip()
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(14)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.keep_with_next = True
            run = p.add_run(clean_heading)
            run.bold = True
            run.font.name = "Times New Roman"
            run.font.size = Pt(12)
            run.font.color.rgb = RGBColor(15, 23, 42)
            continue

        # Subsections or numbered clauses
        is_subclause = line.startswith("### ") or re.match(r"^(\d+\.\d+|[a-z]\))\s+", line)
        if is_subclause:
            clean_sub = line.lstrip("#").strip()
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.25)
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(3)
            run = p.add_run(clean_sub)
            run.font.name = "Times New Roman"
            run.font.size = Pt(10.5)
            continue

        # Standard legal paragraph
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing = 1.15
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

        # Format recitals italic
        if line.startswith("WHEREAS") or line.startswith("WITNESSETH") or line.startswith("NOW, THEREFORE"):
            run = p.add_run(line)
            run.italic = True
        else:
            run = p.add_run(line)

        run.font.name = "Times New Roman"
        run.font.size = Pt(11)

    # Save to memory buffer
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()
