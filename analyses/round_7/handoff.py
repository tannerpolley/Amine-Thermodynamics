"""Recompute the numerical handoff from retained calculation records."""
import argparse
import gzip
import hashlib
import json
import math
from pathlib import Path
from collections import Counter

from comparisons import CANONICAL_VLE, MDEA_RESULTS, MDEA_SALT, mdea_deviations, off_window_population

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE/'results'
REF = ROOT/'analyses/mea_parameter_bundle/results/salt-anchored-435/MEA'
WHEEL = 'c9fbf898b14d004f915f01ed77675867908dd30d77dc28544b2860e9195c80bb'
PUBLIC_PACKAGE = '3945ef7b5ad038196c64055daf194c380be0c86275ccb2ae2625a8229d760a31'
TOLERANCE = REF.parents[1]/'engine-3e83e19c-refit-chain/a6/spec.json'
DEA_COMPARISON = ROOT/'analyses/dea_transfer/results/salt-anchored-435/campaign/data-rows.json.gz'
GROUPS = (
    ('fitted CO2 partial pressure','common149','PartialPressure','aard'),
    ('Kiepe pressure','Kiepe',None,'aard'),
    ('fitted phase mole fraction','common149','PhaseMoleFraction','aard'),
    ('restored species','restored species',None,'aard'),
    ('Jakobsen ratio','Jakobsen',None,'aard'),
    ('loaded density','loaded density',None,'scaled'),
    ('CO2-free density','CO2-free density',None,'scaled'),
    ('fitted heat of absorption','common149','AdditionEnthalpy','scaled'),
    ('heat capacity','Cp',None,'scaled'),
)


def load(path):
    return json.loads(gzip.decompress(path.read_bytes()) if path.suffix=='.gz' else path.read_bytes())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, data):
    path.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')


def gates(rows, reference):
    assert len(rows)==len(reference)==307
    assert [(x['identity'],x['group'],x['row']) for x in rows]==[
        (x['identity'],x['group'],x['row']) for x in reference]
    def metrics(population, group, kind):
        selected = [x for x in population if x['group']==group and
                    (kind is None or (x['row'].get('quantity') or x['row'].get('kind'))==kind)]
        score = scores(selected)
        return (score['AARD_percent'],sum(abs(x['residual'])<=2 for x in selected),
                math.sqrt(math.fsum((x['value']-x['observed'])**2 for x in selected)/len(selected)))
    checks = {}
    for name,group,kind,rule in GROUPS:
        aard,within,rmse = metrics(rows,group,kind)
        base_aard,base_within,base_rmse = metrics(reference,group,kind)
        checks[name] = (aard-base_aard<=2 if rule=='aard' else
                        within>=base_within and aard<=1.25*base_aard and rmse<=1.25*base_rmse)
    return checks


def measured_rows(label):
    return [x for p in sorted((OUT/f'E/{label}/measured').glob('*.json.gz')) for x in load(p)]


def effective_measured(label):
    original = measured_rows(label)
    refined = {q['identity']:q for p in sorted((OUT/f'E/{label}/measured-refined').glob('*.json.gz'))
               for q in load(p)}
    index = {q['identity']:q for q in original}
    assert refined.keys()<=index.keys()
    assert all(not index[k]['available'] and q['P_Pa']==index[k]['P_Pa'] for k,q in refined.items())
    index.update(refined)
    return list(index.values())


def measured_failures(row):
    parent = row.get('parent')
    if not parent:
        return [row.get('cause','Parent data unavailable')]
    P, tolerance = row['realized_Pa'], row['row_tolerance']
    checks = {
        'phase pressure closure': any(abs(p['pressure_residual_Pa'])/P>tolerance for p in parent['phases']),
        'phase normalization': any(abs(p['normalization_residual'])>tolerance for p in parent['phases']),
        'phase charge closure': any(abs(p['charge_residual'])>tolerance for p in parent['phases']),
        'element balances': any(abs(x)>tolerance for x in parent['balances']['scaled_element_residual'].values()),
        'native trials unresolved': any(t.get('evidence','').startswith('unavailable') for t in row.get('native_trials',[])),
        'supplied trials unresolved': row.get('supplied_counts',{}).get('evaluated',0)+row.get('supplied_not_applicable',0)!=6122,
        'ion-rich seed unavailable': not row.get('ion_rich_seed',{}).get('strictly_positive',False),
    }
    return [name for name,failed in checks.items() if failed] or [row.get('cause','Check the native status')]


def selection():
    options = []
    reference = load(REF/'F2-control/replay.json')['rows']
    for label in ('incumbent','F2','F4'):
        folder = OUT/'E'/label
        replay = load(folder/'replay.json.gz')
        previous = {k:v['passed'] for k,v in replay['summary']['relative_to_F2'].items()}
        checks = gates(replay['rows'][:307],reference)
        assert previous==checks
        measured = effective_measured(label)
        assert len({r['identity'] for r in measured})==len(measured)
        measured_pass = len(measured)==321 and all(q['available'] and not q.get('witnesses') for q in measured)
        path = folder/'grid-summary.json'
        grid = load(path) if path.is_file() else None
        grid_pass = (all(grid[k]['states']==n and grid[k]['available']==n and not grid[k]['descent']
                         for k,n in (('grid',1908),('offset',576))) and grid['census']['states']==162
                     and grid['missing_supplied']==grid['census']['descent']==grid['census']['incomplete']==0) if grid else None
        if (folder/'coverage.json').is_file():
            coverage = load(folder/'coverage.json')
            assert grid_pass==coverage['grid_pass']
            if not (folder/'measured-refined').exists():
                assert measured_pass==coverage['measured_pass']
        cost = math.fsum(x['cost'] for x in replay['rows'])
        options.append(dict(label=label,cost=cost,F2_misses=[k for k,v in checks.items() if not v],
                            grid=grid_pass,measured=measured_pass if len(measured)==321 else None))
    controls = OUT/'D/MEA-controls/readback.json'
    control_pass = load(controls)['passed'] if controls.is_file() else None
    eligible = [x for x in options if control_pass and x['grid'] and x['measured'] and not x['F2_misses']]
    tolerance = load(TOLERANCE)['controls']['function_tolerance']
    minimum = min((x['cost'] for x in eligible),default=None)
    tied = [x['label'] for x in eligible if abs(x['cost']-minimum)<=tolerance*minimum]
    selected = next(iter(tied),None)
    donor = selected or 'incumbent'
    path = REF/'F4/parameters.json' if donor=='incumbent' else OUT/f'E/{donor}/parameters.json'
    disposition = ('Expanded gates passed' if selected else 'Historical #435 donor, expanded gates not established')
    return dict(selected=selected,donor=donor,path=path.relative_to(ROOT).as_posix(),parameters=load(path),
                options=options,control_pass=control_pass,ties=tied,relative_cost_tolerance=tolerance,parameter_sha256=sha(path),
                wheel_sha256=WHEEL,disposition=disposition)


def scores(rows, *, pressure=False):
    good = [x for x in rows if x['status']=='Available' and x.get('requested_tolerance_met',True)
            and x.get('value') is not None and x['observed']]
    signed = [x['value']/x['observed']-1 for x in good]
    data = dict(attempted=len(rows),available=len(good))
    if signed:
        data.update(bias_percent=100*math.fsum(signed)/len(signed),
                    AARD_percent=100*math.fsum(map(abs,signed))/len(signed))
        if pressure:
            data['log_RMSE']=math.sqrt(math.fsum(math.log(x['value']/x['observed'])**2 for x in good)/len(good))
    return data



def off_window_comparisons():
    population = off_window_population()
    source_hash = sha(CANONICAL_VLE)
    result = {}
    for label in ('incumbent','F2','F4'):
        path = OUT/f'E/{label}/off-window.json.gz'
        parameter = REF/'F4/parameters.json' if label=='incumbent' else path.with_name('parameters.json')
        proof = load(path)
        assert proof['source_rows']==population and len(proof['rows'])==len(population), (
            f'E {label}: off-window comparison must contain all {len(population)} canonical rows')
        assert (proof['parameter_sha256'],proof['source_sha256'],proof['wheel_sha256'])==(sha(parameter),source_hash,WHEEL)
        pools = {}
        for source,row in zip(population,proof['rows'],strict=True):
            assert row['identity']=='off-window:'+source['observation_id']
            assert row['observed']==float(source['CO2_pressure'])*1000
            assert row['group']==source['source_key'] and row['role']=='comparison' and row['unit']=='Pa'
            if row['status']=='Available' and row.get('requested_tolerance_met'):
                assert row['value']>0
            else:
                assert row['message'], f"E {label}: missing refusal cause for {row['identity']}"
            key = source['source_key']
            pools.setdefault((key,None),[]).append(row)
            if key=='Aronu2011':
                pools.setdefault((key,float(source['MEA_weight_fraction'])),[]).append(row)
        result[label] = {key: scores(rows,pressure=True) for key,rows in pools.items()}
    return result


def mdea_admission(census):
    coverage = {r['key']: r for r in load(MDEA_RESULTS/'phase-search-421/coverage.json') if r['tier']=='data'}
    search = {r['key']:r for r in load(MDEA_SALT/'search-0.json.gz') if r['key'] in coverage}
    archived = load(MDEA_SALT/'search-outcome.json.gz')
    classified = {r['key']:r for r in archived['classifications']}
    joins = {r['key']:r for links in census['joins'].values() for r in links}
    assert len(joins)==sum(map(len,census['joins'].values()))==1564 and joins.keys()==coverage.keys()==search.keys()
    parameter_sha = hashlib.sha256(gzip.decompress((MDEA_SALT/'selection.json.gz').read_bytes())).hexdigest()
    assert (census['parameter_sha256'],census['wheel_sha256'])==(parameter_sha,WHEEL)
    assert all(coverage[r['key']]['observation']==identity for identity,links in census['joins'].items() for r in links)
    bubbles = census['salt_bubble']['rows']
    used = set()
    for key,row in joins.items():
        original = search[key]
        assert row['historical']==coverage[key] and row['same_calculation_as']==archived['aliases'].get(key)
        assert (row['unfinished'],row['descent'],row['completed_without_descent'],row['confirmed'])==(
            not original['available'],original['descent'],original['available'] and not original['descent'],
            any(q['confirmed'] for q in classified.get(key,{}).get('attempts',[])))
        if row['historical']['bubble_multiplier'] is not None:
            continue
        reference_key = row['same_calculation_as'] or key
        assert row['salt_bubble_readback']==reference_key
        used.add(reference_key)
        bubble = bubbles[reference_key]
        assert bubble['T_K']==row['historical']['T_K']
        actual = (original.get('supplied_parent_pressure_Pa')
                  or original.get('pressure_basis',{}).get('search_pressure_Pa')
                  or original.get('pressure_Pa') or row['historical']['pressure_Pa'])
        assert bubble['assigned_Pa']==row['pressure_Pa']==row['historical']['pressure_Pa']==actual
        if row['completed_without_descent']:
            assert original['parent_kind']=='Liquid'
        pressure = bubble['bubble_Pa']
        if pressure is None:
            assert bubble['message']
        else:
            assert bubble['requested_tolerance_met'] and math.isfinite(pressure) and pressure>0
            assert pressure==bubble['result_pressure_Pa'] and bubble['feed_mol']
        assert row['below_bubble_salt'] is (row['pressure_Pa']<pressure if pressure is not None else None), (
            f'B MDEA: stale bubble admission for {key}')
    assert bubbles.keys()==used
    history = load(MDEA_RESULTS/'phase-search-421/coverage-counts.json')
    below = {key for key,row in history['canonical'].items() if row['ratio']<1}
    assert below=={key for key,r in joins.items() if r['below_bubble_421']}==set(census['below_bubble_421'])
    unfinished = {key for key,row in search.items() if not row['available']}
    assert unfinished==set(census['unfinished_435']) and below & unfinished==set(census['intersection'])
    for names,keys in (('below_bubble_observations',below),('below_bubble_unfinished_observations',below & unfinished)):
        assert set(census[names])=={coverage[key]['observation'] for key in keys}
    observations = load(MDEA_SALT/'data-rows.json.gz')
    reduction = mdea_deviations(observations,census['joins'])
    assert any(row['admitted_observations'] for row in reduction), 'B MDEA: admissible subset is empty'
    assert reduction==census['metrics'], 'B MDEA: retained admissible subset or deviations differ from joined contributors'
    return reduction

def pressure_pools(data):
    rows = data['rows']
    source = data['pressure_population']
    lookup = {x['identity']:x for x in rows}
    pressures = [lookup[k] for k in source]
    legacy = [r for r in pressures if r['group']=='common149']
    additions = [r for r in pressures if r['group']=='Table S6 additions']
    hot = [r for r in pressures if float(source[r['identity']]['temperature_reported_C'])+273.15>=370.]
    assert (len(rows),len(lookup),len(pressures),len(legacy),len(additions),len(hot),len(data['hot_wagner']))==(419,419,159,47,112,54,12)
    assert all(lookup[k]['observed']==float(x['CO2_pressure'])*1000 for k,x in source.items())
    pools = dict(all_pressure=pressures,legacy=legacy,added=additions,hot_expanded=hot,
                 hot_published=hot+data['hot_wagner'])
    for label in sorted({r['source_key'] for r in source.values()}):
        pools[label] = [r for r in pressures if source[r['identity']]['source_key']==label]
    for T in (40,60,80,100,120):
        pools[f'{T} C nominal'] = [lookup[k] for k,r in source.items()
             if round(float(r['temperature_series_C'] or r['temperature_reported_C']))==T]
    return pools


def coefficient(document, identity):
    return next(c['value']['magnitude'] for family in ('components','pairs') for entry in document[family]
                for c in entry['coefficients'] if c.get('identity')==identity)


def claims(off_window, b_metrics):
    output = {}
    def add(name, unit, path, field, value, count=None, prior=None):
        assert name not in output, name
        package = PUBLIC_PACKAGE if 'public-1.3.2' in path.parts else WHEEL
        output[name] = dict(unit=unit,record=path.relative_to(ROOT).as_posix(),field=field,
             value=value,formatted=format(value,'.7g') if isinstance(value,float) else value,
             population=count,prior=prior,engine_artifact_sha256=package)
    for label in ('incumbent','historical-F2','F2','F4'):
        path = OUT/f'E/{label}/replay.json.gz'
        data = load(path)
        for name,rows in (('original',data['rows'][:307]),('expanded',data['rows'])):
            value = math.fsum(x['cost'] for x in rows)
            assert abs(value-data['summary'][name+'_cost'])<1e-10
            prior = {'original':152.9581738516127,'expanded':264.23192049220074}[name]
            add(f'E MEA {label} {name} objective','1',path,f'{name} rows: sum cost',value,len(rows),prior)
        old = load(REF/'F2-control/replay.json')['rows']
        prior = scores([q for q in old if q['identity'] in data['pressure_population']])['AARD_percent']
        legacy = [q for q in data['rows'][:307] if q['identity'] in data['pressure_population']]
        rise = scores(legacy)['AARD_percent']-prior
        limit = data['summary']['relative_to_F2']['fitted CO2 partial pressure']
        assert math.isclose(rise,limit['aard_rise_points'],rel_tol=1e-12,abs_tol=1e-12)
        add(f'E MEA {label} legacy pressure AARD rise versus F2','percentage points',
            path,'original pressure fitting rows and #435 F2 control',rise,len(legacy),2.)
        for name,rows in pressure_pools(data).items():
            summary = scores(rows,pressure=True)
            for field,unit in (('bias_percent','%'),('AARD_percent','%'),('log_RMSE','1')):
                assert math.isclose(summary[field],data['summary']['pressure'][name][field],rel_tol=1e-12,abs_tol=1e-12)
                add(f'E MEA {label} {name} {field}',unit,path,f'rows in {name}: observed and value',
                    summary[field],summary['available'])
        if label in off_window:
            path = OUT/f'E/{label}/off-window.json.gz'
            for (source,stock),result in off_window[label].items():
                name = source if stock is None else f'{source} {100*stock:g} wt%'
                result = dict(result,refused=result['attempted']-result['available'])
                for field,unit in (('bias_percent','%'),('AARD_percent','%'),('log_RMSE','1'),
                                   ('available','rows'),('refused','rows')):
                    add(f'E MEA {label} outside fit {name} {field}',unit,path,
                        f'rows/{name}: {field}',result.get(field),result['attempted'])
            add(f'E MEA {label} off-window elapsed','s',path,'seconds',load(path)['seconds'])
    adopted = selection()
    selected = OUT/'E/selection.json'
    assert load(selected)==adopted
    add('E MEA qualified declaration','label',selected,'eligible cost/tie reduction',adopted['selected'])
    prefix = 'component/carbamate-anion/'
    amp_water = 'pair/carbamate-anion/water/k_ij'
    donor = adopted['parameters']
    energy, diameter = [coefficient(donor,prefix+k) for k in ('dispersion_energy_over_k','segment_diameter')]
    water = coefficient(donor,amp_water)
    for label,path in (('DEA',OUT/'F/assessment.json.gz'),('AMP free',OUT/'AMP/free/assessment.json.gz'),
                       ('AMP fixed',OUT/'AMP/fixed/assessment.json.gz')):
        if not path.is_file():
            continue
        identity = load(path)['identity']
        assert identity['donor']['parameter_sha256']==adopted['parameter_sha256']
        values = identity['carbamate']
        assert values[prefix+'dispersion_energy_over_k']==energy
        received = values[prefix+'segment_diameter']
        assert all(values[prefix+k]==received for k in ('born_diameter','debye_huckel_diameter'))
        assert values[prefix+'packing_diameter']==.88*received
        if label.startswith('AMP'):
            coord = next(q for q in identity['coordinates'] if q['identity']=='AMPCOO-segment-diameter')
            assert values[amp_water]==water and received>=coord['bounds'][0]==diameter
        else:
            point = load(OUT/'F/selection.json.gz')['selected'][2]['parameters']
            def size(mapping, species):
                neutral = f'component/{species}/'
                return coefficient(mapping,neutral+'segment_count')*coefficient(mapping,neutral+'segment_diameter')**3
            assert received==diameter*(size(point,'diethanolamine')/size(donor,'monoethanolamine'))**(1/3)
        add(f'{label} carbamate energy divided by k','K',path,'identity/carbamate/dispersion energy',energy)
        add(f'{label} carbamate segment diameter','Å',path,'identity/carbamate/segment diameter',received)
    for label in ('incumbent','F2','F4'):
        data = measured_rows(label)
        if data:
            path = OUT/f'E/{label}/measured-summary.json'
            if path.is_file():
                summary = load(path)
                assert (summary['states'],summary['available'],summary['descents'])==(
                    len(data),sum(q['available'] for q in data),sum(bool(q.get('witnesses')) for q in data))
                for key in ('states','available','descents','seconds'):
                    add(f'D5 {label} {key}','s' if key=='seconds' else 'states',path,key,summary[key],len(data))
                misses = Counter(reason for q in data if not q['available'] for reason in measured_failures(q))
                for reason,n in misses.items():
                    add(f'D5 {label} unresolved, {reason}','states',path,'measured batches: cause',n,len(data))
            refined_dir = OUT/f'E/{label}/measured-refined'
            if refined_dir.is_dir():
                final = effective_measured(label)
                add(f'D5 {label} available with refined pressure closure','states',refined_dir/'pilot.json.gz',
                    'original and refined measured batches',sum(q['available'] for q in final),len(final))
        path = OUT/f'E/{label}/grid-summary.json'
        if path.is_file():
            grid = load(path)
            for group in ('grid','offset','census'):
                for field in ('states','available','descent','incomplete'):
                    if field in grid[group]:
                        add(f'E MEA {label} {group} {field}','states',path,f'{group}/{field}',grid[group][field],grid[group]['states'])
            add(f'E MEA {label} supplied missing','trials',path,'missing_supplied',grid['missing_supplied'],162*6121)
    path = OUT/'A/reference.json.gz'
    doc = load(path)
    for label,outcome in doc['comparisons'].items():
        for i,attempt in enumerate(outcome['attempts']):
            key = f'comparisons/{label}/attempts/{i}'
            checks = attempt['acceptance']
            phase = ('confirmed' if all(checks.values()) else 'failed' if not checks['requested_tolerance']
                     else 'coalesced' if checks['positive_amounts'] and not checks['distinct'] else 'unresolved')
            assert phase==attempt['disposition']
            for field,unit in (('Gibbs_decrease_over_RT_mol','mol'),('numerical_error_over_RT_mol','mol'),('disposition','label')):
                if field in attempt:
                    add(f'A MDEA {label} {i+1} {field}',unit,path,f'{key}/{field}',attempt[field],1)
        final = outcome['fixed_inventory_derivatives'][-1]
        for field,unit in (('eos_volume_m3','m³'),('correction_m3','m³'),('frozen_G_volume_m3','m³'),
                           ('moving_G_volume_m3','m³'),('pressure_tracking_term_J','J'),
                           ('pressure_tracking_direct_J','J'),('engine_tracking_minus_frozen_J','J')):
            if field in final:
                add(f'A MDEA {label} {field}',unit,path,f'comparisons/{label}/fixed_inventory_derivatives/-1/{field}',final[field],1)
    path = OUT/'B/census.json.gz'
    census = load(path)
    for field in ('below_bubble_observations','below_bubble_421','unfinished_435','intersection','below_bubble_unfinished_observations'):
        add(f'B MDEA {field}','count',path,field,len(census[field]),1564)
    fixed = [r for links in census['joins'].values() for r in links if r['historical']['bubble_multiplier'] is None]
    add('B MDEA fixed-pressure search attempts','attempts',path,'joins: fixed-pressure records',len(fixed),1564)
    add('B MDEA completed fixed-pressure attempts without detected descent','attempts',path,
        'joins: completed fixed-pressure records without descent',sum(q['completed_without_descent'] for q in fixed),len(fixed))
    add('B MDEA admitted fixed-pressure search attempts','attempts',path,'joins: admitted and completed without descent',
        sum(q['completed_without_descent'] and q['below_bubble_salt'] is False for q in fixed),len(fixed))
    add('B MDEA salt bubble elapsed','s',path,'salt_bubble/seconds',census['salt_bubble']['seconds'])
    for group in b_metrics:
        source = group['group']
        add(f'B MDEA {source} admitted search attempts','attempts',path,f'metrics/{source}/admitted_search_attempts',
            group['admitted_search_attempts'],group['fixed_pressure_search_attempts'])
        for subset in ('all','resolved_fixed_pressure_subset'):
            result = group[subset]
            add(f'B MDEA {source} {subset} available','rows',path,f'metrics/{source}/{subset}/available',
                result['available'],result['attempted'])
            for field,unit in (('AARD_percent','%'),('bias_percent','%'),('mean_abs_error',group['unit']),
                               ('mean_signed_error_predicted_minus_observed',group['unit'])):
                statistics = result['scores'] or {}
                denominator = 'relative_rows' if unit=='%' else 'rows'
                add(f'B MDEA {source} {subset} {field}',unit,path,f'metrics/{source}/{subset}/scores/{field}',
                    statistics.get(field),statistics.get(denominator,0))
    for label,target in census['targeted'].items():
        add(f'B MDEA targeted {label} disposition','label',path,f'targeted/{label}/outcome',target['outcome'],1)
        for i,attempt in enumerate(target['attempts']):
            for field in ('Gibbs_decrease_over_RT_mol','numerical_error_over_RT_mol'):
                if field in attempt:
                    add(f'B MDEA targeted {label} trial {i+1} {field}','mol',path,f'targeted/{label}/attempts/{i}/{field}',attempt[field],1)
    for row,source in enumerate(census['sobrinorows']):
        for k,v in source.items():
            if isinstance(v,(int,float)) and not isinstance(v,bool):
                add(f'B Sobrino row {row+1} {k}','see record',path,f'sobrinorows/{row}/{k}',v,1)
    for case in ('historical','salt'):
        for label in ('incumbent','refit'):
            p = OUT/f'C/{case}/{label}.json.gz'
            if not p.is_file():
                continue
            doc = load(p)
            for w in ('original','rms'):
                info = doc['objective'][w]
                value = math.fsum(r['cost'] for r in info['rows'])
                assert math.isclose(value,info['objective'],rel_tol=1e-14)
                add(f'C MDEA {case} {label} {w} objective','1',p,f'objective/{w}/rows: sum cost',value,len(info['rows']))
                for name, groups in (('loaded pressure',{'Kuranov'}),('density',{'loaded-density','unloaded-density'})):
                    family = [r for r in info['rows'] if r['group'] in groups]
                    add(f'C MDEA {case} {label} {w} {name} cost share','%',p,f'objective/{w}/rows: {name}',
                        100*math.fsum(q['cost'] for q in family)/value,len(family))
            for name,groups,n in (('loaded total',{'Kuranov'},66),('all fitted pressures',{'Kuranov','Kuranov-binary','Kim'},131),
                                  ('Ermatchkov',{'Ermatchkov'},101),('Xiao',{'Xiao'},20),('development partials',{'Ermatchkov','Xiao'},121)):
                rows = [x for x in doc['rows'] if x['group'] in groups]
                assert len(rows)==n
                for metric in ('bias_percent','AARD_percent'):
                    add(f'C MDEA {case} {label} {name} {metric}','%',p,f'rows in {name}: observed and value',
                        scores(rows).get(metric),n)
        for file in ('search-outcome.json.gz','timing.json'):
            p = OUT/f'C/{case}/{file}'
            if p.is_file():
                doc = load(p)
                add(f'C MDEA {case} {file} seconds','s',p,'seconds',doc['seconds'])
                if 'tally' in doc:
                    rows = load(p.with_name('search-0.json.gz'))
                    assert (len(rows),sum(q['available'] for q in rows),sum(q['descent'] for q in rows))==(
                        doc['tally']['states'],doc['tally']['available'],doc['tally']['descent'])
                    assert [q['key'] for q in rows if not q['available']]==doc['tally']['unavailable']
                    assert doc['confirmed']==[x['key'] for x in doc['classifications']
                                              if any(y['confirmed'] for y in x['attempts'])]
                    for field in ('states','available','descent','unavailable','confirmed'):
                        value = doc['confirmed'] if field=='confirmed' else doc['tally'][field]
                        add(f'C MDEA {case} RMS {field}','states',p,field,len(value) if isinstance(value,list) else value,doc['tally']['states'])
    path = OUT/'D/electrode-incumbent.json.gz'
    if path.is_file():
        rows = load(path)['rows']
        errors = [x['pH']-x['point']['pH'] for x in rows if 'pH' in x]
        for name,value in (('min',min(errors)),('max',max(errors)),('bias',math.fsum(errors)/len(errors))):
            add(f'D MEA model minus electrode pH {name}','pH',path,'rows: pH minus point/pH',value,len(errors))
        for field,unit in (('carbonate_share','1'),('common_molality_minus_raw','pH')):
            values = [q[field] for q in rows if field in q]
            for name,value in (('min',min(values)),('max',max(values))):
                add(f'D MEA electrode {field} {name}',unit,path,f'rows/{field}',value,len(values))
    for name,p in (('DEA',OUT/'F/selection.json.gz'),('AMP free',OUT/'AMP/free/selection.json.gz'),
                   ('AMP fixed slope',OUT/'AMP/fixed/selection.json.gz')):
        if p.is_file():
            value = load(p)['selected']
            cost = None
            if value:
                fit = load(p.with_name(value[1]+'.json.gz'))
                cost = fit['report']['endpoint_replay_cost']
                assert cost==value[0] and fit['point']==value[2]
            add(f'{name} selected converged objective','1',p,'selected fit: report/endpoint_replay_cost',cost)
            if name.startswith('AMP') and value:
                path = 'pair/protonated-aminomethylpropanol/water/k_ij/reciprocal_temperature_slope'
                slope = coefficient(value[2]['parameters'],path)
                add(f'{name} reciprocal temperature slope','K',p,'selected/2/parameters/'+path,slope)
    p = OUT/'F/incumbent-expanded.json.gz'
    if p.is_file():
        rows = load(p)['rows']
        add('F DEA historical expanded objective','1',p,'rows: sum cost',math.fsum(q['cost'] for q in rows),len(rows))
    p = OUT/'F/assessment.json.gz'
    if p.is_file():
        rows = load(p)['expanded_design']
        old = load(DEA_COMPARISON)
        for group in ('Lawson','Lawson-394K','SeoHong','Lal','Carson','Horstmann','Cai','Weiland',
                      'Bottinger-DEACOO','Bottinger-DEA_plus_DEAH','Bottinger-HCO3'):
            pool = [q for q in rows if q['group']==group]
            prior = [q for q in old if q['group']==group]
            assert {q['identity'] for q in pool}=={q['identity'] for q in prior}
            stats = scores(pool)
            baseline = scores(prior)
            for field in ('bias_percent','AARD_percent','available'):
                add(f'F DEA {group} {field}','rows' if field=='available' else '%',p,
                    f'expanded_design/{group}: observed and value',stats.get(field),len(pool),baseline.get(field))
            if group=='Horstmann':
                count = sum(q['value']>0>q['observed'] for q in pool if q['value'] is not None)
                add('F DEA Horstmann positive predictions for negative excess enthalpy','rows',
                    p,'expanded_design/Horstmann: sign disagrees with negative observation',count,len(pool),14)
            if group in ('Lawson','Lawson-394K','SeoHong','Lal','Carson'):
                for reaction in ('carbamate-hydrolysis','DEA-dissociation'):
                    for flag,label in ((True,'outside'),(False,'inside')):
                        test = [q for q in pool if q['outside_ranges'].get(reaction) is flag]
                        ref = [q for q in prior if q['outside_ranges'].get(reaction) is flag]
                        assert {q['identity'] for q in test}=={q['identity'] for q in ref}
                        if test:
                            add(f'F DEA {group} {label} {reaction} AARD','%',p,
                                f'expanded_design/{group}/outside_ranges/{reaction}',scores(test).get('AARD_percent'),
                                len(test),scores(ref).get('AARD_percent'))
    for file in ('methane','methane-refit'):
        p = OUT/f'F/{file}.json.gz'
        if p.is_file():
            rows = [x for x in load(p)['rows'] if 'pCO2_change_Pa' in x]
            if rows:
                add(f'F DEA {file} conditional maximum pCO2 shift','Pa',p,'rows/pCO2_change_Pa: maximum',
                    max(q for row in rows for q in row['pCO2_change_Pa']),len(rows))
    for part in ('F','AMP/free','AMP/fixed'):
        for p in sorted((OUT/part).glob('*outcome.json.gz')):
            doc = load(p)
            for field in ('states','available','descent','confirmed'):
                value = len(doc['confirmed']) if field=='confirmed' else doc['tally'][field]
                add(f'{part} {p.stem} {field}','states',p,field,value,doc['tally']['states'])
    for p in (OUT/'D').glob('**/*.json.gz'):
        if p.name.startswith('coordinate-') or p.name=='unbounded-MDEA.json.gz':
            d = load(p)
            report = d.get('report') or {}
            for field,unit in (('status','label'),('endpoint_replay_cost','1')):
                add(f'D {p.parent.name} {p.stem} {field}',unit,p,'report/'+field,report.get(field))
            for field in ('k_423_bounded','k_423_unbounded','held_value'):
                if field in d:
                    add(f'D {p.parent.name} {p.stem} {field}','see record',p,field,d[field])
    p = OUT/'D/unbounded-MDEA.json.gz'
    if p.is_file():
        docs = load(p)
        for label,key in (('bound','baseline'),('no bound','binary')):
            if key not in docs:
                continue
            data = docs[key]
            native_rows = data['native']['rows']
            for field,flag in (('descent',lambda x:(x['value'] or 0.)<0),
                               ('available',lambda x:x['status']=='Available')):
                value = sum(flag(q) for q in native_rows)
                assert value==data['native'][field]
                add(f'D MDEA {label} binary {field}','states',p,f'{key}/native/rows',value,len(native_rows))
            for field,value in zip(('lower','upper'),data['hull']['onset_bracket_K'],strict=True):
                add(f'D MDEA {label} gap onset {field}','K',p,f'{key}/hull/onset_bracket_K',value)
    p = OUT/'D/cai/assessment.json.gz'
    if p.is_file():
        d = load(p)
        for case in ('original','alternative'):
            rows = d[case+'_rows']
            cost = math.fsum(q['cost'] for q in rows)
            assert math.isclose(cost,d[case+'_cost'],rel_tol=1e-12)
            add(f'D Cai {case} objective','1',p,case+'_rows: sum cost',cost,len(rows))
    p = OUT/'D/AMP-profile/profile-expanded.json'
    if p.is_file():
        d = load(p)
        for slope,point in d['points'].items():
            cost = point['cost']
            row_path = p.parent/point['record']
            if row_path.is_file():
                row = load(row_path)
                if cost is not None:
                    assert math.isclose(math.fsum(q['cost'] for q in row['replay']),cost,rel_tol=1e-12)
                add(f'D AMP profile conditional solve at {slope} K','label',row_path,'report/status',row['report']['status'])
            add(f'D AMP profile conditional objective at {slope} K','1',p,f'points/{slope}/cost',cost,214,d['minimum'])
        for side,b in d['brackets'].items():
            for field in ('within','beyond'):
                add(f'D AMP profile {side} {field} bracket','K',p,f'brackets/{side}/{field}',b[field])
    p = OUT/'D/AMP-worked-terms.json.gz'
    if p.is_file():
        for label,doc in load(p)['rows'].items():
            split = doc.get('old_split_vs_own_parent',{})
            for term,value in split.items():
                add(f'D AMP {label} archive split minus parent {term}','mol',p,
                    f'rows/{label}/old_split_vs_own_parent/{term}',value,1)
            trial = doc.get('trial_vs_own_parent')
            if trial:
                add(f'D AMP {label} trial TPD over RT','1',p,f'rows/{label}/trial_vs_own_parent/total',trial['total'],1)
                for term,value in trial['detail'][-1]['terms'].items():
                    add(f'D AMP {label} trial {term} contribution','1',p,
                        f'rows/{label}/trial_vs_own_parent/detail/-1/terms/{term}',value,1)
    p = OUT/'H/kuranov-82nd.json'
    source = load(p)
    for field,unit in (('T','K'),('m_mdea','mol/kg water'),('m_co2','mol/kg water'),('p_exp','Pa')):
        add(f'H Kuranov Table 2 row 72 {field}',unit,p,f'row/{field}',source['row'][field],1)
    p = OUT/'H/hartono-S11.json.gz'
    for label,results in load(p)['results'].items():
        for field,source in results.items():
            value = scores(source['rows'])['AARD_percent']
            assert abs(value-source['scores']['AARD_percent'])<1e-10
            add(f'H Hartono {label} {field} AARD','%',p,f'results/{label}/{field}/rows: observed and value',
                value,26,3.89 if 'historical' in label else None)
    p = OUT/'H/hong-S31.json.gz'
    rows = list(load(p)['rows'].values())
    wagner = [q for q in rows if q['source'].startswith('Wagner')]
    canonical = [q for q in rows if q not in wagner]
    strict = [q for q in canonical if q['inside_hong_grid']=='True']
    assert (len(strict),len(canonical),len(wagner))==(132,145,23)
    for name,pool in (('all joined',rows),('canonical',canonical),('Wagner',wagner),('strict canonical',strict)):
        available = [q for q in pool if 'fixed_weight' in q]
        add(f'H Hong {name} equal-fugacity solved','rows',p,'rows with fixed_weight',len(available),len(pool))
        add(f'H Hong {name} locally unstable','rows',p,'rows with reported local instability',
            sum(q['fixed_weight']['stability']=='locally unstable' for q in available),len(pool))
    for package in ('study','public-1.3.2'):
        p = OUT/f'H/{package}/cells.json.gz'
        if p.is_file():
            for memo,tables in load(p)['records'].items():
                for table,values in tables.items():
                    n = sum(q['value'] is not None and format(q['value'],q['precision'])==q['published'] for q in values)
                    assert n==sum(q['same_rounded'] for q in values)
                    add(f'H {package} {memo} {table} rounding matches','cells',p,f'records/{memo}/{table}',n,len(values))
        for memo in ('round6','round7'):
            p = OUT/f'H/{package}/{memo}-S15.json'
            cells = [q for group in load(p)['rows'] for row in group['answers'] for q in row.get('quantities',{}).values()]
            assert len(cells)==120, f'H {package} {memo} S15: expected 120 reported cells'
            matches = [q['value'] is not None and format(q['value'],'.10g')==format(q['target'],'.10g')
                       for q in cells]
            assert matches==[q['displayed_match'] for q in cells], f'H {package} {memo} S15: stale rounding flags'
            add(f'H {package} {memo} S15 rounding matches','cells',p,'rows/answers/quantities: value and target at .10g',
                sum(matches),len(cells))
    for p in sorted((OUT/'execution').glob('*.json')):
        data = load(p)
        if 'seconds' in data:
            add(f'{p.stem} elapsed','s',p,'seconds',data['seconds'])
    return output


def dispositions(quantities):
    def value(name):
        return quantities[name]['value']

    e = ('incumbent','F2','F4')
    measured = {label:effective_measured(label) for label in e}
    passing = {label:sum(r['available'] and not r.get('witnesses') for r in rows) for label,rows in measured.items()}
    incomplete = {}
    for label in e[1:]:
        rows = load(OUT/f'E/{label}/grid/search/census.json')['result']['rows']
        incomplete[label] = sum(not q['complete'] for q in rows)
        assert incomplete[label]==value(f'E MEA {label} census incomplete')
    assert all(not r.get('witnesses') for rows in measured.values() for r in rows)
    assert all(not value(f'E MEA {label} {group} descent') for label in e for group in ('grid','offset','census'))
    limit = quantities['E MEA F2 legacy pressure AARD rise versus F2']['prior']
    min_rise = min(value(f'E MEA {label} legacy pressure AARD rise versus F2') for label in e[1:])
    assert all(abs(value(f'E MEA {label} hot_expanded bias_percent')) < abs(value('E MEA incumbent hot_expanded bias_percent'))
               for label in e[1:])
    assert value('E MEA qualified declaration') is None

    a = load(OUT/'A/reference.json.gz')['comparisons']
    tracking, frozen = a['tracking'], a['100 kPa']
    frozen_pressure, = {r['reference']['reference_pressure_pa'] for r in frozen['declaration']['reactions']
                       if r['name'] in {'R1','R2','R3'}}
    derivative = tracking['fixed_inventory_derivatives'][-1]
    assert all(t['disposition']=='confirmed' for t in tracking['attempts'])
    assert all(t['disposition']=='unresolved' and not t['acceptance']['liquid_root'] and t['acceptance']['lowering']
               for t in frozen['attempts'])
    assert derivative['engine_tracking_minus_frozen_J']==0

    b = load(OUT/'B/census.json.gz')
    below = [(identity,t) for identity,links in b['joins'].items() for t in links if t['below_bubble_421']]
    unfinished = sum(t['unfinished'] for links in b['joins'].values() for t in links)
    no_property = sum(not any('target' in t['observation'] for t in links) for links in b['joins'].values())
    sobrino = [q['observation']['value']-q['observation']['observed'] for q in b['sobrinorows']]
    assert b['targeted']['salt']['P_Pa']==b['targeted']['historical']['P_Pa']

    def c(case,label):
        return value(f'C MDEA {case} {label} loaded total AARD_percent')
    assert all(value(f'C MDEA {case} refit original objective')>value(f'C MDEA {case} incumbent original objective')
               for case in ('historical','salt'))
    original_salt = load(MDEA_SALT/'search-outcome.json.gz')
    original_hist = load(MDEA_RESULTS/'bounded-binary-411/stability.json')
    historical_splits = original_hist['liquid_liquid_splits_among_completed_searches']['distinct']
    rms_splits = {case:load(OUT/f'C/{case}/search-outcome.json.gz')['confirmed'] for case in ('historical','salt')}
    assert set(original_salt['confirmed']).isdisjoint(rms_splits['salt'])
    assert value('C MDEA salt RMS unavailable')>len(original_salt['tally']['unavailable'])
    assert value('C MDEA historical RMS unavailable')>len(original_hist['grid']['unavailable'])

    amp = [load(p)['worked_state'] for p in sorted((OUT/'D/bounds/AMP').glob('coordinate-*.json.gz'))]
    amp_unresolved = sum(q['instability']=='resolved descent' and q['stable_assemblage'] is None for q in amp)
    mdea = [load(p)['matched_high_pressure'] for p in sorted((OUT/'D/bounds/MDEA').glob('coordinate-*.json.gz'))]
    mdea_unresolved = sum(q['outcome']=='unresolved' for q in mdea)
    crossings = [math.fsum(value(f'D AMP profile {side} {edge} bracket') for edge in ('within','beyond'))/2
                 for side in (-1,1)]
    binary = quantities['D MDEA no bound binary available']

    dea = load(OUT/'F/original-design.json.gz')
    assert dea['replayed_435']
    dea_search = load(OUT/'F/search-rows.json.gz')
    dea_classifications = load(OUT/'F/search-outcome.json.gz')['classifications']
    dea_confirmed = sum(any(q['confirmed'] for q in state['attempts']) for state in dea_classifications)
    assert dea_confirmed==value('F search-outcome.json confirmed')
    dea_pending = sum(q['descent'] for q in dea_search)-dea_confirmed
    dea_unfinished = sum(not q['available'] for q in dea_search)
    lawson = quantities['F DEA Lawson-394K AARD_percent']
    sign = quantities['F DEA Horstmann positive predictions for negative excess enthalpy']
    f = quantities['F DEA historical expanded objective']

    amp_ref = ROOT/'analyses/amp_transfer/results/salt-anchored-435'
    amp_costs = [value(f'AMP {name} selected converged objective') for name in ('free','fixed slope')]
    amp_prior = [load(amp_ref/f'{label}/selection.json.gz')['cost'] for label in ('free','fixed')]
    amp_states = [load(OUT/f'AMP/{label}/{bank}-rows.json.gz') for label in ('free','fixed') for bank in ('native','supplied')]
    amp_counts = {len(rows) for rows in amp_states}
    assert len(amp_counts)==1 and all(q['available'] and not q['descent'] for rows in amp_states for q in rows)
    amp_n, = amp_counts
    amp_fit_rows, = {sum(q['role']=='fitted' for q in load(OUT/f'AMP/{label}/assessment.json.gz')['rows'])
                     for label in ('free','fixed')}
    revised_s16 = load(OUT/'H/study/round7-S16.json.gz')
    assert revised_s16['phases'] and revised_s16['trial'] and not any(q['confirmed'] for q in revised_s16['attempts'])

    kuranov = load(OUT/'H/kuranov-82nd.json')
    source_row = kuranov['row']['source_row']
    assert source_row==kuranov['row']['row'] and source_row not in kuranov['matched_rows']
    study, public = ('H study round6','H public-1.3.2 round6')
    s15 = [int(value(f'{label} S15 rounding matches')) for label in (study,public)]
    h_public = load(OUT/'H/public-1.3.2/cells.json.gz')['records']['round6']
    assert any(q['refusal'] for q in h_public['S16_cells'] if q['label']=='Plane-value error estimate')
    receipt = load(OUT/'study-wheel.json')
    cap = receipt['total_worker_cap']
    workers = receipt['initial_parallel_work']

    return {
        'E and D5 · MEA model selection': (
            f"Both expanded {quantities['E MEA F2 expanded objective']['population']}-row fits improve the hot-pressure bias. "
            f"Their legacy partial-pressure AARD rises by at least {math.floor(min_rise)} percentage points from the F2 replay, above the {limit:g}-point limit. "
            f"The incumbent has {passing['incumbent']} qualifying measured-state searches out of {len(measured['incumbent'])} after pressure refinement. "
            f"F2 has {passing['F2']} and F4 has {passing['F4']}. "
            f"The {value('E MEA F2 census states')}-state censuses have incomplete entries (F2 {incomplete['F2']}, F4 {incomplete['F4']}). "
            "No resolved descent was found in these finite screens. The exact #435 MEA declaration remains the historical carbamate donor."),
        'A · MDEA reference pressure': (
            f"At {tracking['T_K']:.2f} K and {tracking['P_Pa']/1e6:.3f} MPa the pressure-tracking split is confirmed. "
            f"The {frozen_pressure/1000:g} kPa reference split candidate lowers Gibbs energy. Its liquid-root check remains unresolved. "
            f"The independent pressure-tracking correction is {100*derivative['correction_m3']/derivative['eos_volume_m3']:.1f}% of the EOS volume. "
            f"The matched Engine enthalpies at the same composition coincide. The fixed-volume reference chain term is {derivative['pressure_tracking_term_J']/1000:.2f} kJ per feed."),
        'B · MDEA measured-state census': (
            f"The historical below-bubble group has {len(below)} search attempts on {len({i for i,_ in below})} observations. "
            f"{sum(t['unfinished'] for _,t in below)} attempts overlap the {unfinished} unfinished #435 searches among {sum(map(len,b['joins'].values())):,}. "
            f"{no_property} diagnostic IDs lack a current property row. The {len(sobrino)} Sobrino liquid-branch predictions exceed observations by {min(sobrino):.2f}–{max(sobrino):.2f} kg/m³. "
            f"At {b['targeted']['salt']['P_Pa']/1e6:.3f} MPa the historical comparison reports a {b['targeted']['historical']['outcome']} and the salt case is {b['targeted']['salt']['outcome']}."),
        'C · MDEA pressure reweighting': (
            f"Pressure AARD on {quantities['C MDEA salt incumbent loaded total AARD_percent']['population']} fitted loaded totals changes from {c('salt','incumbent'):.2f}% to {c('salt','refit'):.2f}% for salt and from {c('historical','incumbent'):.2f}% to {c('historical','refit'):.2f}% for the historical pair. "
            "The original-weight objectives worsen in both pairs. "
            f"The original and RMS salt screens confirm {len(original_salt['confirmed'])} and {len(rms_splits['salt'])} splits at different grid states. "
            f"The historical RMS screen confirms {len(rms_splits['historical'])} compared with {historical_splits} in the original historical grid census. Both RMS screens have more unfinished searches."),
        'D · Declaration sensitivities': (
            f"The MEA electrode discrepancy spans {value('D MEA model minus electrode pH min'):+.3f} to {value('D MEA model minus electrode pH max'):+.3f} pH on the digitized {quantities['D MEA model minus electrode pH min']['population']} points. "
            "Cai reweighting slightly reduces its alternate objective and raises the original objective. "
            f"Removing the MDEA binary bound produces {value('D MDEA no bound binary descent')} descents, {binary['population']-binary['value']} incomplete native search and a hull-onset bracket of {value('D MDEA no bound gap onset lower'):.3f}–{value('D MDEA no bound gap onset upper'):.3f} K. "
            f"The AMP conditional slope profile brackets crossings near {crossings[0]:+.1f} and {crossings[1]:+.1f} K. "
            f"{amp_unresolved} AMP inward variants retain unresolved phase identities at the historical absolute pressure after detecting descents. "
            f"{mdea_unresolved} MDEA inward variants leave the matched high-pressure split unresolved."),
        'DEA and F · Broader measurement coverage': (
            "The original DEA transfer replays the #435 objective exactly with the historical donor. "
            f"The expanded {f['population']}-row objective falls from {f['value']:.2f} to {value('DEA selected converged objective'):.2f}. "
            f"The broadened fit confirms {dea_confirmed} measured-state splits. The search records retain {dea_pending} for unresolved descent and {dea_unfinished} for incomplete search. "
            f"Seo–Hong pressure AARD is {value('F DEA SeoHong AARD_percent'):.2f}%, the {lawson['population']} outside-fit Lawson rows have {lawson['value']:.2f}% AARD, and the Horstmann excess-enthalpy sign misses on {sign['value']} of {sign['population']} rows. "
            f"The maximum conditional methane shift is {value('F DEA methane-refit conditional maximum pCO2 shift')/1e6:.3f} MPa for the refit. Dissolved methane effects remain unbounded by the experiment."),
        'AMP · Inherited carbamate inputs': (
            "Both free- and fixed-slope AMP fits converge and preserve the donor checks. "
            f"Their objectives are {amp_costs[0]:.2f} and {amp_costs[1]:.2f} on {amp_fit_rows} rows, compared with {amp_prior[0]:.2f} and {amp_prior[1]:.2f} for #435. "
            f"Each native and supplied-bank search completes all {amp_n} declared states without a resolved descent. "
            "The historical absolute-pressure worked state has unresolved phase identity for the free-slope endpoint."),
        'H · Source and package readbacks': (
            f"Kuranov Table 2 row {source_row} is the unmatched observation after {len(set(kuranov['matched_rows']))} source rows were matched. "
            f"Historical Hartono S11 gives {value('H Hartono historical expanded free pressure AARD'):.4f}% bubble-pressure AARD and {value('H Hartono historical expanded free mole_fraction AARD'):.4f}% vapor mole-fraction AARD. "
            f"The strict canonical Hong group solves {value('H Hong strict canonical equal-fugacity solved')} equal-fugacity rows and fails the local test on {value('H Hong strict canonical locally unstable')}. "
            f"The study wheel and public package match {s15[0]} and {s15[1]} rounded S15 cells, respectively, with physical-check misses retained. "
            f"The study wheel matches {value(f'{study} S16_cells rounding matches')} historical S16 and {value(f'{study} S17_cells rounding matches')} S17 cells at displayed precision. "
            f"Public 1.3.2 matches {value(f'{public} S16_cells rounding matches')} historical S16 cells at displayed precision and omits the plane-value error diagnostic. "
            f"It matches {value(f'{public} S17_cells rounding matches')} of {quantities[f'{public} S17_cells rounding matches']['population']} S17 cells. "
            "The revised S16 exercise retains the parent, trial and failed phase attempts at the same pressure. A future #430-qualified wheel is pending."),
        'Execution': (
            "A simultaneous SIGTERM ended the initial C and E searches before their configured limits. Its sender remains unverified. "
            "The reruns retained completed work and checkpointed batches. The retained timing and refusal records give each interruption, failed implementation check and recovery. "
            f"The original execution exceeded the issue #436 limit of 4 workers total. Its execution record gives a cap of {cap}, with {workers['E_workers']} E workers and {workers['C_workers']} C workers."),
    }


def document(quantities, dispositions, off_window, b_metrics):
    text = ['---','title: Round 7 referee calculations','---','',
            'The study tests whether expanding the measured CO₂ partial-pressure window improves the salt-anchored MEA fit while retaining its original properties and screening coverage.',
            'Deviations on fitted rows describe calibration. The phase calculations screen finite sets of fluid states on declared feeds and pressure bases.',
            'The notebook identifies numerical misses and their consequences for the proposed declarations. It awaits independent evidence review and investigator promotion for manuscript use.',
            '', '## Disposition', '']
    text += [f'- {item} — {status}' for item,status in dispositions.items()]
    text += ['', '## Calculation basis', '',
             'The MEA objective adds 112 CO₂ partial pressures to the original 307 rows at the original pressure weight. The 12 hot Wagner observations enter only the 66-row comparison. The measured-state phase search uses recorded total pressure where available and retains assigned pressures with their basis elsewhere.',
             'The DEA objective combines 90 partial pressures at a log scale of 0.09 and 50 integral heats. The methane calculation uses the calibrated apparatus range and a dry Redlich–Kwong gas. Its liquid calculation holds the methane-free composition fixed.',
             'The MDEA alternative uses an average of squared standardized residuals for each Table S12 family. The loaded-total-pressure group uses a log scale of 0.015. Ermatchkov and Xiao are development comparisons under both weightings.',
             r'The reference-pressure readback adds $\sum_i n_i c_i(T,P_{\rm src})$ to the EOS Gibbs energy in the neutral reaction gauge. At fixed $T,n_i$ its pressure derivative contributes $\sum_i n_i (\partial c_i/\partial P_{\rm src})(dP_{\rm src}/dP)$. The caloric readback compares the explicit temperature derivative at frozen reference pressure with the chain term when the reference pressure follows $P(T,V,n)$.',
             ]

    def displayed(value):
        return '—' if value is None else f'{value:.3f}'

    text += ['', '## MEA CO₂ partial pressure outside the fit window', '',
             'Aronu covers 15 and 45 wt% MEA at 40–80 °C. Jou covers 30 wt% MEA at 0 and 25 °C. The existing assessment limit is 293.15 K, so every endpoint refused the six 0 °C Jou rows. The errors use the available predictions at the reported temperatures, stocks and loadings.',
             '',
             '| Endpoint | Source | Predicted | Refused | AARD (%) | Signed bias (%) |',
             '| --- | --- | ---: | ---: | ---: | ---: |']
    for label,groups in off_window.items():
        for (source,stock),row in groups.items():
            source_label = f'{source}, {100*stock:g} wt%' if stock is not None else source
            text.append(f"| {label} | {source_label} | {row['available']} | {row['attempted']-row['available']} | "
                        f"{displayed(row.get('AARD_percent'))} | {displayed(row.get('bias_percent'))} |")
    fixed = quantities['B MDEA admitted fixed-pressure search attempts']
    admitted = sum(g['resolved_fixed_pressure_subset']['attempted'] for g in b_metrics)
    available = sum(g['resolved_fixed_pressure_subset']['available'] for g in b_metrics)
    text += ['', '## MDEA deviations on admitted fixed-pressure liquid parents', '',
             f"{fixed['value']} of {fixed['population']} retained fixed-pressure search attempts completed without detected descent at or above the matched salt bubble pressure. Each property observation contributes once if at least one of its linked fixed-pressure attempts qualifies. Search counts include aliases. Of {admitted} admitted observations, {available} have an available property prediction.",
             'The pressure criterion uses the assigned absolute pressure. The source and assigned pressure fields distinguish reported and assumed conditions. These are conditional liquid-branch deviations over the finite search. The AARD and signed bias exclude zero observations. The keyed handoff gives their relative-error denominators and the absolute errors in the original property units.',
             '',
             '| Property group | Available / all observations | Full-set AARD (%) | Available / admitted observations | Admitted / fixed-pressure attempts | Admitted AARD (%) | Admitted signed bias (%) |',
             '| --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    for g in b_metrics:
        full, subset = g['all'], g['resolved_fixed_pressure_subset']
        full_scores, subset_scores = full['scores'] or {}, subset['scores'] or {}
        text.append(f"| {g['group']} | {full['available']}/{full['attempted']} | {displayed(full_scores.get('AARD_percent'))} | "
                    f"{subset['available']}/{subset['attempted']} | {g['admitted_search_attempts']}/{g['fixed_pressure_search_attempts']} | "
                    f"{displayed(subset_scores.get('AARD_percent'))} | {displayed(subset_scores.get('bias_percent'))} |")
    text += [
             '', '## Numerical handoff', '',
             'The [quantity-keyed handoff](manuscript-handoff.json) gives the full precision, denominator, comparator and record field for every quantity.',
             'Comparisons below use the same observations or declared state. A dash indicates an unavailable or inapplicable entry.', '',
             '| Quantity | Value | Unit | N | Comparison or limit | Record |',
             '| --- | --- | --- | --- | --- | --- |']
    for name,q in quantities.items():
        path = Path(q['record'])
        href = path.relative_to(HERE.relative_to(ROOT)).as_posix() if path.is_relative_to(HERE.relative_to(ROOT)) else '../../'+path.as_posix()
        fields = [q[k] if q[k] is not None else '—' for k in ('formatted','unit','population','prior')]
        text.append('| '+' | '.join(map(str,(name,*fields,f"[{path.name}]({href})"))) + ' |')
    return '\n'.join(text)+'\n'


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--check',action='store_true')
    cli.add_argument('--selection',action='store_true')
    cli.add_argument('--handoff',type=Path,default=HERE/'manuscript-handoff.json')
    args = cli.parse_args()
    if args.selection:
        save(OUT/'E/selection.json',selection())
        return
    off_window = off_window_comparisons()
    b_metrics = mdea_admission(load(OUT/'B/census.json.gz'))
    quantities = claims(off_window,b_metrics)
    status = dispositions(quantities)
    paths = sorted(OUT.rglob('*'))
    manifest = {path.relative_to(ROOT).as_posix():sha(path) for path in paths if path.is_file()}
    for label in ('incumbent','historical-F2','F2','F4'):
        for path,digest in load(OUT/f'E/{label}/replay.json.gz')['source_hashes'].items():
            assert sha(ROOT/path)==digest
            manifest[path] = digest
    sources = (REF/'F2-control/replay.json',REF/'F4/parameters.json',TOLERANCE,DEA_COMPARISON,CANONICAL_VLE,
               MDEA_RESULTS/'bounded-binary-411/stability.json',
               *(MDEA_RESULTS/'phase-search-421'/name for name in ('coverage.json','coverage-counts.json')),
               *(MDEA_SALT/name for name in ('selection.json.gz','search-0.json.gz','search-outcome.json.gz','data-rows.json.gz')),
               *(ROOT/f'analyses/amp_transfer/results/salt-anchored-435/{label}/selection.json.gz' for label in ('free','fixed')))
    for path in sources:
        manifest[path.relative_to(ROOT).as_posix()] = sha(path)
    data = dict(wheel_sha256=WHEEL,quantities=quantities,source_hashes=manifest,dispositions=status)
    notebook = document(quantities,status,off_window,b_metrics)
    if args.check:
        notes = load(OUT/'dispositions.json')
        for item in status.keys() | notes.keys():
            if notes.get(item)!=status.get(item):
                cli.exit(1,f'Disposition differs from retained contributors for {item}\n')
        retained = load(args.handoff)
        wrong = [k for k,v in quantities.items() if retained['quantities'].get(k)!=v]
        if wrong:
            cli.exit(1,f'Different values or provenance for {wrong}\n')
        if retained!=data or (HERE/'notebook.qmd').read_text()!=notebook:
            cli.exit(1,'Handoff provenance or notebook is stale\n')
        print(f'{len(quantities)} quantities recomputed')
    else:
        save(args.handoff,data)
        (HERE/'notebook.qmd').write_text(notebook)


if __name__=='__main__':
    main()
