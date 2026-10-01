"""LegalEase - Gemini AI Document Generator.

Integrates with Google Gemini to generate structured, professional legal
agreements tailored dynamically to user inputs.
"""

import os
import logging
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

logger = logging.getLogger(__name__)


class GeminiDocumentGenerator:
    """Handles structured legal document drafting using Google Gemini API."""

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        """Initialize the Gemini generator with API credentials and model configuration."""
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "").strip()
        # Default to gemini-2.5-flash which is widely supported in Google AI Studio
        self.model_name = (
            model_name
            or os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
        )
        self._client = None
        self._sdk_type = None

        if not self.api_key:
            logger.warning(
                "GEMINI_API_KEY is not set. Document generation will fail until a valid key is provided."
            )
            return

        self._initialize_sdk()

    def _initialize_sdk(self):
        """Attempt to initialize the official google-genai or legacy google-generativeai SDK."""
        # Strategy 1: Attempt modern google-genai SDK (recommended)
        try:
            from google import genai
            self._client = genai.Client(api_key=self.api_key)
            self._sdk_type = "google-genai"
            logger.info("Initialized modern google-genai Client with model: %s", self.model_name)
            return
        except ImportError:
            pass
        except Exception as e:
            logger.warning("Failed initializing google.genai: %s", e)

        # Strategy 2: Attempt legacy google.generativeai SDK
        try:
            import google.generativeai as legacy_genai
            legacy_genai.configure(api_key=self.api_key)
            # If the configured model is gemini-2.5-flash or gemini-1.5-pro, use it
            self._client = legacy_genai.GenerativeModel(self.model_name)
            self._sdk_type = "google-generativeai"
            logger.info("Initialized google-generativeai GenerativeModel with: %s", self.model_name)
            return
        except ImportError:
            pass
        except Exception as e:
            logger.warning("Failed initializing google.generativeai: %s", e)

        raise RuntimeError(
            "Neither 'google-genai' nor 'google-generativeai' could be loaded. "
            "Please run: pip install google-genai (or pip install google-generativeai)"
        )

    def _build_prompt(
        self, document_type: str, parties: str, terms: str, dates: str
    ) -> str:
        """Build a comprehensive, legally sound prompt for Gemini."""
        prompt = f"""You are a senior legal counsel and expert contract draftsman.
Draft a comprehensive, highly formal, and legally structured legal document based strictly on the user specifications below.

DOCUMENT SPECIFICATIONS:
- Document Type: {document_type}
- Involved Parties: {parties}
- Effective Date: {dates}
- Key Terms & Conditions: {terms}

DRAFTING INSTRUCTIONS & RULES:
1. Title: Create a prominent, formal title in ALL CAPS matching the Document Type (e.g., 'EMPLOYMENT AGREEMENT', 'NON-DISCLOSURE AND CONFIDENTIALITY AGREEMENT', 'RESIDENTIAL LEASE AGREEMENT').
2. Preamble & Recitals:
   - Clearly state the Effective Date: {dates}.
   - Identify each party precisely with legal designations (e.g., 'Employer' and 'Employee', 'Disclosing Party' and 'Receiving Party', 'Landlord' and 'Tenant', 'Service Provider' and 'Client').
   - Include formal recitals beginning with 'WHEREAS...' and concluding with 'NOW, THEREFORE, in consideration of the mutual covenants contained herein...'.
3. Adaptive Sections & Numbered Clauses:
   - Adapt the sections specifically to the document type:
     * For Employment Contracts: Role & Duties, Term, Compensation & Benefits, Working Hours, Confidentiality, Non-Compete/Non-Solicitation, Termination & Notice, Intellectual Property, Governing Law.
     * For NDAs: Definition of Confidential Information, Exclusions, Obligations of Receiving Party, Non-Disclosure Period, Return of Materials, Remedies & Injunctions, Governing Law.
     * For Lease Agreements: Demised Premises, Term of Lease, Rent & Payment Terms, Security Deposit, Utilities & Maintenance, Use of Premises, Default & Eviction, Landlord Access, Governing Law.
     * For Freelance/Service Agreements: Scope of Services, Deliverables & Timeline, Compensation & Invoicing, Independent Contractor Status, Intellectual Property Rights, Warranties, Termination.
     * For Other Agreements: Construct formal, applicable legal sections suitable for the stated purpose.
4. Incorporate User Terms Faithfully:
   - Every single term supplied by the user must be incorporated into an appropriate, enforceable legal clause.
   - Do NOT omit any provided terms.
5. Strict Fact Integrity:
   - Do NOT invent specific names, dates, dollar amounts, or addresses that were not supplied.
   - If critical information is absent (such as an address, governing jurisdiction, or notice period), denote it clearly as [Information Required] or [City, State/Country] rather than fabricating facts.
6. Standard Boilerplate & Protection Clauses:
   - Include standard legal protections: Entire Agreement (Integration clause), Amendments in Writing, Severability, Waiver, and Governing Law.
7. Execution / Signatures:
   - Conclude with a formal 'IN WITNESS WHEREOF' attestation clause.
   - Provide clean signature blocks for each party involved, including lines for:
     * Signature
     * Printed Name
     * Title (if corporate)
     * Date
8. Output Format:
   - Return clean, plain text with structured indentation.
   - Use 'SECTION 1. [TITLE]' or '1. [TITLE]' for section headers.
   - Use numbered sub-clauses (e.g., 1.1, 1.2 or (a), (b)).
   - Do NOT wrap the document in markdown code blocks (such as ```markdown or ```).
   - Ensure the text is ready for direct export into DOCX and PDF documents.
"""
        return prompt

    def generate_document(
        self, document_type: str, parties: str, terms: str, dates: str
    ) -> str:
        """Generate a complete legal document using the configured Gemini model.

        Args:
            document_type: The category/title of legal agreement.
            parties: The entities or individuals entering the agreement.
            terms: Core clauses, financial terms, or operational rules.
            dates: The effective date or duration.

        Returns:
            The raw generated legal document text.
        """
        # Validate inputs
        if not document_type or not document_type.strip():
            raise ValueError("document_type is required and cannot be empty.")
        if not parties or not parties.strip():
            raise ValueError("parties is required and cannot be empty.")
        if not terms or not terms.strip():
            raise ValueError("terms is required and cannot be empty.")
        if not dates or not dates.strip():
            raise ValueError("dates is required and cannot be empty.")

        # Re-check API key in case it was updated in environment
        if not self.api_key:
            self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
            if self.api_key:
                self._initialize_sdk()

        if not self.api_key:
            raise ValueError(
                "Gemini API Key is missing. Please configure GEMINI_API_KEY in your .env file."
            )

        if not self._client:
            self._initialize_sdk()

        prompt = self._build_prompt(document_type, parties, terms, dates)

        logger.info(
            "Calling Gemini (%s - %s) for '%s'",
            self._sdk_type,
            self.model_name,
            document_type,
        )

        try:
            if self._sdk_type == "google-genai":
                response = self._client.models.generateContent(
                    model=self.model_name,
                    contents=prompt,
                )
                text = response.text
            elif self._sdk_type == "google-generativeai":
                response = self._client.generate_content(prompt)
                text = response.text
            else:
                raise RuntimeError("No active Gemini client available.")

            if not text or not text.strip():
                raise RuntimeError("Gemini returned an empty response. Please try again.")

            # Clean markdown code fences if model enclosed response in ```
            cleaned = text.strip()
            if cleaned.startswith("```"):
                lines = cleaned.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                cleaned = "\n".join(lines).strip()

            return cleaned

        except Exception as e:
            logger.error("Error during Gemini document generation: %s", str(e))
            raise RuntimeError(f"Gemini generation error: {str(e)}") from e
