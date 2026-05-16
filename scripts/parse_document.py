import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

import argparse
from pathlib import Path

from document_parsing.tika_parser import TikaParser
from document_parsing.llm_parser import LLMParser


PARSERS = {
    "tika": TikaParser,
    "llm": LLMParser,
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse tender documents.")
    parser.add_argument("path", type=Path, help="Path to PDF/DOCX document")
    parser.add_argument(
        "--parser",
        choices=PARSERS.keys(),
        default="tika",
        help="Parser backend to use",
    )

    args = parser.parse_args()

    selected_parser = PARSERS[args.parser]()
    result = selected_parser.parse(args.path)

    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
