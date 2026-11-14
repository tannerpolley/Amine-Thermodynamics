"""Fixed F2 evidence for #341; historical studies remain frozen."""
# ruff: noqa: E402 -- bind the adopted wheel before using historical producers.
import copy
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import adoption_297 as a
import candidate_evidence_255 as e
import reduced_refit_338 as f

r = a.r
OUT = r.B/'results/paper-evidence-341'
RECORD = r.B/'results/selected-current-best-parameters.json'
FROZEN = r.B/'results/adoption-340'

def setup():
    assert a.sha(RECORD) == 'ae17803e1bcb2ca0a1970e05c7cc235d615c4d8a3a349b5afef0b0401dedefed'
    OUT.mkdir(parents=True, exist_ok=True)
    a.OUT, a.RECORDS = OUT, {'candidate': RECORD}
    a.verify()


def replay():
    values, ok, cost = r.replay(r.s.parameter_mapping(RECORD))
    reference = r.read(FROZEN/'candidate/replay.json')['rows']
    delta = max(a.relative(x['value'], y['value']) for x,y in zip(values,reference,strict=True))
    assert ok and len(values)==307 and delta<=1e-10
    a.write('candidate/replay.json',dict(rows=values,cost=cost,maximum_relative_difference=delta))
    print('F2 replay',cost,delta,flush=True)


def evidence():
    a.evidence()
    rows = e.rows(OUT/'paper-evidence/heat.csv')
    e.table(OUT/'paper-evidence/heat.csv',[dict(x,role='fitted' if x['role']=='fitted' else 'not fitted') for x in rows])


def uncertainty():
    import uncertainty_307 as u
    def bound(name):
        assert name=='MEA'
        spec = r.bind(r.s.parameter_mapping(RECORD))
        declared = copy.deepcopy(r.read(r.B/'results/reduced-refit/F2/information.json')['coordinates'])
        spec.parameter_sha256 = a.sha(RECORD)
        units = {c['identity']:c['value']['unit'] for item in [*r.s.parameter_mapping(RECORD)['components'],*r.s.parameter_mapping(RECORD)['pairs']] for c in item['coefficients']}
        for q in declared:
            q['unit'] = units[q['identity']]
        spec.inputs['coordinates'] = declared
        return spec, declared, OUT/'uncertainty'
    u.BASE = '673bceb'
    u.setup = bound
    u.OUTPUTS['MEA'] = OUT/'uncertainty'
    u.main('MEA')


def comparison():
    # Run the unchanged #339 score producer with only its current-record directory rebound.
    source = (r.B/'scripts/same_data_part1.py').read_text()
    source = source[:source.index("if __name__ == '__main__':")]
    source = source.replace("e.B / 'results/adoption-297/paper-evidence'", "Path("+repr(str(OUT/'paper-evidence'))+")")
    namespace = {'__name__':'comparison_341','Path':Path}
    exec(compile(source,'same_data_part1.py','exec'),namespace)
    namespace['OUT'] = OUT/'same-data-comparison'
    namespace['OUT'].mkdir(exist_ok=True)
    namespace['e'].EV = r.B/'results/same-data-comparison/part1'
    namespace['scores']()
    source = (r.B/'scripts/same_data_comparison.py').read_text().rsplit("if __name__ == '__main__'",1)[0]
    source = source.replace("BUNDLE / 'results/adoption-297/paper-evidence'", "Path("+repr(str(OUT/'paper-evidence'))+")").replace('f8f64820b161377a0d97d1e4ad4f6cea764cd0558dc63231d58e2096988eef97',a.sha(RECORD)).replace('This work f8f64820','This work F2 ae17803e').replace('fitted_parameters=16','fitted_parameters=11')
    source = source.replace("    assert abs(aard - 19.4320747) < 5e-8  # independent source-inventory calculation, rounded to 7 decimals","    # F0's rounded AARD check is inapplicable to F2; exact source-row checks above remain.")
    namespace = {'__name__':'tables_341','__file__':str(r.B/'scripts/same_data_comparison.py')}
    exec(compile(source,'same_data_comparison.py','exec'),namespace)
    destination = OUT/'same-data-comparison'
    shutil.copyfile(r.B/'results/same-data-comparison/published-deviations.json',destination/'published-deviations.json')
    namespace['OUT'] = destination
    namespace['tables']()


def weights():
    spec = r.bind(r.s.parameter_mapping(RECORD))
    values = r.read(OUT/'candidate/replay.json')['rows']
    observations = spec.inputs['observations']['fitted']
    e.table(OUT/'objective-weights.csv',[dict(identity=x['identity'],group=x['group'],scale=o['row'].get('scale'),form=o['row'].get('form'),weight=o['weight'],cost=x['cost']) for x,o in zip(values,observations,strict=True)])
    a.write('objective-declarations.json',observations)
    groups = {}
    for x,o in zip(values,observations,strict=True):
        key = (x['group'],o['constructor'] if o['constructor']=='addition_enthalpy' else o['kind'],str(o['arguments'].get('species')),str(o['arguments'].get('scale',o['row'].get('scale',1.))),o['weight'])
        groups.setdefault(key,[]).append(x['cost'])
    e.table(OUT/'objective-groups.csv',[dict(group=k[0],quantity=k[1],species=k[2],scale=k[3],weight=k[4],n=len(v),cost=sum(v),cost_percent=100*sum(v)/sum(x['cost'] for x in values),rule='Frozen objective declarations; see objective-declarations.json and #255/#338') for k,v in groups.items()])


def stability():
    f.OUT = OUT/'stability'
    f.OUT.mkdir(exist_ok=True)
    shutil.copyfile(r.B/'results/reduced-refit/split-trials.json',f.OUT/'split-trials.json')
    registry = r.read(r.B/'results/reduced-refit/split-registry.json')
    f.split_registry = lambda: registry
    report = f.search('candidate',r.s.parameter_mapping(RECORD))
    assert not any(report[k]['descent'] for k in ('grid','offset','census')), 'Append newly resolved descents to the MEA registry before continuing'


def inventory():
    a.write('file-hashes.json',{str(p.relative_to(r.ROOT)):a.sha(p) for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='file-hashes.json'})


def shared():
    mapping = r.s.parameter_mapping(RECORD)
    ids = {'water','carbon-dioxide','hydronium-cation','hydroxide-anion','bicarbonate-anion','carbonate-anion'}
    spec = r.bind(mapping)
    a.write('shared-parameters.json',dict(parameter_sha256=a.sha(RECORD),components=[c for c in mapping['components'] if c['component_id'] in ids],pairs=[p for p in mapping['pairs'] if {p['component_id_a'],p['component_id_b']}<=ids],sources=mapping['sources'],reactions=[x for x in spec.spec['chemistry']['reactions']['aqueous'] if x['name'] in ('R1','R2','R3')]))
    e.table(OUT/'shared-coefficients.csv',[dict(identity=c['identity'],value=c['value']['magnitude'],unit=c['value']['unit'],source=c.get('provenance')) for item in r.read(OUT/'shared-parameters.json')['components']+r.read(OUT/'shared-parameters.json')['pairs'] for c in item['coefficients']])
    e.table(OUT/'reaction-source-ranges.csv',[dict(reaction=n,minimum_K=273.15,maximum_K=498.15,source='Austgen et al. 1991, Table V p.547, reactions 1a/4a/5a; cites Edwards et al. 1978',pdf_sha256='8c0a6a57e5bf9e28b1f9da8022d54290506fe04b4286b6494ef8a44fd924f8db') for n in ('R1','R2','R3')])


def checks():
    import epcsaft
    from epcsaft import equilibrium as eq
    mapping = r.s.parameter_mapping(RECORD)
    spec = r.bind(mapping)
    model = epcsaft.Mixture(spec.parameters,thermochemistry=spec.thermal)
    rows = []
    for group in ('Kiepe','Cai','common149'):
        observation = next(o for o in spec.inputs['observations']['fitted'] if o['group']==group)
        problem = spec.problems[observation['problem']]
        if group=='Cai':
            problem.T, problem.P = 350., eq.Free(5e4)
        if group=='common149':
            masses = {c['component_id']:c['fixed']['molar_mass']['value']['magnitude'] for c in mapping['components']}
            problem.T, problem.feed = 313.15, eq.Amounts({'monoethanolamine':1.,'water':masses['monoethanolamine']*.7/(.3*masses['water']),'carbon-dioxide':.3})
        answers = []
        for factor in (1.,1.5):
            problem.P = eq.Free(problem.P.guess*factor)
            result = eq.solve_equilibrium(model,problem)
            assert result.success and result.requested_tolerance_met, result.message
            x = result.mole_fractions[:9]
            state = model.state(result.temperature,rho=result.molar_densities[0],x=x)
            values = dict(bubble_pressure_Pa=result.pressure,molar_density_mol_m3=result.molar_densities[0],density_kg_m3=r.reg.predict(model,r.reg.observation(spec.parameters,'phase_density',problem,observed=1000.,scale=1.,form='difference',phase=problem.phases[0].name,mass_basis=True)).value)
            values.update({t:getattr(state,t) for t in ('hard_chain','dispersion','association','debye_huckel','born','cation_mixing','dipolar','residual_helmholtz')})
            values.update({'x_'+c:v for c,v in zip(r.s.COMPONENT_IDS,x,strict=True)})
            answers.append(values)
        passed = all(format(v,'.10g')==format(answers[1][k],'.10g') for k,v in answers[0].items())
        rows.append(dict(group=group,T_K=result.temperature,feed=problem.feed.values,answers=answers,printed_digits_agree=passed))
    a.write('check-values.json',rows)
    assert all(x['printed_digits_agree'] for x in rows)


if __name__=='__main__':
    setup()
    {'replay':replay,'evidence':evidence,'uncertainty':uncertainty,'comparison':comparison,'weights':weights,'shared':shared,'checks':checks,'stability':stability,'inventory':inventory}[sys.argv[1]]()
