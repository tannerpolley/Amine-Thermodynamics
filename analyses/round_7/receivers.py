"""DEA and AMP calibration with full-precision MEA carbamate inputs."""
# ruff: noqa: E402
from collections import Counter
import copy
import math
import sys
from time import monotonic

from calculations import OUT, WORK, Route, a, r, save, transfer
from part_ii import epcsaft

CARB = 'component/carbamate-anion/'
ENERGY = CARB+'dispersion_energy_over_k'
DIAMETER = CARB+'segment_diameter'
WATER = 'pair/carbamate-anion/water/k_ij'
DEA = transfer.dea.OLD / 'f2-carbamate-413-route.json'
AMP = transfer.amp
PRESSURE = {'Lawson':30,'SeoHong':16,'Lal':44}


def donor():
    selection = r.read(OUT/'E/selection.json')
    path = r.ROOT/selection['path']
    assert selection['parameter_sha256']==r.s.sha256(path) and selection['wheel_sha256']==r.SHA
    return r.s.parameter_mapping(path), selection


def inherited(point, *, amp, donor_record=None):
    mea, _ = donor() if donor_record is None else donor_record
    mapping = point['parameters']
    donor_values = r.s.parameter_values(mea)
    for ion in (a.salt.HCO3,a.salt.CO3):
        pair = next(p for p in mea['pairs'] if {p['component_id_a'],p['component_id_b']}=={a.salt.W,ion})
        a.salt.set_pair(mapping,pair['component_id_a'],pair['component_id_b'],pair['coefficients'][0])
    if amp:
        q = next(q for q in point['coordinates'] if q['identity']=='AMPCOO-segment-diameter')
        q['bounds'][0] = donor_values[DIAMETER]
        q['origin'] = max(q['origin'],q['bounds'][0])
        changes = {ENERGY:donor_values[ENERGY], WATER:donor_values[WATER]}
        changes.update({CARB+f:q['origin']*factor for f,_,factor in q['targets']})
        point['parameters'] = r.s.with_parameter_values(mapping,changes)
    else:
        assert (donor_values['component/monoethanolamine/segment_count'],
                donor_values['component/monoethanolamine/segment_diameter'])==(3.0353,3.0435)
        transfer.dea.carbamate(mapping,dict(sigma=donor_values[DIAMETER],epsilon=donor_values[ENERGY]))
    return point


def verify_binding(run, point, *, amp, donor_record=None):
    donor_record = donor() if donor_record is None else donor_record
    updated = inherited(copy.deepcopy(point),amp=amp,donor_record=donor_record)
    original = r.s.parameter_values(epcsaft.parameters.document_mapping(run.bind(point).parameters))
    expected = r.s.parameter_values(updated['parameters'])
    assert all(original[k]==v for k,v in expected.items())
    _, identity = donor_record
    values = {k:v for k,v in original.items() if k.startswith(CARB) or k==WATER}
    if amp:
        q = next(q for q in point['coordinates'] if q['identity']=='AMPCOO-segment-diameter')
        carried = next(x for x in updated['coordinates'] if x['identity']==q['identity'])
        assert q['bounds'][0]==carried['bounds'][0]
    else:
        assert all(values[CARB+f]==values[DIAMETER] for f in ('born_diameter','debye_huckel_diameter'))
        assert values[CARB+'packing_diameter']==.88*values[DIAMETER]
    return dict(donor=identity,parameters=r.s.parameter_fingerprint(point['parameters']),
                carbamate=values,
                coordinates=point['coordinates'])


class ExpandedDEA(Route):
    def bind(self, point):
        spec = super().bind(point)
        observations = spec.inputs['observations']
        fitted, comparisons = (observations[k] for k in ('fitted','comparisons'))
        promoted = [row for row in comparisons if row['group'] in ('SeoHong','Lal')]
        assert len(fitted)==80 and len(promoted)==60
        pressures = [row for row in fitted+promoted if row['group'] in PRESSURE]
        assert Counter(row['group'] for row in pressures)==PRESSURE
        for row in pressures:
            assert row['kind']=='partial_pressure' and row['arguments']['form']=='log_ratio'
            row.update(role='fitted',weight=1/(90*.09**2))
            if row['group']=='Lal':
                p = spec.problems[row['problem']]
                amounts = p.feed.values
                masses = {c['component_id']:c['fixed']['molar_mass']['value']['magnitude'] for c in point['parameters']['components']}
                w = masses['diethanolamine']*amounts['diethanolamine'] / (
                    masses['diethanolamine']*amounts['diethanolamine']+masses['water']*amounts['water'])
                rho = 1021+(w-.20)*(1035-1021)/.10
                assert math.isclose(w*rho,2000*masses['diethanolamine'],rel_tol=1e-12)
                assert row['arguments']['observed']==float(row['row']['p_CO2_kPa'])*1000
        observations['fitted'].extend(promoted)
        observations['comparisons'] = [row for row in comparisons if row not in promoted]
        assert sum(q['group']=='Lawson-394K' for q in observations['comparisons'])==7
        return spec


def fit_starts(run, starts, path):
    candidates = []
    for i, point in enumerate(starts):
        label = f'fit-{i}'
        run.write(f'{label}/start.json',point)
        result = transfer.data_fit(run,label,point)
        record = run.result(f'{label}/outcome.json')
        record['start'] = point
        record['start_replay'] = run.result(f'{label}/start-replay.json')
        save(path/f'{label}.json.gz',record)
        if result:
            candidates.append(result)
    return min(candidates,default=None)


def dea():
    started = monotonic()
    path = OUT/'F'
    old = Route(DEA,WORK/'F/original')
    fit = ExpandedDEA(DEA,WORK/'F/expanded')
    archive = transfer.DEABASE.parent/'salt-anchored-435/campaign/selection.json.gz'
    comparison = r.read(archive)['chosen']['parameters']
    donors = donor()[1]
    transfer_start = monotonic()
    base_starts = [inherited(old.start(q),amp=False) for q in old.config['starts']]
    if donors['donor']=='incumbent':
        identity = verify_binding(old,comparison,amp=False)
        _,ok,cost = old.replay(comparison)
        assert ok and math.isclose(cost,r.read(archive)['chosen']['cost'],rel_tol=1e-10)
        save(path/'original-design.json.gz',dict(point=comparison,objective=cost,identity=identity,
               elapsed_s=monotonic()-transfer_start,replayed_435=True))
    else:
        base = fit_starts(old,base_starts,path/'original-design')
        save(path/'original-design.json.gz',dict(selected=base,elapsed_s=monotonic()-transfer_start,
             identity=verify_binding(old,base[2],amp=False) if base else None))
    old_values = fit.replay(comparison)
    save(path/'incumbent-expanded.json.gz',dict(rows=old_values[0],available=old_values[1],cost=old_values[2]))
    starts = [inherited(fit.start(q),amp=False) for q in fit.config['starts']]
    assert all(len(p['coordinates'])==4 for p in starts)
    selected = fit_starts(fit,starts,path)
    save(path/'selection.json.gz',dict(selected=selected,seconds=monotonic()-started,fit_projection_s=282))
    if not selected:
        return
    endpoint = selected[2]
    identity = verify_binding(fit,endpoint,amp=False)
    transfer.score(fit,endpoint,'DEA')
    old.reduce(endpoint)
    save(path/'assessment.json.gz',dict(identity=identity,original_design=old.result('data-rows.json'),
         expanded_design=fit.result('data-rows.json'),uncertainty=fit.result('conditional-uncertainty.json'),
         deviations=fit.result('deviations.json')))
    states = old.states(old.bind(endpoint))
    transfer.search(old,endpoint,states)
    save(path/'search-outcome.json.gz',old.result('search-outcome.json'))
    save(path/'search-rows.json.gz',old.result('search-0.json'))
    save(path/'timing.json',dict(seconds=monotonic()-started,prior_design_projection_s=282))


def amp():
    started = monotonic()
    free,fixed = [r.read(AMP.ENDPOINTS/label/'parameters.json') for label in AMP.ORIGINAL]
    slope = next(q for q in free['coordinates'] if q['identity']=='AMPH-water-slope')
    promoted = dict(fixed, coordinates=[*fixed['coordinates'],dict(slope,origin=-150.)])
    for family, starts in (('free',(free,promoted)),('fixed',(fixed,AMP.fixed_slope(free,-150.)))):
        path = OUT/'AMP'/family
        fit = AMP.ExpandedPressure(AMP.DECLARATION,WORK/'AMP'/family)
        options = [inherited(copy.deepcopy(point),amp=True) for point in starts]
        selected = fit_starts(fit,options,path)
        save(path/'selection.json.gz',dict(selected=selected,elapsed_s=monotonic()-started))
        if not selected:
            continue
        point = selected[2]
        identity = verify_binding(fit,point,amp=True)
        transfer.score(fit,point,'AMP')
        save(path/'assessment.json.gz',dict(identity=identity,rows=fit.result('data-rows.json'),
             uncertainty=fit.result('conditional-uncertainty.json'),deviations=fit.result('deviations.json')))
        for protocol in ('native','supplied'):
            phase = Route(AMP.DECLARATION,WORK/'AMP'/family/protocol)
            states = phase.states(phase.bind(free))
            assert len(states)==666
            bank = transfer.amp_stability.trial_bank(phase) if protocol=='supplied' else {'trials':[]}
            if protocol=='supplied':
                assert transfer.amp_stability.bank_hash(bank)==transfer.amp_stability.TRIAL_SHA
            transfer.search(phase,point,states,trials=bank['trials']+bank.get('supplied_trials',[]))
            save(path/f'{protocol}-outcome.json.gz',phase.result('search-outcome.json'))
            save(path/f'{protocol}-rows.json.gz',phase.result('search-0.json'))
    save(OUT/'AMP/timing.json',dict(seconds=monotonic()-started,projected_s=714))


if __name__=='__main__':
    a.study.reuse.bind_wheel()
    r.verify()
    {'DEA':dea,'AMP':amp}[sys.argv[1]]()
