"""LegalEase - Streamlit Frontend Application.

Provides a responsive legal-tech UI for inputting contract parameters,
triggering Gemini generation via FastAPI, previewing formatted documents,
inline editing, and downloading as .TXT, .DOCX, and .PDF.
"""

import os
import sys
from datetime import date
from io import BytesIO
import tempfile
import requests
import streamlit as st

# Add parent directory to sys.path to resolve document_utils imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from document_utils.formatter import sanitize_text, format_html_preview
from document_utils.docx_generator import format_docx
from document_utils.pdf_generator import format_pdf
from document_utils.txt_generator import format_txt

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")
DEFAULT_LOGO_PATH = os.path.join(parent_dir, "assets", "logo.png")

# Page Setup
st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Custom Styling for SaaS Legal-Tech aesthetic
st.markdown(
    """
    <style>
    .main {
        background-color: #0b1120;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s;
    }
    .preview-card {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
        max-height: 600px;
        overflow-y: auto;
    }
    .disclaimer-box {
        background: rgba(30, 41, 59, 0.6);
        border-left: 4px solid #f59e0b;
        padding: 12px 16px;
        border-radius: 6px;
        font-size: 12.5px;
        color: #94a3b8;
        margin-top: 24px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize Session State
if "generated_text" not in st.session_state:
    st.session_state.generated_text = ""
if "active_doc_type" not in st.session_state:
    st.session_state.active_doc_type = "Employment Contract"
if "active_terms" not in st.session_state:
    st.session_state.active_terms = ""
if "active_parties" not in st.session_state:
    st.session_state.active_parties = ""
if "active_date" not in st.session_state:
    st.session_state.active_date = "October 1, 2026"
if "show_edit" not in st.session_state:
    st.session_state.show_edit = False
if "uploaded_logo_bytes" not in st.session_state:
    st.session_state.uploaded_logo_bytes = None

# Header Section
header_col1, header_col2, header_col3 = st.columns([1, 1.8, 1])
with header_col2:
    if os.path.exists(DEFAULT_LOGO_PATH):
        st.image(DEFAULT_LOGO_PATH, use_container_width=True)
    else:
        st.markdown(
            "<h1 style='text-align: center; color: #3b82f6; font-size: 42px; margin: 0;'>⚖️</h1>",
            unsafe_allow_html=True,
        )

st.markdown(
    "<h2 style='text-align: center; color: #f8fafc; font-weight: 800; margin-top: 4px; margin-bottom: 2px;'>"
    "LegalEase</h2>"
    "<p style='text-align: center; color: #60a5fa; font-weight: 600; font-size: 15px; margin-bottom: 4px;'>"
    "AI Legal Document Generator</p>"
    "<p style='text-align: center; color: #94a3b8; font-size: 13.5px; margin-bottom: 24px;'>"
    "Create structured, editable, and professional legal documents using AI.</p>",
    unsafe_allow_html=True,
)

# Test Presets Quick Selector
with st.expander("⚡ Quick Test Presets (Click to Auto-fill)", expanded=False):
    preset_col1, preset_col2, preset_col3 = st.columns(3)
    if preset_col1.button("📋 1. Employment Contract"):
        st.session_state.preset_type = "Employment Contract"
        st.session_state.preset_parties = "John Doe (Employee), ABC Technologies Pvt Ltd (Employer)"
        st.session_state.preset_terms = (
            "Salary: ₹50,000 per month; Working hours: 9 AM to 6 PM; "
            "Confidentiality required; 15 days termination notice"
        )
        st.session_state.preset_date = "October 1, 2026"
        st.rerun()

    if preset_col2.button("🔒 2. NDA Agreement"):
        st.session_state.preset_type = "NDA"
        st.session_state.preset_parties = "Jane Doe (Disclosing Party), TechNova Inc. (Receiving Party)"
        st.session_state.preset_terms = (
            "Confidential business information; No unauthorized disclosure; "
            "Confidentiality for 2 years; Return confidential materials upon termination"
        )
        st.session_state.preset_date = "October 1, 2026"
        st.rerun()

    if preset_col3.button("🏠 3. Lease Agreement"):
        st.session_state.preset_type = "Lease Agreement"
        st.session_state.preset_parties = "Alice Smith (Tenant), XYZ Realty (Landlord)"
        st.session_state.preset_terms = (
            "Monthly rent: ₹20,000; Security deposit: ₹60,000; "
            "Residential use only; Lease duration 12 months"
        )
        st.session_state.preset_date = "October 1, 2026"
        st.rerun()

# Document Type Input
doc_options = [
    "Employment Contract",
    "Employment Offer Letter",
    "NDA",
    "Lease Agreement",
    "Freelance Contract",
    "Service Agreement",
    "Business Agreement",
    "General Contract",
    "Other",
]

default_type_idx = 0
if "preset_type" in st.session_state and st.session_state.preset_type in doc_options:
    default_type_idx = doc_options.index(st.session_state.preset_type)

selected_type = st.selectbox("Document Type", doc_options, index=default_type_idx)

if selected_type == "Other":
    custom_type = st.text_input("Specify Custom Document Type", value="Commercial Partnership Agreement")
    document_type = custom_type.strip() or "Custom Legal Agreement"
else:
    document_type = selected_type

# Parties Involved Input
default_parties = st.session_state.get(
    "preset_parties",
    "John Doe (Employee), ABC Technologies Pvt Ltd (Employer)",
)
parties = st.text_area(
    "Parties Involved",
    value=default_parties,
    help="Enter the names and roles of the individuals or organizations involved.",
    placeholder="e.g., John Doe (Employee), ABC Technologies Pvt Ltd (Employer)",
    height=80,
)

# Terms & Conditions Input
default_terms = st.session_state.get(
    "preset_terms",
    "Salary: ₹50,000 per month; Working hours: 9 AM to 6 PM; Confidentiality required; 15 days termination notice",
)
terms = st.text_area(
    "Terms & Conditions (Use semicolons for bullet points)",
    value=default_terms,
    help="Specific clauses or rules that define the agreement. Separate each bullet point using a semicolon.",
    placeholder="e.g., Payment within 30 days; Confidentiality must be maintained; 15 days notice",
    height=100,
)

# Effective Date Input
col_date, col_logo = st.columns([1, 1])

with col_date:
    default_date_val = date(2026, 10, 1)
    picked_date = st.date_input("Effective Date", value=default_date_val)
    effective_date_str = picked_date.strftime("%B %d, %Y")

with col_logo:
    uploaded_logo = st.file_uploader(
        "Optional Company Logo (for DOCX & PDF)",
        type=["png", "jpg", "jpeg"],
        help="Upload custom logo to embed into headers of DOCX and PDF documents.",
    )
    if uploaded_logo is not None:
        st.session_state.uploaded_logo_bytes = uploaded_logo.read()

# Generate Button Action
generate_clicked = st.button("🚀 Generate Document", type="primary", use_container_width=True)

if generate_clicked:
    # Client-side validation
    if not document_type.strip():
        st.error("⚠️ Please specify a Document Type.")
    elif not parties.strip():
        st.error("⚠️ Please enter the Parties Involved.")
    elif not terms.strip():
        st.error("⚠️ Please enter at least one Term or Condition.")
    elif not effective_date_str.strip():
        st.error("⚠️ Please select an Effective Date.")
    else:
        with st.spinner("🤖 Communicating with Gemini AI... Drafting legal document..."):
            payload = {
                "document_type": document_type,
                "parties": parties,
                "terms": terms,
                "dates": effective_date_str,
            }
            try:
                response = requests.post(
                    f"{BACKEND_URL}/generate",
                    json=payload,
                    timeout=60,
                )
                if response.status_code == 200:
                    data = response.json()
                    doc_content = data.get("document", "")
                    st.session_state.generated_text = sanitize_text(doc_content)
                    st.session_state.active_doc_type = document_type
                    st.session_state.active_terms = terms
                    st.session_state.active_parties = parties
                    st.session_state.active_date = effective_date_str
                    st.session_state.show_edit = False
                    st.success("✅ Document Generated Successfully!")
                else:
                    err_msg = response.text
                    try:
                        err_json = response.json()
                        err_msg = err_json.get("detail", err_msg)
                    except Exception:
                        pass
                    st.error(f"❌ Backend Error ({response.status_code}): {err_msg}")
            except requests.exceptions.ConnectionError:
                st.error(
                    f"❌ Could not connect to FastAPI backend at {BACKEND_URL}. "
                    "Make sure your backend server is running via `uvicorn backend.main:app --reload`."
                )
            except Exception as ex:
                st.error(f"❌ Unexpected Error: {str(ex)}")

# Generated Document Section
if st.session_state.generated_text:
    st.markdown("---")
    st.markdown(f"### 📄 {st.session_state.active_doc_type}")

    # Edit Toggle Button
    edit_col1, edit_col2 = st.columns([1, 3])
    with edit_col1:
        if st.button("✏️ " + ("Close Editor" if st.session_state.show_edit else "Click to Edit Document")):
            st.session_state.show_edit = not st.session_state.show_edit
            st.rerun()

    # Inline Editor if enabled
    if st.session_state.show_edit:
        st.info("💡 You can freely modify sections, add clauses, correct parties, or adjust dates below:")
        edited = st.text_area(
            "Edit Document Below:",
            value=st.session_state.generated_text,
            height=380,
            key="document_editor",
        )
        if edited != st.session_state.generated_text:
            st.session_state.generated_text = edited
    else:
        # Styled HTML Preview inside dark-themed card
        html_markup = format_html_preview(st.session_state.generated_text)
        st.markdown(
            f"<div class='preview-card'>{html_markup}</div>",
            unsafe_allow_html=True,
        )

    st.markdown("#### 💾 Download Options")

    # Prepare temporary logo file if user uploaded or default exists
    temp_logo_path = None
    if st.session_state.uploaded_logo_bytes:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            tmp.write(st.session_state.uploaded_logo_bytes)
            temp_logo_path = tmp.name
    elif os.path.exists(DEFAULT_LOGO_PATH):
        temp_logo_path = DEFAULT_LOGO_PATH

    file_prefix = st.session_state.active_doc_type.lower().replace(" ", "_")

    # Download Columns
    d_col1, d_col2, d_col3 = st.columns(3)

    # 1. TXT Download
    with d_col1:
        txt_content = format_txt(
            text=st.session_state.generated_text,
            doc_type=st.session_state.active_doc_type,
            parties=st.session_state.active_parties,
            dates=st.session_state.active_date,
        )
        st.download_button(
            label="📄 Download as .TXT",
            data=txt_content.encode("utf-8"),
            file_name=f"{file_prefix}.txt",
            mime="text/plain",
            use_container_width=True,
        )

    # 2. DOCX Download
    with d_col2:
        try:
            docx_bytes = format_docx(
                text=st.session_state.generated_text,
                doc_type=st.session_state.active_doc_type,
                logo_path=temp_logo_path,
                terms=st.session_state.active_terms,
            )
            st.download_button(
                label="📘 Download as .DOCX",
                data=docx_bytes,
                file_name=f"{file_prefix}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"DOCX error: {e}")

    # 3. PDF Download
    with d_col3:
        try:
            pdf_bytes = format_pdf(
                text=st.session_state.generated_text,
                doc_type=st.session_state.active_doc_type,
                logo_path=temp_logo_path,
                terms=st.session_state.active_terms,
            )
            st.download_button(
                label="📕 Download as .PDF",
                data=pdf_bytes,
                file_name=f"{file_prefix}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"PDF error: {e}")

# Mandatory Legal Safety Disclaimer
st.markdown(
    """
    <div class='disclaimer-box'>
        <strong>⚠️ Legal Safety Notice:</strong> LegalEase generates documents for informational and drafting purposes.
        Generated documents may require review and modification by a qualified legal professional and should be
        checked against applicable local laws before use. LegalEase does not provide formal legal advice or substitute for legal counsel.
    </div>
    """,
    unsafe_allow_html=True,
)
