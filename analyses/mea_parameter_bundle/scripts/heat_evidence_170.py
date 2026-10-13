"""Heat, fixed density translation and heat-capacity assessment (#170/#179)."""
import concurrent.futures as cf
import csv
import json
import math
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
import numpy as np
import epcsaft
from epcsaft import equilibrium as eq
import shared_evaluation as s
import verify_reference_calorics as vrc
import verify_temperature_reference as vt
import verify_solution_heat_capacity as hc
from fit_observations import heat_items, predict, load

BUNDLE = Path(__file__).resolve().parents[1]
ROOT = BUNDLE.parents[1]
ORIGINAL = BUNDLE / 'results/density-cp-160'
IDS = load(ORIGINAL / 'D1-evidence/F1-A/native-fit.json')['coordinates']
SCALES = [.01, .01, .01, .01, 10.]
IONS = ('protonated-monoethanolamine', 'carbamate-anion')
HILLIARD = ((318.15, 0., 3.7195), (318.15, .358, 3.3675), (353.15, .358, 3.4707))


def table(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, list(dict.fromkeys(k for r in rows for k in r)), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def conditional(raw):
    import refit
    ids, scales = raw['coordinates'], raw.get('scales', SCALES)
    active = [ids.index(i) if isinstance(i,str) else i for i in raw['active_bounds']]
    proxy = SimpleNamespace(physical=raw['physical'], covariance=SimpleNamespace(active_bounds=active))
    return refit.identifiability(proxy, np.array(raw['optimizer_jacobian']).reshape(len(raw['targets']),len(ids))/np.array(scales),
        np.array(raw['weighted_residuals']), ids, [-.5,-.5,-.5,-1.,-1000.], [.5,.5,.5,1.,1000.])


def select(campaign_dir, problem):
    directory = Path(campaign_dir) / problem
    aa, bb = [load(directory / letter / 'native-fit.json') for letter in 'AB']
    assert all(r['selection_eligible'] for r in (aa,bb)), f'{problem}: incomplete fit'
    relative = abs(aa['final_cost']-bb['final_cost'])/max(abs(aa['final_cost']),abs(bb['final_cost']),1e-300)
    letter = 'A' if problem=='F1' or aa['final_cost'] <= bb['final_cost'] else 'B'
    return dict(problem=problem, start=letter, relative_start_cost_difference=relative,
        starts_agree=relative<=1e-6, cost_A=aa['final_cost'], cost_B=bb['final_cost'],
        parameters=str(directory/letter/'parameters.json'), fit=str(directory/letter/'native-fit.json'))


def request(mapping, T, loading, density=False):
    template = next(o['request'] for o in s.load_state_packet()['observations'] if o['identity']=='Bottinger2008_state_046')
    req = s.source_feed_request(template, dict(source_key='Amundsen2009', CO2_loading=loading,
        temperature_reported_C=T-273.15, MEA_weight_fraction=.30))
    if loading < .0001:
        system = req['reaction_system']
        analytical = system['analytical_feed_contract']['neutral_analytical_amounts_mol']
        # Scale only the balanced numerical seeds for the absorber's unloaded trace proxy.
        system['feed_amounts_mol'] = [a + .01*(v-a) for a,v in zip(analytical,system['feed_amounts_mol'],strict=True)]
        system.pop('analytical_feed_contract')
        req['feed'] = dict(generation='density-cp-160', basis='30 wt% CO2-free solvent',
                           proxy_loading=loading, numerical_seed_scale=.01)
    req = vt.request_at(req, T, 101325., liquid_only=True)
    if density:
        req['outputs'] = [dict(identity='phase-density', selector='phase.density',
            phase_identity=req['phases'][0]['identity'], unit='kilogram / meter ** 3')]
    return s.corrected_request(req, s.reaction_values(mapping))

def cp_check(mapping, T, loading, observed):
    model = epcsaft.Mixture(epcsaft.Parameters.from_mapping(mapping), thermochemistry=vrc.record())
    problem = s._problem_from_request(request(mapping,T,max(loading,1e-5)))
    result = eq.solve_equilibrium(model, problem)
    if not result.success:
        raise RuntimeError(result.message)
    mass = sum(problem.feed.values.get(c,0.)*m for c,m in zip(s.COMPONENT_IDS,hc.MOLAR_MASS))/1000
    (h, dh), (n, dn) = vrc.first_actions(model, problem, result, [vrc.observable('PhaseProperty',0,
        prop=epcsaft.PropertyObservable.TotalEnthalpy),vrc.observable('PhaseAmount',0)],[(1.,0.,None)])[0]
    ((cp,_),) = vrc.first_actions(model, problem, result, [vrc.observable('PhaseProperty',0,
        prop=epcsaft.PropertyObservable.TotalIsobaricHeatCapacity)],[(0.,0.,None)])[0]
    equilibrium_cp = (n*dh+h*dn)/mass/1000
    return dict(T_K=T, loading=loading, model_loading=max(loading,1e-5), observed_kJ_kg_K=observed, equilibrium_cp_kJ_kg_K=equilibrium_cp,
                deviation_percent=100*(equilibrium_cp/observed-1), frozen_cp_kJ_kg_K=cp*n/mass/1000)

def density_job(mapping, source):
    T = float(source['temperature_C']) + 273.15
    alpha = float(source['co2_loading_mol_per_mol_mea'])
    w = float(source['mea_mass_fraction'])
    req = request(mapping, T, alpha, density=True)
    coordinates = dict(source_key='Amundsen2009', MEA_weight_fraction=w, CO2_loading=alpha,
                       temperature_reported_C=T-273.15)
    req = s.source_feed_request(req, coordinates)
    req = s.corrected_request(req, s.reaction_values(mapping))
    model = epcsaft.Mixture(epcsaft.Parameters.from_mapping(mapping))
    problem = s._problem_from_request(req)
    result = eq.solve_equilibrium(model, problem)
    assert result.success, result.message
    record = s._snapshot_from_result(model, problem, req, result)
    assert record['status']=='evaluated', record['failure_code']
    phase = record['phases'][0]
    x = np.array(phase['mole_fractions'])
    masses = np.array(req['reaction_system']['molar_masses_kg_per_mol'])
    mass = float(x @ masses)
    v = 1. / phase['molar_density_mol_m3']
    ion_x = float(x[s.COMPONENT_IDS.index(IONS[0])] + x[s.COMPONENT_IDS.index(IONS[1])])
    return dict(temperature_K=T, loading=alpha, mea_mass_fraction=w, observed_kg_m3=1000*float(source['value']),
                eos_molar_volume_m3_mol=v, mixture_molar_mass_kg_mol=mass, ion_mole_fraction_sum=ion_x,
                eos_density_kg_m3=mass/v, mole_fractions=x.tolist(), solved_state=record,
                source_locator=source['source_locator'], uncertainty_scope=source['uncertainty_scope'])

def corrected(rows, c):
    result = []
    for r in rows:
        v = r['eos_molar_volume_m3_mol'] + c*1e-6*r['ion_mole_fraction_sum']
        assert v > 0
        rho = r['mixture_molar_mass_kg_mol']/v
        result.append({k:v for k,v in r.items() if k not in ('solved_state', 'mole_fractions')} |
                      dict(corrected_density_kg_m3=rho, corrected_deviation_percent=100*(rho/r['observed_kg_m3']-1),
                           eos_deviation_percent=100*(r['eos_density_kg_m3']/r['observed_kg_m3']-1)))
    return result

def evidence(choices, pool, output_dir, vinjarapu):
    output_dir = Path(output_dir)
    import final_evidence as ef
    evaluation = output_dir / 'evaluation'
    evaluation.mkdir(parents=True, exist_ok=True)
    selected = {p:dict(record=v['parameters'], raw=v['fit']) for p,v in choices.items()}
    selected['F1-no-heat'] = dict(record=str(ORIGINAL/'D1-evidence/F1-double-prime-candidate-parameters.json'),
        raw=str(ORIGINAL/'D1-evidence/F1-A/native-fit.json'))
    packet, groups = ef.observations()
    jobs, excluded = [], []
    for problem, item in selected.items():
        ef.binding(problem,item['record'])
        mask = set(load(item['raw'])['targets'])
        use = groups if problem in ('F1','F2','F6','F1-no-heat') else {'packet':[{**o,'targets':[t for t in o['targets'] if t['identity'] in mask]}
            for o in packet if any(t['identity'] in mask for t in o['targets'])]}
        s.write_json(evaluation/f'{problem}-mask.json', {k:[o['identity'] for o in vv] for k,vv in use.items()})
        for kind, observations in use.items():
            for o in observations:
                T = o['request']['temperature']['value']
                outside_domain = ef.probe.reaction_domain_status(o) if problem!='F6' else None
                if outside_domain or not 293.15<=T<=393.15:
                    excluded.append(dict(problem=problem,kind=kind,identity=o['identity'],temperature_K=T,reason='outside declared reaction domain'))
                else:
                    jobs.append((problem,item['record'],kind,o))
    futures = [pool.submit(ef.job, *job, output_dir=output_dir) for job in jobs]
    records = [f.result()[0] for f in cf.as_completed(futures)]
    records.sort(key=lambda r:(r['problem'], r['kind'], r['identity']))
    with (evaluation/'states.jsonl').open('w') as output:
        for r in records:
            output.write(json.dumps(s._jsonable(r))+'\n')
    ef.summarize(records, [], selected, excluded, output_dir=output_dir, heat_rows=vinjarapu)
    return ef

def decomposition(choices, output_dir):
    directory = output_dir/'activity-contributions'
    directory.mkdir(parents=True, exist_ok=True)
    (directory/'runs').mkdir(exist_ok=True)
    reference = load(BUNDLE/'results/final-rerun/activity-contributions/inputs.json')
    born_reference_path = BUNDLE/'model-d/activity-contributions/inputs.json'
    born_reference = load(born_reference_path)['N6_by_record_sha256']
    inputs = {k:reference[k] for k in ('c2_reference_temperature_K','cohorts','state_count','state_ids','target_count','target_ids')}
    inputs.update(status='Issue 170 heat comparison: 149 base targets',
                  packet=str(BUNDLE/'results/source-corrections-152/state-packet.json.gz'), sha256={},
                  N1_expected_costs={k:load(choices[p]['fit'])['final_cost'] for k,p in (('adopted','F1'),('off-refit','F3'))},
                  N6_by_record_sha256={}, records={}, states={}, evaluation_paths={})
    records = [load(p) for p in sorted((output_dir/'evaluation/states').rglob('*.json'))]
    arguments = []
    for name, problem in (('adopted','F1'),('original','F2'),('off-refit','F3')):
        path = Path(choices[problem]['parameters'])
        inputs['records'][name] = str(path.resolve())
        state_path = directory/'runs'/f'{name}-states.jsonl'
        with state_path.open('w') as output:
            for r in records:
                if r['problem']==problem and r['kind']=='packet' and r['identity'] in inputs['state_ids']:
                    output.write(json.dumps(r)+'\n')
        inputs['states'][name] = str(state_path)
        replay = output_dir/'evaluation'/f'{problem}-replay.json'
        inputs['evaluation_paths'][name] = str(replay)
        if problem != 'F3':
            reference_hash = ('9055458d8b7cd767a0d08e9f37e4fd28631e29c363364d7b842ebade645cb241'
                              if problem=='F1' else 'ebb5f8f9df2aa4ff9bbaec72899dae33fba2233823bb7e389bef92b3d2981900')
            inputs['N6_by_record_sha256'][s.sha256(path)] = born_reference[reference_hash]
        arguments += [name,str(path)]
    inputs['N6_reference_provenance'] = dict(path=str(born_reference_path),sha256=s.sha256(born_reference_path),
        rationale='Separate retained salt-free SSM+DS and original-Born references; Born inputs unchanged. Not fitted to current output.')
    for path in [Path(inputs['packet']), *map(Path, inputs['records'].values()), *map(Path, inputs['states'].values()), *map(Path, inputs['evaluation_paths'].values())]:
        inputs['sha256'][str(path)] = s.sha256(path)
    config = directory/'inputs.json'
    s.write_json(config, inputs)
    env = dict(os.environ, ACTIVITY_OUTPUT=str(directory), ACTIVITY_INPUTS=str(config))
    with (directory/'execution.log').open('w') as log:
        subprocess.run([sys.executable,str(BUNDLE/'model-d/activity-contributions/activity_contributions.py'),'calculate',*arguments],
                       cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT, check=True)

def summarize_fits(campaign_dir, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    choices = {p: select(campaign_dir, p) for p in [f"F{i}" for i in range(1, 7)]}
    assert all(r["starts_agree"] for r in choices.values()), choices
    s.write_json(output_dir / "fit-summary.json", list(choices.values()))
    uncertainty = {p: conditional(load(r['fit'])) for p, r in choices.items()}
    s.write_json(output_dir / "conditional-uncertainty.json", uncertainty)
    se = []
    corr = []
    rows = []
    old = ORIGINAL / "D1-evidence"
    for label in ("no heat", "with heat"):
        for p in choices:
            if label == "no heat":
                choice = next(r for r in load(old / "fit-summary.json") if r["problem"] == p)
                raw = load(old / f"{p}-{choice['start']}/native-fit.json")
            else:
                raw = load(choices[p]["fit"])
            row = dict(problem=p, objective=label, targets=len(raw["targets"]), cost=raw["final_cost"])
            for group, mask in [
                ("pressure", [i for i, t in enumerate(raw["targets"]) if t.endswith("-pco2")]),
                (
                    "species",
                    [
                        i
                        for i, t in enumerate(raw["targets"])
                        if not t.endswith("-pco2") and not t.startswith("vinjarapu")
                    ],
                ),
                ("Bottinger", [i for i, t in enumerate(raw["targets"]) if t.startswith("Bottinger")]),
                ("Matin", [i for i, t in enumerate(raw["targets"]) if t.startswith("Matin")]),
                ("heat", [i for i, t in enumerate(raw["targets"]) if t.startswith("vinjarapu")]),
            ]:
                row[group + "_n"] = len(mask)
                row[group + "_cost"] = math.fsum(0.5 * raw["weighted_residuals"][i] ** 2 for i in mask)
                row[group + "_AARD_percent"] = (
                    100 * math.fsum(abs(raw["predictions"][i] / raw["observed"][i] - 1) for i in mask) / len(mask)
                    if mask
                    else None
                )
            assert abs(row["pressure_cost"] + row["species_cost"] + row["heat_cost"] - row["cost"]) < 1e-8
            row.update(dict(zip(IDS, raw["physical"], strict=True)))
            row["active_bounds"] = (
                ";".join(raw["active_bounds"])
                if raw["active_bounds"] and isinstance(raw["active_bounds"][0], str)
                else ";".join(IDS[i] for i in raw["active_bounds"])
            )
            rows.append(row)
    for p, value in uncertainty.items():
        for coordinate, error in value["conditional_standard_error"].items():
            se.append(dict(problem=p, coordinate=coordinate, conditional_standard_error=error))
        for i, c1 in enumerate(value["free_coordinates"]):
            for j, c2 in enumerate(value["free_coordinates"]):
                corr.append(
                    dict(
                        problem=p,
                        coordinate1=c1,
                        coordinate2=c2,
                        conditional_correlation=value["conditional_correlation"][i][j],
                    )
                )
    table(output_dir / "fit-comparison.csv", rows)
    table(output_dir / "conditional-standard-errors.csv", se)
    table(output_dir / "conditional-correlations.csv", corr)
    s.write_json(output_dir / "inputs.json", load(Path(campaign_dir) / 'inputs.json'))
    print("FIT SUMMARY", [(r["problem"], r["cost_A"], r["cost_B"]) for r in choices.values()])


def main(output_dir, selected_record, no_heat_record, vinjarapu, arcis):
    output_dir = Path(output_dir)
    choices = {r["problem"]: r for r in load(output_dir / "fit-summary.json")}
    current = s.parameter_mapping(Path(selected_record))
    original = s.parameter_mapping(Path(no_heat_record))
    assert current["empirical_density_correction"] == original["empirical_density_correction"]
    c = current["empirical_density_correction"]["c_cm3_mol"]
    sources = [
        r
        for r in csv.DictReader(
            (ROOT / "data/reference/MEA/observations/density_viscosity/Amundsen_2009_density_viscosity.csv").open()
        )
        if r["property"] == "density" and r["co2_loading_mol_per_mol_mea"]
    ]
    values = [density_job(current, r) for r in sources]
    s.write_json(output_dir / "density-states.json", values)
    table(output_dir / "corrected-densities.csv", corrected(values, c))
    cp = [
        dict(record=label, **cp_check(mapping, T, a, observed))
        for label, mapping in [("heat F1", current), ("no-heat F1", original)]
        for T, a, observed in HILLIARD
    ]
    table(output_dir / "heat-capacity-comparison.csv", cp)
    rows = []
    for label, mapping in [("heat F1", current), ("no-heat F1", original)]:
        params = epcsaft.Parameters.from_mapping(mapping)
        for source, sources in [("Vinjarapu2024", vinjarapu), ("Arcis2011", arcis)]:
            predictions = predict(mapping, heat_items(mapping, params, sources, request(mapping, 313.15, .11)))
            for r, y in zip(sources, predictions, strict=True):
                rows.append(
                    dict(
                        record=label,
                        source=source,
                        record_id=r["record_id"],
                        temperature_K=r["temperature_K"],
                        pressure_Pa=r["system_pressure_Pa"],
                        loading=r["alpha_final"],
                        observed_J_mol=r["observed_addition_enthalpy_J_per_mol_CO2"],
                        predicted_J_mol=y.value,
                        scaled_residual=y.residual,
                        scale_J_mol=r["uH_J_per_mol_CO2"],
                        residual_J_mol=y.value - r["observed_addition_enthalpy_J_per_mol_CO2"],
                        role="fitted" if source == "Vinjarapu2024" and label == "heat F1" else "predicted",
                        parameter_sha256=s.sha256(
                            Path(selected_record if label == "heat F1" else no_heat_record)
                        ),
                    )
                )
    table(output_dir / "figure-data/heat.csv", rows)
    heatstats = []
    for label in ["heat F1", "no-heat F1"]:
        for source, pressure in [
            ("Vinjarapu2024", None),
            ("Arcis2011", None),
            ("Arcis2011", 510000),
            ("Arcis2011", 1030000),
        ]:
            part = [
                r
                for r in rows
                if r["record"] == label and r["source"] == source and (pressure is None or r["pressure_Pa"] == pressure)
            ]
            heatstats.append(
                dict(
                    record=label,
                    source=source,
                    pressure_Pa=pressure,
                    n=len(part),
                    RMSE_kJ_mol=math.sqrt(math.fsum(r["residual_J_mol"] ** 2 for r in part) / len(part)) / 1000,
                    bias_kJ_mol=math.fsum(r["residual_J_mol"] for r in part) / len(part) / 1000,
                    minimum_predicted_kJ_mol=min(r["predicted_J_mol"] for r in part) / 1000,
                    maximum_predicted_kJ_mol=max(r["predicted_J_mol"] for r in part) / 1000,
                    heat_cost=math.fsum(0.5 * r["scaled_residual"] ** 2 for r in part),
                )
            )
    table(output_dir / "heat-comparison.csv", heatstats)
    new = list(csv.DictReader((output_dir / "evaluation/targets.csv").open()))
    old = [dict(r, problem="F1") for r in new if r["problem"] == "F1-no-heat"]
    comparisons = []
    for kind, label in [("packet", "Hilliard/Jou packet pressures"), ("canonical", "canonical pressures")]:
        for T in [40, 60, 80, 100, 120, None]:
            part = {
                name: [
                    r
                    for r in data
                    if r["problem"] == "F1"
                    and r["kind"] == kind
                    and r["quantity"] == "pressure"
                    and (
                        T is None
                        or min([40, 60, 80, 100, 120], key=lambda t: abs(float(r["temperature_K"]) - 273.15 - t)) == T
                    )
                ]
                for name, data in [("no heat", old), ("with heat", new)]
            }
            assert {(r["identity"], r["target"]) for r in part["no heat"]} == {
                (r["identity"], r["target"]) for r in part["with heat"]
            }
            if not part["no heat"]:
                continue
            comparisons.append(
                dict(
                    cohort=label,
                    nominal_temperature_C=T,
                    n=len(part["no heat"]),
                    **{
                        name.replace(" ", "_") + "_AARD_percent": 100
                        * math.fsum(abs(float(r["predicted"]) / float(r["observed"]) - 1) for r in values)
                        / len(values)
                        for name, values in part.items()
                    },
                )
            )
    table(output_dir / "high-temperature-comparison.csv", comparisons)
    # Preserve model-generation tables for the current notebook; no added fitting.
    for filename, mask in [
        ("pressure-figure-data.csv", lambda r: r["kind"] == "packet" and r["quantity"] == "pressure"),
        ("species-figure-data.csv", lambda r: r["kind"] == "packet" and r["quantity"] == "species"),
        ("pool-figure-data.csv", lambda r: r["kind"] == "packet" and r["problem"] in ("F1", "F2", "F4", "F5")),
    ]:
        table(output_dir / filename, [r for r in new if mask(r)])
    decomposition(choices, output_dir)
    figures = output_dir / "figure-data"
    s.write_json(
        figures / "input-hashes.json", {str(p.relative_to(output_dir)): s.sha256(p) for p in figures.glob("*.csv")}
    )
    print("POST EVIDENCE", len(values), "density states", len(rows), "heat values", flush=True)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('operation', choices=('summarize','evidence','present','assess'))
    parser.add_argument('--campaign', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--selected-record', type=Path, required=True)
    parser.add_argument('--no-heat-record', type=Path, required=True)
    parser.add_argument('--heat-rows', type=Path, required=True)
    args = parser.parse_args()
    rows = load(args.heat_rows)
    vinjarapu = [r for r in rows if r['record_id'].startswith('vinjarapu')]
    arcis = [r for r in rows if not r['record_id'].startswith('vinjarapu')]
    if args.operation == 'summarize':
        summarize_fits(args.campaign, args.output)
    elif args.operation == 'evidence':
        choices = {r['problem']:r for r in load(args.output/'fit-summary.json')}
        with cf.ProcessPoolExecutor() as pool:
            evidence(choices, pool, args.output, vinjarapu)
    elif args.operation == 'present':
        import final_evidence as ef
        ef.present(output_dir=args.output, heat_rows=vinjarapu, campaign_dir=args.campaign)
    else:
        main(args.output, args.selected_record, args.no_heat_record, vinjarapu, arcis)
