"""Source joins and table-specific executable readbacks."""
# ruff: noqa: E402
import csv
from functools import reduce
from operator import getitem
from pathlib import Path
import sys
from time import monotonic

from calculations import OUT, WORK, Route, a, r, save, transfer
from receivers import AMP
from mea_pressure import REFERENCE
from part_ii import deviation_statistics, epcsaft, eq, reg
from phases import fixed
import public_release
import reference_states_428

TABLES = reference_states_428.BUNDLE/'results/reference-states-428'


def source_rows():
    started = monotonic()
    root = transfer.mdea.RESULTS.parent
    matched = root/'salt-anchored-435/kuranov-matched-pressure.json.gz'
    recovered = r.read(matched)
    k82 = recovered['rows']
    assert [x['row'] for x in k82]==list(range(1,83))
    row = k82[71]
    assert (row['T'],row['m_mdea'],row['m_co2'],row['p_exp'])==(393.16,3.9707,1.4826,1205300.)
    k81 = [x for x in k82 if x['row']!=72]
    for dataset in ('present','salt_anchored','Uyan','Wangler'):
        stat = deviation_statistics([(q['p_exp'],q[dataset]['pressure_Pa']) for q in k81], 'Pa')
        assert abs(stat['AARD_percent']-recovered['grouped']['design_81'][dataset]['AARD_percent'])<1e-10
    save(OUT/'H/kuranov-82nd.json',dict(row=row,doi='10.1021/ie950538r',attachment='QB5PV62N',
          locator='Table 2, printed p.1960, PDF p.2, rightmost block',printed_ten_times_p_MPa=12.053,
          matched_rows=[q['row'] for q in k81],source_model_role='comparison',input_sha256=r.s.sha256(matched),
          identification='Exact difference from the 81 retained matches; published model membership by count',
          seconds=monotonic()-started))
    start = monotonic()
    old = a.ANALYSES/'round_5/results/A/expanded-free.json.gz'
    newer = a.ANALYSES/'amp_transfer/results/salt-anchored-435/free/selection.json.gz'
    historical = r.read(old)['point']
    salt = r.read(newer)['point']
    ab = AMP.ExpandedPressure(AMP.DECLARATION,WORK/'H/hartono')
    results = {}
    for label,point in (('historical expanded free',historical),('salt expanded free',salt)):
        spec = ab.bind(point)
        selected = [row for row in spec.inputs['observations']['fitted'] if row['group']=='binary']
        assert len(selected)==52
        values = {}
        for k in ('pressure','mole_fraction'):
            rows = [spec.prediction(q) for q in selected if q['kind']==k]
            assert len(rows)==26 and all(q['status']=='Available' and q['requested_tolerance_met'] for q in rows)
            values[k] = dict(rows=rows,scores=deviation_statistics([(q['observed'],q['value']) for q in rows],rows[0]['unit']))
        assert {q['identity'] for q in values['pressure']['rows']}.isdisjoint(q['identity'] for q in values['mole_fraction']['rows'])
        results[label] = values
    save(OUT/'H/hartono-S11.json.gz',dict(seconds=monotonic()-start,results=results,round6_printed_percent=3.89,
        prior_sha256=r.s.sha256(old),salt_sha256=r.s.sha256(newer)))
    start = monotonic()
    folder = r.B/'results/same-data-comparison/hong-2027'
    statuses = {}
    from hong_2027 import pressure
    from mea_pressure import canonical
    for source in ('canonical','wagner'):
        with (folder/f'{source}.csv').open(newline='') as stream:
            for row in csv.DictReader(stream):
                if row['three_model_eligible']!='True':
                    continue
                data = dict(row)
                if source=='canonical':
                    raw = canonical()[row['record_id'].removesuffix('-pco2')]
                    data['measured_total_pressure_Pa'] = float(raw['total_pressure'])*1000 if raw['total_pressure'] else None
                try:
                    args = [float(row[k]) for k in ('analytical_loading','T_K','water_per_mea','w')]
                    answer = pressure(*args)
                    data.update(fixed_weight=answer,delta_pCO2_Pa=answer['predicted']-float(row['predicted']))
                except (ValueError,RuntimeError) as error:
                    data['refusal'] = str(error)
                statuses[row['record_id']] = data
    save(OUT/'H/hong-S31.json.gz',dict(rows=statuses,seconds=monotonic()-start,
        basis='At fixed pathway weight an equal-fugacity solve can satisfy residuals while failing the local liquid test. Calculated total pressure and source pCO2 are separate fields.'))


def cells(variant, result, comparison):
    spec = r.read(TABLES/'tables.json')[variant]
    cells = []
    for row, (label, precision, *paths) in enumerate(spec['rows']):
        for column, path in enumerate(paths):
            if not path:
                continue
            expected = reduce(getitem,path,comparison)
            refusal = result.get('refusal')
            value = None
            if not refusal:
                try:
                    value = reduce(getitem,path,result)
                except (KeyError,IndexError,TypeError):
                    refusal = 'This state has no corresponding evaluated phase or trial quantity'
            difference = value-expected if isinstance(value,(int,float)) and isinstance(expected,(int,float)) else None
            cells.append(dict(row=row,column=column,label=label,path=path,precision=precision,
                value=value,retained=expected,difference=difference,
                rounded=format(value,precision) if value is not None else None,
                published=format(expected,precision),same_rounded=value is not None and
                    format(value,precision)==format(expected,precision),refusal=refusal))
    return cells


def common_basis(record):
    for reaction in record.get('reactions',[]):
        if reaction['name'] in ('R1','R3'):
            reaction['ln_K_source'] -= reaction['molality_term']
            reaction['Gamma'] += reaction['molality_term']
    return record


def replay(package):
    start = monotonic()
    route_class = Route
    label = 'study'
    if package:
        public_release.check_public(package)
        receipt, = Path(sys.prefix,'conda-meta').glob('epcsaft-1.3.2-*.json')
        meta = r.read(receipt)
        assert meta['sha256']==r.s.sha256(package) and meta['fn']==package.name
        assert Path(epcsaft.__file__).resolve().is_relative_to(Path(sys.prefix).resolve())
        label = 'public-1.3.2'
        class PublicRoute(Route):
            def verify(self):
                public_release.check_public(package)
        route_class = PublicRoute
    else:
        a.study.reuse.bind_wheel()
        r.verify()
    folder = OUT/'H'/label
    folder.mkdir(parents=True,exist_ok=True)
    reference = REFERENCE/'F4/check-values.json'
    mea_retained = common_basis(r.read(REFERENCE/'F4/reference-state.json'))
    previous = REFERENCE/'F4/parameters.json'
    selected_path = OUT/'E/selection.json'
    selected = r.read(selected_path) if selected_path.is_file() else None
    models = [('round6',previous)]
    if selected:
        models.append(('round7',r.ROOT/selected['path']))
    results = {}
    for round_,path in models:
        outputs = results[round_] = {}
        try:
            bubble_path = folder/f'{round_}-S15.json'
            public_release.calculate_states(package,not package,params=path,reference=reference,output=bubble_path)
            outputs['S15'] = r.read(bubble_path)
        except (AttributeError,TypeError,ValueError,RuntimeError,AssertionError) as error:
            outputs['S15'] = dict(refusal=f'{type(error).__name__}: {error}')
        try:
            outputs['S17'] = reference_states_428.mea(path)
        except (AttributeError,TypeError,ValueError,RuntimeError,AssertionError) as error:
            outputs['S17'] = dict(refusal=f'{type(error).__name__}: {error}')
        save(folder/f'{round_}-S17.json.gz',outputs['S17'])
        outputs['S17_cells'] = cells('mea',common_basis(outputs['S17']),mea_retained)
    try:
        amp = reference_states_428.amp(WORK/'H'/label/'historic-AMP',route_class=route_class,
                                      allow_missing_trial_error=bool(package))
    except (AttributeError,TypeError,ValueError,RuntimeError,AssertionError,KeyError,StopIteration) as error:
        amp = dict(refusal=f'{type(error).__name__}: {error}')
    save(folder/'round6-S16.json.gz',amp)
    results['round6']['S16_cells'] = cells('amp',amp,r.read(TABLES/'amp.json'))
    amp_selection = OUT/'AMP/free/selection.json.gz'
    if amp_selection.is_file() and r.read(amp_selection)['selected']:
        endpoint = r.read(amp_selection)['selected'][2]
        c = r.read(reference_states_428.BUNDLE/'results/reference-states-428/amp.json')
        run = route_class(AMP.DECLARATION,WORK/'H'/label/'revised-AMP')
        spec = run.bind(endpoint)
        stock = {k:v for k,v in zip(c['species'],c['feed_mol'],strict=True) if v and k!='carbon-dioxide'}
        state = dict(T=c['T_K'],stock=stock,a=c['loading'])
        cell_values = None
        try:
            result = fixed(run,spec,state,c['P_Pa'],dict(pair=c['split'],witness=dict(
                support=list(range(len(c['trial']['x']))),kind='Liquid',composition=c['trial']['x'],
                packing=spec.model._model.packing_fraction_coefficient(c['T_K'],c['trial']['x'])*c['trial']['density_mol_m3'])),
                assemblages=True)
            item = run.stability_row(spec,state,1.)
            bubble = reg.predict(spec.model,item).pressure_reference
            result.update(bubble_Pa=bubble.value if bubble is not None else None,
                          AMP_wt_percent=c['AMP_wt_percent'],loading=c['loading'])
            formulas = [spec.spec['element_formulas'][k] for k in result['species']]
            pair = next((q for q in result['attempts'] if q.get('confirmed')),None)
            if pair:
                result['phases'] += [reference_states_428.phase(spec.model,c['T_K'],c['P_Pa'],n,rho,x,formulas)
                    for rho,n,x in sorted(zip(pair['densities_mol_m3'],pair['amounts_mol'],pair['phases'],strict=True))]
                result['split'] = pair
                result['Gibbs_difference_over_RT_mol'] = -pair['Gibbs_decrease_over_RT_mol']
            if trial := result.get('minimum_trial'):
                x,q = trial['composition'],trial['quantities']
                result['trial'] = reference_states_428.phase(spec.model,c['T_K'],c['P_Pa'],
                    1.,1/q['volume_m3_per_mol'],x,formulas)
                result['trial_quantities'] = q
                parent = item.problem
                parent.pressure = type(parent.pressure).fixed(c['P_Pa'])
                solved = eq.solve_equilibrium(spec.model,parent)
                if solved.requested_tolerance_met:
                    plane = eq.stability_test(eq.compile_problem(spec.model,parent),solved).plane_over_rt
                    result['plane_contraction'] = r.math.fsum(w*p for w,p in zip(x,plane,strict=True))
            evaluated = next((t for t in result.get('supplied',[]) if t.get('evidence')=='evaluated'),{})
            cell_values = dict(result,supplied=evaluated,balances=[
                x for x in (result.get('balances'),pair.get('balances') if pair else None) if x])
        except (AttributeError,TypeError,ValueError,RuntimeError,AssertionError) as error:
            result = dict(refusal=f'{type(error).__name__}: {error}')
        save(folder/'round7-S16.json.gz',result)
        results['round7']['S16_cells'] = cells('amp',cell_values or result,c)
    records = {name:{k:v for k,v in outcome.items() if k.endswith('_cells')} for name,outcome in results.items()}
    save(folder/'cells.json.gz',dict(records=records,table_spec_sha256=r.s.sha256(TABLES/'tables.json'),
          round6_mea_sha256=r.s.sha256(REFERENCE/'F4/reference-state.json'),
          round6_amp_sha256=r.s.sha256(TABLES/'amp.json')))
    save(folder/'timing.json',dict(seconds=monotonic()-start, package_sha256=r.s.sha256(package) if package else r.SHA,
                                  qualified_wheel='pending; 8078d7d1 failed #430'))


if __name__=='__main__':
    if sys.argv[1]=='sources':
        a.study.reuse.bind_wheel()
        r.verify()
        source_rows()
    else:
        replay(None if sys.argv[1]=='study' else Path(sys.argv[1]))
