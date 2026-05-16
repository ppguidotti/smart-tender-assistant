import argparse
import json
from pathlib import Path


def main() -> None:
    cli = argparse.ArgumentParser(
        description="Riassume l'esito del parsing di una gara."
    )
    cli.add_argument("parsed_json", type=Path)

    args = cli.parse_args()

    data = json.loads(args.parsed_json.read_text(encoding="utf-8"))

    total = len(data)
    ok = [doc for doc in data if doc.get("text")]
    failed = [doc for doc in data if doc.get("error")]

    print(f"Documenti totali: {total}")
    print(f"Parsing riusciti: {len(ok)}")
    print(f"Parsing falliti: {len(failed)}")
    print()

    print("## Dettaglio documenti")
    for doc in data:
        path = Path(doc["source_path"])
        text = doc.get("text", "")
        error = doc.get("error")

        print(f"- {path.name}")
        print(f"  caratteri estratti: {len(text)}")
        if error:
            print(f"  errore: {error}")

    print()

    total_chars = sum(len(doc.get("text", "")) for doc in data)
    print(f"Totale caratteri estratti: {total_chars}")


if __name__ == "__main__":
    main()
