import json
import os
from typing import Any

from dotenv import load_dotenv
from google import genai


load_dotenv()


ENRICHMENT_PROMPT = """
You are a procurement requirements classification assistant.

Classify each tender requirement from a gap analysis.

Return ONLY valid JSON, without markdown fences.

Schema:
{
  "requirements": [
    {
      "requirement_id": "REQ_001",
      "category": "TECHNICAL | COMPLIANCE | QUALIFICATION | ADMINISTRATIVE",
      "criticality": "BLOCKING | PREFERENTIAL | INFO",
      "weight": 1,
      "reasoning": "short explanation"
    }
  ]
}

Classification rules:
- BLOCKING: if the requirement can prevent participation, contract compliance, or legal/administrative eligibility.
- PREFERENTIAL: if it improves competitiveness but is not mandatory.
- INFO: if it is informational only.

Category rules:
- QUALIFICATION: registrations, MePA, CPV, supplier eligibility, economic qualification, required certifications to bid.
- COMPLIANCE: GDPR, legal obligations, D.lgs, CCNL, financial traceability, public procurement law.
- TECHNICAL: technical skills, platforms, licenses, configurations, engineering capabilities, EDR/XDR.
- ADMINISTRATIVE: documents, forms, declarations, invoices, banking details, operational paperwork.

Weight rules:
- 5: essential blocking requirement
- 3-4: important requirement
- 1-2: secondary or informational requirement
"""


def _extract_json(text: str) -> dict[str, Any]:
    cleaned = text.strip()

    if cleaned.startswith("```json"):
        cleaned = cleaned.removeprefix("```json").strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.removeprefix("```").strip()

    if cleaned.endswith("```"):
        cleaned = cleaned.removesuffix("```").strip()

    return json.loads(cleaned)


def enrich_gap_analysis_with_llm(gap_analysis: dict[str, Any]) -> dict[str, Any]:
    api_key = os.environ["GEMINI_API_KEY"]
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    client = genai.Client(api_key=api_key)

    payload = json.dumps(gap_analysis, ensure_ascii=False, indent=2)

    response = client.models.generate_content(
        model=model_name,
        contents=f"{ENRICHMENT_PROMPT}\n\nInput JSON:\n{payload}",
    )

    if not response.text:
        raise ValueError("Gemini returned an empty response.")

    return _extract_json(response.text)