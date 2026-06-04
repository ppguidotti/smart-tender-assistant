"""LLM prompt and JSON schema for participation-requirement extraction.

Carried over verbatim from the validated Colab notebook (``tca_1_2.py``). Kept
as a versioned artifact (``EXTRACTION_PROMPT_VERSION``) for reproducibility, as
required by ``docs/block_architecture.md`` §B2.

NOTE (scope): this prompt extracts *participation requirements only* and
explicitly skips technical service characteristics. It therefore does not, on
its own, reproduce the TECNICA (SKU) items of VEM's Modulo 1 — broadening the
scope is a separate B2 tuning task.
"""

from __future__ import annotations

EXTRACTION_PROMPT_VERSION = "1.2"

# JSON schema the LLM must conform to (OpenAI ``json_schema`` response format).
LLM_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "requisiti_partecipazione": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "categoria": {
                        "type": "string",
                        "enum": [
                            "economico_finanziario",
                            "tecnico_professionale",
                            "certificazione",
                            "legale",
                            "idoneita_professionale",
                            "esperienza",
                            "altro",
                        ],
                    },
                    "tipo": {"type": "string"},
                    "descrizione": {"type": "string"},
                    "valore": {"type": ["number", "null"]},
                    "unita": {"type": ["string", "null"]},
                    "obbligatorio": {"type": "boolean"},
                    "fonte_testuale": {"type": "string"},
                    "confidenza": {
                        "type": "string",
                        "enum": ["alta", "media", "bassa"],
                    },
                },
                "required": [
                    "categoria",
                    "tipo",
                    "descrizione",
                    "valore",
                    "unita",
                    "obbligatorio",
                    "fonte_testuale",
                    "confidenza",
                ],
                "additionalProperties": False,
            },
        }
    },
    "required": ["requisiti_partecipazione"],
    "additionalProperties": False,
}

LLM_PROMPT = """
Sei un esperto nell'analisi di bandi di gara pubblici.

Il tuo compito è estrarre esclusivamente i requisiti di partecipazione degli operatori economici presenti nel documento.

Definizione di requisito di partecipazione: un requisito di partecipazione è una condizione che l'operatore economico deve possedere per poter partecipare alla procedura di gara.

Sono esempi di requisiti di partecipazione:
- requisiti economico-finanziari;
- requisiti tecnico-professionali;
- requisiti di esperienza pregressa;
- iscrizioni ad albi, registri o camere di commercio;
- certificazioni obbligatorie;
- requisiti legali e di ordine generale;
- autorizzazioni, qualificazioni o abilitazioni richieste.

Informazioni da NON estrarre:
- criteri di valutazione delle offerte;
- elementi premianti;
- requisiti relativi all'esecuzione del contratto;
- obblighi dell'aggiudicatario successivi all'aggiudicazione;
- caratteristiche tecniche del servizio o della fornitura;
- modalità di presentazione dell'offerta;
- cauzioni, garanzie o adempimenti amministrativi non configurabili come requisiti di partecipazione;
- informazioni generali sulla procedura.

Regole di estrazione
- Completezza: estrai tutti i requisiti di partecipazione presenti nel testo.
- Atomicità: se una frase contiene più requisiti distinti, separali in elementi diversi. Esempio: "Fatturato minimo di 500.000 euro e possesso della certificazione ISO 9001" deve produrre due requisiti distinti.
- Deduplicazione: Non creare requisiti duplicati. Se lo stesso requisito compare più volte nel documento: estrailo una sola volta; conserva la formulazione più completa e precisa; evita duplicati dovuti a parafrasi o formulazioni leggermente diverse.
- Normalizzazione: la descrizione deve essere sintetica ma completa. Evita di copiare interi paragrafi.

Mantieni:
- soggetto del requisito;
- eventuali soglie;
- eventuali vincoli temporali;
- eventuali riferimenti essenziali.

Valore numerico
Quando è presente una soglia numerica chiaramente identificabile:
- inseriscila nel campo valore;
- inserisci l'unità di misura nel campo unita.
Esempi:
- 500000 euro → valore = 500000, unita = "EUR"
- 3 anni → valore = 3, unita = "anni"

Se il requisito non contiene una soglia numerica chiara, imposta valore e unita a null.

Obbligatorietà
Imposta obbligatorio=true quando il testo indica che il requisito deve essere posseduto per partecipare.
Imposta obbligatorio=false solo se il requisito è esplicitamente facoltativo o alternativo.

Confidenza
- alta: il testo identifica chiaramente un requisito di partecipazione;
- media: il requisito è probabile ma non completamente esplicito;
- bassa: il requisito è ambiguo o inferito indirettamente.

Fonte testuale
Riporta il passaggio testuale più breve possibile che giustifica l'estrazione del requisito.

Classificazione
Classifica ogni requisito in una delle seguenti categorie:
- economico_finanziario
- tecnico_professionale
- certificazione
- legale
- idoneita_professionale
- esperienza
- altro

Documento da analizzare:

"""
