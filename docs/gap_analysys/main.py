import json
import os
from pathlib import Path
import re
from dotenv import load_dotenv
from openai import OpenAI
import ast
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from datetime import datetime
import time
from neo4j import GraphDatabase
load_dotenv()

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_BASE_URL = os.getenv("AZURE_OPENAI_BASE_URL")
AZURE_OPENAI_MODEL = os.getenv("AZURE_OPENAI_MODEL")

client = OpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    base_url=AZURE_OPENAI_BASE_URL,
    timeout=200.0,
    max_retries=0
)
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_COLLECTION_COMPETENZE = os.getenv("QDRANT_COLLECTION_COMPETENZE", "portfolio_competenze")
QDRANT_COLLECTION_REFERENZE = os.getenv("QDRANT_COLLECTION_REFERENZE", "portfolio_referenze")
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password123")

neo4j_driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USER, NEO4J_PASSWORD)
)

qdrant_client = QdrantClient(url=QDRANT_URL)
embedding_model = SentenceTransformer(EMBEDDING_MODEL)

MODEL = os.getenv("AZURE_OPENAI_MODEL")
PROMPT = """
Sei un assistente per la gap analysis di un singolo requisito di gara.

Riceverai un JSON con:
- requirement: il requisito da valutare
- retrieved_company_evidence.qdrant: evidenze semantiche recuperate da Qdrant
- retrieved_company_evidence.knowledge_graph: evidenze strutturate recuperate da Neo4j

Obiettivo:
Valutare se la knowledge base contiene evidenze sufficienti per coprire il requisito.

Non devi decidere GO/NO-GO.
Non devi stabilire se l’azienda possiede davvero il requisito.
Devi solo valutare se le evidenze disponibili nella knowledge base sono sufficienti.

Valori ammessi per coverage_status:
- covered
- partially_covered
- not_covered
- unknown

Regole obbligatorie:
- Usa solo il JSON ricevuto.
- Non inventare certificazioni, albi, autorizzazioni, partnership, esperienze, documenti o competenze non presenti nelle evidenze.
- Le evidenze del Knowledge Graph sono più forti quando contengono dati strutturati espliciti: certificazioni, albi, partecipazioni a gare, requisiti storici, gap storici.
- Le evidenze Qdrant sono utili per competenze tecniche, esperienze e referenze semanticamente vicine.
- Se Qdrant e Knowledge Graph danno segnali diversi, privilegia l’evidenza più specifica, strutturata e documentata.
- Usa covered solo se le evidenze coprono chiaramente e direttamente il requisito.
- Usa partially_covered solo se le evidenze riguardano lo stesso tema del requisito ma mancano dettagli specifici.
- Usa not_covered solo se nelle evidenze è scritto esplicitamente che il requisito non è soddisfatto, è assente, è scaduto, è revocato o non posseduto. La semplice mancanza di evidenze deve essere classificata come unknown, mai come not_covered.
- Usa unknown se non ci sono evidenze pertinenti oppure se le evidenze sono generiche, deboli o relative a un tema diverso.
- Usa not_covered solo se le evidenze dimostrano esplicitamente che il requisito non è soddisfatto.
- Non scrivere mai “l’azienda non dispone di...” se manca una prova esplicita.
- In caso di mancanza dati, scrivi: “non sono presenti evidenze sufficienti nella knowledge base”.
- Un requisito amministrativo o documentale, come sopralluogo, PEC, polizza, CCNL, DURC, DGUE, firma digitale o garanzia, non è parzialmente coperto da evidenze tecniche ICT generiche.
- Per requisiti mandatory con status partially_covered, unknown o not_covered, descrivi il gap in modo sintetico.

Restituisci solo JSON valido, senza markdown, nel formato:
{
  "requirement_id": "string",
  "coverage_status": "covered | partially_covered | not_covered | unknown",
  "gap_description": "string"
}
""".strip()
def inspect_neo4j_schema():
    with neo4j_driver.session() as session:
        labels = session.run("""
            MATCH (n)
            RETURN labels(n) AS labels, count(n) AS count
            ORDER BY count DESC
        """).data()

        relationships = session.run("""
            MATCH ()-[r]->()
            RETURN type(r) AS type, count(r) AS count
            ORDER BY count DESC
        """).data()

        sample_nodes = session.run("""
            MATCH (n)
            RETURN labels(n) AS labels, properties(n) AS properties
            LIMIT 10
        """).data()

    print("LABELS:")
    print(json.dumps(labels, ensure_ascii=False, indent=2))

    print("RELATIONSHIPS:")
    print(json.dumps(relationships, ensure_ascii=False, indent=2))

    print("SAMPLE NODES:")
    print(json.dumps(sample_nodes, ensure_ascii=False, indent=2))
    
def load_json(path: str):
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"File non trovato: {path}")

    text = file_path.read_text(encoding="utf-8").strip()

    # Caso 1: JSON valido
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Caso 2: literal Python valido:
    # apici singoli, None, True, False
    try:
        return ast.literal_eval(text)
    except Exception as e:
        raise ValueError(
            "Il file non è né JSON valido né un literal Python valido. "
            "Controlla apici, parentesi, virgole, None/True/False oppure null/true/false."
        ) from e



def save_json(path: str, data: dict):
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def save_text(path: str, text: str):
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)


def normalize_text(text) -> str:
    if text is None:
        return ""

    if not isinstance(text, str):
        text = str(text)

    text = text.lower()
    text = text.replace("/", " ")
    text = text.replace("-", " ")
    text = re.sub(r"[^\w\sàèéìòù]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()




def truncate_text(text, max_chars=500) -> str:
    if text is None:
        return ""

    if not isinstance(text, str):
        text = json.dumps(text, ensure_ascii=False)

    if len(text) <= max_chars:
        return text

    return text[:max_chars].strip() + "..."

def normalize_requirement_type(req: dict) -> str:
    if "obbligatorio" in req:
        return "mandatory" if req.get("obbligatorio") is True else "optional"

    raw_type = req.get("type") or req.get("tipo")

    if not raw_type:
        return "unknown"

    value = str(raw_type).strip().lower()

    mapping = {
        "escludente": "mandatory",
        "mandatory": "mandatory",
        "obbligatorio": "mandatory",
        "obbligatoria": "mandatory",

        "preferenziale": "rewarding",
        "premiale": "rewarding",
        "rewarding": "rewarding",

        "informativo": "informative",
        "informativa": "informative",
        "informative": "informative",

        "optional": "optional",
        "opzionale": "optional"
    }

    return mapping.get(value, "unknown")

def create_embedding(text: str) -> list[float]:
    vector = embedding_model.encode(text, normalize_embeddings=True)
    return vector.tolist()

def qdrant_vector_search(requirement_text: str, top_k: int = 2) -> list[dict]:
    query_vector = create_embedding(requirement_text)

    collections = [
        QDRANT_COLLECTION_COMPETENZE,
        QDRANT_COLLECTION_REFERENZE
    ]

    results = []

    for collection_name in collections:
        search_result = qdrant_client.query_points(
            collection_name=collection_name,
            query=query_vector,
            limit=top_k,
            with_payload=True
        )

        for point in search_result.points:
            payload = point.payload or {}
            print("Qdrant:", collection_name, point.id, round(point.score, 3))
            text = (
                payload.get("testo_vettorializzato")
                or payload.get("text")
                or payload.get("descrizione")
                or payload.get("contenuto")
                or payload.get("content")
                or payload.get("page_content")
                or payload.get("testo")
                or str(payload)
            )

            results.append({
                "item_type": "qdrant_result",
                "collection": collection_name,
                "id": str(point.id),
                "title": (
                    payload.get("nome_competenza")
                    or payload.get("oggetto_progetto")
                    or payload.get("titolo")
                    or payload.get("title")
                    or payload.get("nome")
                    or payload.get("tipo")
                    or ""
                ),
                "text": truncate_text(text, max_chars=700),
                "source": (
                    payload.get("fonte_dati")
                    or payload.get("nome_cliente")
                    or payload.get("source")
                    or payload.get("document")
                    or payload.get("file")
                    or payload.get("fonte")
                    or ""
                ),
                "score": point.score,
                "payload": payload
            })

    results = sorted(results, key=lambda x: x["score"], reverse=True)
    return results[:top_k]

def is_requirement_dict(item: dict) -> bool:
    """
    Riconosce un singolo requisito.
    """
    if not isinstance(item, dict):
        return False

    return any(
        key in item
        for key in [
            "descrizione",
            "text",
            "testo_originale",
            "fonte_testuale",
            "categoria",
            "tipo",
            "obbligatorio"
        ]
    )
def get_structured_company_kg() -> dict:
    with neo4j_driver.session() as session:
        azienda = session.run("""
            MATCH (a:Azienda)
            RETURN properties(a) AS azienda
            LIMIT 1
        """).data()

        certificazioni = session.run("""
            MATCH (a:Azienda)-[:POSSIEDE_CERTIFICAZIONE]->(c:Certificazione)
            RETURN properties(c) AS certificazione
            ORDER BY c.nome
        """).data()

        albi = session.run("""
            MATCH (a:Azienda)-[:ISCRITTA_A]->(albo:Albo)
            RETURN properties(albo) AS albo
            ORDER BY albo.nome
        """).data()

        gare = session.run("""
            MATCH (a:Azienda)-[:HA_PARTECIPATO_A]->(g:Gara)
            RETURN properties(g) AS gara
        """).data()

        requisiti_storici = session.run("""
            MATCH (g:Gara)-[:RICHIEDE_REQUISITO]->(r:RequisitoGara)
            RETURN properties(g) AS gara, properties(r) AS requisito
        """).data()

        gap_storici = session.run("""
            MATCH (g:Gara)-[:HA_RILEVATO_GAP]->(gap:GapRilevato)
            RETURN properties(g) AS gara, properties(gap) AS gap
        """).data()

    return {
        "azienda": azienda[0]["azienda"] if azienda else None,
        "certificazioni": [x["certificazione"] for x in certificazioni],
        "albi": [x["albo"] for x in albi],
        "gare": [x["gara"] for x in gare],
        "requisiti_storici": requisiti_storici,
        "gap_storici": gap_storici
    }

def extract_raw_requirements(requirements_json) -> list[dict]:
    """
    Estrae una lista piatta di requisiti:
    - requisiti_partecipazione
    - document + requirements
    - lista di documenti con requirements
    - lista diretta di requisiti
    """

    if isinstance(requirements_json, dict):

        if "tender" in requirements_json:
            tender = requirements_json.get("tender", {})
            if isinstance(tender.get("requirements"), list):
                return tender["requirements"]

        if isinstance(requirements_json.get("requisiti_partecipazione"), list):
            return requirements_json["requisiti_partecipazione"]

        if "document" in requirements_json and isinstance(requirements_json.get("requirements"), list):
            document_name = requirements_json.get("document", "unknown_document")
            extracted = []

            for req in requirements_json.get("requirements", []):
                if isinstance(req, dict):
                    req_copy = dict(req)
                    req_copy["source_document"] = document_name
                    extracted.append(req_copy)

            return extracted

        if isinstance(requirements_json.get("requirements"), list):
            return requirements_json["requirements"]

        if is_requirement_dict(requirements_json):
            return [requirements_json]

    if isinstance(requirements_json, list):
        extracted = []

        for index, item in enumerate(requirements_json):
            if not isinstance(item, dict):
                raise ValueError(
                    f"L’elemento in posizione {index} della lista non è un oggetto JSON"
                )

            # Nuovo caso: lista diretta di requisiti
            if is_requirement_dict(item) and not isinstance(item.get("requirements"), list):
                extracted.append(item)
                continue

            # Vecchio caso: lista di documenti con requirements
            document_name = item.get("document", f"unknown_document_{index + 1}")
            requirements = item.get("requirements", [])

            if not isinstance(requirements, list):
                raise ValueError(
                    f"Nel documento {document_name} il campo 'requirements' non è una lista"
                )

            for req in requirements:
                if not isinstance(req, dict):
                    continue

                req_copy = dict(req)
                req_copy["source_document"] = document_name
                extracted.append(req_copy)

        return extracted

    raise ValueError(
        "Formato input non riconosciuto. "
        "Attesi: tender.requirements, requisiti_partecipazione, "
        "document + requirements, lista di documenti con requirements, "
        "oppure lista diretta di requisiti."
    )
def tokenize(text: str) -> list[str]:
    stopwords = {
        "deve", "devono", "essere", "avere", "con", "per", "del", "della",
        "dello", "dei", "degli", "delle", "alla", "allo", "alle", "agli",
        "nel", "nella", "nelle", "negli", "un", "una", "uno", "il", "lo",
        "la", "i", "gli", "le", "di", "a", "da", "in", "su", "che", "e",
        "o", "al", "ai", "come", "entro", "relativo", "relativa",
        "concorrente", "fornitore", "appalto", "bando", "gara",
        "categoria", "informatica", "software", "pubblici", "dati",
        "attività", "tecniche", "risoluzione", "conformità", "garantire",
        "contratto", "servizio", "servizi", "pacchetti", "sicurezza"
    }

    normalized = normalize_text(text)

    return [
        word
        for word in normalized.split()
        if len(word) > 3 and word not in stopwords
    ]
def normalize_gap_statuses(gap_analysis: dict) -> dict:
    for item in gap_analysis.get("requirement_gap_analysis", []):
        status = item.get("coverage_status")
        description = item.get("gap_description", "").lower()

        weak_phrases = [
            "non specificano",
            "non specifica",
            "non dimostrano",
            "non dimostra",
            "non forniscono",
            "non fornisce",
            "non sono presenti evidenze sufficienti",
            "non chiaramente",
            "non specificano chiaramente",
            "ma non specificano",
            "ma non dimostrano",
            "ma non forniscono"
        ]

        if status == "partially_covered" and any(p in description for p in weak_phrases):
            item["coverage_status"] = "unknown"

    return gap_analysis

def get_requirements(requirements_json) -> list[dict]:
    raw_requirements = extract_raw_requirements(requirements_json)

    valid_requirements = []

    for index, req in enumerate(raw_requirements):
        if not isinstance(req, dict):
            raise ValueError(f"Il requisito in posizione {index} non è un oggetto JSON")

        text = (
            req.get("text")
            or req.get("descrizione")
            or req.get("testo_originale")
            or req.get("fonte_testuale")
        )

        if text is None or str(text).strip() == "":
            raise ValueError(
                f"Il requisito in posizione {index} non ha testo valido. "
                "Campi accettati: text, descrizione, testo_originale, fonte_testuale."
            )

        valid_requirements.append({
    "id": req.get("id", f"REQ_{index + 1:03d}"),
    "text": str(text),

    "type": normalize_requirement_type(req),

    # campi da propagare nell’output finale
    "categoria": req.get("categoria") or req.get("category") or "unknown",
    "tipo": req.get("tipo") or req.get("type") or "unknown",
    "obbligatorio": bool(req.get("obbligatorio", False)),

    
    "category": normalize_text(
        req.get("category")
        or req.get("categoria")
        or "unknown"
    ),
    "original_type": req.get("tipo"),
    "source": req.get("source") or req.get("fonte_testuale"),
    "source_document": req.get("source_document"),
    "confidence": req.get("confidenza"),
    "value": req.get("valore"),
    "unit": req.get("unita")
         })

    return valid_requirements


def stringify_value(value) -> str:
    if value is None:
        return ""

    if isinstance(value, (str, int, float, bool)):
        return str(value)

    if isinstance(value, list):
        return " ".join(stringify_value(v) for v in value)

    if isinstance(value, dict):
        return " ".join(
            f"{k} {stringify_value(v)}"
            for k, v in value.items()
        )

    return str(value)


def kg_record_to_text(record: dict) -> str:
    labels = " ".join(record.get("labels", []))
    properties = stringify_value(record.get("properties", {}))
    related = stringify_value(record.get("related", []))

    return f"{labels} {properties} {related}"


def load_neo4j_records() -> list[dict]:
    with neo4j_driver.session() as session:
        records = session.run("""
            MATCH (n)
            OPTIONAL MATCH (n)-[r]-(m)
            RETURN
                elementId(n) AS node_id,
                labels(n) AS labels,
                properties(n) AS properties,
                collect({
                    relationship: type(r),
                    related_labels: labels(m),
                    related_properties: properties(m)
                })[0..5] AS related
        """).data()

    return records


def search_neo4j_evidence(requirement_text: str, top_k: int = 3) -> list[dict]:
    requirement_tokens = set(tokenize(requirement_text))

    if not requirement_tokens:
        return []

    records = load_neo4j_records()

    scored = []

    for record in records:
        record_text = normalize_text(kg_record_to_text(record))
        matched_terms = [
            token
            for token in requirement_tokens
            if token in record_text
        ]

        score = len(matched_terms)

        if score > 0:
            scored.append({
                "item_type": "neo4j_kg_result",
                "id": record.get("node_id"),
                "labels": record.get("labels", []),
                "properties": record.get("properties", {}),
                "related": record.get("related", []),
                "matched_terms": matched_terms[:10],
                "kg_score": score
            })

    scored = sorted(scored, key=lambda x: x["kg_score"], reverse=True)

    return scored[:top_k]



def test_azure_connection():
    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "user", "content": "Rispondi solo con: ok"}
        ],
        temperature=0,
        max_tokens=10
    )

    print(completion.choices[0].message.content)
    


def extract_json_from_model_output(raw_output: str) -> dict:
    """
    Prova a convertire l’output del modello in JSON.
    Serve nel caso in cui il modello restituisca testo sporco.
    """

    try:
        return json.loads(raw_output)
    except json.JSONDecodeError:
        pass

    start = raw_output.find("{")
    end = raw_output.rfind("}")

    if start == -1 or end == -1 or end <= start:
        raise ValueError("Il modello non ha restituito un JSON valido")

    cleaned = raw_output[start:end + 1]

    return json.loads(cleaned)

def build_single_requirement_context(req: dict) -> dict:
    qdrant_matches = qdrant_vector_search(
        requirement_text=req["text"],
        top_k=2
    )

    kg_token_matches = search_neo4j_evidence(
        requirement_text=req["text"],
        top_k=3
    )

    kg_structured = get_structured_company_kg()

    return {
        "requirement": req,
        "retrieved_company_evidence": {
            "qdrant": qdrant_matches,
            "knowledge_graph": {
                "structured_company_data": kg_structured,
                "token_matches": kg_token_matches
            }
        }
    }
def enrich_result_with_requirement_metadata(req: dict, result: dict) -> dict:
    result["categoria"] = req.get("categoria")
    result["tipo"] = req.get("tipo")
    result["obbligatorio"] = req.get("obbligatorio")

    return result

def analyze_single_requirement(single_context: dict) -> dict:
    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": PROMPT},
            {"role": "user", "content": json.dumps(single_context, ensure_ascii=False)}
        ],
        temperature=0,
        max_tokens=500
    )

    raw_output = completion.choices[0].message.content

    return extract_json_from_model_output(raw_output)

def build_final_gap_analysis(results: list[dict]) -> dict:
    covered = sum(1 for x in results if x.get("coverage_status") == "covered")
    partial = sum(1 for x in results if x.get("coverage_status") == "partially_covered")
    not_covered = sum(1 for x in results if x.get("coverage_status") == "not_covered")
    unknown = sum(1 for x in results if x.get("coverage_status") == "unknown")

    total = len(results)

    if total == 0:
        overall_gap_level = "high"
    elif not_covered > 0 or unknown >= total * 0.5:
        overall_gap_level = "high"
    elif partial > 0 or unknown > 0:
        overall_gap_level = "medium"
    else:
        overall_gap_level = "low"

    return {
        "analysis_type": "gap_analysis",
        "summary": (
            f"Analisi completata su {total} requisiti. "
            f"Coperti: {covered}; parzialmente coperti: {partial}; "
            f"non coperti: {not_covered}; unknown: {unknown}."
        ),
        "overall_gap_level": overall_gap_level,
        "total_requirements": total,
        "covered_count": covered,
        "partially_covered_count": partial,
        "not_covered_count": not_covered,
        "unknown_count": unknown,
        "requirement_gap_analysis": results
    }

def run_gap_analysis():
    requirements_json = load_json("input/requirements.json")
    requirements = get_requirements(requirements_json)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    total = len(requirements)
    print(f"Requisiti trovati: {total}")

    all_results = []
    all_contexts = []

    for index, req in enumerate(requirements, start=1):
        print(f"\nAnalizzo requisito {index}/{total}: {req['id']}")
        time.sleep(20)

        single_context = build_single_requirement_context(req)
        all_contexts.append(single_context)

        try:
            result = analyze_single_requirement(single_context)

            result = normalize_gap_statuses({
                "requirement_gap_analysis": [result]
            })["requirement_gap_analysis"][0]

        except Exception as e:
            print(f"Errore sul requisito {req['id']}:")
            print(type(e).__name__, e)
            save_json(
                  f"output/error_context_{req['id']}.json",
                   single_context
                )
            result = {
                "requirement_id": req["id"],
                "coverage_status": "unknown",
                "gap_description": (
    "Non sono presenti evidenze sufficienti nella knowledge base per dimostrare "
    "la copertura esplicita di questo requisito."
)
            }
        result = enrich_result_with_requirement_metadata(req, result)
        all_results.append(result)

        print("Risultato:", result)


    final_analysis = build_final_gap_analysis(all_results)

    save_json(f"output/gap_analysis_{timestamp}.json", final_analysis)
    save_json(f"output/retrieved_contexts_{timestamp}.json", all_contexts)

    print("\nAnalisi completata.")
    print(f"File salvato: output/gap_analysis_{timestamp}.json")
    print(json.dumps(final_analysis, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    run_gap_analysis()

