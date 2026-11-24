"""Fixed-parameter MEA pressure-reference sensitivity and single-ion activity readout."""
import csv
import math
from time import monotonic
import tomllib

from recall import OUT
from part_ii import ROOT, np, reg, stable
from reference_states_428 import BUNDLE, balances, epcsaft, eq, heat_items, identity, phase, phase_passed, request, s, source_log_k, vrc

PARAMETERS = BUNDLE/'results/selected-current-best-parameters.json'
WORKED = BUNDLE/'results/reference-states-428/mea.json'
IDS = s.COMPONENT_IDS
W, H, OH, C, B = map(IDS.index, ('water','hydronium-cation','hydroxide-anion','carbonate-anion','bicarbonate-anion'))
P0 = 100000.
TOL = 1e-10


def setup():
    mapping = s.parameter_mapping(PARAMETERS)
    return mapping, epcsaft.Mixture(epcsaft.Parameters.from_mapping(mapping), thermochemistry=vrc.record())


def references(problem, override):
    if override:
        rows = problem.reactions
        for r in rows[:3]:
            r.reference = eq.ReactionReference(r.reference.source_basis, reference_pressure_pa=P0)
        problem.reactions = rows
    return problem


def read_state(model, problem, override, formulas):
    result = eq.solve_equilibrium(model, references(problem, override))
    row = dict(status=result.message, success=result.requested_tolerance_met, T_K=result.temperature, P_Pa=result.pressure,
               feed_mol=problem.feed.values, max_residual=max(map(abs,result.residuals),default=None))
    if result.requested_tolerance_met and result.amounts:
        row['phases'] = [phase(model, result.temperature, result.pressure, n, rho, result.phase_mole_fractions(i), formulas)
                         for i, (n,rho) in enumerate(zip(result.amounts,result.molar_densities,strict=True))]
        feed = problem.feed.values
        feed = [feed.get(c,0.) for c in IDS] if isinstance(feed,dict) else feed
        row['balances'] = balances(feed,row['phases'],formulas)
        row['liquid_checks_pass'] = (phase_passed(row['phases'][0],result.pressure,TOL) and
                                    max(map(abs,row['balances']['scaled_element_residual'].values()))<=TOL)
        row['quotients'] = [dict(name=rx.name, basis=a.basis, P_ref_Pa=a.reference_pressure_pa,
                                 ln_Q=a.log_quotient, ln_K=source_log_k(rx.correlation,result.temperature), cause=a.cause)
                            for rx, a in zip(problem.reactions, [a for a in eq.reaction_activities(model,result) if a.phase_index==0],strict=True)]
        row['reference_checks_pass'] = all(a['P_ref_Pa']==p and a['ln_Q'] is not None and abs(a['ln_Q']-a['ln_K'])<=TOL
                                           for a,p in zip(row['quotients'], [P0 if override else result.pressure]*3+[P0]*2,strict=True))
    return row, result


def changes(baseline, changed):
    return dict(absolute=changed-baseline, percent=None if baseline==0 else 100*(changed/baseline-1))


def sensitivity(save):
    import probe

    start = monotonic()
    mapping, model = setup()
    archived = BUNDLE/'results/paper-evidence-341/paper-evidence/state-targets.csv'
    declaration = ROOT/'analyses/solvent_specification_mea/declarations.toml'
    formulas = [tomllib.loads(declaration.read_text())['element_formulas'][c] for c in IDS]
    with archived.open() as stream:
        retained = list(csv.DictReader(stream))
        prior = {r['identity']: r for r in retained
                 if r['kind']=='canonical' and r['status']=='Available' and float(r['temperature_K'])==313.15}
    with s.CANONICAL_VLE.open() as stream:
        selected = sorted((r for r in csv.DictReader(stream) if 'canonical:'+r['observation_id'] in prior and
                           float(r['MEA_weight_fraction'])==.30), key=lambda r:float(r['CO2_loading']))
    keys = [selected[i]['observation_id'] for i in (0,-1)]
    cases = probe.pressure_observations(lambda row: row['observation_id'] in keys)
    bot = next(o for o in probe.OBSERVATIONS if o['identity']=='Bottinger2008_state_046')
    cases.extend((bot,dict(identity='100 kPa control',request=request(mapping,313.15,.30))))
    cases[-1]['request']['pressure']['value'] = P0
    rows = []
    result_428 = stable.read(WORKED)
    for case in cases:
        results = []
        for override in (False,True):
            problem = s._problem_from_request(s.corrected_request(case['request'],s.reaction_values(mapping),mapping))
            row, result = read_state(model, problem, override, formulas)
            if case['identity'] in prior and row.get('phases'):
                row['value_Pa'] = result.pressure * result.phase_mole_fractions(1)[0]
            results.append(row)
        original, changed = results
        entry = dict(identity=case['identity'], baseline=original, fixed_reference=changed)
        if original.get('phases') and changed.get('phases'):
            entry['species_x_change'] = {c:changes(a,b) for c,a,b in zip(IDS,original['phases'][0]['x'],changed['phases'][0]['x'],strict=True)}
            if case['identity'] in prior:
                entry.update(pCO2_change=changes(original['value_Pa'],changed['value_Pa']),
                             bubble_pressure_change=changes(original['P_Pa'],changed['P_Pa']),
                             prior_prediction_Pa=float(prior[case['identity']]['predicted']))
            elif case['identity']==bot['identity']:
                fractions = dict(zip(IDS,original['phases'][0]['x'],strict=True))
                readback = {'MEA + MEAH+':fractions['monoethanolamine']+fractions['protonated-monoethanolamine'],
                            'MEACOO-':fractions['carbamate-anion']}
                entry['prior_speciation_check'] = {r['target']:dict(predicted=readback[r['species']], archived=float(r['predicted']),
                        within_1e_10=math.isclose(readback[r['species']],float(r['predicted']),rel_tol=TOL))
                    for r in retained if r['identity']==bot['identity'] and r['status']=='Available'}
        rows.append(entry)
    heats = []
    for override in (False,True):
        item, = heat_items(mapping, model.parameters, [dict(temperature_K=313.15, system_pressure_Pa=1734000., alpha_final=.31,
                           observed_addition_enthalpy_J_per_mol_CO2=0., uH_J_per_mol_CO2=1.)], request(mapping,313.15,.11))
        for name in ('problem','final_problem'):
            setattr(item,name,references(getattr(item,name),override))
        prediction = reg.predict(model,item)
        heat = dict(status=prediction.status.name,message=prediction.message,value_kJ_mol=prediction.value/1000 if prediction.status.name=='Available' else None,
                    reference_pressures_Pa=[P0 if override else 1734000.]*3+[P0]*2)
        heat['endpoints'] = [read_state(model,p,override,formulas)[0] for p in (item.problem,item.final_problem)]
        heats.append(heat)
    conversion = [dict(reaction=r['name'], common_ln_K=r['ln_K_source']-(r['molality_term'] if r['name'] in ('R1','R3') else 0.),
                       common_Gamma=r['Gamma']+(r['molality_term'] if r['name'] in ('R1','R3') else 0.),
                       original_sum=r['ln_K_source']+r['Gamma'], molality_term=r['molality_term'])
                  for r in result_428['reactions']]
    save('q4',start, species=list(IDS), rows=rows, heat=heats, heat_previous_kJ_mol=result_428['heat_kJ_mol'],
         heat_change=changes(*(r['value_kJ_mol'] for r in heats)) if all(r['value_kJ_mol'] is not None for r in heats) else None,
         checks=dict(control_max_abs_dx=max(abs(v['absolute']) for v in rows[-1]['species_x_change'].values()),
                     S15_basis_invariant=all(math.isclose(row['common_ln_K']+row['common_Gamma'], row['original_sum'], abs_tol=TOL, rel_tol=0)
                                             for row in conversion),
                     archived_pressure_replay=all(math.isclose(row['baseline']['value_Pa'],row['prior_prediction_Pa'],rel_tol=TOL)
                                                  for row in rows if 'prior_prediction_Pa' in row)),
         S15_common_basis=conversion, inputs=identity(PARAMETERS,WORKED,archived,s.CANONICAL_VLE,s.STATE_PACKET,declaration))


def activity_grid(save):
    start = monotonic()
    mapping, model = setup()
    P = 101325.
    Mw = mapping['components'][W]['fixed']['molar_mass']['value']['magnitude']
    digitized = OUT/'ph-digitization.json'
    sources = stable.read(digitized)
    temperatures = {source['T_K'] for source in sources}
    x_water = [float(i==W) for i in range(len(IDS))]
    terms = {}
    epsilons = (1e-10,1e-12,1e-14)
    for T in sorted(temperatures|{313.15}):
        template = s._problem_from_request(request(mapping,T,.3))
        direction = template.neutral_reference.solute_molality_ratios
        water = model.state(T,P=P,x=x_water,phase='liquid')
        rho = water.molar_density
        terms[T] = (rho,[])
        for e in epsilons:
            amount = [1. if i==W else e*Mw*direction[c] for i,c in enumerate(IDS)]
            terms[T][1].append(model.log_fugacity_terms(T,rho,[n/sum(amount) for n in amount]))
    rows = []
    for T, loading, symbol in [(313.15,i/20,None) for i in range(1,11)]+[
            (source['T_K'],p['loading'],dict(p,source=source['source'])) for source in sources for p in source['points']]:
        problem = s._problem_from_request(request(mapping,T,loading))
        result = eq.solve_equilibrium(model,problem)
        row = dict(T_K=T,P_Pa=P,loading=loading,symbol=symbol,message=result.message,feed_mol=problem.feed.values)
        rows.append(row)
        if not result.requested_tolerance_met:
            continue
        raw, common, *_ = eq.reaction_activities(model,result)
        assert common.basis.startswith('common-molality') and common.reference_pressure_pa==P and raw.basis.startswith('raw-mole-fraction')
        logs = common.species.log_activities
        pH = -logs[H]/math.log(10)
        m0 = common.species.standard_molality_mol_per_kg
        water_K = source_log_k(problem.reactions[0].correlation,T)-2*math.log(Mw*m0)
        water_pH = -(water_K+2*logs[W]-logs[OH])/math.log(10)
        x = list(result.phase_mole_fractions(0))
        rho = result.molar_densities[0]
        solution = model.log_fugacity_terms(T,rho,x)
        ref_density, reference = terms[T]
        masses = x[W]*Mw
        charges = [c['fixed']['charge_number']['value']['magnitude'] for c in mapping['components']]
        row.update(pH=pH, raw_R1_pH=-raw.species.log_activities[H]/math.log(10), water_reaction_pH=water_pH,
                   water_reaction_pass=abs(pH-water_pH)<=TOL, x=x, carbonate_share=x[C]/(x[C]+x[B]),
                   charge_residual=math.fsum(xi*z for xi,z in zip(x,charges,strict=True)),
                   reference_rho=ref_density, density_mol_m3=rho, max_residual=max(map(abs,result.residuals)), ions={})
        if symbol:
            row['model_minus_electrode_pH'] = pH-symbol['pH']
        for i, z in enumerate(charges):
            if not z:
                continue
            molality = x[i]/masses
            ln_gamma = logs[i]-math.log(molality/m0)
            ion = dict(mol_kg_water=molality,ln_gamma=ln_gamma,dilutions=[])
            row['ions'][IDS[i]] = ion
            for e, anchor in zip(epsilons,reference,strict=True):
                try:
                    dH = solution.debye_huckel[i]-anchor.debye_huckel[i]
                    born = solution.born[i]-anchor.born[i]
                    other = math.fsum(getattr(solution,k)[i]-getattr(anchor,k)[i]
                                      for k in ('hard_chain','dispersion','association','dipolar','cation_mixing'))
                    lnZ = solution.log_compressibility_factor-anchor.log_compressibility_factor
                    remainder = (other-lnZ)+(math.log(rho/ref_density)+lnZ)+math.log(x[W])
                    ion['dilutions'].append(dict(epsilon=e,DH=dH,Born=born,remainder=remainder,delta_ln_Z=lnZ,
                                                 closure=dH+born+remainder-ln_gamma))
                except (TypeError, ValueError) as error:
                    ion['dilutions'].append(dict(epsilon=e,cause=str(error)))
            penultimate, last = ion['dilutions'][-2:]
            if 'closure' in last and 'closure' in penultimate:
                ion['terminal_change'] = {k:abs(last[k]-penultimate[k]) for k in ('DH','Born','remainder')}
                ion['closure_within_dilution_change'] = abs(last['closure'])<=sum(ion['terminal_change'].values())+TOL
                ion['attribution_5dp'] = {k:round(last[k],5) if round(last[k],5)==round(penultimate[k],5)
                                         and ion['closure_within_dilution_change'] else None for k in ion['terminal_change']}
    control = next(r for r in rows if r['T_K']==313.15 and r['loading']==.30 and r['symbol'] is None)
    carbonate, = (BUNDLE/'results/shared-ion-electrostatics-423').glob('*/*/P0/carbonate-share.json')
    save('q5',start, rows=rows, retained_carbonate_comparison=stable.read(carbonate),
         inputs=identity(PARAMETERS,digitized,s.STATE_PACKET,carbonate), stock_MEA_mass_fraction=.30,
         control_pass=(round(control['pH'],6),round(control['raw_R1_pH'],6))==(8.887695,10.632054))
    assert (round(control['pH'],6),round(control['raw_R1_pH'],6))==(8.887695,10.632054)
