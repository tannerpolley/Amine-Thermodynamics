"""#243: probe both initialized cation-B fitted sets; retain #242 diagnosis separately."""
import copy, json, math
from pathlib import Path
import epcsaft
from epcsaft import equilibrium as eq, regression as reg
from pinned_engine import SHA256
from MEA.solvent_specification import SolventSpecification, jsonable
AN, out, H = Path(__file__).resolve().parent, dict(wheel_sha256=SHA256), 'protonated-aminomethylpropanol'
for run in ('redesign-1-B-fixed-1', 'redesign-2-B-fixed-1'):
    spec = SolventSpecification(AN / f'{run}.toml', parameter='start')
    def shifted(dk):  # same start document with AMPH+-CO2 k moved by dk
        doc = copy.deepcopy(spec.inputs['start'])
        next(p for p in doc['pairs'] if {p['component_id_a'], p['component_id_b']} == {H, 'carbon-dioxide'})['coefficients'][0]['value']['magnitude'] += dk
        return epcsaft.Mixture(epcsaft.Parameters.from_mapping(doc), thermochemistry=spec.thermal)
    for r in [r for r in spec.inputs['observations']['fitted'] if r['identity'] in ('hartono-2021:0', 'hartono-2021:14', 'hartono-2021:31', 'hartono-2021:46')]:
        state, p = eq.solve_equilibrium(spec.model, spec.problems[r['problem']]), spec.prediction(r)
        x, y = (dict(zip(spec.model.component_ids, state.mole_fractions[9 * i:9 * i + 9])) for i in (0, 1))
        lnP = [math.log(reg.predict(shifted(dk), spec.observation(r)).value) for dk in (-0.05, 0.05)]
        out[f"{run}:{r['identity']}"] = dict(P_calc=p.get('value'), status=p['status'], branch=p.get('branch'), stable_root_count=p.get('stable_root_count'), success=state.success,
            packing_fractions=list(state.packing_fractions), CO2_share=y['carbon-dioxide'], liquid=x, dlnP_dk_central=(lnP[1] - lnP[0]) / 0.1)
(AN / 'results/redesign/probe-cation-b.json').write_text(json.dumps(jsonable(out), indent=1, default=float) + '\n')
