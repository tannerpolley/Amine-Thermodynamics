"""Electrode readback and single-coordinate sensitivity fits."""
# ruff: noqa: E402
import copy
import os
import sys
from time import monotonic

from calculations import MDEA, OUT, WORK, Route, a, mdea_incumbent, r, save, transfer
from mdea_reference import route
from part_ii import active_bound_indices, target_identity
from receivers import AMP, donor
import mea as prior_mea
from mea_pressure import REFERENCE, expanded, replay
from reference_states_428 import request


def electrode(mapping, path, label):
    start = monotonic()
    model = r.bind(mapping).model
    source = prior_mea.OUT/'ph-digitization.json'
    series, = [x for x in r.read(source) if x['T_K']==313.15]
    assert len(series['points'])==197
    original = {x['loading']: x for x in r.read(REFERENCE/'F4/q5.json')['result']['rows']
                if x['T_K']==313.15 and x['symbol'] is not None}
    T,P = 313.15,101325.
    rows = []
    for point in series['points']:
        row = dict(source=series['source'],T_K=T,P_Pa=P,MEA_mass_fraction=.30,point=point)
        rows.append(row)
        problem = r.s._problem_from_request(request(mapping,T,point['loading']))
        assert problem.P==P
        result = r.eq.solve_equilibrium(model,problem)
        row.update(message=result.message,requested_tolerance_met=result.requested_tolerance_met,
                   residual=max(map(abs,result.residuals),default=None),feed_mol=problem.feed.values)
        if not result.requested_tolerance_met:
            continue
        raw,common,*_ = r.eq.reaction_activities(model,result)
        x = list(result.phase_mole_fractions(0))
        carbonate = x[prior_mea.C]
        pH = -common.species.log_activities[prior_mea.H]/r.math.log(10)
        raw_pH = -raw.species.log_activities[prior_mea.H]/r.math.log(10)
        carbon_total = sum(x[r.s.COMPONENT_IDS.index(c)] for c in
                           ('carbon-dioxide','carbamate-anion','bicarbonate-anion','carbonate-anion'))
        row.update(pH=pH, signed_delta=pH-point['pH'], raw_mole_fraction_pH=raw_pH,
                   common_molality_minus_raw=pH-raw_pH,
                   carbonate_share=carbonate/(carbonate+x[prior_mea.B]),
                   carbonate_total_carbon_share=carbonate/carbon_total,
                   historical_pH=original[point['loading']].get('pH'),
                   mole_fractions=x)
    save(OUT/f'D/electrode-{label}.json.gz',dict(seconds=monotonic()-start,rows=rows,wheel_sha256=r.SHA,
        input_sha256=r.s.sha256(source),parameter_sha256=r.s.sha256(path),
        limits='Electrode pressure and electrode-to-EOS activity scale unreported'))


def held(point, index, fraction):
    trial = copy.deepcopy(point)
    q = trial['coordinates'].pop(index)
    lo,hi = q['bounds']
    at_lower = abs(q['origin']-lo) < abs(q['origin']-hi)
    value = lo + fraction*(hi-lo) if at_lower else hi - fraction*(hi-lo)
    kind = q.get('kind','parameter')
    if kind=='parameter':
        updates = {target_identity(trial['parameters'],family,target): factor*value
                   for family,target,factor in q['targets']}
        trial['parameters'] = r.s.with_parameter_values(trial['parameters'],updates)
    else:
        reaction = next(rx for rows in trial['reactions'].values() for rx in rows if rx['name']==q['name'])
        law = reaction['correlation']
        if kind=='reaction_coordinate':
            law[q['coefficient']] = value
        elif kind=='reaction_enthalpy_shift':
            delta = value/r.epcsaft.GAS_CONSTANT_J_PER_MOL_K
            law['a'] += delta/q['pivot_temperature']
            law['b'] -= delta
        else:
            raise ValueError(kind)
    return trial,dict(coordinate=q,held_value=value,fraction=fraction)


def inward(case):
    start = monotonic()
    if case=='MDEA':
        point,source = mdea_incumbent('salt')
        run = route('salt','D/bounds')
    else:
        source = OUT/'AMP/free/selection.json.gz'
        point = r.read(source)['selected'][2]
        run = AMP.ExpandedPressure(AMP.DECLARATION,WORK/'D/bounds/AMP')
    values,ok,cost = run.replay(point)
    assert ok
    save(OUT/f'D/bounds/{case}/baseline.json.gz',dict(rows=values,objective=cost,
        parameter_sha256=r.s.sha256(source)))
    for i in active_bound_indices(point['coordinates']):
        for fraction in (.01,.05,.10):
            trial,meta = held(point,i,fraction)
            name = f'coordinate-{i}-{fraction:g}'
            tick = monotonic()
            endpoint,report = a.f.fit(name,trial,{},[],route=run,penalty_rows=[])
            artifact = dict(meta,point=endpoint,report=report,seconds=monotonic()-tick,parameter_sha256=r.s.sha256(source))
            if endpoint:
                run.reduce(endpoint)
                artifact['rows'] = run.result('data-rows.json')
                if case=='MDEA':
                    spec = run.bind(endpoint)
                    transfer.coexistence_421.fixed(run,spec)
                    artifact['matched_high_pressure'] = run.result('fixed-pressure.json')
                    artifact['targeted'] = transfer.objective.q3_checks(run,endpoint)
                else:
                    from phases import fixed
                    import reference_states_428
                    prior = r.read(reference_states_428.BUNDLE/'results/reference-states-428/amp.json')
                    spec = run.bind(endpoint)
                    stock = {k:v for k,v in zip(prior['species'],prior['feed_mol'],strict=True) if v and k!='carbon-dioxide'}
                    state = dict(T=prior['T_K'],stock=stock,a=prior['loading'])
                    artifact['worked_state'] = fixed(run,spec,state,prior['P_Pa'],dict(pair=prior['split']),assemblages=True)
            save(OUT/f'D/bounds/{case}/{name}.json.gz',artifact)
    save(OUT/f'D/bounds/{case}/timing.json',dict(seconds=monotonic()-start,active=active_bound_indices(point['coordinates'])))


def unbounded_mdea():
    started = monotonic()
    bounded, source = mdea_incumbent('salt')
    run = route('salt','D/unbounded')
    ref = run.load(run.config['starts'][2])
    trial = transfer.substitute(ref)
    T = run.config['k_bound']['temperature_K']
    trial['parameters'] = MDEA.rereference(trial['parameters'],T)
    q = next(q for q in trial['coordinates'] if q['identity'].startswith(MDEA.PAIR+'/a0'))
    q['origin'] = MDEA.k_at(trial['parameters'],T)
    endpoint,report = a.f.fit('fit',trial,{},[],route=run,penalty_rows=[])
    baseline = MDEA.binary_check(run,bounded)
    result = dict(point=endpoint,report=report,source_sha256=r.s.sha256(source),baseline=baseline,
                  k_423_bounded=MDEA.k_at(bounded['parameters'],T),released_coordinate=q,
                  stages=[r.read(p) for p in sorted((run.out/'fit').glob('stage-*/fit.json'))])
    if endpoint:
        run.reduce(endpoint)
        result.update(k_423_unbounded=MDEA.k_at(endpoint['parameters'],T),
                      properties=run.result('data-rows.json'),binary=MDEA.binary_check(run,endpoint))
    save(OUT/'D/unbounded-MDEA.json.gz',dict(result,seconds=monotonic()-started))


def amp_profile():
    import amp_profile as prior
    source = OUT/'AMP/free/selection.json.gz'
    original = r.read(a.ANALYSES/'round_5/results/A/expanded-free.json.gz')['slope_K']
    retained = OUT/'D'/'AMP-profile'
    def write(name, value, *, start=None):
        save(retained/name.removeprefix('A/'),dict(value,seconds=None if start is None else monotonic()-start))
    prior.calculate(WORK/'D/AMP-profile','expanded',endpoint=source,retain=write,extra_slopes=(-150.,original))


def amp_terms():
    import numpy as np
    folder = r.B/'results/split-diagnosis-433'
    sys.path.insert(0,str(folder))
    os.environ['EPCA_WHEEL_433'] = str(r.WHEEL)
    import decompose
    from reference_states_428 import source_log_k
    started = monotonic()
    source = OUT/'AMP/free/selection.json.gz'
    point = r.read(source)['selected'][2]
    baseline = r.read(transfer.amp_stability.AMP_REFERENCE)
    T,P,feed = (baseline[k] for k in ('T_K','P_Pa','feed_mol'))
    run = Route(AMP.DECLARATION,WORK/'D/worked-AMP')
    continuation = copy.deepcopy(point)
    law = next(rx['correlation'] for rx in continuation['reactions']['aqueous'] if rx['name']=='AMP-dissociation')
    T_ref = 353.22
    coeff = r.eq.ReactionLogPolynomial(**law)
    derivative = -coeff.b/T_ref**2+coeff.c/T_ref+coeff.d-2*coeff.e/T_ref**3+2*coeff.f*T_ref
    b = -T_ref*T_ref*derivative
    law.update(a=source_log_k(coeff,T_ref)-b/T_ref,b=b,c=0.,d=0.,e=0.,f=0.)
    cases = {'original':point,'constant-enthalpy R5':continuation,
             'slope only at fixed 353.22 K k':decompose.slope_move(point,-150.,T_ref)}
    out = {}
    for label,p in cases.items():
        spec = run.bind(p)
        try:
            problem,res,report = decompose.parent(spec,T,P,feed,baseline['phases'][0])
            attempts = decompose.try_attempts(spec,problem,res,report,baseline['phases'],baseline['trial'])
            out[label] = decompose.summary(spec,T,P,decompose.describe(res),baseline['phases'],baseline['trial'],
                                           np.array(report.standard_over_rt),attempts,report)
        except (RuntimeError,ValueError,AssertionError) as exc:
            out[label] = dict(refusal=str(exc))
    save(OUT/'D/AMP-worked-terms.json.gz',dict(rows=out,seconds=monotonic()-started,T_K=T,P_Pa=P,
         reference_temperature_K=T_ref,parent_endpoint_sha256=r.s.sha256(source),R5_continuation=law))


def cai():
    start = monotonic()
    mapping, selection = donor()
    label = selection['donor']
    source = REFERENCE/'F4/declaration.json' if label=='incumbent' else OUT/f'E/{label}/optimizer.json.gz'
    _, fitted, ties = a.mea_start('F4')
    a.f.OUT = r.OUT = WORK/'D/cai'
    def originals(spec):
        return expanded(spec) if selection['selected'] else spec.inputs['observations']['fitted']
    def rows(spec):
        return [dict(row,weight=.04) if row['group']=='Cai' else row for row in originals(spec)]
    prior, prior_ok, prior_cost = r.replay(mapping,rows)
    save(OUT/'D/cai/incumbent-alternative-weight.json.gz',dict(rows=prior,available=prior_ok,cost=prior_cost,selection=selection))
    endpoint,report = a.f.fit('cai',mapping,a.f.LITERATURE,fitted,ties,rows=rows)
    save(OUT/'D/cai/fit.json.gz',dict(point=endpoint,report=report,declared_source=r.s.sha256(source),seconds=monotonic()-start))
    if endpoint:
        original,ok,cost = r.replay(endpoint,originals)
        alternative,alt_ok,alt_cost = r.replay(endpoint,rows)
        save(OUT/'D/cai/assessment.json.gz',dict(original_rows=original,original_available=ok,original_cost=cost,
             alternative_rows=alternative,alternative_available=alt_ok,alternative_cost=alt_cost,
             parameters={k:[v,r.s.parameter_values(endpoint)[k]] for k,v in r.s.parameter_values(mapping).items()
                         if r.s.parameter_values(endpoint)[k]!=v},seconds=monotonic()-start))
        replay(endpoint,'cai-sensitivity')


if __name__=='__main__':
    a.study.reuse.bind_wheel()
    r.verify()
    arg = sys.argv[1]
    if arg=='electrode':
        path = REFERENCE/'F4/parameters.json'
        electrode(r.s.parameter_mapping(path),path,'incumbent')
    elif arg=='unbounded':
        unbounded_mdea()
    elif arg=='profile':
        amp_profile()
    elif arg=='terms':
        amp_terms()
    elif arg=='cai':
        r.OUT = a.OUT
        cai()
    else:
        inward(arg)
