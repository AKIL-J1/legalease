"""LegalEase - FastAPI Backend Routes.

Defines Pydantic request models, input validation, and document generation
endpoints connecting to the Gemini AI core.
"""

import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, field_validator

from ai_core.gemini_generator import GeminiDocumentGenerator

logger = logging.getLogger(__name__)

router = APIRouter()

# Instantiate the AI document generator
gemini_generator = GeminiDocumentGenerator()


class DocumentRequest(BaseModel):
    """Pydantic model validating legal document generation requests."""

    document_type: str = Field(
        ...,
        min_length=2,
        max_length=150,
        description="Type of legal document (e.g. Employment Contract, NDA, Lease Agreement)",
        examples=["Employment Contract"],
    )
    parties: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="Names and roles of parties involved",
        examples=["John Doe (Employee), ABC Technologies Pvt Ltd (Employer)"],
    )
    terms: str = Field(
        ...,
        min_length=3,
        max_length=4000,
        description="Key terms, clauses, or rules separated by semicolons",
        examples=["Salary: $50,000 per year; Working hours: 9 AM - 5 PM; Confidentiality required"],
    )
    dates: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Effective date or duration",
        examples=["October 1, 2026"],
    )

    @field_validator("document_type", "parties", "terms", "dates")
    @classmethod
    def check_not_empty(cls, v: str) -> str:
        """Ensure fields are not whitespace-only."""
        stripped = v.strip()
        if not stripped:
            raise ValueError("Field cannot be empty or purely whitespace.")
        return stripped


class DocumentResponse(BaseModel):
    """Pydantic response model for successful generation."""

    success: bool = True
    document: str
    message: Optional[str] = "Document generated successfully"


@router.get("/health", tags=["Health"])
def health_status() -> Dict[str, Any]:
    """Endpoint for checking router health."""
    return {
        "status": "healthy",
        "service": "LegalEase Document Generator API",
        "model_configured": gemini_generator.model_name,
    }


@router.get("/presets", tags=["Templates"])
def get_presets() -> Dict[str, Any]:
    """Provide verified test-case presets for quick testing."""
    return {
        "presets": [
            {
                "id": "employment_contract",
                "document_type": "Employment Contract",
                "parties": "John Doe (Employee), ABC Technologies Pvt Ltd (Employer)",
                "terms": "Salary: ₹50,000 per month; Working hours: 9 AM to 6 PM; Confidentiality required; 15 days termination notice",
                "dates": "October 1, 2026",
            },
            {
                "id": "nda",
                "document_type": "NDA",
                "parties": "Jane Doe (Disclosing Party), TechNova Inc. (Receiving Party)",
                "terms": "Confidential business information; No unauthorized disclosure; Confidentiality for 2 years; Return confidential materials upon termination",
                "dates": "October 1, 2026",
            },
            {
                "id": "lease_agreement",
                "document_type": "Lease Agreement",
                "parties": "Alice Smith (Tenant), XYZ Realty (Landlord)",
                "terms": "Monthly rent: ₹20,000; Security deposit: ₹60,000; Residential use only; Lease duration 12 months",
                "dates": "October 1, 2026",
            },
        ]
    }


@router.post(
    "/generate",
    response_model=DocumentResponse,
    status_code=status.HTTP_200_OK,
    tags=["Generation"],
    summary="Generate AI Legal Document",
)
def generate_legal_document(request: DocumentRequest) -> Dict[str, Any]:
    """Receive document specifications, prompt Gemini AI, and return structured

    legal document text.
    """
    logger.info("Received generation request for '%s'", request.document_type)

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
            "message": "Document generated successfully",
        }

    except ValueError as ve:
        logger.warning("Validation error during generation: %s", str(ve))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve),
        )
    except Exception as e:
        logger.error("Generation failed: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document generation failed: {str(e)}",
        )
