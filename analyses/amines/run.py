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
    parser.add_argument("stage", choices=("rows", "fit", "replay", "phase", "properties", "alternate-starts", "water-calibration", "born-sensitivity"))
    parser.add_argument("--output", type=Path, default=ROOT / "build/amine-reproduction")
    args = parser.parse_args()
    module = import_module(f"{__package__}.{args.amine}")
    if args.fit_set not in module.FIT_SETS:
        parser.error(f"{args.amine} fit sets: {', '.join(module.FIT_SETS)}")
    declaration = module.FIT_SETS[args.fit_set]
    verify()
    target = args.output.resolve() / args.amine / args.fit_set / args.stage
    name = "summary.json.gz"
    if args.stage == "alternate-starts" and args.amine in ("mea", "amp") and args.fit_set == "reported":
        record = fit.alternate_starts(declaration, target)
    elif args.fit_set == "without-binary-gap-bound" and args.amine == "mdea" and args.stage in ("fit", "phase"):
        if args.stage == "fit":
            record = fit.mdea_without_gap_bound(declaration, target)
        else:
            local = target.parent / "fit"
            point, selected = fit.retained_endpoint({"retained": local if local.exists() else declaration["retained"]})
            route = fit.route_for(declaration)
            fingerprint = dict(wheel=verify(), endpoint_fingerprint=selected["endpoint_fingerprint"])
            record = dict(module.binary_stability_search(route, point), **fingerprint)
            reactive = module.binary_stability_search(route, point, reactive=True)
            fit.save(target / "reactive-zero-loading.json.gz", dict(reactive, **fingerprint))
    elif args.amine == "mea" and args.fit_set == "reported" and args.stage == "water-calibration":
        point, selected = fit.retained_endpoint(declaration)
        record = properties.water_calibration(fit.route_for(declaration), point)
        record.update(wheel=verify(), endpoint_fingerprint=selected["endpoint_fingerprint"])
    elif args.amine == "mea" and args.fit_set == "reported" and args.stage == "born-sensitivity":
        point, selected = fit.retained_endpoint(declaration)
        record = module.born_sensitivity(fit.route_for(declaration), point)
        record.update(wheel=verify(), endpoint_fingerprint=selected["endpoint_fingerprint"])
    elif args.stage == "replay":
        name = "endpoint.json.gz"
        if args.amine == "salt":
            record = module.replay(declaration)
        elif "retained" in declaration:
            record = fit.replay_endpoint(declaration)
        else:
            record = fit.replay_retained(declaration)
            if args.amine == "amp" and args.fit_set == "first-data":
                endpoint = fit.read(declaration["endpoint"])
                if fit.fingerprint(endpoint) != record["endpoint_fingerprint"]:
                    raise ValueError("The first AMP fit does not match the replay endpoint")
                record["endpoint"] = endpoint
    elif args.amine == "salt" and args.stage in ("rows", "fit"):
        record = getattr(module, args.stage)(declaration)
    elif args.fit_set in ("water-anion-control", "common-pressure-weight") and args.stage == "fit":
        manifest = fit.control_manifest(module.FIT_SETS["reported"], declaration)
        fit.save(target / "manifest.json.gz", manifest)
        record = fit.reported_fit(declaration, manifest, target)
    elif args.fit_set in ("water-anion-control", "common-pressure-weight") and args.stage == "properties":
        local = target.parent / "fit"
        chosen = local if (local / "selection.json").is_file() else declaration["retained"]
        record = properties.control_properties(args.amine, module.FIT_SETS["reported"], declaration, chosen)
    elif args.fit_set == "water-bicarbonate-ablation" and args.stage == "fit":
        reported = module.FIT_SETS["reported"]
        if args.amine == "mdea":
            from .mea import FIT_SETS

            manifest = fit.control_manifest(reported, declaration,
                                            bicarbonate_donor=FIT_SETS["water-bicarbonate-ablation"]["retained"])
        else:
            manifest = fit.move_manifest(args.amine, reported, args.output.resolve(), ablation=True)
        fit.save(target / "manifest.json.gz", manifest)
        record = fit.reported_fit(reported | declaration, manifest, target)
    elif args.fit_set == "water-bicarbonate-ablation" and args.stage == "properties":
        reported = module.FIT_SETS["reported"]
        local = target.parent / "fit"
        chosen = local if (local / "selection.json").is_file() else declaration["retained"]
        point, selected = fit.retained_endpoint(reported | {"retained": chosen})
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
    elif "fit_from" in declaration:
        if args.stage == "fit":
            source = module.FIT_SETS[declaration["fit_from"]]
            manifest = fit.pressure_fit_manifest(declaration, source, module.FIT_SETS["reported"])
            fit.save(target / "manifest.json.gz", manifest)
            record = fit.reported_fit(declaration, manifest, target)
        elif args.stage in ("phase", "properties"):
            local = target.parent / "fit"
            chosen = local if (local / "selection.json").is_file() else declaration["retained"]
            point, selection = fit.retained_endpoint({"retained": chosen})
            route = fit.route_for(declaration)
            if args.stage == "properties":
                attempt = fit.read(chosen / f'{selection["selected"]}.json.gz')
                record = properties.property_rows(route, point, attempt["replay"]["rows"])
            else:
                record = phase.fresh_searches(args.amine, route, point, target)
            record.update(wheel=verify(), endpoint_fingerprint=selection["endpoint_fingerprint"])
        else:
            parser.error("This pressure fit set supports fit, phase and properties")
    elif args.stage in ("alternate-starts", "water-calibration", "born-sensitivity") or "retained" not in declaration or (args.amine == "mdea" and args.fit_set != "reported"):
        parser.error("This fit set is replayed on the locked wheel")
    elif args.stage == "rows":
        record = fit.rows(declaration, fit.manifest(declaration))
    elif args.stage == "fit":
        if args.amine == "mdea":
            manifest = fit.mdea_weighted_manifest(declaration, module.FIT_SETS["without-binary-gap-bound"])
        elif "preserved" in declaration:
            manifest = fit.move_manifest(args.amine, declaration, args.output.resolve())
        else:
            manifest = fit.reported_manifest(args.amine, declaration, args.output.resolve())
        fit.save(target / "manifest.json.gz", manifest)
        record = fit.reported_fit(declaration, manifest, target)
    else:
        fresh = target.parent / "fit"
        chosen = fresh if (fresh / "selection.json").is_file() else declaration["retained"]
        point, selection = fit.retained_endpoint(declaration | {"retained": chosen})
        route = fit.route_for(declaration)
        if args.stage == "phase":
            if "preserved" in declaration or args.amine == "mdea":
                record = phase.fresh_searches(args.amine, route, point, target)
                if args.amine == "mdea":
                    for reactive, name_ in ((False, "binary-neutral"), (True, "reactive-zero-loading")):
                        search = module.binary_stability_search(route, point, reactive=reactive)
                        search.update(wheel=verify(), endpoint_fingerprint=selection["endpoint_fingerprint"])
                        fit.save(target / f"{name_}.json.gz", search)
                    fit.save(target / "binary-gap.json.gz", module.binary_gap(point))
                    worked = module.loaded_split_state(route, point)
                    worked.update(wheel=verify(), endpoint_fingerprint=selection["endpoint_fingerprint"])
                    fit.save(target / "loaded-split-state.json.gz", worked)
                first = args.output.resolve() / "amp/first-data/phase/supplied.json.gz"
                if not first.is_file():
                    first = declaration["retained"].parents[1] / "first-data/phase/supplied.json.gz"
                if args.amine == "amp":
                    fit.save(target / "measured-controls.json.gz", phase.amp_measured_controls(route, point, fit.read(first)))
            else:
                record = phase.reported_searches(args.amine, args.fit_set, route, point, target)
        else:
            record = properties.property_rows(route, point)
            record.update(properties.reported_curves(args.amine, route, point))
            if "preserved" in declaration or args.amine == "mdea":
                fit.save(target / "derivatives.json.gz", properties.reported_derivatives(args.amine, route, point))
            if args.amine == "dea" and "preserved" in declaration:
                fit.save(target / "lawson-methane.json.gz", module.lawson_methane(route, point))
            if args.amine == "mdea":
                record.update(module.move_property_cases(route, point))
            if args.amine == "mea" and "preserved" in declaration:
                selected = fit.read(chosen / f'{selection["selected"]}.json.gz')
                for family, result in module.display_properties(route, point, selected).items():
                    fit.save(target / f"{family}.json.gz", result)
                module.write_reported_property_summary(fit_folder=chosen, output=target / "uncertainty-and-activities.json.gz")
        record.update(wheel=verify(), endpoint_fingerprint=selection["endpoint_fingerprint"])
    path = target / name
    fit.save(path, record)
    print(path)


if __name__ == "__main__":
    main()
