import json
import os

from dotenv import load_dotenv
from google import genai

load_dotenv()


SYSTEM_PROMPT = """
Sei un assistente esperto nell'analisi di bandi di gara italiani.

Obiettivo:
estrarre requisiti utili per una decisione GO/NO-GO.

Devi distinguere:
- requisiti escludenti: se non soddisfatti possono impedire la partecipazione o rendere l'offerta non valutabile;
- requisiti preferenziali: migliorano la valutazione o la competitività, ma non bloccano necessariamente la partecipazione;
- requisiti informativi: informazioni rilevanti ma non direttamente vincolanti.

Categorie consentite:
- NORMATIVA
- QUALIFICAZIONE
- TECNICA
- AMMINISTRATIVA
- ECONOMICA
- CONTRATTUALE
- SICUREZZA_PRIVACY
- SCADENZA

Tipi consentiti:
- ESCLUDENTE
- PREFERENZIALE
- INFORMATIVO

Impatto GO/NO-GO consentito:
- ALTO
- MEDIO
- BASSO

Per ogni requisito restituisci:
- id progressivo nel formato REQ-001, REQ-002, ...
- testo_originale: frase o passaggio originale dal documento
- requisito_normalizzato: requisito riscritto in forma chiara e operativa
- categoria
- tipo
- fonte.documento
- fonte.sezione, se individuabile
- riferimenti_normativi
- evidenze_richieste
- penale_associata, se presente
- scadenza, se presente
- impatto_go_no_go

Regole:
- Non inventare riferimenti normativi, penali o scadenze.
- Se un campo non è presente nel testo, usa null o lista vuota.
- Mantieni le evidenze brevi ma verificabili.
- Rispondi SOLO JSON valido.

Formato:

{
  "requirements": [
    {
      "id": "REQ-001",
      "testo_originale": "...",
      "requisito_normalizzato": "...",
      "categoria": "TECNICA",
      "tipo": "ESCLUDENTE",
      "fonte": {
        "documento": "...",
        "sezione": "..."
      },
      "riferimenti_normativi": ["..."],
      "evidenze_richieste": ["..."],
      "penale_associata": null,
      "scadenza": null,
      "impatto_go_no_go": "ALTO"
    }
  ]
}
"""


class GeminiRequirementExtractor:
    def __init__(self, model: str = "gemini-2.5-flash-lite"):
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
