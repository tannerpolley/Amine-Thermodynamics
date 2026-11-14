"""Declaration-driven Part II calculations (#337); Engine owns numerical methods."""
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import zipfile
from types import SimpleNamespace

for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'analyses/mea_parameter_bundle/scripts'), str(ROOT/'analyses/mea_parameter_bundle/calibration-misfit')]
import epcsaft
import numpy as np
from epcsaft import equilibrium as eq, regression as reg
from MEA.solvent_specification import SolventSpecification, jsonable, deviation_statistics, conditional_information
import stable_refit_255 as stable

SHARED = ROOT/'analyses/mea_parameter_bundle/results/adoption-340/part-ii-shared-values.json'
SHARED_SHA = '4c27d47ea7b6e018b0603efb8a29fc2f3fe3c6f8fdc12ccc12cb10bb4b315334'
WHEEL = ROOT/'build/engine-wheels/main-391dfe5d64ede5036bf160bc6ae037ad5e14af32/epcsaft-1.3.0-cp313-cp313-manylinux_2_39_x86_64.whl'
SHA = '0962e21d2fa7a8ba1ed4622f1110b3e8053bacd878fa41c999d85e8b9afab66b'


def target_identity(mapping, family, target):
    if family=='temperature_law_coefficient':
        return target
    return next(c['identity'] for block in (mapping['components'] if isinstance(target,str) else mapping['pairs']) if (block.get('component_id')==target if isinstance(target,str) else {block['component_id_a'],block['component_id_b']}==set(target)) for c in block['coefficients'] if c['family']==family)


class Route:
    def __init__(self, declaration):
        self.path = Path(declaration).resolve()
        self.config = json.loads(self.path.read_text())
        self.out = self.path.parent/self.config['output']
        available = int(next(x for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')).split()[1])/1e6
        self.workers = max(1, min(int(os.environ['AGENT_HEAVY_CORES']), int((available-7)/.35)))
        self.controls = self.config['optimizer']
        self.verify()
        identity = dict(declaration_sha256=hashlib.sha256(self.path.read_bytes()).hexdigest(),wheel_sha256=SHA,shared_values_sha256=SHARED_SHA)
        if (self.out/'identity.json').exists():
            assert self.result('identity.json')==identity, 'Use a new output directory for changed declarations'
        self.write('identity.json',identity)

    def load(self, reference):
        path = self.path.parent/reference['path']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == reference['sha256'], path
        return json.loads(path.read_text())

    def verify(self):
        assert hashlib.sha256(SHARED.read_bytes()).hexdigest() == SHARED_SHA
        assert hashlib.sha256(WHEEL.read_bytes()).hexdigest() == SHA
        with zipfile.ZipFile(WHEEL) as archive:
            for name in archive.namelist():
                if name.startswith(('epcsaft/', 'epcsaft.libs/')) and not name.endswith('/'):
                    assert archive.read(name) == (Path(epcsaft.__file__).parent.parent/name).read_bytes(), name

    def write(self, name, value):
        path = self.out/name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(jsonable(value), indent=2, allow_nan=False)+'\n')

    def result(self, name):
        return json.loads((self.out/name).read_text())

    def start(self, reference, *, adopt=True):
        mapping = self.load(reference)
        laws = self.load(reference['reactions']) if 'reactions' in reference else SolventSpecification(self.path.parent/self.config['specification']).spec['chemistry']['reactions']
        declared = self.load(reference.get('coordinates',self.config['coordinates']))
        if adopt:
            shared = json.loads(SHARED.read_text())
            fixed = json.loads((ROOT/'analyses/solvent_specification_mea/inputs/endpoint.json').read_text())
            assert hashlib.sha256((ROOT/'analyses/solvent_specification_mea/inputs/endpoint.json').read_bytes()).hexdigest()==shared['parameter_sha256']
            common = {'water','carbon-dioxide','hydronium-cation','hydroxide-anion','bicarbonate-anion','carbonate-anion'}
            mapping['components'] = [copy.deepcopy(next(c for c in fixed['components'] if c['component_id']==old['component_id'])) if old['component_id'] in common else old for old in mapping['components']]
            mapping['pairs'] = [copy.deepcopy(next(p for p in fixed['pairs'] if {p['component_id_a'],p['component_id_b']}=={old['component_id_a'],old['component_id_b']})) if {old['component_id_a'],old['component_id_b']}<=common else old for old in mapping['pairs']]
            for group in laws.values():
                for reaction in group:
                    if reaction['name'] in ('R1', 'R2', 'R3'):
                        source = next(r for r in shared['reactions'] if r['name'] == reaction['name'])
                        reaction['correlation'], reaction['reference'] = source['correlation'], source['reference']
            mapping['correlations'] = [copy.deepcopy(c) for c in mapping['correlations'] if c.get('component_id') not in common]+[copy.deepcopy(c) for c in fixed['correlations'] if c.get('component_id') in common]
            for section in ('sites','edges','no_cross_association'):
                def shared_node(node):
                    return {node.get('component_id'),node.get('component_id_a'),node.get('component_id_b'),node.get('endpoint_a',{}).get('component_id'),node.get('endpoint_b',{}).get('component_id')}-{None} <= common
                mapping['topology'][section] = [c for c in mapping['topology'].get(section,[]) if not shared_node(c)]+[copy.deepcopy(c) for c in fixed['topology'].get(section,[]) if shared_node(c)]
            for ion in self.config['born_ties']:
                component = next(c for c in mapping['components'] if c['component_id'] == ion)
                sigma = next(c['value']['magnitude'] for c in component['coefficients'] if c['family']=='segment_diameter')
                next(c for c in component['coefficients'] if c['family']=='born_diameter')['value']['magnitude'] = sigma
                declared = [q for q in declared if q.get('targets') != [['born_diameter',ion,1.0]]]
                coordinate = next((q for q in declared if ['segment_diameter',ion,1.0] in q.get('targets',[])),None)
                if coordinate is not None and ['born_diameter',ion,1.0] not in coordinate['targets']:
                    coordinate['targets'].append(['born_diameter',ion,1.0])
        for q in declared:
            if q.get('targets'):
                family,target,factor = q['targets'][0]
                q['origin'] = stable.s.parameter_values(mapping)[target_identity(mapping,family,target)]/factor
        for q in declared:
            if q.get('kind')=='reaction_coordinate':
                law = next(r['correlation'] for group in laws.values() for r in group if r['name']==q['name'])
                assert q['origin']==law.get(q['coefficient'],0.), f"Start {reference['path']}: reaction coordinate does not match completed law"
            if not q['bounds'][0]<=q['origin']<=q['bounds'][1]:
                raise ValueError(f"Start {reference['path']}: {q.get('identity',q.get('name'))} origin {q['origin']} outside bounds {q['bounds']}")
        return dict(parameters=mapping, reactions=laws, coordinates=declared)

    def bind(self, point):
        spec = SolventSpecification(self.path.parent/self.config['specification'])
        spec.parameters = epcsaft.Parameters.from_mapping(point['parameters'])
        spec.model = epcsaft.Mixture(spec.parameters, thermochemistry=spec.thermal)
        assert list(spec.parameters.component_ids)==self.config['species']
        spec.inputs['endpoint'] = point
        spec.construction_parameters = {k:spec.parameters for k in spec.construction_parameters}
        spec.spec['chemistry']['reactions'] = copy.deepcopy(point['reactions'])
        interval = self.config['calculation_interval_K']
        for problem in spec.problems.values():
            assert interval[0] <= problem.T <= interval[1], problem.T
            for reaction in problem.reactions:
                law = next(r['correlation'] for group in point['reactions'].values() for r in group if r['name']==reaction.name)
                reaction.correlation = eq.ReactionLogPolynomial(**dict(law, temperature_min=interval[0], temperature_max=interval[1]))
        for group in spec.spec['chemistry']['reactions'].values():
            for reaction in group:
                reaction['correlation'].update(temperature_min=interval[0], temperature_max=interval[1])
        for role in ('fitted','comparisons'):
            for row in spec.inputs['observations'][role]:
                row['temperature_domain'] = interval
                row['role'] = row.get('role',self.config.get('roles',{}).get(row['group'], 'fitted' if role=='fitted' else 'not fitted'))
                assert row['role'] in ('fitted','not fitted','comparison only')
                assert (row['role']=='fitted') == (role=='fitted')
        spec.inputs['coordinates'] = copy.deepcopy(point['coordinates'])
        if 'covariance' in self.config:
            covariance = self.load(self.config['covariance'])
            rows = spec.inputs['observations']['fitted']
            assert covariance['identities']==[r['identity'] for r in rows]
            assert all(r['weight']==1 and r['arguments']['form']=='difference' and r['arguments']['scale']==1 for r in rows), 'Covariance uses raw difference observations, as in PZ'
            spec.spec['measurement_covariance'] = covariance['covariance']
        return spec

    def endpoint_mapping(self, start, report, declared):
        point, values = copy.deepcopy(start), iter(report['physical'])
        for coordinate, optimizer in zip(point['coordinates'], report['optimizer'], strict=True):
            coordinate['origin'] += coordinate['scale']*optimizer
            if coordinate.get('kind') == 'reaction_enthalpy_shift':
                shift = coordinate['origin']
                coordinate['bounds'] = [v-shift for v in coordinate['bounds']]
                coordinate['origin'] = 0.
        updates = {}
        for q in declared:
            for family, target, factor in q.get('targets',[]):
                identity = target_identity(start['parameters'],family,target)
                updates[identity] = next(values)
        point['parameters'] = stable.s.with_parameter_values(start['parameters'], updates)
        point['reactions'] = report['reactions']
        for coordinate in point['coordinates']:
            if coordinate.get('kind') == 'reaction_coordinate':
                law = next(r['correlation'] for group in point['reactions'].values() for r in group if r['name']==coordinate['name'])
                origin = law.get(coordinate['coefficient'], 0.)
                # Transport only the completion offset, not the fitted displacement.
                delta = origin-coordinate['origin']
                coordinate['bounds'] = [v+delta for v in coordinate['bounds']]
                coordinate['origin'] = origin
        return point

    def replay(self, point, rows=None):
        spec = self.bind(point)
        records = spec.inputs['observations']['fitted'] if rows is None else rows(spec)
        values = [spec.prediction(record) for record in records]
        ok = all(r['status']=='Available' and r.get('requested_tolerance_met') for r in values)
        if ok:
            residuals = spec.whiten(np.array([r['residual'] for r in values]),records)
            for row, residual in zip(values,residuals,strict=True):
                row.update(weighted_residual=float(residual),cost=.5*float(residual)**2)
        return values, ok, math.fsum(r['cost'] for r in values) if ok else None

    def states(self, spec):
        states = []
        for role in ('fitted','comparisons'):
            for row in spec.inputs['observations'][role]:
                if row['constructor']=='residual_excess_enthalpy':
                    continue
                if row['constructor']=='saturation_capped_addition_enthalpy':
                    states.append(dict(key=row['identity']+':cap',cap_record=row['identity']))
                for field in ('problem','initial','final','bubble'):
                    if field in row:
                        states.append(dict(key=row[field], problem=row[field]))
        states.extend(dict(key=r['problem'],problem=r['problem']) for r in spec.inputs['observations']['phase_states'])
        states.extend(stable.states(self.config['stocks'],self.config['loadings']))
        return list({r['key']:r for r in states}.values())

    def stability_row(self, spec, state, scale):
        if 'cap_record' in state:
            record = next(r for role in ('fitted','comparisons') for r in spec.inputs['observations'][role] if r['identity']==state['cap_record'])
            prediction = reg.predict(spec.model,spec.observation(record))
            if prediction.status.name!='Available':
                raise ValueError(prediction.message)
            parent, args = copy.copy(spec.problems[record['initial']]), record['arguments']
            parent.feed = eq.Amounts({c:parent.feed.values.get(c,0.)+prediction.endpoint_loading*args['basis_amount']*args['feed'].get(c,0.) for c in spec.parameters.component_ids})
            return reg.stability(spec.parameters,parent,scale=scale)
        if 'problem' in state:
            parent = copy.copy(spec.problems[state['problem']])
            bubble = copy.copy(parent) if isinstance(parent.P, eq.Free) else None
            parent.phases = [copy.copy(parent.phases[0])]
            parent.phases[0].amount = eq.Free()
            parent.P = 1e5 if bubble is not None else parent.P
        else:
            template = next(p for p in spec.problems.values() if p.reactions)
            feed = dict(state['stock'], **{'carbon-dioxide':state['a']*state['stock'][self.config['amine']]})
            parent = eq.Problem(T=state['T'], P=1e5, feed=eq.Amounts(feed), phases=[eq.Phase('L',kind='liquid',support=self.config['species'])], reactions=template.reactions, neutral_reference=template.neutral_reference, row_tolerance=template.row_tolerance)
            bubble = copy.copy(parent)
            bubble.P = eq.Free(1e5)
            bubble.phases = list(parent.phases)+[eq.Phase('V',kind='vapor',support=self.config['vapor_species'],amount=eq.Pinned(0.))]
        return reg.stability(spec.parameters, parent, scale=scale, **(dict(pressure_reference=bubble,pressure_ratio=state.get('c',1.05)) if bubble else {}))

    def grid(self, point, states):
        registry = self.result('split-record.json') if (self.out/'split-record.json').exists() else self.load(self.config['split_record'])
        assert registry['amine']==self.config['amine'] and registry['species']==self.config['species']
        supplied = registry.setdefault('supplied_trials',[])
        supplied.extend(w for w in registry['trials'] if not w.get('resolved_descent') and w not in supplied)
        registry['trials'] = [w for w in registry['trials'] if w.get('resolved_descent')]
        witnesses = registry['trials']
        trials = witnesses+supplied
        measured = stable.grid(point, states, trials, route=self)
        for row in measured:
            for witness in row.get('witnesses',[]):
                if witness.get('resolved_descent') and witness not in witnesses:
                    witnesses.append(witness)
        self.write('split-record.json',registry)
        self.write('search-'+str(len(list(self.out.glob('search-*.json'))))+'.json',measured)
        return measured

    def segment(self, anchor, endpoint, t):
        point = copy.deepcopy(anchor)
        point['parameters'] = stable.segment(anchor['parameters'],endpoint['parameters'],t)
        for dest, left, right in zip(point['coordinates'],anchor['coordinates'],endpoint['coordinates'],strict=True):
            dest['origin'] = left['origin']+t*(right['origin']-left['origin'])
            dest['bounds'] = [a+t*(b-a) for a,b in zip(left['bounds'],right['bounds'],strict=True)]
        for group in point['reactions']:
            for dest, left, right in zip(point['reactions'][group],anchor['reactions'][group],endpoint['reactions'][group],strict=True):
                for key in ('a','b','c','d','e','f'):
                    dest['correlation'][key] = left['correlation'].get(key,0.)+t*(right['correlation'].get(key,0.)-left['correlation'].get(key,0.))
        return point

    def search(self, point):
        measured = self.grid(point,self.states(self.bind(point)))
        tally = dict(stable.tally(measured),unavailable_searches=[row for row in measured if not row.get('available')])
        return dict(grid=tally,offset=dict(descent=0),census=dict(descent=0),stable=not tally['descent'] and not tally['unavailable'])

    def campaign(self):
        import reduced_refit_338 as reduced
        assert len(self.config['starts'])==2 and self.config['loadings'][0]==1e-5, 'Part II requires two complete starts and loadings from 1e-5 mol/mol'
        candidates = [reduced.candidate(f'start-{i}',self.start(ref),{},[],{},route=self) for i,ref in enumerate(self.config['starts'])]
        candidates = [r for r in candidates if r is not None]
        converged = [r for r in candidates if r['optimizer_converged']]
        chosen = min(converged,key=lambda r:r['cost']) if converged else None
        self.write('selection.json',dict(candidates=candidates,chosen=chosen,ties=[r['name'] for r in converged if chosen and abs(r['cost']-chosen['cost'])<=self.controls['function_tolerance']]))
        return chosen

    def marks(self, T, problem=None):
        used = {r.name for r in problem.reactions} if problem is not None else set(self.config['reaction_ranges_K'])
        return {name: 'reaction not used' if name not in used else 'source range unknown' if self.config['reaction_ranges_K'].get(name) is None else not self.config['reaction_ranges_K'][name][0]<=T<=self.config['reaction_ranges_K'][name][1] for name in used|set(self.config['reaction_ranges_K'])}

    def uncertainty(self, point):
        (self.out/'conditional-uncertainty.json').unlink(missing_ok=True)
        spec = self.bind(point)
        declared = point['coordinates']
        rows = spec.inputs['observations']['fitted']
        ev = reg.differentiate(spec.parameters,spec.coordinates(),[spec.observation(r) for r in rows],optimizer=[0.]*len(declared),thermochemistry=spec.thermal)
        replay, available, _ = self.replay(point)
        assert all(status.name=='Available' for status in ev.statuses)
        assert available and [r['identity'] for r in replay]==[r['identity'] for r in rows]
        assert np.allclose(ev.predictions,[r['value'] for r in replay],rtol=1e-8,atol=0.), 'Differentiation/replay row mismatch'
        J = spec.whiten(np.array(ev.residual_optimizer_gradient).reshape(-1,len(declared)))/np.array([q['scale'] for q in declared])
        active = [i for i,q in enumerate(declared) if min(q['origin']-q['bounds'][0],q['bounds'][1]-q['origin'])<=1e-6*q['scale']]
        result = conditional_information(SimpleNamespace(physical=[q['origin'] for q in declared],covariance=SimpleNamespace(active_bounds=active)),J,spec.whiten(np.array([r['residual'] for r in replay])),[q['identity'] for q in declared],[q['bounds'][0] for q in declared],[q['bounds'][1] for q in declared])
        self.write('conditional-uncertainty.json',dict(result,coordinates=declared,active_bounds=active))

    def reduce(self, point):
        spec, output = self.bind(point), []
        for role in ('fitted','comparisons'):
            for record in spec.inputs['observations'][role]:
                T = spec.problems[record.get('problem',record.get('initial'))].T
                output.append(dict(spec.prediction(record), role=record['role'], T_K=T, outside_ranges=self.marks(T,spec.problems[record.get('problem',record.get('initial'))])))
        summary = []
        for group,role,unit in sorted({(r['group'],r['role'],r.get('unit') or 'unit unspecified') for r in output}):
            for name in {name for r in output for name in r['outside_ranges']}:
                for outside in (False,True,'source range unknown','reaction not used'):
                    rows = [r for r in output if (r['group'],r['role'],r.get('unit') or 'unit unspecified',r['outside_ranges'].get(name,'reaction not used'))==(group,role,unit,outside)]
                    pairs = [(r['observed'],r['value']) for r in rows if r.get('value') is not None and r.get('status')=='Available']
                    summary.append(dict(group=group,role=role,unit=unit,range_name=name,outside_range=outside,rows=len(rows),available=len(pairs),statistics=deviation_statistics(pairs,unit) if pairs else None))
        self.write('data-rows.json',output)
        self.write('deviations.json',summary)

    def curves(self, point):
        spec, output = self.bind(point), []
        for row in self.load(self.config['curve_rows']):
            record = copy.deepcopy(row['observation'])
            for key, declaration in row['problems'].items():
                spec.problems[key] = spec.problem(declaration['template'],declaration['bindings'])
            record.update(observation_parameters=spec.parameter_sha256,temperature_domain=self.config['calculation_interval_K'])
            T = spec.problems[record.get('problem',record.get('initial'))].T
            assert self.config['calculation_interval_K'][0]<=T<=self.config['calculation_interval_K'][1]
            output.append(dict(spec.prediction(record),curve=row['curve'],loading=row['loading'],T_K=T,outside_ranges=self.marks(T,spec.problems[record.get('problem',record.get('initial'))])))
        self.write('curve-data.json',output)


if __name__ == '__main__':
    route = Route(sys.argv[1])
    assert not route.config.get('replay_only') or sys.argv[2]=='replay', 'Frozen replay fixture cannot run a campaign'
    if sys.argv[2] == 'fit':
        route.campaign()
    elif sys.argv[2] == 'report':
        point = route.result('selection.json')['chosen']['parameters']
        route.reduce(point)
        route.uncertainty(point)
        route.curves(point)
    elif sys.argv[2] == 'replay':
        point = route.start(route.config['reference'],adopt=False)
        rows, available, cost = route.replay(point)
        reference = route.load(route.config['reference_predictions'])
        errors = [abs(r['value']/old['value']-1) for r,old in zip(rows,reference,strict=True)]
        report = dict(rows=len(rows),available=available,cost=cost,max_relative_prediction_error=max(errors),relative_cost_error=abs(cost/route.config['reference_cost']-1),wheel_sha256=SHA,shared_values_sha256=SHARED_SHA)
        route.write('replay.json',dict(report,values=rows))
        print(report,flush=True)
        assert available and max(report['max_relative_prediction_error'],report['relative_cost_error'])<=1e-8
    else:
        raise ValueError('Expected replay, fit or report')
