# LegalEase – AI-Powered Legal Document Generator

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-FF4B4B.svg?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-AI%20Core-4285F4.svg?logo=google&logoColor=white)](https://ai.google.dev)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://python.org)

LegalEase is a full-stack, AI-powered legal document generation platform that allows individuals, entrepreneurs, and organizations to draft structured, enforceable, and professional legal agreements in seconds.

By combining **FastAPI**, **Streamlit**, and **Google Gemini**, LegalEase transforms key business terms, party names, and effective dates into comprehensive contracts featuring standard legal recitals, numbered clauses, boilerplates, terms schedules, and execution blocks. Users can preview, dynamically edit, and export their documents into **Microsoft Word (.DOCX)**, **Print-Ready .PDF**, and **Plain Text (.TXT)** with embedded corporate branding.

---

## 1. Features

- **Dynamic Contract Drafting**: Generate Employment Contracts, NDAs, Lease Agreements, Freelance Contracts, Service Agreements, and custom contracts.
- **Strict Fact Preservation**: Preserves user-provided names, dates, numbers, and terms without fabricating unverified facts. Missing items are explicitly flagged as `[Information Required]`.
- **Automatic Terms Schedule**: Semicolon-separated terms are automatically formatted into a structured schedule table in Word and bulleted terms in PDF.
- **Branded Exports**:
  - **DOCX**: Formatted in standard legal Times New Roman, 1-inch margins, schedule table, and corporate footer.
  - **PDF**: Generated with running headers, page numbers (`Page X`), custom logo embedding, and legal footer.
  - **TXT**: Formatted with standard text borders and ASCII headers.
- **Live Inline Editor**: Modify clauses, fine-tune wording, or add custom provisions before downloading.
- **Interactive Document Preview**: Dark-themed legal card preview with semantic headings and highlighted recitals.
- **One-Click Presets**: Pre-configured test cases for Employment Contracts, NDAs, and Residential Leases.

---

## 2. Project Architecture

```
LegalEase/
│
├── backend/
│   ├── __init__.py
│   ├── main.py                  # FastAPI initialization, CORS, health endpoints
│   └── routes.py                # Pydantic validation & POST /generate endpoint
│
├── ai_core/
│   ├── __init__.py
│   └── gemini_generator.py      # Google Gemini integration, prompts, and SDK handling
│
├── document_utils/
│   ├── __init__.py
│   ├── formatter.py             # Unicode sanitization & HTML preview blocks
│   ├── docx_generator.py        # python-docx builder (A4, Times New Roman, terms table)
│   ├── pdf_generator.py         # FPDF builder (branded headers, footers, pagination)
│   └── txt_generator.py         # Plain text formatter with legal borders
│
├── frontend/
│   ├── __init__.py
│   └── app.py                   # Streamlit web interface with forms, editor & downloads
│
├── tests/
│   ├── __init__.py
│   └── test_api.py              # Unit tests for API, formatters, and exporters
│
├── assets/
│   └── logo.png                 # LegalEase corporate logo for DOCX/PDF branding
│
├── .env.example                 # Template for environment configuration
├── .gitignore                   # Excludes venv, .env, and generated artifacts
├── requirements.txt             # Pinned Python package dependencies
├── run.bat                      # One-click Windows startup script
├── run.sh                       # One-click Linux / macOS startup script
└── README.md                    # Complete documentation
```

---

## 3. Prerequisites

- **Python**: Version 3.10, 3.11, or 3.12 installed on your system.
- **pip**: Python package manager.
- **Google Gemini API Key**: Free or paid API key from [Google AI Studio](https://aistudio.google.com).
- **Git** (optional): For cloning the repository.

---

## 4. Windows VS Code Step-by-Step Setup

Follow these exact steps in your Windows terminal or VS Code integrated terminal (`Ctrl + ~`):

### Step 1: Open the Project in VS Code
Open the `LegalEase` folder in Visual Studio Code:
```cmd
code .
```

### Step 2: Create a Virtual Environment
```cmd
python -m venv venv
```

### Step 3: Activate the Virtual Environment
On Windows Command Prompt (CMD):
```cmd
venv\Scripts\activate.bat
```
Or in Windows PowerShell:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\venv\Scripts\Activate.ps1
```
*(Your prompt will now show `(venv)` at the beginning of the line).*

### Step 4: Install Dependencies
```cmd
pip install -r requirements.txt
```

### Step 5: Configure Environment Variables
Copy the example environment file:
```cmd
copy .env.example .env
```
Open `.env` in VS Code and add your Gemini API Key:
```env
GEMINI_API_KEY=AIzaSy...your_actual_api_key_here...
GEMINI_MODEL=gemini-2.5-flash
BACKEND_URL=http://127.0.0.1:8000
```

> **Note on Model Selection**: `gemini-2.5-flash` is configured by default for ultra-fast generation and wide availability across Google AI Studio tiers. You can also specify `gemini-3.8-flash` or `gemini-1.5-pro`.

---

## 5. Running the Application

### Option A: Automatic One-Click Startup (Windows)
Double-click `run.bat` or run:
```cmd
run.bat
```
This automatically activates `venv`, starts FastAPI on port 8000, and launches Streamlit on port 8501 in your browser.

---

### Option B: Manual Two-Terminal Startup

#### Terminal 1 — Start FastAPI Backend:
```cmd
venv\Scripts\activate
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```
- API Health Check: `http://127.0.0.1:8000/`
- Interactive Swagger Docs: `http://127.0.0.1:8000/docs`

#### Terminal 2 — Start Streamlit Frontend:
Open a second terminal window in VS Code (`Split Terminal` or `New Terminal`):
```cmd
venv\Scripts\activate
streamlit run frontend/app.py
```
Streamlit will automatically open your default browser at:
`http://localhost:8501`

---

## 6. How to Use LegalEase

1. **Select Document Type**: Choose from Employment Contract, Offer Letter, NDA, Lease Agreement, Freelance Contract, Service Agreement, or select **Other** for custom agreements.
2. **Enter Parties Involved**: Specify names and legal roles (e.g., `John Doe (Employee), ABC Technologies Pvt Ltd (Employer)`).
3. **Specify Terms & Conditions**: Provide key operational or financial terms separated by semicolons (e.g., `Salary: ₹50,000 per month; Working hours: 9 AM to 6 PM; Confidentiality required; 15 days termination notice`).
4. **Select Effective Date**: Choose the date when the agreement takes effect.
5. **Optional Logo**: Upload your corporate logo (`.png` or `.jpg`) to be embedded in the exported documents.
6. **Click "Generate Document"**: Gemini AI will draft the contract.
7. **Review & Edit**:
   - Preview the formatted document in the styled card.
   - Click **"Click to Edit Document"** to customize clauses, adjust names, or add supplementary provisions.
8. **Export**:
   - Click **Download as .TXT** for standard plain text.
   - Click **Download as .DOCX** for an editable Microsoft Word document with Times New Roman typography, tables, and footers.
   - Click **Download as .PDF** for a branded PDF ready for signing.

---

## 7. Test Cases & Verification

LegalEase includes built-in test presets in the UI and an automated test suite.

### Running Automated Tests
```cmd
python -m unittest tests/test_api.py -v
```

### Manual Test Case 1: Employment Contract
- **Document Type**: `Employment Contract`
- **Parties**: `John Doe (Employee), ABC Technologies Pvt Ltd (Employer)`
- **Terms**: `Salary: ₹50,000 per month; Working hours: 9 AM to 6 PM; Confidentiality required; 15 days termination notice`
- **Date**: `October 1, 2026`

### Manual Test Case 2: Non-Disclosure Agreement (NDA)
- **Document Type**: `NDA`
- **Parties**: `Jane Doe (Disclosing Party), TechNova Inc. (Receiving Party)`
- **Terms**: `Confidential business information; No unauthorized disclosure; Confidentiality for 2 years; Return confidential materials upon termination`
- **Date**: `October 1, 2026`

### Manual Test Case 3: Lease Agreement
- **Document Type**: `Lease Agreement`
- **Parties**: `Alice Smith (Tenant), XYZ Realty (Landlord)`
- **Terms**: `Monthly rent: ₹20,000; Security deposit: ₹60,000; Residential use only; Lease duration 12 months`
- **Date**: `October 1, 2026`

---

## 8. Troubleshooting

| Issue | Likely Cause | Solution |
| :--- | :--- | :--- |
| **"Could not connect to FastAPI backend"** | Backend server is not running on port 8000 | Verify Terminal 1 is running `uvicorn backend.main:app --reload` and visit `http://127.0.0.1:8000` |
| **"Gemini API Key is missing"** | `.env` file does not exist or `GEMINI_API_KEY` is empty | Copy `.env.example` to `.env` and set `GEMINI_API_KEY="AIzaSy..."` |
| **"Invalid API Key" or 403 Forbidden** | Expired or incorrect Google AI Studio key | Generate a fresh key at [aistudio.google.com](https://aistudio.google.com) |
| **"ModuleNotFoundError: No module named 'docx'"** | Virtual environment dependencies not installed | Run `pip install -r requirements.txt` inside your active virtual environment |
| **"pip is not recognized"** | Python not added to system PATH on Windows | Reinstall Python and check "Add Python to PATH" |

---

## 9. Security & Privacy Notes

- **Secret Isolation**: The Gemini API key is stored strictly on the backend via environment variables and is never exposed to the client or browser bundle.
- **Git Protection**: `.env`, virtual environment directories (`venv/`), and compiled caches are excluded in `.gitignore`.
- **Data Minimization**: Only the parameters supplied in the form are sent to the AI model. No persistent logging of sensitive contract data occurs unless configured.

---

## 10. Legal Safety Notice & Disclaimer

> **⚠️ DISCLAIMER**: LegalEase is an artificial intelligence drafting and legal information assistance tool. Generated documents are provided solely for informational and drafting convenience. Generated documents **do not constitute legal advice**, do not establish an attorney-client relationship, and may require review and customization by a licensed legal professional in your jurisdiction prior to signing or reliance. Always ensure your agreements comply with applicable local, state, and national laws.
