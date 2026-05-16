import argparse
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from document_parsing.tika_parser import TikaParser


SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".doc", ".xlsx", ".xml"}


def parse_tender_folder(tender_dir: Path, output_dir: Path) -> None:
    parser = TikaParser()

    files = sorted(
        p for p in tender_dir.rglob("*")
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
    )

    output_dir.mkdir(parents=True, exist_ok=True)

    results = []

    for file_path in files:
        print(f"Parsing: {file_path}")

        try:
            parsed = parser.parse(file_path)
            results.append(parsed.model_dump())
        except Exception as exc:
            results.append({
                "source_path": str(file_path),
                "parser": "tika",
                "text": "",
                "metadata": {},
                "error": str(exc),
            })

    output_path = output_dir / f"{tender_dir.name}.json"

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print()
    print(f"Documenti analizzati: {len(results)}")
    print(f"Output scritto in: {output_path}")


def main() -> None:
    cli = argparse.ArgumentParser(
        description="Esegue il parsing di tutti i documenti supportati in una cartella gara."
    )
    cli.add_argument("tender_dir", type=Path, help="Cartella della gara da analizzare")
    cli.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs/parsed_tenders"),
        help="Cartella in cui salvare il JSON di output",
    )

    args = cli.parse_args()

    if not args.tender_dir.exists():
        raise FileNotFoundError(f"Cartella non trovata: {args.tender_dir}")

    parse_tender_folder(args.tender_dir, args.output_dir)


if __name__ == "__main__":
    main()
