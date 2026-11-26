"""Replay one declared amine fit set at its retained endpoint."""

import argparse
from importlib import import_module
from pathlib import Path
import sys

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    __package__ = "analyses.amines"

from .fit import replay_endpoint, replay_retained, save  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("amine", choices=("salt", "mea", "dea", "mdea", "amp"))
    parser.add_argument("fit_set")
    parser.add_argument("stage", choices=("replay",))
    args = parser.parse_args()
    module = import_module(f"{__package__}.{args.amine}")
    if args.fit_set not in module.FIT_SETS:
        parser.error(f"{args.amine} fit sets: {', '.join(module.FIT_SETS)}")
    declaration = module.FIT_SETS[args.fit_set]
    if args.amine == "salt":
        record = module.replay(declaration)
    elif "archive" in declaration:
        record = replay_retained(declaration)
    else:
        record = replay_endpoint(declaration)
    path = Path(__file__).resolve().parent / "results" / args.amine / args.fit_set / args.stage / "endpoint.json.gz"
    save(path, record)
    print(path)


if __name__ == "__main__":
    main()
