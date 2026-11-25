"""Declaration-driven Part II calculations (#337); Engine owns numerical methods."""
import copy
import dataclasses
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
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
WHEEL = ROOT/'build/engine-wheels/main-05e94210fa64cf69725e45babc0411d32139df5a/epcsaft-1.3.1-cp313-cp313-manylinux_2_39_x86_64.whl'
SHA = 'c9fbf898b14d004f915f01ed77675867908dd30d77dc28544b2860e9195c80bb'
RUN_BYTES = 99_338_608  # #402: retained piperazine run, retransfer-345


def target_identity(mapping, family, target):
    if family=='temperature_law_coefficient':
        return target
    return next(c['identity'] for block in (mapping['components'] if isinstance(target,str) else mapping['pairs']) if (block.get('component_id')==target if isinstance(target,str) else {block['component_id_a'],block['component_id_b']}==set(target)) for c in block['coefficients'] if c['family']==family)


def calculation_declaration(value):
    if dataclasses.is_dataclass(value): return {f.name: calculation_declaration(getattr(value,f.name)) for f in dataclasses.fields(value)}
    if isinstance(value, dict): return {k: calculation_declaration(v) for k,v in value.items()}
    if isinstance(value, (list,tuple)): return [calculation_declaration(v) for v in value]
    if hasattr(value,'name') and hasattr(value,'value'): return value.name
    if type(value).__module__.startswith('epcsaft'):
        return {k: calculation_declaration(getattr(value,k)) for k in dir(value) if not k.startswith('_') and not callable(getattr(value,k))}
    return value

def density_branch(trials):
    sides = {t.get('density_side') for t in trials}
    if not sides:
        return 'none'
    if len(sides)>1:
        return 'mixed'
    return {1: 'vapor', 2: 'liquid'}.get(next(iter(sides)), 'unresolved')

def branch_counts(row):
    native = row.get('witnesses', [])
    supplied = [dict(density_side=t.get('quantities', {}).get('density_side'))
                for t in row.get('supplied_trials', []) if stable.supplied_negative(t)]
    return dict(native_branch=density_branch(native), supplied_branch=density_branch(supplied),
                native_liquid_descent=any(t.get('density_side')==2 for t in native),
                liquid_liquid_split=row.get('parent_kind')=='Liquid' and any(t.get('density_side')==2 for t in native))


def active_bound_indices(coordinates):
    return [i for i, q in enumerate(coordinates)
            if min(q['origin']-q['bounds'][0], q['bounds'][1]-q['origin']) <= 1e-6*q['scale']]


def select_campaign_endpoint(candidates, tolerance):
    converged = [row for row in candidates if row is not None and row['optimizer_converged']]
    chosen = min(converged, key=lambda row: row['cost'], default=None)
    ties = [row['name'] for row in converged if abs(row['cost'] - chosen['cost']) <= tolerance]
    return chosen, ties


class Route:
    branch_counts = staticmethod(branch_counts)
    density_branch = staticmethod(density_branch)
    def __init__(self, declaration, out=None, *, shared_values=None, fixed_reference_pressure_pa=None):
        self.path = Path(declaration).resolve()
        self.config = json.loads(self.path.read_text())
        self.out = Path(out) if out else self.path.parent/self.config['output']
        available = int(next(x for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')).split()[1])/1e6
        self.workers = max(1, min(int(os.environ['AGENT_HEAVY_CORES']), int((available-7)/.35)))
        self.controls = self.config['optimizer']
        self.shared_values = shared_values
        self.fixed_reference_pressure_pa = fixed_reference_pressure_pa
        self.verify()
        identity = dict(declaration_sha256=hashlib.sha256(self.path.read_bytes()).hexdigest(),wheel_sha256=SHA,
                        shared_values_sha256=SHARED_SHA if shared_values is None else shared_values[1])
        if fixed_reference_pressure_pa is not None:
            identity['fixed_reference_pressure_pa'] = fixed_reference_pressure_pa
        if (self.out/'identity.json').exists():
            assert self.result('identity.json')==identity, 'Use a new output directory for changed declarations'
        self.write('identity.json',identity)

    def load(self, reference):
        path = self.path.parent/reference['path']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == reference['sha256'], path
        return json.loads(path.read_text())

    def verify(self):
        assert hashlib.sha256(SHARED.read_bytes()).hexdigest() == SHARED_SHA
        if self.shared_values is not None:
            path, digest = self.shared_values
            assert hashlib.sha256(path.read_bytes()).hexdigest() == digest
        assert hashlib.sha256(WHEEL.read_bytes()).hexdigest() == SHA
        with zipfile.ZipFile(WHEEL) as archive:
            for name in archive.namelist():
                if name.startswith(('epcsaft/', 'epcsaft.libs/')) and not name.endswith('/'):
                    assert archive.read(name) == (Path(epcsaft.__file__).parent.parent/name).read_bytes(), name

    def write(self, name, value):
        path = self.out/name
        data = (json.dumps(jsonable(value), indent=2, allow_nan=False)+'\n').encode()
        projected = sum(f.stat().st_size for f in self.out.rglob('*') if f != path and f.is_file()) + len(data)
        if projected > RUN_BYTES:
            raise RuntimeError(f'{path}: run folder would reach {projected} bytes (limit {RUN_BYTES})')
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def check_run_output(self):
        path = f'{self.out.resolve()}/'
        if path.startswith(f'{ROOT}/') and (subprocess.run(['git', 'check-ignore', '-q', '--', path], cwd=ROOT).returncode or subprocess.check_output(['git', 'ls-files', '--', path], cwd=ROOT)):
            raise RuntimeError(f'{path}: choose a run folder ignored by Git or outside the repository')

    def result(self, name):
        return stable.read(self.out/name)

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
        if self.shared_values is not None:
            shared = stable.read(self.shared_values[0])
            assert shared['wheel_sha256'] == SHA
            for pair in shared['water_ion_pairs']:
                assert pair in point['parameters']['pairs'], pair
        datasets = self.load(self.config['dataset_changes']) if 'dataset_changes' in self.config else {}
        interval = self.config['calculation_interval_K']
        reactions = copy.deepcopy(point['reactions'])
        for group in reactions.values():
            for reaction in group:
                reaction['correlation'].update(temperature_min=interval[0], temperature_max=interval[1])
        if self.fixed_reference_pressure_pa is not None:
            datasets.update(reactions=reactions, reaction_reference_pressure_pa=self.fixed_reference_pressure_pa)
        spec = SolventSpecification(self.path.parent/self.config['specification'], **datasets)
        spec.parameters = epcsaft.Parameters.from_mapping(point['parameters'])
        spec.model = epcsaft.Mixture(spec.parameters, thermochemistry=spec.thermal)
        assert list(spec.parameters.component_ids)==self.config['species']
        spec.inputs['endpoint'] = point
        spec.construction_parameters = {k:spec.parameters for k in spec.construction_parameters}
        for problem in spec.problems.values():
            assert interval[0] <= problem.T <= interval[1], problem.T
            if self.fixed_reference_pressure_pa is None:
                for reaction in problem.reactions:
                    law = next(r['correlation'] for group in reactions.values() for r in group if r['name']==reaction.name)
                    reaction.correlation = eq.ReactionLogPolynomial(**law)
        if self.fixed_reference_pressure_pa is None:
            spec.spec['chemistry']['reactions'] = reactions
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
        states.extend(stable.states(*self.grid_axes(spec)))
        return list({r['key']:r for r in states}.values())

    def grid_axes(self, spec):
        """#337 rule (b) grid from the declared fitted stocks and data loadings: 0.1 mol/mol loading steps from 1e-5 to the
        largest data loading, and fitted concentrations within 1 wt% of the lowest of their group searched once, at that lowest."""
        loadings = self.config['loadings']
        if not self.config['stocks']:
            return [], []
        assert loadings[0]==1e-5, 'Part II grid loadings start at 1e-5 mol/mol'
        top = loadings[-1]
        loadings = [1e-5]+[round(.1*k,4) for k in range(1,math.ceil(top/.1-1e-9))]+[top]
        masses = {c['component_id']:c['fixed']['molar_mass']['value']['magnitude'] for c in epcsaft.parameters.document_mapping(spec.parameters)['components']}
        weight = lambda stock: 100*masses[self.config['amine']]*stock[self.config['amine']]/math.fsum(masses[c]*n for c,n in stock.items())
        stocks = []
        for stock in sorted(self.config['stocks'], key=weight):
            if not stocks or weight(stock)-weight(stocks[-1])>1.:
                stocks.append(stock)
        return stocks, loadings

    def stability_row(self, spec, state, scale):
        if 'cap_record' in state:
            record = next(r for role in ('fitted','comparisons') for r in spec.inputs['observations'][role] if r['identity']==state['cap_record'])
            prediction = reg.predict(spec.model,spec.observation(record))
            if prediction.status.name!='Available':
                raise ValueError(prediction.message)
            parent, args = copy.copy(spec.problems[record['initial']]), record['arguments']
            parent.feed = eq.Amounts({c:parent.feed.values.get(c,0.)+prediction.endpoint_loading*args['basis_amount']*args['feed'].get(c,0.) for c in spec.parameters.component_ids})
            bubble = None
        elif 'binary_x' in state:
            water, amine = 'water', self.config['amine']
            feed = {water:1-state['binary_x'], amine:state['binary_x']}
            parent = eq.Problem(T=state['T'], P=state['P'], feed=eq.Amounts(feed),
                                phases=[eq.Phase('L',kind='liquid',support=list(feed))], row_tolerance=1e-10)
            bubble = None
        elif 'problem' in state:
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
        if state.get('compressed'):
            bubble = copy.copy(parent)
            bubble.P = eq.Free(1e5)
            bubble.phases = list(parent.phases)+[eq.Phase('V',kind='vapor',support=self.config['vapor_species'],amount=eq.Pinned(0.))]
        item = reg.stability(spec.parameters, parent, scale=scale, **(dict(pressure_reference=bubble,pressure_ratio=state.get('c',1.05)) if bubble else {}))
        removed = set(eq.compile_problem(spec.model,item.problem).removed_species)
        if removed:
            # ponytail: remove when tannerpolley/epcsaft#24 excludes compiler-certified absent species.
            support = {i for i,v in enumerate(item.problem.feed.values) if v>0}
            support.update(i for rx in item.problem.reactions for i,v in enumerate(rx.stoichiometry) if v!=0)
            support = sorted(support-removed)
            charges = {c['component_id']:c['fixed']['charge_number']['value']['magnitude'] for c in epcsaft.parameters.document_mapping(spec.parameters)['components']}
            neutral = [i for i in support if charges[spec.parameters.component_ids[i]]==0]
            trials = []
            for ids,kind in ((support,'Liquid'),(neutral,'Liquid'),(neutral,'Vapor')):
                phase = type(item.problem.phases[0])()
                phase.name, phase.kind, phase.support, phase.support_declared = 'feasible', getattr(type(phase.kind),kind), ids, True
                trials.append(phase)
            item.stability_options.trials = trials
        return item

    def temperature(self, spec, state):
        if 'cap_record' in state:
            return spec.problems[next(r for role in ('fitted','comparisons') for r in spec.inputs['observations'][role] if r['identity']==state['cap_record'])['initial']].T
        return spec.problems[state['problem']].T if 'problem' in state else state['T']

    def stability_metadata(self, spec, item):
        return dict(restricted_trial_families=True,removed_species=list(eq.compile_problem(spec.model,item.problem).removed_species)) if item.stability_options.trials else {}

    def pressure_basis(self, spec, state, item, prediction):
        reference = prediction.pressure_reference
        out = dict(declared_pressure_Pa=item.problem.pressure.value if item.pressure_reference is None else None,
                   search_pressure_Pa=reference.value*item.pressure_ratio if reference else item.problem.pressure.value if item.pressure_reference is None else None,
                   pressure_ratio=item.pressure_ratio if item.pressure_reference is not None else None,
                   model_bubble_pressure_Pa=reference.value if reference else None)
        if item.pressure_reference is None and 'binary_x' not in state:
            try:
                bubble = eq.solve_equilibrium(spec.model, self.stability_row(spec, dict(state, compressed=True), 1.).pressure_reference)
                out.update(model_bubble_pressure_Pa=bubble.pressure if bubble.requested_tolerance_met else None, message=bubble.message)
            except Exception as error: out['message'] = str(error)
        return out

    def penalty_states(self, states, spec):
        copies = {}
        self.penalty_unavailable = []
        for state in states:
            for ratio in (1.05, 3.):
                candidate = dict(state, key=f"compressed:{state['key']}:{ratio}", c=ratio, compressed=True)
                try:
                    item = self.stability_row(spec,candidate,1.)
                except Exception as error:
                    self.penalty_unavailable.append(dict(source=state['key'],pressure_ratio=ratio,message=str(error)))
                    continue
                identity = json.dumps(calculation_declaration([item.problem,item.pressure_reference,ratio]),sort_keys=True)
                row = copies.setdefault(identity, dict(candidate, sources=[]))
                if state['key'] not in row['sources']: row['sources'].append(state['key'])
        binary = self.config.get('binary_penalty', {})
        return list(copies.values()) + [
            dict(key=f'binary:{T}:{x}', T=T, P=binary['pressure_Pa'], binary_x=x)
            for T in binary.get('temperatures_K',[]) for x in binary['x_MDEA']
        ]

    def same_calculations(self, point, states):
        """Data-state key -> the first key whose search the Engine receives identically; grid keys differ by construction."""
        spec, first, same = self.bind(point), {}, {}
        for state in states:
            if state['key'].startswith('grid:'):
                continue
            try:
                item = self.stability_row(spec, state, 1.)
            except Exception:
                continue  # measured on its own, where the refusal is recorded
            identity = json.dumps(calculation_declaration([item.problem, item.pressure_reference, item.pressure_ratio if item.pressure_reference is not None else None, item.stability_options.trials]), sort_keys=True)
            same[state['key']] = first.setdefault(identity, state['key'])
        return {key: source for key, source in same.items() if key != source}

    def grid(self, point, states, *, trial_set=None):
        self.check_run_output()
        registry = (dict(amine=self.config['amine'],species=self.config['species'],trials=list(trial_set)) if trial_set is not None else
                    self.result('split-record.json') if (self.out/'split-record.json').exists() else self.load(self.config['split_record']))
        assert registry['amine']==self.config['amine'] and registry['species']==self.config['species']
        supplied = registry.setdefault('supplied_trials',[])
        supplied.extend(w for w in registry['trials'] if not w.get('resolved_descent') and w not in supplied)
        registry['trials'] = [w for w in registry['trials'] if w.get('resolved_descent')]
        witnesses = registry['trials']
        for witness in witnesses+supplied:
            witness.setdefault('density_side', None)
            witness.setdefault('branch', density_branch([witness]))
        trials = witnesses+supplied
        identity = hashlib.sha256(json.dumps(jsonable([point, states, trials, self.config, trial_set is None]), sort_keys=True).encode()).hexdigest()
        cache = getattr(self, '_grid_cache', {})
        if identity in cache:
            return cache[identity]
        self.short_rows = True
        copies = self.same_calculations(point, states)
        rows = {r['key']: r for r in stable.grid(point, [s for s in states if s['key'] not in copies], trials, route=self)}
        measured = [rows[s['key']] if s['key'] not in copies else dict(rows[copies[s['key']]], key=s['key'], seconds=0., same_calculation_as=copies[s['key']]) for s in states]
        for row in measured:
            for witness in row.get('witnesses',[]):
                witness.setdefault('branch', density_branch([witness]))
                if witness.get('resolved_descent') and witness not in witnesses:
                    witnesses.append(witness)
        if trial_set is None:
            self.write('split-record.json',registry)
        self.write('search-'+str(len(list(self.out.glob('search-*.json'))))+'.json',measured)
        if len(cache)==4:
            cache.pop(next(iter(cache)))
        cache[identity] = measured
        self._grid_cache = cache
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
        tally['branches'] = {
            group: {source: {branch: sum(row.get(source+'_branch', 'unresolved' if stable.descent(row) else 'none')==branch
                                        for row in measured if row['key'].startswith('grid:')==(group=='grid'))
                             for branch in ('liquid','vapor','mixed','unresolved','none')}
                    for source in ('native','supplied')} for group in ('data','grid')}
        tally['liquid_liquid_splits'] = {group: sum(row.get('liquid_liquid_split',False) for row in measured if row['key'].startswith('grid:')==(group=='grid')) for group in ('data','grid')}
        return dict(grid=tally,offset=dict(descent=0),census=dict(descent=0),penalty_trigger=any(row.get('native_liquid_descent',False) for row in measured),stable=not tally['descent'] and not tally['unavailable'])

    def campaign(self):
        self.check_run_output()
        import reduced_refit_338 as reduced
        assert len(self.config['starts'])==2 and self.config['loadings'][0]==1e-5, 'Part II requires two complete starts and loadings from 1e-5 mol/mol'
        candidates = [reduced.candidate(f'start-{i}',self.start(ref),{},[],{},route=self) for i,ref in enumerate(self.config['starts'])]
        candidates = [r for r in candidates if r is not None]
        chosen, ties = select_campaign_endpoint(candidates, self.controls['function_tolerance'])
        self.write('selection.json', dict(candidates=candidates, chosen=chosen, ties=ties))
        return chosen

    def marks(self, T, problem=None):
        used = {r.name for r in problem.reactions} if problem is not None else set(self.config['reaction_ranges_K'])
        return {name: 'reaction not used' if name not in used else 'source range unknown' if self.config['reaction_ranges_K'].get(name) is None else not self.config['reaction_ranges_K'][name][0]<=T<=self.config['reaction_ranges_K'][name][1] for name in used|set(self.config['reaction_ranges_K'])}

    def differentiate_endpoint(self, point):
        spec = self.bind(point)
        declared = point['coordinates']
        rows = spec.inputs['observations']['fitted']
        ev = reg.differentiate(spec.parameters,spec.coordinates(),[spec.observation(r) for r in rows],optimizer=[0.]*len(declared),thermochemistry=spec.thermal)
        replay, available, _ = self.replay(point)
        assert all(status.name=='Available' for status in ev.statuses)
        assert available and [r['identity'] for r in replay]==[r['identity'] for r in rows]
        assert np.allclose(ev.predictions,[r['value'] for r in replay],rtol=1e-8,atol=0.), 'Differentiation/replay row mismatch'
        return spec, replay, ev

    def uncertainty(self, point):
        (self.out/'conditional-uncertainty.json').unlink(missing_ok=True)
        spec, replay, ev = self.differentiate_endpoint(point)
        declared = point['coordinates']
        J = spec.whiten(np.array(ev.residual_optimizer_gradient).reshape(-1,len(declared)))/np.array([q['scale'] for q in declared])
        active = active_bound_indices(declared)
        result = conditional_information(SimpleNamespace(physical=[q['origin'] for q in declared],covariance=SimpleNamespace(active_bounds=active)),J,spec.whiten(np.array([r['residual'] for r in replay])),[q['identity'] for q in declared],[q['bounds'][0] for q in declared],[q['bounds'][1] for q in declared])
        self.write('conditional-uncertainty.json',dict(result,coordinates=declared,active_bounds=active))
        return spec, replay, ev

    def reduce(self, point, fitted=None):
        spec, output = self.bind(point), []
        fitted = {} if fitted is None else {row['identity']: row for row in fitted}
        for role in ('fitted','comparisons'):
            for record in spec.inputs['observations'][role]:
                T = spec.problems[record.get('problem',record.get('initial'))].T
                prediction = fitted.get(record['identity']) if role == 'fitted' else None
                output.append(dict(prediction if prediction is not None else spec.prediction(record), role=record['role'], T_K=T, outside_ranges=self.marks(T,spec.problems[record.get('problem',record.get('initial'))])))
        summary = []
        for group,role,unit in sorted({(r['group'],r['role'],r.get('unit') or 'unit unspecified') for r in output}):
            for name in {name for r in output for name in r['outside_ranges']}:
                for outside in (False,True,'source range unknown','reaction not used'):
                    rows = [r for r in output if (r['group'],r['role'],r.get('unit') or 'unit unspecified',r['outside_ranges'].get(name,'reaction not used'))==(group,role,unit,outside)]
                    pairs = [(r['observed'],r['value']) for r in rows if r.get('value') is not None and r.get('status')=='Available']
                    summary.append(dict(group=group,role=role,unit=unit,range_name=name,outside_range=outside,rows=len(rows),available=len(pairs),statistics=deviation_statistics(pairs,unit) if pairs else None))
        self.write('data-rows.json',output)
        self.write('deviations.json',summary)
        return output

    def curves(self, point, declarations=None):
        spec, output = self.bind(point), []
        for row in self.load(self.config['curve_rows']) if declarations is None else declarations:
            record = copy.deepcopy(row['observation'])
            for key, declaration in row['problems'].items():
                spec.problems[key] = spec.problem(declaration['template'],declaration['bindings'])
            record.update(observation_parameters=spec.parameter_sha256,temperature_domain=self.config['calculation_interval_K'])
            T = spec.problems[record.get('problem',record.get('initial'))].T
            assert self.config['calculation_interval_K'][0]<=T<=self.config['calculation_interval_K'][1]
            output.append(dict(spec.prediction(record),curve=row['curve'],loading=row['loading'],T_K=T,outside_ranges=self.marks(T,spec.problems[record.get('problem',record.get('initial'))])))
        self.write('curve-data.json',output)
        return output


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
