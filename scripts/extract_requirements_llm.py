import argparse
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from requirement_extraction.llm_extractor import GeminiRequirementExtractor


def main() -> None:
    cli = argparse.ArgumentParser()
    cli.add_argument("parsed_json", type=Path)
    cli.add_argument("--output-dir", type=Path, default=Path("outputs/requirements"))
    cli.add_argument("--max-docs", type=int, default=1)
    cli.add_argument("--max-chars", type=int, default=15000)

    args = cli.parse_args()

    parsed_data = json.loads(args.parsed_json.read_text(encoding="utf-8"))
    tender_id = args.parsed_json.stem

    extractor = GeminiRequirementExtractor()
    all_requirements = []

    docs = [doc for doc in parsed_data if doc.get("text")][: args.max_docs]

    for doc in docs:
        source = Path(doc["source_path"]).name
        text = doc["text"][: args.max_chars]

        print(f"Estrazione requisiti da: {source}")
        print(f"Caratteri inviati al modello: {len(text)}")

        prompt_text = f"""
TENDER_ID: {tender_id}
SOURCE_DOCUMENT: {source}

TESTO DOCUMENTO:
{text}
"""

        result = extractor.extract(prompt_text)
        requirements = result.get("requirements", [])

        for req in requirements:
            req["source_document"] = source

        all_requirements.extend(requirements)

    final_result = {
        "tender_id": tender_id,
        "requirements": all_requirements,
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    output_path = args.output_dir / f"{tender_id}_requirements_llm.json"

    output_path.write_text(
        json.dumps(final_result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print()
    print(f"Requisiti estratti: {len(all_requirements)}")
    print(f"Output scritto in: {output_path}")


if __name__ == "__main__":
    main()
