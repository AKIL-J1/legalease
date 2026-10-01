/**
 * LegalEase - Full-Stack Express Server with Gemini AI Integration.
 * Serves API routes and integrates Vite middleware for the web application.
 */

import express, { Request, Response } from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import { GoogleGenAI } from '@google/genai';
import dotenv from 'dotenv';

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Serve public assets (logo, etc.)
app.use('/public', express.static(path.join(__dirname, 'public')));
app.use('/assets', express.static(path.join(__dirname, 'assets')));

// Shared Gemini client utility on the server with user-agent telemetry
const apiKey = process.env.GEMINI_API_KEY || '';
const ai = new GoogleGenAI({
  apiKey: apiKey,
  httpOptions: {
    headers: {
      'User-Agent': 'aistudio-build',
    },
  },
});

// Health check endpoint
app.get('/api/health', (_req: Request, res: Response) => {
  res.json({
    status: 'success',
    service: 'LegalEase API',
    apiKeyConfigured: !!apiKey,
    model: 'gemini-3.8-flash',
  });
});

// Root endpoint matching FastAPI specification
app.get('/api/info', (_req: Request, res: Response) => {
  res.json({
    status: 'success',
    message: 'LegalEase API is running',
    version: '1.0.0',
  });
});

// Contract drafting prompt generator
function constructLegalPrompt(documentType: string, parties: string, terms: string, dates: string): string {
  return `You are a senior corporate counsel and expert contract draftsman.
Draft a comprehensive, highly formal, and legally structured legal document based strictly on the user specifications below.

DOCUMENT SPECIFICATIONS:
- Document Type: ${documentType}
- Involved Parties: ${parties}
- Effective Date: ${dates}
- Key Terms & Conditions: ${terms}

DRAFTING INSTRUCTIONS & RULES:
1. Title: Create a prominent, formal title in ALL CAPS matching the Document Type (e.g., 'EMPLOYMENT AGREEMENT', 'NON-DISCLOSURE AND CONFIDENTIALITY AGREEMENT', 'RESIDENTIAL LEASE AGREEMENT').
2. Preamble & Recitals:
   - Clearly state the Effective Date: ${dates}.
   - Identify each party precisely with legal designations (e.g., 'Employer' and 'Employee', 'Disclosing Party' and 'Receiving Party', 'Landlord' and 'Tenant', 'Service Provider' and 'Client').
   - Include formal recitals beginning with 'WHEREAS...' and concluding with 'NOW, THEREFORE, in consideration of the mutual covenants contained herein...'.
3. Adaptive Sections & Numbered Clauses:
   - Adapt the sections specifically to the document type:
     * Employment Contracts: Role & Duties, Term, Compensation & Benefits, Working Hours, Confidentiality, Non-Compete/Non-Solicitation, Termination & Notice, Intellectual Property, Governing Law.
     * NDAs: Definition of Confidential Information, Exclusions, Obligations of Receiving Party, Non-Disclosure Period, Return of Materials, Remedies & Injunctions, Governing Law.
     * Lease Agreements: Demised Premises, Term of Lease, Rent & Payment Terms, Security Deposit, Utilities & Maintenance, Use of Premises, Default & Eviction, Landlord Access, Governing Law.
     * Freelance/Service Agreements: Scope of Services, Deliverables & Timeline, Compensation & Invoicing, Independent Contractor Status, Intellectual Property Rights, Warranties, Termination.
     * Other Agreements: Construct formal, applicable legal sections suitable for the stated purpose.
4. Incorporate User Terms Faithfully:
   - Every single term supplied by the user must be incorporated into an appropriate, enforceable legal clause.
   - Do NOT omit any provided terms.
5. Strict Fact Integrity:
   - Do NOT invent specific names, dates, dollar amounts, or addresses that were not supplied.
   - If critical information is absent (such as an address, governing jurisdiction, or notice period), denote it clearly as [Information Required] or [City, State/Country] rather than fabricating facts.
6. Standard Boilerplate & Protection Clauses:
   - Include standard legal protections: Entire Agreement, Amendments in Writing, Severability, Waiver, and Governing Law.
7. Execution / Signatures:
   - Conclude with a formal 'IN WITNESS WHEREOF' attestation clause.
   - Provide clean signature blocks for each party involved, including lines for Signature, Printed Name, Title, and Date.
8. Output Format:
   - Return clean, plain text with structured indentation and numbered sections (e.g. SECTION 1, 1.1).
   - Do NOT wrap the document in markdown code blocks like \`\`\`markdown or \`\`\`.
`;
}

// Document Generation Endpoint (supports both /generate and /api/generate)
async function handleGenerate(req: Request, res: Response) {
  try {
    const { document_type, parties, terms, dates } = req.body;

    if (!document_type || !document_type.toString().trim()) {
      return res.status(400).json({ detail: 'document_type is required and cannot be empty.' });
    }
    if (!parties || !parties.toString().trim()) {
      return res.status(400).json({ detail: 'parties is required and cannot be empty.' });
    }
    if (!terms || !terms.toString().trim()) {
      return res.status(400).json({ detail: 'terms is required and cannot be empty.' });
    }
    if (!dates || !dates.toString().trim()) {
      return res.status(400).json({ detail: 'dates is required and cannot be empty.' });
    }

    if (!apiKey) {
      return res.status(500).json({
        detail: 'GEMINI_API_KEY is not configured on the server. Please check the Secrets panel.',
      });
    }

    const prompt = constructLegalPrompt(document_type, parties, terms, dates);

    const response = await ai.models.generateContent({
      model: 'gemini-3.8-flash',
      contents: prompt,
    });

    let text = response.text || '';
    if (!text.trim()) {
      return res.status(500).json({ detail: 'Empty response returned from Gemini.' });
    }

    // Clean any accidental markdown code fences
    let cleaned = text.trim();
    if (cleaned.startsWith('```')) {
      const lines = cleaned.split('\n');
      if (lines[0].startsWith('```')) lines.shift();
      if (lines.length && lines[lines.length - 1].trim() === '```') lines.pop();
      cleaned = lines.join('\n').trim();
    }

    return res.json({
      success: true,
      document: cleaned,
      message: 'Document generated successfully',
    });
  } catch (error: any) {
    console.error('Error in /api/generate:', error);
    return res.status(500).json({
      detail: error.message || 'Internal server error while generating document',
    });
  }
}

app.post('/api/generate', handleGenerate);
app.post('/generate', handleGenerate);

// Setup Vite middleware in dev or static files in production
async function startServer() {
  if (process.env.NODE_ENV !== 'production') {
    const { createServer: createViteServer } = await import('vite');
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa',
    });
    app.use(vite.middlewares);
  } else {
    app.use(express.static(path.join(__dirname, 'dist')));
    app.get('*', (_req, res) => {
      res.sendFile(path.join(__dirname, 'dist', 'index.html'));
    });
  }

  app.listen(PORT, () => {
    console.log(`LegalEase Server running at http://localhost:${PORT}`);
  });
}

startServer().catch((err) => {
  console.error('Failed to start server:', err);
});
