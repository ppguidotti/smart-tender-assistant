from dotenv import load_dotenv
from openai import OpenAI
import json
import os

load_dotenv()

ENRICHMENT_SCHEMA = {
    "type": "object",
    "properties": {
        "requirements": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "requirement_id": {"type": "string"},
                    "category": {
                        "type": "string",
                        "enum": [
                            "TECHNICAL",
                            "COMPLIANCE",
                            "QUALIFICATION",
                            "ADMINISTRATIVE",
                        ],
                    },
                    "criticality": {
                        "type": "string",
                        "enum": [
                            "BLOCKING",
                            "PREFERENTIAL",
                            "INFO",
                        ],
                    },
                    "weight": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 5,
                    },
                    "reasoning": {"type": "string"},
                },
                "required": [
                    "requirement_id",
                    "category",
                    "criticality",
                    "weight",
                    "reasoning",
                ],
                "additionalProperties": False,
            },
        }
    },
    "required": ["requirements"],
    "additionalProperties": False,
}

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


def enrich_gap_analysis_with_llm(gap_analysis: dict) -> dict:
    try:
        client = OpenAI(
            base_url=os.environ["GROK_ENDPOINT"],
            api_key=os.environ["GROK_API_KEY"],
            timeout=60,
        )

        completion = client.chat.completions.create(
            model=os.getenv(
                "GROK_MODEL",
                "grok-4-1-fast-non-reasoning",
            ),
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": ENRICHMENT_PROMPT,
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        gap_analysis,
                        ensure_ascii=False,
                    ),
                },
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "requirement_enrichment",
                    "schema": ENRICHMENT_SCHEMA,
                },
            },
        )

        content = completion.choices[0].message.content

        if not content:
            raise ValueError("Grok returned an empty response.")

        return json.loads(content)

    except Exception as exc:
        raise RuntimeError(
            f"Grok enrichment failed: {exc}"
        ) from exc