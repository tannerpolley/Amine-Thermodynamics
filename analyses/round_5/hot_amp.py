"""Extend the reported fixed-slope AMP liquid paths to 458 K for diagnosis."""
from pathlib import Path
from tempfile import TemporaryDirectory
from time import monotonic
import json

from amp import DECLARATION, ENDPOINTS
from common import digest, fingerprints, save
from curvature import hessian
from part_ii import Route, eq, reg, np, stable
from reaction_reference import AMP_RECORD, source_log_k
from phases import fixed


def calculate(work, overlap_only=False):
    started = monotonic()
    cfg = stable.read(DECLARATION)
    cfg['specification'] = str(DECLARATION.parent / cfg['specification'])
    cfg['calculation_interval_K'][1] = 458.
    declaration = work/'AMP-458-K.json'
    declaration.write_text(json.dumps(cfg, indent=2)+'\n')
    route = Route(declaration,work/'hot')
    original_route = Route(DECLARATION,work/'original')
    params = ENDPOINTS/'slope-150/parameters.json'
    point = stable.read(params)
    spec, original = route.bind(point), original_route.bind(point)
    grid = [s for s in original_route.states(original) if s['key'].startswith('grid:')]
    last = max(r['T'] for r in grid)
    archive = stable.read(AMP_RECORD)
    samples = [last + j*5 for j in range(1+int((458.-last)//5))]
    if samples[-1] < 458.:
        samples.append(458.)
    edge = [r for r in grid if r['T'] == last]
    selected = sorted(edge, key=lambda r: not (r['a']==archive['loading'] and r['stock']['water']==archive['feed_mol'][2]))
    continuity = []
    for old, new in zip(next(p for p in original.problems.values() if p.reactions).reactions,
                        next(p for p in spec.problems.values() if p.reactions).reactions,strict=True):
        T = original_route.config['calculation_interval_K'][1]
        coeff = ('a','b','c','d','e','f','reference_temperature')
        assert all(getattr(old.correlation,k)==getattr(new.correlation,k) for k in coeff)
        left = (3*source_log_k(old.correlation,T)-4*source_log_k(old.correlation,T-.001)
                + source_log_k(old.correlation,T-.002))/.002
        right = (-3*source_log_k(new.correlation,T)+4*source_log_k(new.correlation,T+.001)
                 - source_log_k(new.correlation,T+.002))/.002
        continuity.append(dict(name=old.name, T_boundary_K=T, logK=source_log_k(old.correlation,T),
                               value_difference=source_log_k(new.correlation,T)-source_log_k(old.correlation,T),
                               derivative_below_per_K=left, derivative_above_per_K=right,
                               derivative_difference_per_K=right-left))
    save('D/hot-declaration.json',dict(declaration=cfg,declaration_sha256=digest(declaration),continuity=continuity,
         inputs=fingerprints(DECLARATION,params,AMP_RECORD)))
    if overlap_only:
        original_search = ENDPOINTS/'slope-150/search-1.json.gz'
        archive_grid = {row['key']: row for row in stable.read(original_search)}
        extended = {row['key']: row for row in stable.grid(point, grid, [], route=route)}
        rows = []
        for state in grid:
            key = state['key']
            old, new = archive_grid[key], extended[key]
            old_p, new_p = old.get('pressure_Pa'), new.get('pressure_Pa')
            old_tpd, new_tpd = old.get('raw_minimum'), new.get('raw_minimum')
            rows.append(dict(key=key, original=old, extension=new,
                             delta_Pa=new_p-old_p if old_p is not None and new_p is not None else None,
                             delta_TPD_over_RT=new_tpd-old_tpd if old_tpd is not None and new_tpd is not None else None,
                             same_availability=old.get('optimized_available')==new.get('optimized_available'),
                             same_descent=old.get('native_branch')==new.get('native_branch')))
        save('D/overlap.json.gz', dict(rows=rows, declaration_sha256=digest(declaration),
             inputs=fingerprints(DECLARATION,params,original_search)), start=started)
        return
    bubbles = {}
    paths = []
    def sample(state, T, interval_route=route, interval_spec=spec):
        requested = dict(state,T=T)
        item = interval_route.stability_row(interval_spec,requested,1.)
        model = interval_spec.model
        key = (interval_route.path, tuple(state['stock'].items()), state['a'], T)
        if key not in bubbles:
            bubbles[key] = eq.solve_equilibrium(model,item.pressure_reference)
        bubble = bubbles[key]
        result = dict(T_K=T,bubble_message=bubble.message,bubble_Pa=bubble.pressure)
        if not bubble.requested_tolerance_met:
            return dict(result,refusal=bubble.message)
        P = bubble.pressure*state['c']
        item.problem.pressure = type(item.problem.pressure).fixed(P)
        item.pressure_reference = None
        parent = eq.solve_equilibrium(model,item.problem)
        result.update(P_Pa=P,parent_message=parent.message)
        if not parent.requested_tolerance_met:
            return dict(result,refusal=parent.message)
        prediction = reg.predict(model,item)
        result['search']=stable.stability_payload(prediction)
        if prediction.stability is None:
            return dict(result,refusal=prediction.message)
        rr=prediction.stability.report.trials
        result.update(liquid=any(t.resolved_descent and t.quantities.get('density_side')==2 for t in rr),
                      vapor=any(t.resolved_descent and t.quantities.get('density_side')==1 for t in rr))
        try:
            result['curvature']=hessian(interval_spec,T,P,parent.phase_mole_fractions(0),parent.molar_densities[0])
            result['negative']=result['curvature']['sign']=='negative' if result['curvature']['sign']!='undecided' else None
        except (ValueError,RuntimeError,np.linalg.LinAlgError) as error:
            result['curvature_refusal']=str(error)
        return result

    def retain():
        save('D/hot-paths.json.gz',dict(paths=paths, planned_paths=len(selected),temperature_grid_K=samples,
             projection_minutes=[3,9]),start=started)
    for state in selected:
        record=dict(state=state,original_overlap=sample(state,last,original_route,original),rows=[],brackets={})
        paths.append(record)
        for T in samples:
            try:
                row=sample(state,T)
            except (RuntimeError,ValueError,AssertionError) as error:
                row=dict(T_K=T,refusal=f'{type(error).__name__}: {error}')
            record['rows'].append(row)
            if 'refusal' in row:
                break
        for mark in ('liquid','vapor','negative'):
            sampled=[q for q in record['rows'] if q.get(mark) is not None]
            found=[(a,b) for a,b in zip(sampled,sampled[1:]) if not a[mark] and b[mark]]
            record['brackets'][mark]=dict(reentries=sum(a[mark] and not b[mark] for a,b in zip(sampled,sampled[1:])),
                                          sampled_first=next((r['T_K'] for r in sampled if r[mark]),None),
                                          refined=None)
            if not found:
                continue
            (left,right),*_ = found
            refinements=[]
            record['brackets'][mark]['refinements']=refinements
            while right['T_K'] - left['T_K'] > .5:
                mid=sample(state,(left['T_K']+right['T_K'])/2)
                refinements.append(mid)
                if mid.get(mark) is None:
                    break
                if mid[mark]:
                    right=mid
                else:
                    left=mid
            record['brackets'][mark]['refined']=[left['T_K'],right['T_K']]
            if mark=='liquid':
                try:
                    record['seeded_liquid_confirmation']=fixed(route,spec,dict(state,T=right['T_K']),right['P_Pa'],
                                                              dict(pair=archive['split']))
                except (RuntimeError,ValueError,AssertionError) as error:
                    record['seeded_liquid_confirmation']=dict(refusal=str(error))
        retain()
        if monotonic()-started>=1080:
            record['stop']='Continuation reached twice the 9-minute upper projection'
            retain()
            break


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--overlap', action='store_true')
    with TemporaryDirectory() as directory:
        calculate(Path(directory), parser.parse_args().overlap)
