"""Stage the retained #430 records for the display-only preservation check."""

import argparse
import json
from hashlib import sha256
from pathlib import Path
from shutil import copyfile

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "analyses/amines/sources.json"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", nargs="?", type=Path, default=ROOT / "tmp/issue-430-display-records")
    args = parser.parse_args()
    catalog = json.loads(SOURCES.read_text())
    for source, entry in catalog.items():
        if "record" not in entry or entry["disposition"] in {"orphan", "stage"}:
            continue
        original = ROOT / source
        if sha256(original.read_bytes()).hexdigest() != entry["sha256"]:
            raise ValueError(f"Changed retained input: {source}")
        target = args.destination / entry["record"]
        target.parent.mkdir(parents=True, exist_ok=True)
        copyfile(original, target)


if __name__ == "__main__":
    main()
