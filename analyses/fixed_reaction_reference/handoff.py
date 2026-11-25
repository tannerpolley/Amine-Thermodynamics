"""Recompute #440 comparisons from the archived and fixed-reference contributors."""
# ruff: noqa: E402
from collections import Counter
from functools import cache
from hashlib import sha256
import json
from math import fsum, log, sqrt
import sys

from refit import (BASE, COUNTS, HERE, OUT, P_REF, REPLAY_TOLERANCE, configured, fingerprint, r,
                   remove_reference_pressure, row_manifest, rms, save, starts, start_vector, qmc, SEED, np)
from round_8.records import NAMES, blob
from round_8.reductions import phase_outcome, witness_direction

HANDOFF = HERE/'manuscript-handoff.json'
R7 = 'analyses/round_7/'
R8 = 'analyses/round_8/'


def original(path):
    return json.loads(blob(path,BASE))


@cache
def archived(path):
    assert (r.ROOT/path).read_bytes()==blob(path,BASE), f'changed archived contributor: {path}'
    return r.read(r.ROOT/path)


def summary(rows, pressure=False):
    good = [q for q in rows if q.get('status')=='Available' and q.get('requested_tolerance_met',True)
            and q.get('value') is not None]
    ratios = [q['value']/q['observed'] for q in good if q['observed']]
    result = dict(rows=len(rows),available=len(good),point_count=len(ratios),
                  fitted=sum(q.get('role')=='fitted' for q in rows))
    if ratios:
        result.update(AARD_percent=100*fsum(abs(x-1) for x in ratios)/len(ratios),
                      bias_percent=100*fsum(x-1 for x in ratios)/len(ratios))
        signed = [q['value']-q['observed'] for q in good]
        result.update(mean_abs_error=fsum(map(abs,signed))/len(signed),
                      mean_signed_error_predicted_minus_observed=fsum(signed)/len(signed))
        if pressure and all(x>0 for x in ratios):
            result['log_RMSE'] = sqrt(fsum(log(x)**2 for x in ratios)/len(ratios))
    return result


class Quantities:
    def __init__(self):
        self.items = {}
        self.files = {}
        self.attempts = {}
        self.selections = {}
        self.old = original(R7+'manuscript-handoff.json')['quantities']

    def read(self, path):
        if path not in self.files:
            absolute = OUT/path
            self.files[path] = (r.read(absolute), sha256(absolute.read_bytes()).hexdigest()) if absolute.is_file() else (None,None)
        return self.files[path][0]

    def reference(self,path):
        return dict(path=str((OUT/path).relative_to(r.ROOT)),sha256=self.files[path][1])

    def quantity(self,key,old,new,*,unit='1',population=None,pressure_basis=None,sources=(),old_source=None,
                 old_field=None,endpoint=None,independent=False,disposition=None):
        source = {'revision':BASE,'path':old_source,'field':old_field,
                  'sha256':sha256(blob(old_source,BASE)).hexdigest() if old_source else None}
        refs = [self.reference(p) for p in sources]
        numerical = all(isinstance(x,(int,float)) and not isinstance(x,bool) for x in (old,new))
        changed = new-old if numerical else None
        self.items[key] = dict(old=old,new=new,unit=unit,population=population,pressure_basis=pressure_basis,
                               absolute_change=changed,percent_change=100*changed/old if numerical and old else None,
                               transition=[old,new] if isinstance(old,str) and new is not None else None,
                               disposition=disposition or ('independent contributor' if independent else 'open' if new is None else 'replayed'),
                               old_contributor=source,new_contributors=refs,endpoint_fingerprint=endpoint)

    def fit(self,design):
        base = f'{design}/reference-control.json.gz'
        control = self.read(base)
        if control is None:
            return
        manifests = f'{design}/manifest.json.gz'
        declaration = self.read(manifests)
        archived = control['source']
        old = self.cost(control['tracking'],f'{design} tracking objective')
        fixed = self.cost(control['fixed_at_old_parameters'],f'{design} objective at old parameters')
        assert abs(old-archived['objective'])<=REPLAY_TOLERANCE[design]*abs(old), f'{design} tracking objective'
        share = dict(population=dict(fitted=COUNTS[design],comparison=0),old_source=archived['path'])
        self.quantity(f'{design} objective at old parameters',old,fixed,sources=(base,),**share)
        if declaration is None:
            return
        assert declaration['wheel']==r.SHA and declaration['engine_commit']==r.COMMIT
        assert declaration['source']==archived and declaration['fixed_reference_pressure_pa']==P_REF
        tracking,old_point,_ = configured(design,'handoff-tracking',fixed=False)
        new,point,_ = configured(design,'handoff-fixed')
        old_rows,fixed_rows = row_manifest(tracking.bind(old_point)),row_manifest(new.bind(point))
        assert fingerprint(old_rows)==declaration['tracking_row_fingerprint'], f'{design} tracking fitted declaration'
        assert fingerprint(fixed_rows)==declaration['fixed_row_fingerprint'], f'{design} fixed fitted declaration'
        assert remove_reference_pressure(old_rows)==remove_reference_pressure(fixed_rows), f'{design} fitted row invariants'
        spec = new.bind(declaration['start_A_declaration'])
        assert declaration['rows']==row_manifest(spec), f'{design} bound manifest'
        actual_starts,_ = starts(spec)
        assert actual_starts==declaration['starts'], f'{design} Engine start readbacks'
        if design!='MEA':
            donor = declaration['donor']
            donor_path = f'MEA/{self.selections["MEA"][0]}.json.gz'
            donor_record = self.read(donor_path)
            assert donor['endpoint']==donor_record['endpoint_fingerprint'] and donor['sha256']==r.s.sha256(OUT/donor_path), f'{design} MEA donor'
            assert donor['parameter_sha256']==fingerprint(donor_record['endpoint']['parameters']), f'{design} donor parameters'
            self.quantity(f'{design} donor binding',None,dict(donor,salt_pairs=declaration['salt_pairs']),
                          sources=(manifests,donor_path),endpoint=donor['endpoint'])
        distances = {pair:sqrt(fsum((x-y)**2 for x,y in zip(
            declaration['starts'][pair[0]]['normalized'],declaration['starts'][pair[1]]['normalized'],strict=True))/
            len(declaration['coordinate_order'])) for pair in ('AB','AC','BC')}
        assert all(abs(v-declaration['pair_rms_distances'][k])<=4e-16 and v>=.2 for k,v in distances.items())
        self.quantity(f'{design} start distances',None,distances,sources=(manifests,))
        replacement_path = f'{design}/replacement-starts.json.gz'
        replacement = self.read(replacement_path)
        if replacement:
            assert replacement['wheel']==r.SHA and replacement['manifest_fingerprint']==fingerprint(declaration)
            accepted = {k:actual_starts[k] for k in replacement['accepted_original']}
            assert list(accepted)==[k for k in 'ABC' if self.read(f'{design}/{k}.json.gz')['report']['status']
                                    !='initial_evaluation_failed']
            native = spec.coordinates()
            lower,upper = (np.array([getattr(q,k) for q in native]) for k in ('lower','upper'))
            candidates = qmc.LatinHypercube(d=len(native),seed=SEED).random(64)
            remaining = set(range(64))-{q['draw'] for q in actual_starts.values()}
            for label,item in replacement['draws'].items():
                d = np.min([rms(candidates,v['normalized']) for v in accepted.values()],axis=0)
                i = max(remaining,key=lambda j:(d[j],-j))
                remaining.remove(i)
                vector = start_vector(spec,i,lower+(upper-lower)*candidates[i])
                separation = {k:float(rms(vector['normalized'],v['normalized'])) for k,v in accepted.items()}
                assert label==f'LHS-{i:02d}' and vector==item['start'], f'{design} {label} Latin hypercube readback'
                assert min(separation.values())>=.20 and separation==item['pair_rms_distances'], f'{design} {label} start separation'
                valid = item.get('statuses')==['Available']*COUNTS[design] and len(item.get('predictions',[]))==COUNTS[design]
                assert valid==(item['disposition']=='eligible'), f'{design} {label} initial evaluation'
                evaluation = {k:v for k,v in item.items() if k not in ('statuses','predictions')}
                evaluation['available_rows'] = item.get('statuses',[]).count('Available') if valid else None
                self.quantity(f'{design} {label} start screening',None,evaluation,unit='residual evaluation',
                              sources=(manifests,replacement_path),
                              disposition='replayed' if valid else 'refused at initial evaluation')
                if valid:
                    accepted[label] = actual_starts[label] = vector
            if 'exhausted' in replacement:
                assert replacement['accepted']==list(accepted) and replacement['remaining']==sorted(remaining)
                if replacement['exhausted']:
                    assert len(accepted)<3 and all(min(rms(candidates[i],v['normalized']) for v in accepted.values())<.20
                                                   for i in remaining), f'{design} premature LHS exhaustion'
            self.quantity(f'{design} admitted-start distances',None,
                          {x+'/'+y:float(rms(accepted[x]['normalized'],accepted[y]['normalized']))
                           for j,x in enumerate(accepted) for y in list(accepted)[j+1:]},
                          sources=(manifests,replacement_path))
        attempts, eligible = {}, {}
        for label in (*actual_starts,*(['A-loose'] if design=='MEA' else [])):
            path = f'{design}/{label}.json.gz'
            q = self.read(path)
            if q is None:
                self.quantity(f'{design} {label} fit',None,None,sources=(manifests,replacement_path),
                              disposition='open')
                continue
            start = 'A' if label=='A-loose' else label
            assert q['start']==label and q['optimizer_start']==actual_starts[start]['optimizer'], f'{design} {label} start identity'
            assert q['manifest_fingerprint']==fingerprint(declaration) and q['wheel']==r.SHA, f'{design} {label} manifest'
            report = q['report']
            cost, replay_pass, endpoint = None, False, q.get('endpoint_fingerprint')
            if endpoint:
                assert endpoint==fingerprint(q['endpoint']), f'{design} {label} endpoint fingerprint'
                assert all(rx['reference']['reference_pressure_pa']==P_REF
                           for group in q['endpoint']['reactions'].values() for rx in group), f'{design} {label} references'
            if q.get('replay'):
                cost = self.cost(q['replay'],f'{design} {label} objective')
                native = report['data_cost'] if report['data_cost'] is not None else report['final_cost']
                replay_pass = cost is not None and abs(cost-native)<=REPLAY_TOLERANCE[design]*abs(native)
                assert replay_pass==q.get('replay_passed'), f'{design} {label} independent objective replay'
            grad_norm, active, solver_gradient = self.stationarity(q)
            gradient_tolerance = q['controls']['gradient_tolerance']
            if solver_gradient is not None:
                native_gradient = report['covariance']['projected_gradient_norm']
                assert abs(solver_gradient-native_gradient)<=1e-8, f'{design} {label} optimizer gradient replay'
            probe_path = f'{design}/stationarity/{label}.json.gz'
            probe = self.read(probe_path)
            if probe and probe['endpoint']==endpoint:
                for j,t in enumerate(probe['trials']):
                    trial_cost = self.cost(t['replay'],f'{design} {label} descent probe {j}') if 'replay' in t else None
                    assert t['relative_reduction']==((cost-trial_cost)/cost if trial_cost is not None else None)
                self.quantity(f'{design} {label} descent probe',None,
                    dict(predicted=probe['relative_linearized_reduction'],
                         measured=[t['relative_reduction'] for t in probe['trials']]),
                    sources=(path,probe_path),endpoint=endpoint)
            chain = [q]
            while 'previous_stage' in chain[-1]:
                chain.append(chain[-1]['previous_stage'])
            chain.reverse()
            start_report = chain[0]['report']
            stages = [dict(status=v['report']['status'],initial_cost=v['report']['initial_cost'],
                           objective=(v.get('replay') or {}).get('cost'),iterations=v['report']['iterations'],
                           fit_seconds=v['fit_seconds'],replay_seconds=v.get('replay_seconds'),
                           diagnostic_seconds=v.get('diagnostic_seconds')) for v in chain]
            check_path = f'{design}/initial/{label}.json.gz'
            initial = self.read(check_path)
            attempts[label] = dict(status=report['status'],initial_cost=start_report['initial_cost'] if start_report['residual_evaluations'] else None,
                                   objective=cost,projected_gradient_inf=grad_norm,active_bounds=active,
                                   solver_scale_projected_gradient_inf=solver_gradient,gradient_tolerance=gradient_tolerance,
                                   termination=report['message'],draw=actual_starts[start]['draw'],
                                   stationarity_met=(solver_gradient<=q['controls']['gradient_tolerance']
                                                     if solver_gradient is not None else None),
                                   fit_seconds=fsum(v['fit_seconds'] for v in stages),
                                   replay_seconds=fsum(v['replay_seconds'] or 0. for v in stages) if endpoint else None,
                                   iterations=sum(v['iterations'] for v in stages),failure=report['failures'][:1],endpoint=endpoint,
                                   attempted=(q.get('replay') or (initial or {}).get('replay') or {}).get('attempted'),
                                   refused=(q.get('replay') or (initial or {}).get('replay') or {}).get('refused'),
                                   fit_stages=stages)
            for k in ('status','objective','projected_gradient_inf','solver_scale_projected_gradient_inf','stationarity_met','active_bounds'):
                self.quantity(f'{design} {label} {k}',None,attempts[label][k],sources=(path,manifests)+((replacement_path,) if label.startswith('LHS-') else ()),endpoint=endpoint,
                              disposition='refused at initial evaluation' if report['status']=='initial_evaluation_failed' else None,**share)
            if replay_pass and report['status']=='converged' and label in actual_starts:
                eligible[label] = (cost,q)
        self.attempts[design] = attempts
        selection_path = f'{design}/selection.json'
        selection = self.read(selection_path)
        selected, endpoint, cost = None,None,None
        if selection is not None:
            assert all(k in attempts for k in 'ABC'), f'{design} missing declared attempt'
            best = min((v[0] for v in eligible.values()),default=None)
            tied = [k for k,(v,q) in eligible.items() if abs(v-best)<=declaration['fit_controls']['function_tolerance']*best]
            selected = tied[0] if tied else None
            if selected:
                cost, q = eligible[selected]
                endpoint = q['endpoint_fingerprint']
            assert (selected,tied,endpoint,cost)==(selection['selected'],selection['tied'],selection['endpoint_fingerprint'],
                                                selection['cost']), f'{design} selected objective or endpoint fingerprint'
        self.selections[design] = (selected,endpoint)
        sources = (selection_path,base,manifests)+((f'{design}/{selected}.json.gz',) if selected else ())
        if design=='MDEA' and (OUT/'MDEA/stationarity/A-continuation.json.gz').exists() and selected=='A':
            sources = (*sources,'MDEA/stationarity/A-continuation.json.gz')
            disposition = 'undecided' if self.read(sources[-1])['report']['status']!='converged' else None
        else:
            disposition = None
        self.quantity(f'{design} selected objective',old,cost,sources=sources,endpoint=endpoint,
                      disposition=disposition,**share)
        if selected:
            q = self.read(f'{design}/{selected}.json.gz')
            uncertainty = q['diagnostics'].get('uncertainty',{})
            old_coordinates = {d['identity']:d for d in declaration['prior_declaration']['coordinates']}
            new_coordinates = {d['identity']:d for d in q['endpoint']['coordinates']}
            assert set(old_coordinates)==set(new_coordinates), f'{design} coordinate mapping'
            for k,d in new_coordinates.items():
                old = old_coordinates[k]
                value = old['bounds'][0]-d['bounds'][0] if d.get('kind')=='reaction_enthalpy_shift' else d['origin']
                self.quantity(f'{design} selected parameter {k}',old['origin'],value,
                    sources=sources,endpoint=endpoint,unit=d.get('unit','see bound declaration'),**share)
                if k in uncertainty.get('conditional_standard_error',{}):
                    self.quantity(f'{design} conditional standard error {k}',None,uncertainty['conditional_standard_error'][k],
                                  sources=sources,endpoint=endpoint,unit=d.get('unit','coordinate units'),**share)
            if design in ('DEA','AMP_free','AMP_fixed'):
                spectra = [r.s.parameter_values(v['parameters']) for v in (declaration['prior_declaration'],q['endpoint'])]
                for text,family,unit in (('carbamate energy divided by k','dispersion_energy_over_k','K'),
                                         ('carbamate segment diameter','segment_diameter','Å')):
                    identity = f'component/carbamate-anion/{family}'
                    value = [v[identity] for v in spectra]
                    self.quantity(f'{design} {text}',*value,unit=unit,sources=sources,old_source=archived['path'],endpoint=endpoint)
                if design.startswith('AMP'):
                    identity = 'pair/protonated-aminomethylpropanol/water/k_ij/reciprocal_temperature_slope'
                    values = [v[identity] for v in spectra]
                    self.quantity(f'C4 {design} reciprocal temperature slope',*values,unit='K',
                                  sources=sources,old_source=archived['path'],endpoint=endpoint)
            spreads = {}
            for label,(_cost,record) in eligible.items():
                if label==selected:
                    continue
                other = {row['identity']:row for row in record['replay']['rows']}
                for group in sorted({row['group'] for row in q['replay']['rows']}):
                    left = [row for row in q['replay']['rows'] if row['group']==group]
                    values = [(x['value'],other[x['identity']]['value']) for x in left]
                    spreads[f'{label} {group}'] = dict(rows=len(left),unit=left[0]['unit'],
                        max_absolute=max(abs(x-y) for x,y in values),
                        max_relative=max((abs(y/x-1) for x,y in values if x),default=None))
                differences = {d['identity']:d['origin'] for d in record['endpoint']['coordinates']}
                spreads[f'{label} endpoint coordinate RMS'] = sqrt(fsum(
                    ((d['origin']-differences[k])/(d['bounds'][1]-d['bounds'][0]))**2 for k,d in new_coordinates.items())/len(new_coordinates))
            self.quantity(f'C6 {design} fitted-row endpoint prediction spread',None,spreads,
                          sources=sources+tuple(f'{design}/{k}.json.gz' for k in eligible if k!=selected),
                          population=COUNTS[design],endpoint=endpoint)

    @staticmethod
    def cost(data, key):
        rows = data['rows']
        cost = .5*fsum(q['weighted_residual']**2 for q in rows) if all('weighted_residual' in q for q in rows) else None
        assert (cost is None and data['cost'] is None or cost is not None and
                abs(cost-data['cost'])<=1e-14*abs(cost)), f'{key}: changed objective contributor'
        assert len(rows)==data['attempted'] and sum('weighted_residual' not in q for q in rows)==data['refused']
        return data['cost']

    @staticmethod
    def stationarity(q):
        data = q.get('diagnostics',{})
        if 'jacobian_bound_normalized' not in data:
            return None,None,None
        coordinates = q['endpoint']['coordinates']
        rows = q['replay']['rows']
        residual = [r['weighted_residual'] for r in rows]
        products = [[a*b for a,b in zip(col,residual,strict=True)]
                    for col in zip(*data['jacobian_bound_normalized'],strict=True)]
        gradients = [fsum(col) for col in products]
        bound, projected = {},[]
        for d,g in zip(coordinates,gradients,strict=True):
            lower,upper = d['bounds']
            side = ('lower' if d['origin']-lower<=1e-6*d['scale'] else
                    'upper' if upper-d['origin']<=1e-6*d['scale'] else None)
            if side:
                bound[d['identity']]=side
            projected.append(0. if side=='lower' and g>0 or side=='upper' and g<0 else g)
        norm = max(map(abs,projected))
        # The archived dot uses BLAS summation. Bound its roundoff against the fsum replay.
        n_eps = len(residual)*sys.float_info.epsilon
        roundoff = n_eps/(1-n_eps)*max(fsum(map(abs,col)) for col in products)
        assert bound==data['active_bounds'] and abs(norm-data['projected_gradient_inf'])<=roundoff, q.get('start')
        normalized = [abs(min((d['bounds'][1]-d['origin'])/d['scale'],
                              max((d['bounds'][0]-d['origin'])/d['scale'],
                                  -g*d['scale']/(d['bounds'][1]-d['bounds'][0]))))
                      for g,d in zip(gradients,coordinates,strict=True)]
        return data['projected_gradient_inf'], bound,max(normalized)

    def properties(self,design):
        selected,endpoint = self.selections.get(design,(None,None))
        path = ('E/MEA/replay.json.gz' if design=='MEA' else
                f'{design}/property-comparisons/selected.json.gz'
                if (OUT/f'{design}/property-comparisons/selected.json.gz').exists() else f'{design}/properties.json.gz')
        result = self.read(path)
        if result:
            assert result.get('endpoint_fingerprint',endpoint)==endpoint, f'{design} properties endpoint fingerprint'
            if design=='MEA':
                point = self.read(f'MEA/{selected}.json.gz')['endpoint']
                assert result['summary']['parameter_fingerprint']==r.s.parameter_fingerprint(point['parameters']), 'MEA pressure endpoint'
        folders = {'MEA':('E/incumbent/replay.json.gz','rows'),'DEA':('F/assessment.json.gz','expanded_design'),
                   'MDEA':('C/salt/refit.json.gz','rows'),'AMP_free':('AMP/free/assessment.json.gz','rows'),
                   'AMP_fixed':('AMP/fixed/assessment.json.gz','rows')}
        p,field = folders[design]
        old_file = R7+'results/'+p
        old = archived(old_file)[field]
        new = result['rows'] if result else []
        if design=='MEA':
            old,new = ([dict(q,role='fitted' if i<COUNTS[design] else 'comparison') for i,q in enumerate(pool)]
                       for pool in (old,new))
        groups = sorted({(q['group'],q.get('unit') or 'unspecified') for q in old})
        for group,unit in groups:
            left,right = ([q for q in pool if q['group']==group and (q.get('unit') or 'unspecified')==unit] for pool in (old,new))
            if left and right:
                assert {x['identity']:x['observed'] for x in left}=={q['identity']:q['observed'] for q in right}, f'{design} {group} row keys'
            for side in ('all','matched') if right else ('all',):
                if side=='matched':
                    keys = set.intersection(*[{q['identity'] for q in pool if q.get('status')=='Available' and
                                               q.get('requested_tolerance_met',True) and q.get('value') is not None}
                                              for pool in (left,right)])
                    left,right = ([q for q in pool if q['identity'] in keys] for pool in (left,right))
                a,b = (summary(pool,pressure=unit=='Pa') if pool else {} for pool in (left,right))
                counts = {k:dict(rows=v.get('rows'),available=v.get('available'),fitted=v.get('fitted'))
                          for k,v in (('old',a),('new',b))}
                for statistic in ('AARD_percent','bias_percent','log_RMSE','available','mean_abs_error',
                                  'mean_signed_error_predicted_minus_observed'):
                    if statistic not in a:
                        continue
                    self.quantity(f'{design} {group} {unit} {side} {statistic}',a[statistic],b.get(statistic),
                        unit='%' if statistic.endswith('percent') else 'rows' if statistic=='available' else
                             unit if 'error' in statistic else '1',
                        sources=(path,),old_source=old_file,old_field=field,population=counts,endpoint=endpoint,
                        pressure_basis='source row and observation basis retained; pressure residuals use calculated pressure')
        if design=='DEA' and new:
            for group in ('Lawson','Lawson-394K','SeoHong','Lal','Carson'):
                for law in ('carbamate-hydrolysis','DEA-dissociation'):
                    for outside in (False,True):
                        subsets = [[q for q in rows if q['group']==group and q['outside_ranges'].get(law) is outside]
                                   for rows in (old,new)]
                        before,after = (summary(rows).get('AARD_percent') for rows in subsets)
                        if before is not None:
                            self.quantity(f'DEA {group} {"outside" if outside else "inside"} {law} AARD',before,after,
                                          unit='%',population=len(subsets[0]),sources=(path,),old_source=old_file,endpoint=endpoint,
                                          pressure_basis='source observation pressure; group range checked per reaction')
            count = [sum(q['group']=='Horstmann' and q.get('value') is not None and q['value']>0 and q['observed']<0 for q in rows)
                     for rows in (old,new)]
            self.quantity('DEA Horstmann positive predictions for negative excess enthalpy',*count,unit='rows',
                          sources=(path,),old_source=old_file,endpoint=endpoint)
            density = [q for q in new if q['group']=='Weiland']
            old_density = [q for q in old if q['group']=='Weiland']
            control_path = f'DEA/controls/{selected}.json.gz'
            control = self.read(control_path)
            if control and 'rows' in control:
                keys = {k.removesuffix(':problem') for k in control['rows']}
                for label in ('all 44 density samples','four historically split feeds'):
                    left,right = (pool if label.startswith('all') else [q for q in pool if q['identity'] in keys]
                                  for pool in (old_density,density))
                    self.quantity(f'C3 DEA AARD {label}',summary(left)['AARD_percent'],summary(right)['AARD_percent'],
                                  unit='%',population=len(left),sources=(path,control_path),old_source=old_file,endpoint=endpoint)
            p = 'DEA/screen/selected/declared/summary.json.gz'
            screen = self.read(p)
            if screen:
                baseline = R7+'results/F/search-outcome.json.gz'
                prior = archived(baseline)['confirmed']
                current = [q['key'] for q in screen['classifications'] if any(a['confirmed'] for a in q['attempts'])]
                sets = [{k.removesuffix(':problem') for k in keys} for keys in (prior,current)]
                old_score,new_score = (summary([q for q in rows if q['identity'] in keys])['AARD_percent']
                                       for rows,keys in zip((old_density,density),sets,strict=True))
                self.quantity('C3 DEA AARD on split feeds in each model',old_score,new_score,unit='%',
                              population=dict(old=len(prior),new=len(current),tested_density_rows=44),
                              sources=(path,p),old_source=baseline,endpoint=endpoint,
                              pressure_basis='assigned absolute density-cell pressure')
                self.quantity('C3 DEA split-feed comparison',sorted(prior),sorted(current),unit='state IDs',
                              population=44,sources=(p,),old_source=baseline,endpoint=endpoint,
                              pressure_basis='assigned absolute density-cell pressure')
                point = self.read(f'DEA/{selected}.json.gz')['endpoint']
                species_path = 'analyses/dea_transfer/inputs/part-ii-346/f2-carbamate-413-route.json'
                masses = {q['component_id']:q['fixed']['molar_mass']['value']['magnitude']
                          for q in point['parameters']['components']}
                species = original(species_path)['species']
                for key in sorted(set(prior)|set(current)):
                    identity = key.removesuffix(':problem')
                    left,right = (next(q for q in rows if q['identity']==identity) for rows in (old_density,density))
                    entries = [next((q for q in source if q['key']==key),{})
                               for source in (archived(baseline)['classifications'],screen['classifications'])]
                    values = []
                    for row,entry in zip((left,right),entries,strict=True):
                        states = [dict(density_kg_m3=rho*fsum(masses[k]*x for k,x in zip(species,composition,strict=True)),
                                       mole_fraction=n/fsum(attempt['amounts_mol']))
                                  for attempt in entry.get('attempts',[]) if attempt['confirmed']
                                  for rho,composition,n in zip(attempt['densities_mol_m3'],attempt['phases'],attempt['amounts_mol'],strict=True)]
                        values.append(dict(single_liquid_density=row['value'],observed_density=row['observed'],daughters=states))
                    self.quantity(f'C3 DEA {key} single liquid and daughters',*values,unit='kg/m³ and mole fraction',
                                  sources=(p,path,f'DEA/{selected}.json.gz'),old_source=baseline,endpoint=endpoint,
                                  pressure_basis='assigned absolute density-cell pressure',population=1)
        if design=='MDEA' and new:
            self.mdea_deviations(old,new,path,old_file)
        if design.startswith('AMP') and new:
            added = ('hartono-2021-supplemental','tong')
            counts = [dict(Counter(q['group'] for q in rows if q['group'] in added and q['role']=='fitted'))
                      for rows in (old,new)]
            self.quantity(f'C4 {design} added pressure rows',*counts,unit='rows',population=sum(counts[0].values()),
                          sources=(path,),endpoint=endpoint,old_source=old_file,pressure_basis='measured pressure')

    def mdea_deviations(self,old,new,path,old_file):
        selected,endpoint = self.selections['MDEA']
        for name,groups in (('loaded total',{'Kuranov'}),('all fitted pressures',{'Kuranov','Kuranov-binary','Kim'}),
                            ('development partials',{'Ermatchkov','Xiao'})):
            self.mdea_scores(name,old,new,lambda q:q['group'] in groups,path,old_file,endpoint)
        for outside in (False,True):
            for group in ('Kuranov','Kuranov-413K','Ermatchkov','Xiao','corrected-Kamps','Sedighi','Zheng'):
                self.mdea_scores(f'{group} outside R5 = {outside}',old,new,
                    lambda q:q['group']==group and q['outside_ranges'].get('MDEA-dissociation') is outside,path,old_file,endpoint)
        fit_path = f'MDEA/{selected}.json.gz'
        fitted = {q['identity']:q for q in self.read(fit_path)['replay']['rows']}
        for scoring,objective in archived(old_file)['objective'].items():
            rows = objective['rows']
            assert set(fitted)=={row['identity'] for row in rows}
            costs = [(q['group'],q['cost'],0.5*q['weight']*fitted[q['identity']]['residual']**2) for q in rows]
            totals = [fsum(q[i] for q in costs) for i in (1,2)]
            assert abs(totals[0]-objective['objective'])<1e-10
            self.quantity(f'C5 MDEA salt refit {scoring} objective',*totals,sources=(fit_path,path),
                          old_source=old_file,population=len(rows),endpoint=endpoint)
            for name,groups in (('loaded pressure',{'Kuranov'}),('density',{'loaded-density','unloaded-density'})):
                family = [q for q in costs if q[0] in groups]
                values = [100*fsum(q[i] for q in family)/totals[i-1] for i in (1,2)]
                self.quantity(f'C5 MDEA salt refit {scoring} {name} cost share',*values,unit='%',
                              sources=(fit_path,path),old_source=old_file,population=len(family),endpoint=endpoint)

    def mdea_scores(self,name,old,new,predicate,path,old_file,endpoint):
        left,right = ([q for q in rows if predicate(q)] for rows in (old,new))
        assert {q['identity'] for q in left}=={q['identity'] for q in right}
        if left:
            a,b = (summary(rows,True) for rows in (left,right))
            for metric in ('AARD_percent','bias_percent','log_RMSE','available'):
                self.quantity(f'C5 MDEA salt refit {name} {metric}',a.get(metric),b.get(metric),
                              unit='%' if metric.endswith('percent') else 'rows' if metric=='available' else '1',
                              sources=(path,),old_source=old_file,endpoint=endpoint,population=dict(rows=len(left),fitted=a['fitted']),
                              pressure_basis='same source rows; calculated bubble pressure')

    def phases(self,design):
        selected,endpoint = self.selections.get(design,(None,None))
        paths = {'MDEA':R8+'results/C6-replays.json.gz','AMP_free':R8+'results/C4-replays.json.gz',
                 'AMP_fixed':R8+'results/C4-replays.json.gz','DEA':R7+'results/F/search-outcome.json.gz'}
        oldfile = paths.get(design)
        old = archived(oldfile) if oldfile else {}
        old_record = f'{design}/controls/tracking.json.gz'
        tracking = self.read(old_record)
        fixed = self.read(f'{design}/controls/fixed-at-old.json.gz')
        extra = ('A-continuation','A-descent-continuation') if design=='MDEA' else ()
        for label in (*self.attempts.get(design,{}),*extra,'fixed-at-old'):
            path = f'{design}/controls/{label}.json.gz'
            record = self.read(path)
            if not record:
                continue
            if label in extra:
                fit = self.read(f'MDEA/stationarity/{label}.json.gz')
                fingerprint_ = fit['endpoint_fingerprint']
            else:
                fingerprint_ = self.attempts.get(design,{}).get(label,{}).get('endpoint')
            if fingerprint_:
                assert record['endpoint_fingerprint']==fingerprint_,f'{design} {label} phase endpoint fingerprint'
            rows = record.get('rows') or {k:dict(P_Pa=q['P_Pa'],refusal=record.get('refusal'))
                                            for k,q in (fixed or {}).get('rows',{}).items()}
            for key,row in rows.items():
                before = None
                if design=='MDEA':
                    p = min((k for k in old['rows'] if k.startswith('MDEA-0:')),
                            key=lambda k:abs(float(k.split(':')[1])-row['P_Pa']))
                    before = phase_outcome(old['rows'][p].get('value',{}))
                elif design=='AMP_free' and key in old['rows']:
                    before = phase_outcome(old['rows'][key].get('value',{}))
                elif design=='DEA':
                    before = 'confirmed split' if key in old['confirmed'] else None
                if tracking and key in tracking.get('rows',{}):
                    before = phase_outcome(tracking['rows'][key].get('value',{}))
                value = phase_outcome(row['value']) if 'value' in row else (
                    'no endpoint' if not fingerprint_ and label in self.attempts.get(design,{}) else 'unavailable')
                sources = (path,old_record) if tracking else (path,)
                self.quantity(f'{design} {label} phase {key}',before,value,unit='outcome',sources=sources,
                              old_source=oldfile,pressure_basis=dict(type='retained absolute pressure',P_Pa=row['P_Pa']),
                              population=1,endpoint=fingerprint_,
                              disposition='refused at initial evaluation' if value=='no endpoint' else
                              'undecided' if value in ('unavailable','unresolved','unresolved phase identity') else None)
        for path in sorted((OUT/design/'screen/selected').glob('*/summary.json.gz')):
            rel = str(path.relative_to(OUT))
            result = self.read(rel)
            assert result['endpoint_fingerprint']==endpoint, f'{design} screen endpoint fingerprint'
            rows = result['rows']
            classified = {q['key']:q for q in result['classifications']}
            count = Counter()
            for q in rows:
                k = q.get('same_calculation_as',q['key'])
                entry = classified.get(k,{})
                category = ('confirmed split' if any(a['confirmed'] for a in entry.get('attempts',[])) else
                            'unavailable search' if not q['available'] else 'unresolved descent or identity' if q['descent']
                            else 'no resolved descent')
                count[category] += 1
            protocol = path.parent.name
            baseline = (R7+'results/F/search-outcome.json.gz' if design=='DEA' else
                        R7+'results/C/salt/search-outcome.json.gz' if design=='MDEA' else
                        R7+f"results/AMP/{design.split('_')[1]}/{protocol}-outcome.json.gz")
            old = archived(baseline)
            before = {**{k:old['tally'][k] for k in ('states','available','descent')},'confirmed':len(old['confirmed'])}
            self.quantity(f'{design} {protocol} finite search counts',before,dict(count),unit='states',
                          population=len(rows),sources=(rel,),endpoint=endpoint,old_source=baseline,
                          pressure_basis='individual absolute or bubble-scaled pressure per row')
            if design=='MDEA':
                self.quantity('C2 MDEA release endpoint fingerprint',old['parameter_fingerprint'],endpoint,unit='SHA-256',
                              sources=(rel,),old_source=baseline,endpoint=endpoint)
            old_paths = {'DEA':'F/search-rows.json.gz','MDEA':'C/salt/search-0.json.gz'}
            old_rows_path = R7+'results/'+old_paths.get(design,f"AMP/{design.split('_')[-1]}/{protocol}-rows.json.gz")
            old_rows = archived(old_rows_path)
            assert {q['key'] for q in rows}=={q['key'] for q in old_rows}
            for metric,counts in (
                ('descent flags',[sum(q['descent'] for q in v) for v in (old_rows,rows)]),
                ('descent flags on unavailable searches',[sum(q['descent'] and not q['available'] for q in v) for v in (old_rows,rows)]),
            ):
                self.quantity(f'{design} {protocol} {metric}',*counts,unit='states',population=len(rows),sources=(rel,),
                              old_source=old_rows_path,endpoint=endpoint,
                              pressure_basis='declared search pressures; descent flags include unavailable searches')
            for is_grid in (True,False):
                def measures(pool, confirmed):
                    subset = [q for q in pool if q['key'].startswith('grid:')==is_grid]
                    return dict(attempts=len(subset),distinct=len({q.get('same_calculation_as',q['key']) for q in subset}),
                                available=sum(q['available'] for q in subset),descents=sum(q['descent'] for q in subset),
                                confirmed=[q['key'] for q in subset if q.get('same_calculation_as',q['key']) in confirmed],
                                unavailable_by_event=dict(Counter(q.get('event') or q.get('status') for q in subset if not q['available'])))
                current = {q['key'] for q in result['classifications'] if any(x['confirmed'] for x in q['attempts'])}
                a,b = measures(old_rows,set(old['confirmed'])),measures(rows,current)
                self.quantity(f'{design} {protocol} {"grid" if is_grid else "measured"} stratum',a,b,unit='states',
                              population=a['attempts'],sources=(rel,),old_source=old_rows_path,endpoint=endpoint,
                              pressure_basis='declared state pressures within this stratum')
            if design=='MDEA':
                self.mdea_census(result,rel)

    def mdea_census(self,result,screen_path):
        from comparisons import mdea_deviations

        p = 'MDEA/screen/selected/declared/state-inventory.json.gz'
        inventory = self.read(p)
        if not inventory:
            return
        _,endpoint = self.selections['MDEA']
        assert inventory['endpoint_fingerprint']==endpoint
        keys = {q['key']:q for q in inventory['rows']}
        rows = {q['key']:q for q in result['rows']}
        assert keys.keys()==rows.keys()
        path = R7+'results/B/census.json.gz'
        old = archived(path)
        links = {}
        for identity,entries in old['joins'].items():
            links[identity] = []
            for archived_entry in entries:
                key = archived_entry['key']
                q = keys[key]
                pressure = q.get('declared_pressure_Pa') or q.get('search_Pa')
                bubble = q.get('bubble_Pa')
                link = dict(archived_entry,pressure_Pa=pressure,completed_without_descent=rows[key]['available'] and not rows[key]['descent'],
                            below_bubble_salt=pressure<bubble if pressure is not None and bubble is not None else None)
                links[identity].append(link)
        raw = 'MDEA/properties.json.gz'
        current = self.read(raw)
        assert current['endpoint_fingerprint']==endpoint
        keyed = {(q['group'],q['role'],q['unit']):q for q in mdea_deviations(current['rows'],links)}
        for before in old['metrics']:
            group,role,unit = label = tuple(before[k] for k in ('group','role','unit'))
            if label not in keyed:
                continue
            after = keyed[label]
            self.quantity(f'C2 MDEA {group} {role} {unit} admitted search attempts',before['admitted_search_attempts'],
                          after['admitted_search_attempts'],unit='states',sources=(screen_path,p,raw),
                          pressure_basis='individually assigned pressure',endpoint=endpoint,old_source=path)
            for subset in ('all','resolved_fixed_pressure_subset'):
                a,b = (q[subset] for q in (before,after))
                self.quantity(f'C2 MDEA {group} {role} {unit} {subset}',a,b,unit=unit,
                              population={'old':a['attempted'],'new':b['attempted']},sources=(screen_path,p,raw),
                              endpoint=endpoint,old_source=path,pressure_basis='below-bubble gate uses individually assigned pressure')
        for item in old['sobrinorows']:
            before = item['observation']
            after = next(q for q in current['rows'] if q['identity']==before['identity'])
            q = keys[item['search']['key']]
            assert before['observed']==after['observed']
            self.quantity(f'C2 MDEA Sobrino {before["row"]["source_row"]} density',before['value'],after['value'],
                          unit='kg/m³',population=1,sources=(screen_path,p,raw),endpoint=endpoint,old_source=path,
                          pressure_basis=dict(type='assigned absolute pressure',P_Pa=q['declared_pressure_Pa']))
        witness_path = 'MDEA/screen/selected/declared/witness-readbacks.json.gz'
        witnesses = self.read(witness_path)
        if witnesses:
            assert witnesses['endpoint_fingerprint']==endpoint
            tracked = archived(R8+'results/mdea-phase-outcomes.json.gz')['quantities']['classifications']
            expected = {q['key']:q for q in result['classifications'] if not q['key'].startswith('grid:')}
            assert all(k.removeprefix('bubble:') in expected for k in witnesses['rows'])
            labels = {'liquid','vapor'}
            for key,q in expected.items():
                readback = witnesses['rows'].get(key,{})
                old = next((v for v in tracked if v['key']==key),{})
                directions = {witness_direction(w) for w in readback.get('value',[])}
                value = dict(directions=sorted(directions or {'unclassified'}),attempts=len(q['attempts']),
                             confirmed=sum(v['confirmed'] for v in q['attempts']),refusal=readback.get('refusal'))
                self.quantity(f'C2 MDEA measured witness {key}',old.get('directions'),value,unit='direction and outcomes',
                              population=1,sources=(screen_path,p,witness_path),pressure_basis=keys[key],
                              old_source=R8+'results/mdea-phase-outcomes.json.gz',endpoint=endpoint,
                              disposition='undecided' if readback.get('refusal') or not labels.intersection(directions) else None)

    def c1(self):
        for path in sorted((OUT/'C1').glob('*.json.gz')):
            rel = str(path.relative_to(OUT))
            q = self.read(rel)
            if not q.get('steps'):
                continue
            center = q['center']
            assert center['volume_m3']==fsum(v['amount_mol']/v['rho_mol_m3'] for v in center['values'])
            for step in q['steps']:
                pts = step['points']
                for p in pts.values():
                    if 'G_J' in p:
                        assert p['G_J']==fsum(v['eos_G_J']+v['standard_G_J'] for v in p['values']), rel
                if 'signed_volume_error_m3' in step:
                    v = (pts['P+']['G_J']-pts['P-']['G_J'])/(2*step['step_Pa'])
                    assert v-center['volume_m3']==step['signed_volume_error_m3'], rel
                    assert step['volume_admitted']==all(p['admitted'] for p in (center,pts['P+'],pts['P-'])), rel
                if 'eq12_minus_Gibbs_Helmholtz_J' in step:
                    T,dt = q['T_K'],step['step_K']
                    h = -T*T*(pts['T+']['G_J']/(T+dt)-pts['T-']['G_J']/(T-dt))/(2*dt)
                    eq12 = fsum(c['eq12_H_J'] for c in step['caloric_components'])
                    assert eq12-h==step['eq12_minus_Gibbs_Helmholtz_J'], rel
                    assert step['enthalpy_admitted']==all(p['admitted'] for p in (center,pts['T+'],pts['T-'])), rel
            for key,error,metric in (('volume','volume_arithmetic_error_m3','signed_volume_error_m3'),
                                     ('enthalpy','caloric_arithmetic_error_J','engine_minus_Gibbs_Helmholtz_J'),
                                     ('Eq. 12','caloric_arithmetic_error_J','eq12_minus_Gibbs_Helmholtz_J')):
                available = [s for s in q['steps'] if metric in s]
                if not available:
                    continue
                admitted = [s for s in available if s.get(('volume' if key=='volume' else 'enthalpy')+'_admitted')]
                used = admitted or available
                latest = used[-1]
                span = max(s[metric] for s in used)-min(s[metric] for s in used)
                num = latest[error]+span
                scale = q['apparent_amine_feed_mol'] if key!='volume' else 1.
                value = dict(signed_error=latest[metric]/scale,estimated_error=num/scale,
                             admitted_steps=len(admitted),
                             disposition=('agreement within numerical error' if len(admitted)>=2 and abs(latest[metric])<=num
                                          else 'undecided'))
                if key=='volume':
                    value.update(relative_error=latest['relative_volume_error'],relative_estimated_error=num/q['center']['volume_m3'])
                if key=='enthalpy' and 'H_over_T_minus_S_check_J' in latest:
                    value['secondary_H_over_T_minus_S_error_J_per_mol'] = (
                        latest['H_over_T_minus_S_check_J']-latest['Gibbs_Helmholtz_H_J'])/scale
                self.quantity(f'C1 {path.name.removesuffix(".json.gz")} {key}',None,value,disposition=value['disposition'],
                              unit='J/mol apparent amine' if key!='volume' else 'm³',sources=(rel,),
                              pressure_basis=dict(T_K=q['T_K'],P_Pa=q['P_Pa']),endpoint=q['endpoint_fingerprint'])
        for mode in ('fixed-at-old','selected'):
            paths = tuple(f'C1/{mode}-MDEA-daughter-{i}.json.gz' for i in (1,2))
            branches = [self.read(p) for p in paths]
            if not all(q and q.get('steps') for q in branches):
                continue
            a,b = branches
            assert (a['T_K'],a['P_Pa'],a['endpoint_fingerprint'],a['apparent_amine_feed_mol'])==(
                b['T_K'],b['P_Pa'],b['endpoint_fingerprint'],b['apparent_amine_feed_mol'])
            for key,metric,error in (('volume','signed_volume_error_m3','volume_arithmetic_error_m3'),
                                     ('enthalpy','engine_minus_Gibbs_Helmholtz_J','caloric_arithmetic_error_J'),
                                     ('Eq. 12','eq12_minus_Gibbs_Helmholtz_J','caloric_arithmetic_error_J')):
                available = [(left[metric]+right[metric],left[error]+right[error])
                             for left,right in zip(a['steps'],b['steps'],strict=True)
                             if left.get(('volume' if key=='volume' else 'enthalpy')+'_admitted')
                             and right.get(('volume' if key=='volume' else 'enthalpy')+'_admitted') and metric in left and metric in right]
                if not available:
                    continue
                delta,err = available[-1]
                span = max(d for d,e in available)-min(d for d,e in available)
                scale = a['apparent_amine_feed_mol'] if key!='volume' else 1.
                value = dict(signed_error=delta/scale,estimated_error=(err+span)/scale,admitted_steps=len(available),
                             disposition=('agreement within numerical error' if len(available)>=2 and abs(delta)<=err+span
                                          else 'undecided'))
                self.quantity(f'C1 {mode} MDEA daughter-inventory sum {key}',None,value,disposition=value['disposition'],
                              unit='J/mol apparent amine' if key!='volume' else 'm³',sources=paths,
                              pressure_basis=dict(T_K=a['T_K'],P_Pa=a['P_Pa']),
                              endpoint=a['endpoint_fingerprint'])

    def numerical_diagnosis(self):
        p = 'MDEA/stationarity/A-continuation.json.gz'
        continued = self.read(p)
        if continued:
            prior = self.read('MDEA/A.json.gz')
            assert continued['source']==prior['endpoint_fingerprint']
            assert continued['endpoint_fingerprint']==fingerprint(continued['endpoint'])
            cost = self.cost(continued['replay'],'MDEA A continuation')
            norm,_,optimizer_gradient = self.stationarity(continued)
            report = continued['report']
            self.quantity('MDEA A continuation',prior['replay']['cost'],
                dict(cost=cost,iterations=report['iterations'],status=report['status'],termination=report['message'],
                     projected_gradient_inf=norm,optimizer_gradient=optimizer_gradient,
                     gradient_tolerance=continued['controls']['gradient_tolerance'],failures=report['failures'],
                     fit_seconds=continued['fit_seconds'],replay_seconds=continued['replay_seconds'],
                     diagnostic_seconds=continued['diagnostic_seconds']),
                endpoint=continued['endpoint_fingerprint'],sources=('MDEA/A.json.gz',p),
                disposition='undecided' if report['status']!='converged' else None)
        for design in ('AMP_free','AMP_fixed'):
            path = f'{design}/root-probe.json.gz'
            record = self.read(path)
            if record:
                manifest = f'{design}/manifest.json.gz'
                assert record['manifest_fingerprint']==fingerprint(self.read(manifest))
                for label,data in record['starts'].items():
                    self.quantity(f'{design} {label} bubble guess diagnostic',None,data['guesses'],unit='Pa',
                                  sources=(path,manifest),pressure_basis={'row':data['row']})
        p = 'MDEA/root-probe.json.gz'
        probe = self.read(p)
        if probe:
            for start,data in probe['records'].items():
                ranges = {}
                for multiplier in sorted({q['multiplier'] for q in data['nodes']}):
                    nodes = [q for q in data['nodes'] if q['multiplier']==multiplier]
                    pressures = [q['pressure'] for q in nodes if q['admitted']]
                    ranges[str(multiplier)] = dict(attempted=len(nodes),admitted=len(pressures),
                                                   min_Pa=min(pressures,default=None),max_Pa=max(pressures,default=None))
                self.quantity(f'MDEA {start} saturation guess diagnostic',None,ranges,
                              sources=(p,),unit='Pa',pressure_basis=dict(target_Pa=data['P_Pa'],row=data['row']))
        p = 'MDEA/stationarity/A-projected-direction.json.gz'
        probe = self.read(p)
        if probe:
            prior = self.read('MDEA/A.json.gz')
            assert probe['endpoint']==prior['endpoint_fingerprint']
            old_cost = prior['replay']['cost']
            reductions = []
            for trial in probe['trials']:
                cost = self.cost(trial['replay'],'MDEA projected gradient line')
                reduction = (old_cost-cost)/old_cost if cost is not None else None
                assert trial['relative_reduction']==reduction
                reductions.append(dict(step=trial['step'],cost=cost,relative_reduction=reduction))
            self.quantity('MDEA A projected gradient line',old_cost,reductions,sources=('MDEA/A.json.gz',p),
                          endpoint=probe['endpoint'])
            retry_path = 'MDEA/stationarity/A-descent-continuation.json.gz'
            retry = self.read(retry_path)
            if retry and retry.get('replay'):
                assert retry['source']==fingerprint(probe['trials'][-1]['point'])
                assert retry['endpoint_fingerprint']==fingerprint(retry['endpoint'])
                cost = self.cost(retry['replay'],'MDEA A admitted-descent continuation')
                self.quantity('MDEA A admitted-descent continuation',old_cost,
                    dict(cost=cost,optimizer_gradient=retry['report']['covariance']['projected_gradient_norm'],
                         status=retry['report']['status'],message=retry['report']['message'],
                         fit_seconds=retry['fit_seconds'],replay_seconds=retry['replay_seconds']),
                    sources=(p,retry_path),endpoint=retry['endpoint_fingerprint'],
                    disposition='undecided' if retry['report']['covariance']['projected_gradient_norm']>
                    retry['controls']['gradient_tolerance'] else None)
        p = 'R1-R3-R5.json'
        row = self.read(p)
        if row:
            assert row['actual_prediction']['residual']==row['actual_residual']
            assert row['actual_residual']-row['expected_residual']==row['difference']
            self.quantity('Legacy R1 weighted residual at row 129',row['expected_residual'],row['actual_residual'],
                          sources=(p,),old_source=row['source']+'/fit.json',disposition='undecided')

    def archived_inventory(self):
        root = original(R8+'manuscript-handoff.json')
        profile_root = 'AMP_free/conditional-profile/'
        profile_path = profile_root+'profile-expanded.json'
        profile = self.read(profile_path)
        if profile:
            assert profile['endpoint_fingerprint']==self.selections['AMP_free'][1] and profile['wheel']==r.SHA
            assert profile['delta_cutoff']==.5*profile['stage_variance']*3.84146
        electrode_path = 'MEA/electrode/D/electrode-selected.json.gz'
        electrode = self.read(electrode_path)
        hartono_path = 'AMP_free/hartono-S11.json.gz'
        hartono = self.read(hartono_path)
        for name,meta in self.old.items():
            key = f'Round 7 {name}'
            value = meta.get('value')
            record = meta.get('record')
            if not record or not record.startswith('analyses/'):
                record = R7+'manuscript-handoff.json'
            match = {}
            if electrode and name.startswith(('D MEA electrode ','D MEA model minus electrode ')):
                selected = self.selections['MEA'][0]
                meapath = f'MEA/{selected}.json.gz'
                endpoint = self.read(meapath)['endpoint']
                assert electrode['parameter_sha256']==sha256(json.dumps(endpoint['parameters'],indent=2,
                    allow_nan=False).encode()+b'\n').hexdigest()
                field = ('signed_delta' if 'model minus' in name else
                         'carbonate_share' if 'carbonate_share' in name else 'common_molality_minus_raw')
                values = [row[field] for row in electrode['rows'] if row['requested_tolerance_met']]
                mode = name.split()[-1]
                val = min(values) if mode=='min' else max(values) if mode=='max' else fsum(values)/len(values)
                match = dict(new=val,disposition='replayed',population=len(values),
                             endpoint_fingerprint=self.selections['MEA'][1],
                             new_contributors=[self.reference(p) for p in (electrode_path,meapath)])
            elif hartono and name.startswith('H Hartono salt expanded free '):
                assert hartono['endpoint_fingerprint']==self.selections['AMP_free'][1]
                old = archived(record)['results']['salt expanded free'][name.split()[-2]]['rows']
                rows = hartono['rows'][name.split()[-2]]
                assert {q['identity']:q['observed'] for q in rows}=={q['identity']:q['observed'] for q in old}
                scores = summary(rows)
                match = dict(new=scores.get('AARD_percent'),disposition='replayed' if scores['available']==26 else 'partial',
                             new_contributors=[self.reference(hartono_path)],endpoint_fingerprint=hartono['endpoint_fingerprint'])
            elif name=='D Cai incumbent alternative objective':
                label,endpoint = self.selections['MEA']
                path = f'MEA/{label}.json.gz'
                fit = self.read(path)
                rows = fit['replay']['rows']
                assert sum(q['group']=='Cai' for q in rows)==50
                value_after = .5*fsum(q['residual']**2*.04 if q['group']=='Cai' else q['weighted_residual']**2
                                      for q in rows)
                match = dict(new=value_after,disposition='replayed',endpoint_fingerprint=endpoint,
                             new_contributors=[self.reference(path)])
            elif profile and name.startswith('D AMP profile '):
                parts = name.split()
                if 'conditional' in parts:
                    slope = parts[-2]
                    item = profile['points'].get(slope)
                    if item is not None:
                        contributor = profile_root+item['record']
                        run = self.read(contributor)
                        paths = (profile_path,contributor) if run else (profile_path,)
                        if run:
                            if item['cost'] is not None:
                                assert abs(fsum(q['cost'] for q in run['replay'])-item['cost'])<=1e-12*item['cost']
                            assert item['status']==run['report']['status']
                        result = item.get('status') if 'solve' in parts else item['cost']
                        match = dict(new=result,new_contributors=[self.reference(p) for p in paths],
                                     disposition='replayed' if result is not None else 'undecided')
                elif parts[-1]=='bracket':
                    bracket = profile['brackets'].get(parts[-3])
                    if bracket:
                        result = bracket[parts[-2]]
                        match = dict(new=result,new_contributors=[self.reference(profile_path)],
                                     disposition='replayed' if bracket['closed'] else 'undecided')
            elif name.startswith('F DEA '):
                item = name.removeprefix('F DEA ')
                match = self.items.get('DEA '+item,{})
                candidates = [q for q in self.items if q.startswith('DEA ') and ' all ' in q]
                for q in candidates:
                    group,stat = item.rsplit(' ',1)
                    if q.startswith(f'DEA {group} ') and q.endswith(' '+stat):
                        match=self.items[q]
                        break
            elif name.endswith('selected converged objective'):
                design = ('AMP_fixed' if name.startswith('AMP fixed') else 'AMP_free' if name.startswith('AMP') else
                          'DEA' if name.startswith('DEA') else 'MDEA')
                match = self.items.get(f'{design} selected objective',{})
            elif name=='E MEA incumbent original objective':
                match = self.items.get('MEA selected objective',{})
            elif name=='D5 incumbent unresolved, phase pressure closure':
                match = self.items.get('MEA measured unresolved pressure closure',{})
            elif name.startswith('D5 incumbent ') or name=='E MEA incumbent supplied missing':
                path = 'MEA/screen/summary.json.gz'
                screen = self.read(path)
                field = name.removeprefix('D5 incumbent ')
                if screen and (field in screen['measured'] or name.endswith('supplied missing')):
                    counts = screen['measured']
                    val = screen['grid']['missing_supplied'] if name.endswith('supplied missing') else counts[field]
                    match = dict(new=val,disposition='replayed',new_contributors=[self.reference(path)])
            elif name=='E MEA incumbent legacy pressure AARD rise versus F2':
                paths = 'E/MEA/replay.json.gz',R7+'results/E/incumbent/replay.json.gz'
                replay = self.read(paths[0])
                if replay:
                    old = archived(paths[1])
                    pool = set(old['pressure_population'])
                    assert pool==set(replay['pressure_population'])
                    legacy = [[q for q in doc['rows'][:307] if q['identity'] in pool] for doc in (old,replay)]
                    old_aard,new_aard = (summary(rows,pressure=True)['AARD_percent'] for rows in legacy)
                    match = dict(new=value+new_aard-old_aard,disposition='replayed',
                                 new_contributors=[self.reference(paths[0])],
                                 endpoint_fingerprint=self.selections['MEA'][1])
            elif name.startswith('E MEA incumbent '):
                match = self.items.get(name.replace('E MEA incumbent ','MEA pressure ',1),{})
                if not match:
                    item = name.removeprefix('E MEA incumbent ')
                    if item.startswith('outside fit '):
                        match = self.items.get(item.replace('outside fit ','MEA off-window ',1),{})
                    elif item=='expanded objective':
                        match = self.items.get('MEA expanded 419-row objective cross-score',{})
                if not match and any(name.startswith(f'E MEA incumbent {g} ') for g in ('grid','offset','census')):
                    with_grid = name.removeprefix('E MEA incumbent ').split()
                    sub = 'main' if with_grid[0]=='grid' else with_grid[0]
                    new_key = 'MEA native and supplied census counts' if sub=='census' else f'MEA {sub} finite search counts'
                    better = self.items.get(new_key,{})
                    if better and with_grid[-1] in better['new']:
                        match = dict(better,new=better['new'][with_grid[-1]])
            elif name.startswith(('F search-outcome.json ','AMP/free ','AMP/fixed ')) and name.split()[-1] in (
                    'states','available','descent','confirmed'):
                parts = name.split()
                design = {'F':'DEA','AMP/free':'AMP_free','AMP/fixed':'AMP_fixed'}[parts[0]]
                protocol = 'declared' if design=='DEA' else parts[1].split('-')[0]
                match = self.items.get(f'{design} {protocol} finite search counts',{})
                if match:
                    counts = match['new']
                    val = dict(states=sum(counts.values()),
                               available=sum(counts.values())-counts.get('unavailable search',0),
                               confirmed=counts.get('confirmed split',0),
                               descent=self.items[f'{design} {protocol} descent flags']['new'])[parts[-1]]
                    match = dict(match,new=val)
            elif name=='C MDEA salt search-outcome.json.gz seconds':
                path = 'MDEA/screen/selected/declared/summary.json.gz'
                replay = self.read(path)
                if replay:
                    match = dict(new=replay['seconds'],disposition='replayed',new_contributors=[self.reference(path)])
            elif name.startswith('C MDEA salt refit '):
                match = self.items.get('C5 '+name[2:],{})
                if not match:
                    match = self.items.get('MDEA '+name.removeprefix('C MDEA salt refit ').replace(' AARD_percent',' Pa all AARD_percent').replace(' bias_percent',' Pa all bias_percent'),{})
            elif name.startswith('C MDEA salt RMS '):
                metric = name.split()[-1]
                item = self.items.get('MDEA declared finite search counts',{})
                if item:
                    c = item['new']
                    counts = dict(states=sum(c.values()),available=sum(v for k,v in c.items() if k!='unavailable search'),
                                  descent=self.items['MDEA declared descent flags']['new'],
                                  unavailable=c.get('unavailable search',0),confirmed=c.get('confirmed split',0))
                    match = dict(item,new=counts[metric])
            elif name.startswith('B MDEA ') and ' all ' in name:
                group,metric = name.removeprefix('B MDEA ').split(' all ',1)
                candidates = [q for k,q in self.items.items() if k.startswith(f'MDEA {group} ') and k.endswith(f' all {metric}')]
                if len(candidates)==1:
                    match = candidates[0]
            elif name.startswith('B MDEA ') and ('resolved_fixed_pressure_subset' in name or name.endswith(' admitted search attempts')):
                text = name.removeprefix('B MDEA ')
                suffix = ' admitted search attempts' if text.endswith(' admitted search attempts') else ' resolved_fixed_pressure_subset'
                group = text.split(suffix)[0]
                candidates = [v for k,v in self.items.items() if k.startswith(f'C2 MDEA {group} ') and k.endswith(suffix)]
                if len(candidates)==1:
                    item, = candidates
                    if suffix==' admitted search attempts':
                        val = item['new']
                    else:
                        metric = text.split()[-1]
                        val = item['new']['available'] if metric=='available' else (item['new']['scores'] or {}).get(metric)
                    match = dict(item,new=val,disposition='replayed' if val is not None else 'undecided')
            elif name.startswith(('AMP free ','AMP fixed ')):
                label = 'AMP_free' if name.startswith('AMP free ') else 'AMP_fixed'
                metric = name.removeprefix('AMP free ').removeprefix('AMP fixed ').removeprefix('slope ')
                match = self.items.get(f'{label} {metric}') or self.items.get(f'C4 {label} {metric}',{})
            elif name.startswith('DEA carbamate '):
                match = self.items.get(name,{})
            if match:
                new = match['new']
                numerical = all(isinstance(x,(int,float)) and not isinstance(x,bool) for x in (value,new))
                delta = new-value if numerical else None
                self.items[key] = dict(unit=meta.get('unit'),population=meta.get('population'),pressure_basis=None,
                    endpoint_fingerprint=None,transition=None) | dict(match,old=value,absolute_change=delta,
                    percent_change=100*delta/value if numerical and value else None,
                    old_contributor=dict(revision=BASE,path=record,field=meta.get('field'),sha256=sha256(blob(record,BASE)).hexdigest()))
            else:
                historical = (name.endswith(' elapsed') or 'original-slope' in name or 'historical' in name or
                              name.startswith(('E MEA F2 ','E MEA F4 ','H public-','H study-','A MDEA tracking ','B Sobrino row ',
                                               'H Kuranov Table 2','H Hong ','D5 F2 ','D5 F4 ','C MDEA salt incumbent ','D AMP original archive ',
                                               'D AMP original trial ','D AMP constant-enthalpy R5 ','D AMP slope only at fixed ')))
                self.quantity(key,value,value if historical else None,unit=meta.get('unit'),population=meta.get('population'),
                              old_source=record,old_field=meta.get('field'),independent=historical,
                              disposition='historical contributor' if historical else None)
        for i,name in enumerate(NAMES,1):
            item = root['items'][f'C{i}']
            path = R8+f'results/{name}.json.gz'
            for key,meta in item['quantities'].items():
                value = archived(path)['quantities'][key]
                historical = key in ('low_pressure_controls','archived_design','hot_original','original_R5_control',
                                     'original_slope_control','round7_F4_display_excluded','published_Kamps_28','published_table_snapshot')
                markers = {1:{'branches':('C1 selected',),'reference_controls':('MDEA fixed-at-old phase',)},
                           2:{'fingerprint':('C2 MDEA release endpoint fingerprint',),
                              'classifications':('MDEA declared','C2 MDEA measured witness'),'counts':('MDEA declared',),'strata':('MDEA declared',),
                              'targeted':('MDEA A phase 263',),'grid_confirmed':('MDEA declared grid',)},
                           3:{'all_44':('C3 DEA AARD all 44',),'four':('C3 DEA AARD four historically',),
                              'rows':('C3 DEA Weiland','C3 DEA weiland'),'first_split':('C3 DEA weiland',)},
                           4:{'rows':('AMP_free A phase','AMP_fixed A phase'),'grid':('AMP_free native','AMP_fixed native'),
                              'worked_state':('AMP_free A phase worked','AMP_fixed A phase worked'),
                              'added_pressure_rows':('C4 AMP_free added','C4 AMP_fixed added')},
                           5:{'available':('C5 mixed salt',),'models':('C5 MDEA salt refit',),'properties':('C5 Kuranov matched',
                              'C5 Carson matched','C5 Xiao matched','C5 Ermatchkov matched'),'residuals':('C5 ',)},
                           6:{'AMP':('AMP_free selected','AMP_fixed selected','C6 AMP'), 'MDEA':('MDEA selected','C6 MDEA'),
                              'MEA #435':('MEA selected','C6 MEA'),'unavailable':('C6 ',)},
                           7:{'hong':('C7 Hong',),'kamps':('C5 C7 corrected-Kamps',),'kuranov':('C7 Kuranov',)}}
                if i==5 and key=='available':
                    salt_path = 'salt.json.gz'
                    rows = self.read(salt_path)['combined']
                    counts = {k:sum(q.get('status')=='Available' for q in rows[k]) for k in value}
                    self.quantity('Round 8 C5 available',value,counts,unit='rows',sources=(salt_path,),
                                  old_source=path,old_field=meta['field'])
                    continue
                linked = [item for item in self.items if item.startswith(markers.get(i,{}).get(key,()))]
                self.quantity(f'Round 8 C{i} {key}',value if historical else (value if isinstance(value,(int,float,str)) else len(value)),
                              value if historical else linked or None,old_source=path,old_field=meta['field'],
                              disposition='historical contributor' if historical else 'reduced under linked quantities' if linked else None)
        salt_path = 'salt.json.gz'
        salt = self.read(salt_path)
        assert salt['wheel']==r.SHA
        source_table = 'analyses/mea_parameter_bundle/results/carbonate-ions-282/inputs/peiper-pitzer-1982-table6.csv'
        data = salt['reconstruction']
        target = (data['numerator']-data['ideal_co2'])/fsum(data['ions'].values())
        assert abs(target-data['target'])<1e-14
        self.quantity('C5 Peiper–Pitzer first NaHCO3 ionic osmotic target',data['target'],target,
                      independent=True,sources=(salt_path,),old_source=source_table,population=1,
                      pressure_basis='prescribed molalities with dissolved ideal CO₂ removed')
        for stage,e in salt['stages'].items():
            assert e['passed'] and e['differences']['maximum_relative_prediction_difference']==0
            scale = .003 if e['group']=='NaCl' else .01
            cost = .5*fsum(((q['value']-q['observed'])/scale)**2 for q in e['rows'])
            assert abs(cost-e['replayed_cost'])<=1e-13*cost, stage
            self.quantity(f'C5 {stage} retained replay objective',e['retained_cost'],cost,
                          sources=(salt_path,),population=len(e['rows']),independent=True,
                          old_source=f'analyses/mea_parameter_bundle/results/salt-anchored-435/salt/{stage}.json')
        self.quantity('C5 mixed salt refusals',6,len(salt['mixed_refusals']),unit='rows',population=len(salt['combined']['mixed']),
                      sources=(salt_path,),independent=True,
                      old_source='analyses/mea_parameter_bundle/results/salt-anchored-435/salt/summary.json')

    def matched_literature(self):
        literature = R8+'results/literature-populations.json.gz'
        old = archived(literature)['quantities']
        selection,endpoint = self.selections.get('MDEA',(None,None))
        p = f'MDEA/property-comparisons/{selection}.json.gz'
        new = self.read(p)
        for key in ('published_Kamps_28','published_table_snapshot'):
            self.quantity(f'C7 {key}',old[key],old[key],old_source=literature,
                          old_field=f'quantities.{key}',independent=True,
                          pressure_basis='published comparison population')
        hong = old['hong']
        self.quantity('C7 Hong local instability count',hong['local_failures'],hong['local_failures'],unit='states',
                      old_source=literature,population=hong['inside_count'],independent=True,
                      pressure_basis='Hong reconstruction within its declared grid')
        hong_path = 'MEA/hong-matched.json.gz'
        hong_rows = self.read(hong_path)
        if hong_rows:
            assert len(hong_rows['rows'])==hong['inside_count']
        self.quantity('C7 Hong matched population refitted MEA AARD',hong['matched_scores']['adopted']['AARD_percent'],
                      summary(hong_rows['rows'],True).get('AARD_percent') if hong_rows else None,unit='%',
                      old_source=literature,sources=(hong_path,),population=hong['inside_count'],
                      pressure_basis='source partial pressures; Hong reconstruction kept on its original basis',
                      endpoint=self.selections['MEA'][1])
        for name,value in old['kuranov']['published'].items():
            self.quantity(f'C7 Kuranov published AARD {name}',value,value,old_source=literature,
                          unit='%',population='published membership by count',independent=True,
                          pressure_basis='published total pressures')
        keys = {str(q) for q in old['kuranov']['source_rows']}
        values = []
        if new:
            assert new['endpoint_fingerprint']==endpoint and selection
            values = [q for q in new['rows'] if q['group'] in ('Kuranov','Kuranov-binary','Kuranov-413K')
                      and q['row']['source_row'] in keys]
            values.append(new['additional_Kuranov_72'])
            assert {q['row']['source_row'] for q in values}==keys and len(values)==82
        self.quantity('C7 Kuranov row-matched 82 AARD',old['kuranov']['current']['AARD_percent'],
                      summary(values,True).get('AARD_percent'),unit='%',population=len(keys),
                      pressure_basis='source total pressures; row 72 comparison only',sources=(p,),
                      old_source=literature,old_field='quantities.kuranov.current',endpoint=endpoint)
        c5 = R8+'results/salt-and-weighting.json.gz'
        properties = archived(c5)['quantities']['properties'] | {'corrected-Kamps': old['kamps']}
        for group,q in properties.items():
            before = q['salt/refit']
            keys = set(before['common_keys'])
            right = [v for v in new['rows'] if v['identity'] in keys] if new else []
            if right:
                assert len(right)==len(keys) and {v['identity'] for v in right}==keys
            for metric in ('AARD_percent','bias_percent'):
                self.quantity(f"C5 {'C7 ' if group=='corrected-Kamps' else ''}{group} matched {metric}",
                              before['matched'][metric],summary(right).get(metric),unit='%',
                              population=len(keys),sources=(p,),
                              old_source=literature if group=='corrected-Kamps' else c5,endpoint=endpoint,
                              pressure_basis='common source row keys; archived exclusions retained')

    def mea_comparisons(self):
        endpoint = self.selections['MEA'][1]
        oldpath = R7+'results/E/incumbent/replay.json.gz'
        p = 'E/MEA/replay.json.gz'
        new = self.read(p)
        old = archived(oldpath)
        if new:
            a,b = (v['summary']['expanded_cost'] for v in (old,new))
            self.quantity('MEA expanded 419-row objective cross-score',a,b,population=419,endpoint=endpoint,
                          old_source=oldpath,sources=(p,),pressure_basis='historical sensitivity residual definition')
            pair = [v['hot_wagner'] for v in (old,new)]
            assert [(q['identity'],q['observed']) for q in pair[0]]==[(q['identity'],q['observed']) for q in pair[1]]
            a,b = (summary(rows,True) for rows in pair)
            for metric in ('AARD_percent','bias_percent','log_RMSE','available'):
                self.quantity(f'MEA pressure unfitted hot Wagner {metric}',a[metric],b[metric],
                              unit='%' if metric.endswith('percent') else 'rows' if metric=='available' else '1',
                              old_source=oldpath,population=dict(fitted=0,comparison=len(pair[0])),sources=(p,),endpoint=endpoint,
                              pressure_basis='observed CO₂ partial pressure; model bubble partial pressure')
        for group,stats in old['summary']['pressure'].items():
            updated = (new or {}).get('summary',{}).get('pressure',{}).get(group,{})
            for key in ('AARD_percent','bias_percent','log_RMSE','available'):
                self.quantity(f'MEA pressure {group} {key}',stats[key],updated.get(key),
                              unit='%' if key.endswith('percent') else 'rows' if key=='available' else '1',
                              old_source=oldpath,population=stats['attempted'],sources=(p,),endpoint=endpoint,
                              pressure_basis='observed partial pressure; model bubble partial pressure')
        op = R7+'results/E/incumbent/off-window.json.gz'
        p = 'MEA/off-window.json.gz'
        offwindow = self.read(p)
        if offwindow:
            assert offwindow['endpoint_fingerprint']==endpoint
            before,after = archived(op)['rows'],offwindow['rows']
            assert {(q['identity'],q['observed']) for q in before}=={(q['identity'],q['observed']) for q in after}
            for group,w in (('Jou1995',None),('Aronu2011',None),('Aronu2011','0.15'),('Aronu2011','0.45')):
                label = group if w is None else f'{group} {int(float(w)*100)} wt%'
                a,b = (summary([q for q in rows if q['group']==group and (w is None or
                    q['row']['source_coordinates']['MEA_weight_fraction']==w)],True) for rows in (before,after))
                a['refused'],b['refused'] = (q['rows']-q['available'] for q in (a,b))
                for metric in ('AARD_percent','bias_percent','log_RMSE','available','refused'):
                    self.quantity(f'MEA off-window {label} {metric}',a.get(metric),b.get(metric),
                                  unit='%' if metric.endswith('percent') else 'rows' if metric in ('available','refused') else '1',
                                  old_source=op,population=a['rows'],sources=(p,),endpoint=endpoint,
                                  pressure_basis='observed partial pressure; model bubble partial pressure')
        p = 'MEA/heat-comparison.json.gz'
        heat = self.read(p)
        if heat:
            assert heat['endpoint_fingerprint']==endpoint
            from round_8.records import Sources
            retained = Sources().display('mea-heat-sensitivity')['replay']['rows']
            for group in {q['source'] for q in retained}:
                before,after = ([dict(q,observed=q['observed_kJ_mol'],value=q['predicted_kJ_mol'],
                                     status='Available' if q['status']=='available' else q['status'])
                                 for q in pool if q['source']==group] for pool in (retained,heat['rows']['rows']))
                assert {q['record_id'] for q in before}=={q['record_id'] for q in after}
                a,b = (summary(rows) for rows in (before,after))
                self.quantity(f'MEA {group} retained heat AARD',a.get('AARD_percent'),b.get('AARD_percent'),
                              unit='%',population=a['rows'],sources=(p,),endpoint=endpoint,
                              pressure_basis='retained absolute calorimetry pressure')

    def mea_screen(self):
        _,endpoint = self.selections['MEA']
        base = 'analyses/mea_parameter_bundle/results/salt-anchored-435/MEA/F4/search/'
        p = 'MEA/screen/grid.json.gz'
        result = self.read(p)
        if result:
            old_path = base+'grid.json.gz'
            previous = {q['key']:q for q in archived(old_path)['result']}
            assert result['endpoint_fingerprint']==endpoint and len(previous)==len(result['data'])
            assert set(previous)=={q['key'] for q in result['data']}
            for name,left,right in (('main',0,1908),('offset',1908,2484)):
                new = result['data'][left:right]
                counts = [dict(states=len(v),available=sum(q['available'] for q in v),
                               descent=sum(r.descent(q) for q in v)) for v in ([previous[q['key']] for q in new],new)]
                self.quantity(f'MEA {name} finite search counts',*counts,unit='states',old_source=old_path,
                              population=len(new),endpoint=endpoint,sources=(p,),pressure_basis='model bubble times declared multiplier')
        p = 'MEA/screen/census.json.gz'
        result = self.read(p)
        if result:
            old_path = base+'census.json'
            old = archived(old_path)['result']['summary']
            assert result['endpoint_fingerprint']==endpoint and old['states']==result['data']['summary']['states']
            self.quantity('MEA native and supplied census counts',old,result['data']['summary'],unit='states',
                          old_source=old_path,population=old['states'],endpoint=endpoint,sources=(p,),
                          pressure_basis='declared circuit pressure and native/supplied trials')
        summary_path = 'MEA/screen/summary.json.gz'
        result = self.read(summary_path)
        batches = tuple(f'E/MEA/measured/{i}.json.gz' for i in range(41))
        new = [row for p in batches for row in self.read(p) or []]
        old = [row for i in range(41) for row in archived(R7+f'results/E/incumbent/measured/{i}.json.gz')]
        previous = {q['identity']:q for q in old}
        assert all(q['identity'] in previous for q in new) and len(new)==len({q['identity'] for q in new})
        if result:
            from round_7.handoff import measured_failures
            assert result['endpoint_fingerprint']==endpoint and len(new)==len(old)==321
            metric = 'phase pressure closure'
            old_path = R7+'results/E/incumbent/measured-summary.json'
            missed = [sum(metric in measured_failures(row) for row in rows if not row['available'])
                      for rows in (old,new)]
            self.quantity('MEA measured unresolved pressure closure',*missed,unit='states',
                          sources=(summary_path,*batches),old_source=old_path,population=len(old),endpoint=endpoint)
        fields = ('source total pressure','1.05 times #435 bubble pressure','assigned observation pressure',None)
        for field in fields:
            def counts(rows):
                pool = [q for q in rows if q.get('pressure_basis')==field]
                return dict(states=len(pool),available=sum(q['available'] for q in pool),
                            descents=sum(bool(q.get('witnesses')) for q in pool),
                            unavailable=dict(Counter(q.get('cause') for q in pool if not q['available'])))
            self.quantity(f'MEA measured screen {field or "pressure not resolved"}',counts(old),counts(new) if new else None,
                          unit='states',population=len(old),pressure_basis=field,endpoint=endpoint,sources=(summary_path,*batches),
                          old_source=R7+'results/E/incumbent/measured-summary.json',
                          disposition='partial' if new and not result else None)
        refinements = 'MEA/screen/refinement.json.gz'
        refine = self.read(refinements)
        if refine:
            assert refine['endpoint_fingerprint']==endpoint
            trials = refine['recalculated']
            self.quantity('MEA measured pressure-refinement pilot',0,sum(q['available'] for q in trials),
                          unit='available states',population=len(trials),endpoint=endpoint,sources=(refinements,),
                          old_source=R7+'results/E/incumbent/measured-summary.json',
                          pressure_basis='same retained external pressure with tighter internal control',
                          disposition='released' if refine['released'] else 'stopped after pilot')

    def curves(self):
        from property_replays import MDEA_CURVES
        from round_8.records import Sources

        def differences(old,new,keys):
            left = {keys(q):q for q in old}
            right = {keys(q):q for q in new}
            assert len(left)==len(old) and len(right)==len(new) and right.keys()<=left.keys()
            pairs = [(left[k]['value'],q['value']) for k,q in right.items() if q.get('value') is not None and left[k].get('value') is not None]
            nonzero = [abs(y/x-1) for x,y in pairs if x]
            return (dict(requested=len(left),available=sum(q.get('value') is not None for q in old)),
                    dict(requested=len(right),available=sum(q.get('value') is not None for q in new),paired=len(pairs),
                         maximum_relative_change=max(nonzero,default=None),maximum_absolute_change=max((abs(x-y) for x,y in pairs),default=None)))

        loader = Sources()
        for p in sorted((OUT/'MEA/curves').glob('*.json.gz')):
            path = str(p.relative_to(OUT))
            data = self.read(path)
            endpoint = self.selections['MEA'][1]
            assert data['endpoint_fingerprint']==endpoint and data['pressure_reference_Pa']==P_REF
            base = data['source']
            old = loader.read(base,BASE)
            assert sha256(blob(base,BASE)).hexdigest()==data['source_sha256']
            fields = ('curve','sampling','temperature_K','pressure_Pa','analytical_loading','mea_mass_fraction','liquid_mea_mole_fraction','quantity')
            if p.name=='pressure.json.gz':
                fields = tuple(f for f in fields if f!='pressure_Pa')
            if p.name=='mea-water.json.gz':
                fields = tuple(f for f in fields if f!='temperature_K')
            def key(q):
                return tuple(str(q.get(f) or '') if f in ('curve','sampling','quantity') else float(q[f]) if q.get(f) not in (None,'') else None for f in fields)
            for unit in sorted({q['unit'] for q in old}):
                prior,now = ([dict(q,value=float(q['value']) if q.get('value') not in ('',None) else None) for q in v if q['unit']==unit]
                             for v in (old,data['rows']))
                before,after = differences(prior,now,key)
                self.quantity(f'MEA display {p.name.removesuffix(".json.gz")} {unit}',before,after,unit=unit,
                              population=len(prior),pressure_basis='retained figure sample coordinates',
                              sources=(path,),old_source=base,endpoint=endpoint)
        paths = tuple(str(p.relative_to(OUT)) for p in sorted((OUT/'MDEA/curves').glob('batch-*.json.gz')))
        old = archived(MDEA_CURVES)['rows']
        endpoint = self.selections['MDEA'][1]
        replay = [self.read(path) for path in paths]
        assert all(q['endpoint_fingerprint']==endpoint for q in replay)
        for group in sorted({q['group'] for q in old}):
            prior = [q for q in old if q['group']==group]
            now = [q for item in replay for q in item['rows'] if q['group']==group]
            before,after = differences(prior,now,lambda q:q['identity'])
            self.quantity(f'MDEA display {group} Pa',before,after if now else None,unit='Pa',population=len(prior),
                          pressure_basis='archived curve temperature, aqueous stock and loading',
                          sources=paths,old_source=MDEA_CURVES,endpoint=endpoint,
                          disposition='partial' if now and len(now)<len(prior) else None)
        archive_path = 'MDEA/curves/archive/batch-000.json.gz'
        if archive := self.read(archive_path):
            p = {q['identity']:q for q in old}
            error = [abs(q['value']/p[q['identity']]['value']-1) for q in archive['rows'] if q.get('value') is not None]
            assert len(error)==24 and max(error)<1e-9, 'MDEA historical display identity'
            self.quantity('MDEA archived curve declaration readback',0,max(error),unit='relative',population=len(error),
                          sources=(archive_path,),old_source=MDEA_CURVES,endpoint=archive['endpoint_fingerprint'])
        curve_sources = {
            'DEA':'analyses/dea_transfer/results/refit-413/curve-data.json',
            'AMP_free':'analyses/amp_transfer/results/salt-anchored-435/curve-data.json',
            'AMP_fixed':'analyses/amp_transfer/results/retransfer-412-f2-05e94210/slope-150/curve-data.json',
        }
        for design,prior_path in curve_sources.items():
            path = 'DEA/property-comparisons/selected.json.gz' if design=='DEA' else f'{design}/properties.json.gz'
            current = self.read(path)
            old = archived(prior_path)
            if isinstance(old,dict):
                old = old['rows']
            new = current['curves'] if current else []
            identities = {q['identity'] for q in new}
            endpoint = self.selections[design][1]
            for group,unit in sorted({(q['group'],q['unit']) for q in old if q['identity'] in identities}):
                prior,now = ([q for q in v if (q['group'],q['unit'])==(group,unit)] for v in (old,new))
                before,after = differences(prior,now,lambda q:q['identity'])
                self.quantity(f'{design} display {group} {unit}',before,after,unit=unit,population=len(prior),
                              sources=(path,),old_source=prior_path,endpoint=endpoint,
                              pressure_basis='archived curve temperature, stock and loading')

    def compute(self):
        for design in COUNTS:
            self.fit(design)
            self.properties(design)
            self.phases(design)
        self.c1()
        self.mea_comparisons()
        self.mea_screen()
        self.curves()
        self.matched_literature()
        self.numerical_diagnosis()
        self.archived_inventory()
        timing = self.read('stages.json')
        if timing:
            for stage,data in timing.items():
                self.quantity(f'Campaign stage {stage}',None,data,unit='s',sources=('stages.json',),
                              disposition=data['disposition'])
        starting = json.loads(blob(str(HANDOFF.relative_to(r.ROOT)),'d8f4c877f'))['quantities']
        starting = {k:v['disposition'] for k,v in starting.items() if v['disposition'] in ('open','undecided')}
        return dict(base=BASE,reference_pressure_pa=P_REF,wheel=r.SHA,starting_dispositions=starting,
                    selected_starts={k:v[0] for k,v in self.selections.items()},
                    fit_attempts=self.attempts,quantities=self.items)


def main(check):
    quantities = Quantities()
    expected = quantities.compute()
    if check:
        retained = json.loads(HANDOFF.read_text())
        for key in sorted(expected['quantities'].keys() | retained['quantities'].keys()):
            assert retained['quantities'].get(key)==expected['quantities'].get(key), f'{key}: changed contributor or stale disposition'
        assert retained==expected, 'stale fit attempt inventory'
        print(f"{len(expected['quantities'])} retained comparison quantities verified")
    else:
        save(HANDOFF,expected)
        from notebook import render
        (HERE/'notebook.qmd').write_text(render(expected))


if __name__=='__main__':
    from refit import a
    a.study.reuse.bind_wheel()
    main(sys.argv[1:]==['--check'])
