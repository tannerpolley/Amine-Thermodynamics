"""Run a stage of a declared amine fit set."""

import argparse
from importlib import import_module
from pathlib import Path
import sys

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    __package__ = "analyses.amines"

from . import fit, phase, properties  # noqa: E402
from .records import ROOT  # noqa: E402
from .wheel import verify  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("amine", choices=("salt", "mea", "dea", "mdea", "amp"))
    parser.add_argument("fit_set")
    parser.add_argument("stage", choices=("rows", "fit", "replay", "phase", "properties"))
    parser.add_argument("--output", type=Path, default=ROOT / "build/amine-reproduction")
    args = parser.parse_args()
    module = import_module(f"{__package__}.{args.amine}")
    if args.fit_set not in module.FIT_SETS:
        parser.error(f"{args.amine} fit sets: {', '.join(module.FIT_SETS)}")
    declaration = module.FIT_SETS[args.fit_set]
    verify()
    target = args.output.resolve() / args.amine / args.fit_set / args.stage
    name = "summary.json.gz"
    if args.stage == "replay":
        name = "endpoint.json.gz"
        if args.amine == "salt":
            record = module.replay(declaration)
        elif "archive" in declaration:
            record = fit.replay_retained(declaration)
        else:
            record = fit.replay_endpoint(declaration)
    elif args.amine == "salt" and args.stage in ("rows", "fit"):
        record = getattr(module, args.stage)(declaration)
    elif args.fit_set == "water-bicarbonate-ablation" and args.stage == "fit":
        reported = module.FIT_SETS["reported"]
        manifest = fit.move_manifest(args.amine, reported, args.output.resolve(), ablation=True)
        fit.save(target / "manifest.json.gz", manifest)
        record = fit.reported_fit(reported | declaration, manifest, target)
    elif args.fit_set == "water-bicarbonate-ablation" and args.stage == "properties":
        reported = module.FIT_SETS["reported"]
        point, selected = fit.retained_endpoint(reported | {"retained": target.parent / "fit"})
        spec = fit.route_for(declaration).bind(point)
        if args.amine == "mea":
            rows = module.ablation_pressures(spec)
        else:
            from .model import evaluate

            source = spec.inputs["observations"]
            rows = {group: evaluate(spec, [row for row in source[role] if row["group"] == group])
                    for group, role in (("Kuranov", "fitted"), ("Ermatchkov", "comparisons"), ("Carson", "fitted"))}
        record = dict(wheel=verify(), endpoint_fingerprint=selected["endpoint_fingerprint"], rows=rows)
    elif args.amine == "amp" and args.fit_set == "first-data" and args.stage == "phase":
        point = fit.read(declaration["endpoint"])
        route = fit.route_for(declaration)
        record = phase.fresh_searches(args.amine, route, point, target)
    elif "retained" not in declaration or (args.amine == "mdea" and args.fit_set != "reported"):
        parser.error("This fit set is replayed on the locked wheel")
    elif args.stage == "rows":
        record = fit.rows(declaration, fit.manifest(declaration))
    elif args.stage == "fit":
        held = fit.read(declaration["retained"] / "manifest.json.gz")
        if held["wheel"] != verify():
            manifest = fit.move_manifest(args.amine, declaration, args.output.resolve())
        else:
            manifest = fit.reported_manifest(args.amine, declaration, args.output.resolve())
        fit.save(target / "manifest.json.gz", manifest)
        record = fit.reported_fit(declaration, manifest, target)
    else:
        fresh = target.parent / "fit"
        point, selection = fit.retained_endpoint(
            declaration | {"retained": fresh} if (fresh / "selection.json").is_file() else declaration)
        route = fit.route_for(declaration)
        if args.stage == "phase":
            if (fresh / "selection.json").is_file():
                record = phase.fresh_searches(args.amine, route, point, target)
            else:
                record = phase.reported_searches(args.amine, args.fit_set, route, point, target)
        else:
            record = properties.property_rows(route, point)
            record.update(properties.reported_curves(args.amine, route, point))
        record.update(wheel=verify(), endpoint_fingerprint=selection["endpoint_fingerprint"])
    path = target / name
    fit.save(path, record)
    print(path)


if __name__ == "__main__":
    main()
