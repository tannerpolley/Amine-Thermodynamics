"""Check the pinned Engine declaration for parameter-dependent Merkley endpoints.

No fitting and no outside-fit evaluation. Uses the declared item-(l) starts.
"""
import concurrent.futures
import importlib.util
import inspect
import multiprocessing
from pathlib import Path
import sys
import zipfile

AN = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('stage2', AN/'scripts/stage2.py')
s = importlib.util.module_from_spec(spec)
sys.modules['stage2'] = s
spec.loader.exec_module(s)
OUT = 'results/stage2-density'


def saturation_row(row):
    r = dict(row, pressure_MPa=str(float(row['proposed_pressure_kPa'])/1000))
    result = s.saturation(r)
    lp = next(float(q['alpha_LP_mol_CO2_per_mol_MDEA'])
              for q in s.j.rows('Merkley1987_loading_points.csv')
              if q['temperature_K'] == row['temperature_K']
              and q['MDEA_mass_percent'] == row['MDEA_mass_percent'])
    result.update(row=row, alpha_LP=lp)
    if result['status'] == 'Available' and result['sign_changes'] == 1:
        alpha = min(lp, result['alpha_sat'])
        result.update(alpha_endpoint=alpha, truncation_mol_CO2_per_mol_MDEA=lp-alpha)
        T, P = float(row['temperature_K']), float(row['proposed_pressure_kPa'])*1000
        nw = s.j.water(float(row['MDEA_mass_percent'])/100)
        item = s.reg.addition_enthalpy(s.params, s.j.problem(T,P,nw,0.),
            s.j.problem(T,P,nw,alpha), {s.j.C:1.}, alpha,T,P,phase='vapor',
            observed=float(row['heat_kJ_mol_CO2'])*1000,form='difference',scale=3000.)
        pred = s.reg.predict(s.model,item)
        result.update(heat_status=pred.status.name, heat_J_mol_CO2=pred.value if pred.status.name=='Available' else None)
    return result


def main():
    runtime = s.load('inputs/runtime.json')
    wheel = Path(runtime['wheel'])
    assert s.p.sha(wheel) == runtime['wheel_sha256'] == s.p.shared.ENGINE_WHEEL_SHA256
    with zipfile.ZipFile(wheel) as z:
        for name in z.namelist():
            if name.startswith('epcsaft/') and not name.endswith('/'):
                assert z.read(name) == (Path(s.p.epcsaft.__file__).parent.parent/name).read_bytes()
    source = Path(s.reg.__file__)
    output = dict(runtime=runtime, installed_files_byte_identical=True,
        regression_sha256=s.p.sha(source), workers=16, BLAS_threads_per_process=1,
        fit_signature=str(inspect.signature(s.reg.fit)),
        addition_enthalpy_signature=str(inspect.signature(s.reg.addition_enthalpy)),
        observation_members=[x for x in dir(s.reg.Observation()) if not x.startswith('_')],
        observation_kinds=list(s.reg.ObservationKind.__members__),
        rows=[])
    rows = [r for r in s.j.rows('Merkley1987_stage1.csv')
            if float(r['MDEA_mass_percent'])<=40 and float(r['temperature_K']) in (333.15,388.71)]
    for label in ('A1','B1'):
        doc = s.load(f'results/item-l/amended-starts/{label}.json')
        s.setup(doc)
        with concurrent.futures.ProcessPoolExecutor(max_workers=min(16,len(rows)),
                mp_context=multiprocessing.get_context('fork')) as pool:
            records = list(pool.map(saturation_row,rows))
        output['rows'].extend(dict(r,start=label) for r in records)
        try:
            prob = s.j.problem(388.71,1121000.,s.j.water(.4),.36)
            prob.feed = s.eq.Amounts({s.j.W:s.j.water(.4),s.j.M:1.,s.j.C:s.eq.Free(.36)})
            s.reg.observation(s.params,'pressure',prob,observed=1121000.,form='log_ratio')
        except Exception as e:
            output['free_feed_refusal'] = f'{type(e).__name__}: {e}'
        print(label,[(r['row']['temperature_K'],r['row']['MDEA_mass_percent'],r.get('alpha_sat'),r.get('truncation_mol_CO2_per_mol_MDEA')) for r in records],flush=True)
    output['conclusion'] = ('Pinned native addition_enthalpy accepts fixed endpoint feeds and a fixed feed_amount. '
        'No saturation-capped observation or callback is exposed. Free CO2 feed is refused. '
        'The requested parameter-dependent cap cannot be passed to reg.fit through these declarations.')
    s.p.write(f'{OUT}/merkley-fit-capability.json',output)


if __name__ == '__main__':
    main()
