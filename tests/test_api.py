"""LegalEase - Test Suite.

Tests FastAPI endpoints, request validation, text sanitization,
DOCX generation, PDF generation, and TXT formatting.
"""

import os
import sys
import unittest
from fastapi.testclient import TestClient

# Ensure root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.main import app
from document_utils.formatter import sanitize_text, parse_terms, format_html_preview
from document_utils.docx_generator import format_docx
from document_utils.pdf_generator import format_pdf
from document_utils.txt_generator import format_txt


class LegalEaseTestSuite(unittest.TestCase):
    """Unit and integration tests for LegalEase."""

    def setUp(self):
        self.client = TestClient(app)
        self.sample_text = (
            "# EMPLOYMENT CONTRACT\n\n"
            "This Agreement is entered into as of October 1, 2026.\n\n"
            "SECTION 1. DUTIES AND RESPONSIBILITIES\n"
            "The Employee shall perform software engineering duties.\n\n"
            "SECTION 2. COMPENSATION\n"
            "The Company shall pay a monthly salary of INR 50,000.\n\n"
            "IN WITNESS WHEREOF, the parties execute this Agreement.\n"
        )
        self.sample_terms = (
            "Salary: 50,000 per month; Working hours: 9 AM to 6 PM; Confidentiality required"
        )

    def test_health_check_endpoint(self):
        """Test GET / returns 200 with status success."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get("status"), "success")
        self.assertIn("LegalEase API is running", data.get("message"))

    def test_router_health(self):
        """Test GET /health returns 200."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("status"), "healthy")

    def test_presets_endpoint(self):
        """Test GET /presets returns test cases."""
        response = self.client.get("/presets")
        self.assertEqual(response.status_code, 200)
        presets = response.json().get("presets", [])
        self.assertEqual(len(presets), 3)

    def test_generate_missing_fields_validation(self):
        """Test POST /generate rejects empty or missing fields with 422 Unprocessable Entity."""
        bad_payload = {
            "document_type": "",
            "parties": "John Doe",
            "terms": "Salary 50k",
            "dates": "Oct 1",
        }
        response = self.client.post("/generate", json=bad_payload)
        self.assertEqual(response.status_code, 422)

    def test_text_sanitizer(self):
        """Test sanitize_text normalizes curly quotes and special whitespace."""
        raw = "“Agreement” and ‘Terms’ — with special\u00a0space"
        cleaned = sanitize_text(raw)
        self.assertEqual(cleaned, '"Agreement" and \'Terms\'  --  with special space')

    def test_parse_terms(self):
        """Test parse_terms correctly extracts semicolon-separated clauses."""
        terms_str = "Payment in 30 days; Confidentiality; 15 days notice;"
        parsed = parse_terms(terms_str)
        self.assertEqual(len(parsed), 3)
        self.assertEqual(parsed[0], "Payment in 30 days")
        self.assertEqual(parsed[1], "Confidentiality")
        self.assertEqual(parsed[2], "15 days notice")

    def test_format_html_preview(self):
        """Test HTML preview formatting generates styled tags."""
        html_out = format_html_preview(self.sample_text)
        self.assertIn("<h1", html_out)
        self.assertIn("SECTION 1. DUTIES AND RESPONSIBILITIES", html_out)
        self.assertIn("IN WITNESS WHEREOF", html_out)

    def test_docx_generation(self):
        """Test DOCX generator produces non-empty bytes."""
        docx_bytes = format_docx(
            text=self.sample_text,
            doc_type="Employment Contract",
            terms=self.sample_terms,
        )
        self.assertIsInstance(docx_bytes, bytes)
        self.assertGreater(len(docx_bytes), 1000)

    def test_pdf_generation(self):
        """Test PDF generator produces non-empty bytes."""
        pdf_bytes = format_pdf(
            text=self.sample_text,
            doc_type="Employment Contract",
            terms=self.sample_terms,
        )
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertGreater(len(pdf_bytes), 500)
        # PDF files begin with %PDF
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))

    def test_txt_generation(self):
        """Test TXT generator produces formatted legal string."""
        txt_out = format_txt(
            text=self.sample_text,
            doc_type="Employment Contract",
            parties="John Doe, ABC Tech",
            dates="October 1, 2026",
        )
        self.assertIn("EMPLOYMENT CONTRACT", txt_out)
        self.assertIn("Effective Date: October 1, 2026", txt_out)
        self.assertIn("LegalEase", txt_out)


if __name__ == "__main__":
    unittest.main()
