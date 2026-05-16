import json
import os

from dotenv import load_dotenv
from google import genai

load_dotenv()


SYSTEM_PROMPT = """
Sei un assistente esperto nell'analisi di bandi di gara italiani.

Obiettivo:
estrarre requisiti rilevanti per decisione GO/NO-GO.

Categorie consentite:
- amministrativo
- tecnico
- economico
- certificazioni
- documentazione_richiesta
- sicurezza_privacy
- contrattuale
- scadenze

Per ogni requisito restituisci:
- category
- requirement
- source_document
- evidence
- priority (must / should / optional)

Rispondi SOLO JSON valido.

Formato:

{
  "requirements": [
    {
      "category": "...",
      "requirement": "...",
      "source_document": "...",
      "evidence": "...",
      "priority": "must"
    }
  ]
}
"""


class GeminiRequirementExtractor:
    def __init__(self, model: str = "gemini-2.5-flash"):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY non trovata")

        self.client = genai.Client(api_key=api_key)
        self.model = model

    def extract(self, tender_text: str) -> dict:
        response = self.client.models.generate_content(
            model=self.model,
            contents=[
                SYSTEM_PROMPT,
                tender_text,
            ],
        )

        text = response.text.strip()

        if text.startswith("```json"):
            text = text.removeprefix("```json").removesuffix("```").strip()

        return json.loads(text)
