/**
 * LegalEase – AI-Powered Legal Document Generator
 * Interactive Web Application Frontend
 */

import React, { useState, useRef } from 'react';
import {
  Scale,
  FileText,
  FileCheck2,
  Download,
  Edit3,
  Eye,
  Sparkles,
  Upload,
  AlertTriangle,
  Copy,
  Check,
  RefreshCw,
  Table as TableIcon,
  Code2,
  FolderGit2,
  Layers,
  ChevronRight,
  ShieldAlert,
} from 'lucide-react';
import { jsPDF } from 'jspdf';
import {
  Document as DocxDocument,
  Packer,
  Paragraph,
  TextRun,
  HeadingLevel,
  AlignmentType,
  Table,
  TableRow,
  TableCell,
  WidthType,
  ShadingType,
  BorderStyle,
  Footer,
} from 'docx';
import confetti from 'canvas-confetti';

interface Preset {
  id: string;
  name: string;
  docType: string;
  parties: string;
  terms: string;
  date: string;
}

const PRESETS: Preset[] = [
  {
    id: 'emp',
    name: 'Employment Contract',
    docType: 'Employment Contract',
    parties: 'John Doe (Employee), ABC Technologies Pvt Ltd (Employer)',
    terms: 'Salary: ₹50,000 per month; Working hours: 9 AM to 6 PM; Confidentiality required; 15 days termination notice',
    date: 'October 1, 2026',
  },
  {
    id: 'nda',
    name: 'Non-Disclosure Agreement',
    docType: 'NDA',
    parties: 'Jane Doe (Disclosing Party), TechNova Inc. (Receiving Party)',
    terms: 'Confidential business information; No unauthorized disclosure; Confidentiality for 2 years; Return confidential materials upon termination',
    date: 'October 1, 2026',
  },
  {
    id: 'lease',
    name: 'Lease Agreement',
    docType: 'Lease Agreement',
    parties: 'Alice Smith (Tenant), XYZ Realty (Landlord)',
    terms: 'Monthly rent: ₹20,000; Security deposit: ₹60,000; Residential use only; Lease duration 12 months',
    date: 'October 1, 2026',
  },
];

const CODE_FILES: Record<string, { path: string; language: string; content: string }> = {
  'backend/main.py': {
    path: 'backend/main.py',
    language: 'python',
    content: `# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from backend.routes import router

app = FastAPI(
    title="LegalEase – AI Legal Document Generator",
    description="High-performance backend API for generating structured legal documents using Google Gemini.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
def home():
    return {
        "status": "success",
        "message": "LegalEase API is running"
    }

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
`,
  },
  'backend/routes.py': {
    path: 'backend/routes.py',
    language: 'python',
    content: `# backend/routes.py
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from ai_core.gemini_generator import GeminiDocumentGenerator

router = APIRouter()
gemini_generator = GeminiDocumentGenerator()

class DocumentRequest(BaseModel):
    document_type: str = Field(..., min_length=2, max_length=150)
    parties: str = Field(..., min_length=3, max_length=1000)
    terms: str = Field(..., min_length=3, max_length=4000)
    dates: str = Field(..., min_length=2, max_length=100)

    @field_validator("document_type", "parties", "terms", "dates")
    @classmethod
    def check_not_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Field cannot be empty or purely whitespace.")
        return stripped

@router.post("/generate")
def generate_legal_document(request: DocumentRequest):
    try:
        generated_text = gemini_generator.generate_document(
            document_type=request.document_type,
            parties=request.parties,
            terms=request.terms,
            dates=request.dates,
        )
        return {
            "success": True,
            "document": generated_text,
            "message": "Document generated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
`,
  },
  'ai_core/gemini_generator.py': {
    path: 'ai_core/gemini_generator.py',
    language: 'python',
    content: `# ai_core/gemini_generator.py
import os
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class GeminiDocumentGenerator:
    def __init__(self, api_key=None, model_name=None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "").strip()
        self.model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
        self._initialize_sdk()

    def _initialize_sdk(self):
        try:
            from google import genai
            self._client = genai.Client(api_key=self.api_key)
            self._sdk_type = "google-genai"
            return
        except Exception:
            pass

        try:
            import google.generativeai as legacy_genai
            legacy_genai.configure(api_key=self.api_key)
            self._client = legacy_genai.GenerativeModel(self.model_name)
            self._sdk_type = "google-generativeai"
            return
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Gemini SDK: {e}")

    def generate_document(self, document_type, parties, terms, dates):
        prompt = f"""You are a senior corporate counsel and expert contract draftsman.
Draft a comprehensive, highly formal legal document based strictly on the specifications:
- Document Type: {document_type}
- Involved Parties: {parties}
- Effective Date: {dates}
- Key Terms & Conditions: {terms}

Follow formal legal conventions with title, recitals (WHEREAS), numbered clauses, boilerplates, and execution signatures."""

        if self._sdk_type == "google-genai":
            response = self._client.models.generateContent(model=self.model_name, contents=prompt)
            return response.text
        else:
            response = self._client.generate_content(prompt)
            return response.text
`,
  },
  'frontend/app.py': {
    path: 'frontend/app.py',
    language: 'python',
    content: `# frontend/app.py
import os
import requests
import streamlit as st
from document_utils.formatter import sanitize_text, format_html_preview
from document_utils.docx_generator import format_docx
from document_utils.pdf_generator import format_pdf
from document_utils.txt_generator import format_txt

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="LegalEase", page_icon="⚖️", layout="centered")

st.markdown("<h2 style='text-align: center;'>LegalEase</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #60a5fa;'>AI Legal Document Generator</p>", unsafe_allow_html=True)

document_type = st.selectbox("Document Type", ["Employment Contract", "NDA", "Lease Agreement", "Freelance Contract", "Other"])
parties = st.text_area("Parties Involved")
terms = st.text_area("Terms & Conditions (Use semicolons for bullet points)")
date_val = st.text_input("Effective Date", value="October 1, 2026")

if st.button("Generate Document", type="primary"):
    res = requests.post(f"{BACKEND_URL}/generate", json={
        "document_type": document_type,
        "parties": parties,
        "terms": terms,
        "dates": date_val
    })
    st.session_state.generated_text = res.json()["document"]

if "generated_text" in st.session_state:
    st.markdown(format_html_preview(st.session_state.generated_text), unsafe_allow_html=True)
    st.download_button("Download as .TXT", data=format_txt(st.session_state.generated_text))
    st.download_button("Download as .DOCX", data=format_docx(st.session_state.generated_text, document_type))
    st.download_button("Download as .PDF", data=format_pdf(st.session_state.generated_text, document_type))
`,
  },
  'requirements.txt': {
    path: 'requirements.txt',
    language: 'text',
    content: `fastapi>=0.110.0
uvicorn>=0.28.0
pydantic>=2.6.0
streamlit>=1.32.0
python-docx>=1.1.0
fpdf2>=2.7.8
Pillow>=10.2.0
requests>=2.31.0
google-genai>=0.1.1
google-generativeai>=0.4.0
python-dotenv>=1.0.1
httpx>=0.27.0
`,
  },
};

export default function App() {
  const [docType, setDocType] = useState('Employment Contract');
  const [customDocType, setCustomDocType] = useState('');
  const [parties, setParties] = useState(
    'John Doe (Employee), ABC Technologies Pvt Ltd (Employer)'
  );
  const [terms, setTerms] = useState(
    'Salary: ₹50,000 per month; Working hours: 9 AM to 6 PM; Confidentiality required; 15 days termination notice'
  );
  const [effectiveDate, setEffectiveDate] = useState('October 1, 2026');
  const [logoPreview, setLogoPreview] = useState<string | null>('/public/logo.png');

  // Generation and editing state
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedDoc, setGeneratedDoc] = useState('');
  const [activeTab, setActiveTab] = useState<'preview' | 'edit' | 'terms' | 'code'>('preview');
  const [selectedCodeFile, setSelectedCodeFile] = useState('backend/routes.py');
  const [copiedKey, setCopiedKey] = useState<string | null>(null);
  const [errorBanner, setErrorBanner] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const currentType = docType === 'Other' ? (customDocType || 'Custom Agreement') : docType;

  // Apply a preset
  const applyPreset = (preset: Preset) => {
    setDocType(preset.docType);
    setParties(preset.parties);
    setTerms(preset.terms);
    setEffectiveDate(preset.date);
    setErrorBanner(null);
  };

  // Handle Logo Upload
  const handleLogoUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        setLogoPreview(event.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  // Generate Document Action
  const handleGenerate = async () => {
    if (!parties.trim()) {
      setErrorBanner('Please specify the Parties Involved.');
      return;
    }
    if (!terms.trim()) {
      setErrorBanner('Please specify Terms & Conditions (separated by semicolons).');
      return;
    }

    setErrorBanner(null);
    setIsGenerating(true);

    try {
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          document_type: currentType,
          parties: parties.trim(),
          terms: terms.trim(),
          dates: effectiveDate.trim(),
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to generate document');
      }

      setGeneratedDoc(data.document || '');
      setActiveTab('preview');
      confetti({
        particleCount: 50,
        spread: 60,
        origin: { y: 0.6 },
      });
    } catch (err: any) {
      console.error(err);
      setErrorBanner(err.message || 'Error communicating with AI service');
    } finally {
      setIsGenerating(false);
    }
  };

  // Parse terms for schedule table
  const parsedTermsList = terms
    .split(';')
    .map((t) => t.trim())
    .filter((t) => t.length > 0);

  // Download TXT
  const downloadTxt = () => {
    if (!generatedDoc) return;
    const border = '='.repeat(72);
    const content = `${border}\n${currentType.toUpperCase().padStart(36 + currentType.length / 2)}\n${border}\nEffective Date: ${effectiveDate}\nParties: ${parties}\n${'-'.repeat(72)}\n\n${generatedDoc}\n\n${'-'.repeat(72)}\nLegalEase - AI-Powered Legal Document Generator\nGenerated for informational & drafting purposes.\n${border}`;
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${currentType.toLowerCase().replace(/\s+/g, '_')}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Download DOCX
  const downloadDocx = async () => {
    if (!generatedDoc) return;

    try {
      const docChildren: any[] = [];

      // Main Title
      docChildren.push(
        new Paragraph({
          text: currentType.toUpperCase(),
          heading: HeadingLevel.TITLE,
          alignment: AlignmentType.CENTER,
          spacing: { before: 200, after: 300 },
          run: {
            font: 'Times New Roman',
            bold: true,
            size: 32,
            color: '0F172A',
          },
        })
      );

      // Terms Table if present
      if (parsedTermsList.length > 0) {
        docChildren.push(
          new Paragraph({
            text: 'Schedule of Incorporated Key Terms',
            heading: HeadingLevel.HEADING_2,
            spacing: { before: 200, after: 100 },
            run: {
              font: 'Times New Roman',
              bold: true,
              size: 24,
              color: '1E3A8A',
            },
          })
        );

        const tableRows = [
          new TableRow({
            children: [
              new TableCell({
                width: { size: 1000, type: WidthType.DXA },
                shading: { type: ShadingType.CLEAR, fill: '1E3A8A' },
                children: [
                  new Paragraph({
                    text: 'No.',
                    alignment: AlignmentType.CENTER,
                    run: { font: 'Times New Roman', bold: true, color: 'FFFFFF' },
                  }),
                ],
              }),
              new TableCell({
                width: { size: 8000, type: WidthType.DXA },
                shading: { type: ShadingType.CLEAR, fill: '1E3A8A' },
                children: [
                  new Paragraph({
                    text: 'Agreed Term / Specification',
                    run: { font: 'Times New Roman', bold: true, color: 'FFFFFF' },
                  }),
                ],
              }),
            ],
          }),
          ...parsedTermsList.map(
            (termItem, index) =>
              new TableRow({
                children: [
                  new TableCell({
                    width: { size: 1000, type: WidthType.DXA },
                    shading: {
                      type: ShadingType.CLEAR,
                      fill: index % 2 === 0 ? 'F8FAFC' : 'FFFFFF',
                    },
                    children: [
                      new Paragraph({
                        text: String(index + 1),
                        alignment: AlignmentType.CENTER,
                        run: { font: 'Times New Roman' },
                      }),
                    ],
                  }),
                  new TableCell({
                    width: { size: 8000, type: WidthType.DXA },
                    shading: {
                      type: ShadingType.CLEAR,
                      fill: index % 2 === 0 ? 'F8FAFC' : 'FFFFFF',
                    },
                    children: [
                      new Paragraph({
                        text: termItem,
                        run: { font: 'Times New Roman' },
                      }),
                    ],
                  }),
                ],
              })
          ),
        ];

        docChildren.push(
          new Table({
            rows: tableRows,
            width: { size: 9000, type: WidthType.DXA },
            borders: {
              top: { style: BorderStyle.SINGLE, size: 1, color: 'CBD5E1' },
              bottom: { style: BorderStyle.SINGLE, size: 1, color: 'CBD5E1' },
              left: { style: BorderStyle.SINGLE, size: 1, color: 'CBD5E1' },
              right: { style: BorderStyle.SINGLE, size: 1, color: 'CBD5E1' },
              insideHorizontal: { style: BorderStyle.SINGLE, size: 1, color: 'E2E8F0' },
              insideVertical: { style: BorderStyle.SINGLE, size: 1, color: 'E2E8F0' },
            },
          })
        );

        docChildren.push(
          new Paragraph({
            text: '',
            spacing: { after: 200 },
          })
        );
      }

      // Document Body
      const lines = generatedDoc.split('\n');
      for (const rawLine of lines) {
        const line = rawLine.trim();
        if (!line) continue;

        if (line.startsWith('## ') || line.match(/^(SECTION\s+\d+|[0-9]{1,2}\.\s+[A-Z])/)) {
          docChildren.push(
            new Paragraph({
              text: line.replace(/^##\s*/, ''),
              heading: HeadingLevel.HEADING_1,
              spacing: { before: 240, after: 100 },
              run: {
                font: 'Times New Roman',
                bold: true,
                size: 24,
                color: '0F172A',
              },
            })
          );
        } else if (line.startsWith('### ') || line.match(/^(\d+\.\d+|[a-z]\))\s+/)) {
          docChildren.push(
            new Paragraph({
              text: line.replace(/^###\s*/, ''),
              spacing: { before: 120, after: 60 },
              indent: { left: 400 },
              run: {
                font: 'Times New Roman',
                bold: true,
                size: 22,
                color: '1E293B',
              },
            })
          );
        } else {
          const isRecital =
            line.startsWith('WHEREAS') ||
            line.startsWith('WITNESSETH') ||
            line.startsWith('NOW, THEREFORE');
          docChildren.push(
            new Paragraph({
              alignment: AlignmentType.JUSTIFIED,
              spacing: { before: 60, after: 120, line: 276 },
              children: [
                new TextRun({
                  text: line,
                  font: 'Times New Roman',
                  size: 22,
                  italics: isRecital,
                  color: '334155',
                }),
              ],
            })
          );
        }
      }

      const docx = new DocxDocument({
        sections: [
          {
            properties: {
              page: {
                margin: {
                  top: 1440,
                  bottom: 1440,
                  left: 1440,
                  right: 1440,
                },
              },
            },
            footers: {
              default: new Footer({
                children: [
                  new Paragraph({
                    alignment: AlignmentType.CENTER,
                    children: [
                      new TextRun({
                        text: 'LegalEase Inc. | contact@legalease.com | Prepared for drafting purposes',
                        font: 'Times New Roman',
                        italics: true,
                        size: 18,
                        color: '94A3B8',
                      }),
                    ],
                  }),
                ],
              }),
            },
            children: docChildren,
          },
        ],
      });

      const blob = await Packer.toBlob(docx);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${currentType.toLowerCase().replace(/\s+/g, '_')}.docx`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Error generating DOCX:', err);
      alert('Failed to generate DOCX file.');
    }
  };

  // Download PDF
  const downloadPdf = () => {
    if (!generatedDoc) return;

    try {
      const doc = new jsPDF({
        orientation: 'p',
        unit: 'mm',
        format: 'a4',
      });

      const pageWidth = doc.internal.pageSize.getWidth();
      const pageHeight = doc.internal.pageSize.getHeight();
      const margin = 20;
      const contentWidth = pageWidth - margin * 2;

      let yPos = margin + 5;

      // Title
      doc.setFont('times', 'bold');
      doc.setFontSize(16);
      doc.setTextColor(15, 23, 42);
      doc.text(currentType.toUpperCase(), pageWidth / 2, yPos, { align: 'center' });
      yPos += 8;

      // Divider
      doc.setDrawColor(59, 130, 246);
      doc.setLineWidth(0.4);
      doc.line(margin + 20, yPos, pageWidth - margin - 20, yPos);
      yPos += 10;

      // Process body text
      doc.setFont('times', 'normal');
      doc.setFontSize(10.5);
      doc.setTextColor(30, 41, 59);

      const lines = generatedDoc.split('\n');

      const checkPageBreak = (neededHeight: number) => {
        if (yPos + neededHeight > pageHeight - margin - 15) {
          // Footer for previous page
          doc.setFont('times', 'italic');
          doc.setFontSize(8.5);
          doc.setTextColor(148, 163, 184);
          doc.text(
            `LegalEase Inc. | contact@legalease.com | Page ${doc.internal.pages.length - 1}`,
            pageWidth / 2,
            pageHeight - 10,
            { align: 'center' }
          );

          doc.addPage();
          yPos = margin + 5;
          doc.setFont('times', 'normal');
          doc.setFontSize(10.5);
          doc.setTextColor(30, 41, 59);
        }
      };

      for (const rawLine of lines) {
        const line = rawLine.trim();
        if (!line) {
          yPos += 3;
          continue;
        }

        // Section Heading
        if (line.startsWith('## ') || line.match(/^(SECTION\s+\d+|[0-9]{1,2}\.\s+[A-Z])/)) {
          checkPageBreak(12);
          yPos += 4;
          doc.setFont('times', 'bold');
          doc.setFontSize(12);
          doc.setTextColor(15, 23, 42);
          const headingText = line.replace(/^##\s*/, '');
          doc.text(headingText, margin, yPos);
          yPos += 6;
          doc.setFont('times', 'normal');
          doc.setFontSize(10.5);
          doc.setTextColor(30, 41, 59);
          continue;
        }

        // Attestation or Signatures
        if (line.includes('IN WITNESS WHEREOF')) {
          checkPageBreak(15);
          yPos += 6;
          doc.setFont('times', 'bold');
          doc.text(line, pageWidth / 2, yPos, { align: 'center' });
          yPos += 7;
          doc.setFont('times', 'normal');
          continue;
        }

        // Recitals or standard paragraph
        const isRecital =
          line.startsWith('WHEREAS') ||
          line.startsWith('WITNESSETH') ||
          line.startsWith('NOW, THEREFORE');
        doc.setFont('times', isRecital ? 'italic' : 'normal');

        const splitParagraph = doc.splitTextToSize(line, contentWidth);
        checkPageBreak(splitParagraph.length * 5 + 2);
        doc.text(splitParagraph, margin, yPos);
        yPos += splitParagraph.length * 5 + 2;
      }

      // Add footer to final page
      doc.setFont('times', 'italic');
      doc.setFontSize(8.5);
      doc.setTextColor(148, 163, 184);
      doc.text(
        `LegalEase Inc. | contact@legalease.com | Page ${doc.internal.pages.length - 1}`,
        pageWidth / 2,
        pageHeight - 10,
        { align: 'center' }
      );

      doc.save(`${currentType.toLowerCase().replace(/\s+/g, '_')}.pdf`);
    } catch (err) {
      console.error('Error generating PDF:', err);
      alert('Failed to generate PDF file.');
    }
  };

  const copyToClipboard = (text: string, key: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Top Navbar */}
      <header className="border-b border-slate-800 bg-slate-900/90 backdrop-blur sticky top-0 z-50 px-4 lg:px-8 py-3.5 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-blue-500/20 overflow-hidden border border-blue-400/30">
            {logoPreview ? (
              <img src={logoPreview} alt="Logo" className="w-full h-full object-cover" />
            ) : (
              <Scale className="w-5 h-5 text-white" />
            )}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-lg tracking-tight text-white">LegalEase</span>
              <span className="text-[10px] font-semibold uppercase px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-400 border border-blue-500/30">
                AI Legal Suite
              </span>
            </div>
            <p className="text-xs text-slate-400">AI-Powered Legal Document Generator</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setActiveTab('code')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all ${
              activeTab === 'code'
                ? 'bg-blue-600 text-white border-blue-500'
                : 'bg-slate-800/80 text-slate-300 border-slate-700 hover:bg-slate-700'
            }`}
          >
            <Code2 className="w-3.5 h-3.5" />
            <span>Python Project Code</span>
          </button>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 lg:p-8 grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Form & Presets (5 cols) */}
        <section className="lg:col-span-5 flex flex-col gap-6">
          {/* Quick Presets */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 shadow-sm">
            <div className="flex items-center justify-between mb-2.5">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                Quick Test Cases (One-Click Auto-Fill)
              </span>
            </div>
            <div className="grid grid-cols-3 gap-2">
              {PRESETS.map((p) => (
                <button
                  key={p.id}
                  onClick={() => applyPreset(p)}
                  className="px-2.5 py-2 rounded-lg bg-slate-800/90 hover:bg-slate-800 border border-slate-700/80 text-left transition hover:border-blue-500/50 group"
                >
                  <p className="text-xs font-medium text-slate-200 group-hover:text-blue-400 truncate">
                    {p.name}
                  </p>
                  <span className="text-[10px] text-slate-400 block truncate">{p.docType}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Configuration Form Card */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col gap-5">
            <h2 className="text-base font-semibold text-white flex items-center gap-2 border-b border-slate-800 pb-3">
              <Layers className="w-4 h-4 text-blue-400" />
              Contract Parameters
            </h2>

            {/* Document Type */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                Document Type
              </label>
              <select
                value={docType}
                onChange={(e) => setDocType(e.target.value)}
                className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-blue-500"
              >
                <option value="Employment Contract">Employment Contract</option>
                <option value="Employment Offer Letter">Employment Offer Letter</option>
                <option value="NDA">Non-Disclosure Agreement (NDA)</option>
                <option value="Lease Agreement">Residential Lease Agreement</option>
                <option value="Freelance Contract">Freelance Work Contract</option>
                <option value="Service Agreement">Service Agreement</option>
                <option value="Business Agreement">Business Agreement</option>
                <option value="General Contract">General Contract</option>
                <option value="Other">Other (Custom Specification)</option>
              </select>

              {docType === 'Other' && (
                <input
                  type="text"
                  placeholder="e.g. Commercial Partnership Agreement"
                  value={customDocType}
                  onChange={(e) => setCustomDocType(e.target.value)}
                  className="mt-2 w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-blue-500"
                />
              )}
            </div>

            {/* Parties Involved */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                Parties Involved
              </label>
              <p className="text-[11px] text-slate-400 mb-1.5">
                Names and roles of the individuals or organizations entering the agreement.
              </p>
              <textarea
                rows={2}
                value={parties}
                onChange={(e) => setParties(e.target.value)}
                placeholder="e.g. John Doe (Employee), ABC Technologies Pvt Ltd (Employer)"
                className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-sm text-slate-100 focus:outline-none focus:border-blue-500"
              />
            </div>

            {/* Terms & Conditions */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                Terms & Conditions (Separate with semicolons)
              </label>
              <p className="text-[11px] text-slate-400 mb-1.5">
                Specific clauses, rules, and compensation items. Use semicolons (;) for bullet points.
              </p>
              <textarea
                rows={3}
                value={terms}
                onChange={(e) => setTerms(e.target.value)}
                placeholder="e.g. Salary: ₹50,000 per month; Working hours: 9 AM to 6 PM; 15 days termination notice"
                className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-sm text-slate-100 focus:outline-none focus:border-blue-500"
              />
            </div>

            {/* Date and Optional Logo Grid */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                  Effective Date
                </label>
                <input
                  type="text"
                  value={effectiveDate}
                  onChange={(e) => setEffectiveDate(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                  Corporate Logo (Branding)
                </label>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/png,image/jpeg,image/jpg"
                  onChange={handleLogoUpload}
                  className="hidden"
                />
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="w-full bg-slate-950 hover:bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs font-medium text-slate-300 flex items-center justify-center gap-1.5 transition"
                >
                  <Upload className="w-3.5 h-3.5 text-blue-400" />
                  <span>{logoPreview ? 'Change Logo' : 'Upload Logo'}</span>
                </button>
              </div>
            </div>

            {/* Error Notification */}
            {errorBanner && (
              <div className="p-3 bg-red-950/80 border border-red-800 rounded-lg text-xs text-red-300 flex items-start gap-2">
                <AlertTriangle className="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" />
                <span>{errorBanner}</span>
              </div>
            )}

            {/* Generate Action Button */}
            <button
              onClick={handleGenerate}
              disabled={isGenerating}
              className="mt-2 w-full py-3 px-4 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 active:scale-[0.99] font-bold text-sm text-white shadow-lg shadow-blue-600/30 flex items-center justify-center gap-2 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isGenerating ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Drafting Legal Document with Gemini...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 text-amber-300" />
                  <span>Generate Document</span>
                </>
              )}
            </button>
          </div>

          {/* Legal Safety Banner */}
          <div className="bg-amber-950/30 border border-amber-800/40 rounded-xl p-4 flex gap-3 items-start">
            <ShieldAlert className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
            <p className="text-xs text-amber-200/80 leading-relaxed">
              <strong>Legal Safety Notice:</strong> LegalEase generates documents for informational
              and drafting purposes. Generated documents may require review and modification by a
              qualified legal professional and should be checked against applicable local laws before use.
            </p>
          </div>
        </section>

        {/* Right Column: Output Viewer, Editor, & Code Browser (7 cols) */}
        <section className="lg:col-span-7 flex flex-col gap-4">
          {/* Output Control Tabs */}
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <div className="flex gap-2">
              <button
                onClick={() => setActiveTab('preview')}
                className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition ${
                  activeTab === 'preview'
                    ? 'bg-blue-600 text-white'
                    : 'bg-slate-900 text-slate-400 hover:text-slate-200'
                }`}
              >
                <Eye className="w-3.5 h-3.5" />
                <span>Document Preview</span>
              </button>

              <button
                onClick={() => setActiveTab('edit')}
                className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition ${
                  activeTab === 'edit'
                    ? 'bg-blue-600 text-white'
                    : 'bg-slate-900 text-slate-400 hover:text-slate-200'
                }`}
              >
                <Edit3 className="w-3.5 h-3.5" />
                <span>Inline Editor</span>
                {generatedDoc && (
                  <span className="w-2 h-2 rounded-full bg-emerald-400 inline-block"></span>
                )}
              </button>

              <button
                onClick={() => setActiveTab('terms')}
                className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition ${
                  activeTab === 'terms'
                    ? 'bg-blue-600 text-white'
                    : 'bg-slate-900 text-slate-400 hover:text-slate-200'
                }`}
              >
                <TableIcon className="w-3.5 h-3.5" />
                <span>Terms Schedule ({parsedTermsList.length})</span>
              </button>

              <button
                onClick={() => setActiveTab('code')}
                className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition ${
                  activeTab === 'code'
                    ? 'bg-indigo-600 text-white'
                    : 'bg-slate-900 text-slate-400 hover:text-slate-200'
                }`}
              >
                <FolderGit2 className="w-3.5 h-3.5" />
                <span>VS Code Project Files</span>
              </button>
            </div>

            {/* Export Action Buttons */}
            {generatedDoc && (
              <div className="flex items-center gap-1.5">
                <button
                  onClick={downloadTxt}
                  title="Download Plain Text"
                  className="px-2.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-medium flex items-center gap-1 border border-slate-700 transition"
                >
                  <FileText className="w-3 h-3 text-slate-400" />
                  <span>.TXT</span>
                </button>
                <button
                  onClick={downloadDocx}
                  title="Download Microsoft Word Document"
                  className="px-2.5 py-1.5 bg-blue-900/60 hover:bg-blue-800 text-blue-200 rounded-lg text-xs font-medium flex items-center gap-1 border border-blue-700 transition"
                >
                  <Download className="w-3 h-3 text-blue-400" />
                  <span>.DOCX</span>
                </button>
                <button
                  onClick={downloadPdf}
                  title="Download Branded PDF"
                  className="px-2.5 py-1.5 bg-rose-950/80 hover:bg-rose-900 text-rose-200 rounded-lg text-xs font-medium flex items-center gap-1 border border-rose-800 transition"
                >
                  <Download className="w-3 h-3 text-rose-400" />
                  <span>.PDF</span>
                </button>
              </div>
            )}
          </div>

          {/* Tab 1: Preview View */}
          {activeTab === 'preview' && (
            <div className="flex-1 bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl min-h-[580px] max-h-[750px] overflow-y-auto flex flex-col">
              {!generatedDoc ? (
                <div className="flex-1 flex flex-col items-center justify-center text-center p-8 text-slate-500">
                  <div className="w-16 h-16 rounded-2xl bg-slate-800/80 border border-slate-700 flex items-center justify-center mb-4">
                    <Scale className="w-8 h-8 text-slate-400" />
                  </div>
                  <h3 className="text-base font-semibold text-slate-300 mb-1">
                    No Document Generated Yet
                  </h3>
                  <p className="text-xs max-w-sm text-slate-400 leading-relaxed mb-6">
                    Configure the contract parameters on the left or select a quick test case, then
                    click <strong>Generate Document</strong> to draft a formal agreement.
                  </p>
                  <div className="flex flex-wrap gap-2 justify-center">
                    {PRESETS.map((p) => (
                      <button
                        key={p.id}
                        onClick={() => {
                          applyPreset(p);
                          handleGenerate();
                        }}
                        className="px-3 py-1.5 rounded-lg bg-blue-950/60 hover:bg-blue-900 border border-blue-800/60 text-xs font-medium text-blue-300 transition flex items-center gap-1.5"
                      >
                        <ChevronRight className="w-3.5 h-3.5" />
                        <span>Run Test: {p.name}</span>
                      </button>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="space-y-4 font-serif text-slate-200 text-sm leading-relaxed">
                  {/* Document Header Branding */}
                  <div className="text-center pb-4 border-b border-slate-800">
                    {logoPreview && (
                      <img
                        src={logoPreview}
                        alt="Logo"
                        className="h-12 mx-auto mb-3 object-contain"
                      />
                    )}
                    <h1 className="text-xl font-bold tracking-wide uppercase text-white font-sans">
                      {currentType}
                    </h1>
                    <p className="text-xs text-slate-400 font-sans mt-1">
                      Effective Date: {effectiveDate}
                    </p>
                  </div>

                  {/* Render Parsed Document Paragraphs */}
                  {generatedDoc.split('\n').map((rawLine, idx) => {
                    const line = rawLine.trim();
                    if (!line) return <div key={idx} className="h-2" />;

                    if (
                      line.startsWith('## ') ||
                      line.match(/^(SECTION\s+\d+|[0-9]{1,2}\.\s+[A-Z])/)
                    ) {
                      return (
                        <div key={idx} className="pt-3 pb-1 border-l-2 border-blue-500 pl-3 my-2">
                          <h2 className="text-sm font-bold uppercase tracking-wider text-blue-300 font-sans">
                            {line.replace(/^##\s*/, '')}
                          </h2>
                        </div>
                      );
                    }

                    if (line.startsWith('### ') || line.match(/^(\d+\.\d+|[a-z]\))\s+/)) {
                      return (
                        <div key={idx} className="pl-4 font-semibold text-slate-300 text-xs font-sans">
                          {line.replace(/^###\s*/, '')}
                        </div>
                      );
                    }

                    if (
                      line.startsWith('WHEREAS') ||
                      line.startsWith('WITNESSETH') ||
                      line.startsWith('NOW, THEREFORE')
                    ) {
                      return (
                        <p
                          key={idx}
                          className="italic text-slate-300 bg-slate-950/60 p-2.5 rounded-lg border-l-2 border-indigo-400 text-xs leading-relaxed"
                        >
                          {line}
                        </p>
                      );
                    }

                    if (line.includes('IN WITNESS WHEREOF')) {
                      return (
                        <div
                          key={idx}
                          className="text-center pt-6 pb-2 text-xs font-bold text-slate-300 border-t border-dashed border-slate-700 mt-6"
                        >
                          {line}
                        </div>
                      );
                    }

                    return (
                      <p key={idx} className="text-slate-300 text-justify text-xs leading-relaxed">
                        {line}
                      </p>
                    );
                  })}
                </div>
              )}
            </div>
          )}

          {/* Tab 2: Live Editor View */}
          {activeTab === 'edit' && (
            <div className="flex-1 bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl min-h-[580px] flex flex-col gap-3">
              <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                <span className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                  <Edit3 className="w-3.5 h-3.5 text-blue-400" />
                  Editable Document Workspace
                </span>
                <span className="text-[11px] text-slate-400">
                  {generatedDoc.length} characters | All changes live-sync with preview & downloads
                </span>
              </div>
              <textarea
                value={generatedDoc}
                onChange={(e) => setGeneratedDoc(e.target.value)}
                placeholder="Generated document text will appear here. You can freely edit or type clauses..."
                className="flex-1 w-full bg-slate-950 border border-slate-800 rounded-xl p-4 text-xs font-mono text-slate-200 leading-relaxed focus:outline-none focus:border-blue-500 resize-none min-h-[460px]"
              />
            </div>
          )}

          {/* Tab 3: Terms Table Schedule */}
          {activeTab === 'terms' && (
            <div className="flex-1 bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl min-h-[580px] flex flex-col gap-4">
              <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                <span className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                  <TableIcon className="w-3.5 h-3.5 text-blue-400" />
                  Schedule of Key Contractual Terms
                </span>
                <span className="text-[11px] text-slate-400">
                  Automatically embedded into DOCX table and PDF bullets
                </span>
              </div>

              {parsedTermsList.length === 0 ? (
                <div className="p-8 text-center text-slate-500 text-xs">
                  No terms separated by semicolons entered yet.
                </div>
              ) : (
                <div className="border border-slate-800 rounded-xl overflow-hidden">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-slate-950 text-slate-400 font-semibold border-b border-slate-800">
                      <tr>
                        <th className="py-2.5 px-4 w-14 text-center">No.</th>
                        <th className="py-2.5 px-4">Stipulated Clause / Specification</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/80">
                      {parsedTermsList.map((item, idx) => (
                        <tr key={idx} className="hover:bg-slate-800/40 transition">
                          <td className="py-2.5 px-4 text-center font-mono text-slate-400 font-bold">
                            {idx + 1}
                          </td>
                          <td className="py-2.5 px-4 text-slate-200 font-medium">{item}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {/* Tab 4: VS Code Project Explorer */}
          {activeTab === 'code' && (
            <div className="flex-1 bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl min-h-[580px] flex flex-col gap-4">
              <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                <div>
                  <span className="text-xs font-bold text-slate-200 flex items-center gap-1.5">
                    <FolderGit2 className="w-4 h-4 text-blue-400" />
                    Local Python Project Explorer
                  </span>
                  <p className="text-[11px] text-slate-400">
                    Full codebase for running in your local Windows / VS Code environment
                  </p>
                </div>
                <button
                  onClick={() =>
                    copyToClipboard(
                      CODE_FILES[selectedCodeFile]?.content || '',
                      selectedCodeFile
                    )
                  }
                  className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-semibold flex items-center gap-1.5 border border-slate-700 transition"
                >
                  {copiedKey === selectedCodeFile ? (
                    <>
                      <Check className="w-3.5 h-3.5 text-emerald-400" />
                      <span className="text-emerald-400">Copied!</span>
                    </>
                  ) : (
                    <>
                      <Copy className="w-3.5 h-3.5 text-slate-400" />
                      <span>Copy File Code</span>
                    </>
                  )}
                </button>
              </div>

              {/* File Selector Tabs */}
              <div className="flex flex-wrap gap-1.5 border-b border-slate-800/80 pb-2">
                {Object.keys(CODE_FILES).map((fileName) => (
                  <button
                    key={fileName}
                    onClick={() => setSelectedCodeFile(fileName)}
                    className={`px-2.5 py-1 rounded text-[11px] font-mono transition ${
                      selectedCodeFile === fileName
                        ? 'bg-blue-600 text-white font-bold'
                        : 'bg-slate-950 text-slate-400 hover:bg-slate-800'
                    }`}
                  >
                    {fileName}
                  </button>
                ))}
              </div>

              {/* Code Viewer */}
              <div className="flex-1 bg-slate-950 border border-slate-800 rounded-xl p-4 overflow-x-auto overflow-y-auto max-h-[460px]">
                <pre className="text-xs font-mono text-slate-200 leading-relaxed">
                  <code>{CODE_FILES[selectedCodeFile]?.content}</code>
                </pre>
              </div>
            </div>
          )}
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 py-4 px-8 text-center text-xs text-slate-500">
        <p>LegalEase – AI-Powered Legal Document Generator | FastAPI • Streamlit • Google Gemini</p>
      </footer>
    </div>
  );
}
