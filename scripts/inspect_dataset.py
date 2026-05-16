from collections import Counter
from pathlib import Path


SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".doc", ".xlsx", ".xml"}


def inspect_dataset(root: Path) -> None:
    tender_dirs = sorted([p for p in root.iterdir() if p.is_dir()])

    print(f"Gare trovate: {len(tender_dirs)}")
    print()

    global_extensions = Counter()

    for tender_dir in tender_dirs:
        files = [p for p in tender_dir.rglob("*") if p.is_file()]
        extensions = Counter(p.suffix.lower() for p in files)

        global_extensions.update(extensions)

        supported = [
            p for p in files
            if p.suffix.lower() in SUPPORTED_EXTENSIONS
        ]

        print(f"## {tender_dir.name}")
        print(f"File totali: {len(files)}")
        print(f"File supportati inizialmente: {len(supported)}")
        print("Estensioni:")
        for ext, count in sorted(extensions.items()):
            label = ext if ext else "[senza estensione]"
            print(f"  - {label}: {count}")
        print()

    print("## Estensioni globali")
    for ext, count in sorted(global_extensions.items()):
        label = ext if ext else "[senza estensione]"
        print(f"- {label}: {count}")


def main() -> None:
    root = Path("data/raw/bandi_gara_pubblici")

    if not root.exists():
        raise FileNotFoundError(f"Cartella non trovata: {root}")

    inspect_dataset(root)


if __name__ == "__main__":
    main()
