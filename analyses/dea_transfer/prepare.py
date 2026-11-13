"""#317 source preparation (no Engine call): specification row packets and the declarations (chemistry, templates, datasets).

Basis: one mol analytical DEA; water from the unloaded mass fraction; loading mol CO2/mol DEA; K and Pa.
"""
import csv, hashlib, json, math, tomllib
from pinned import AN, REF, ROOT, DEA, H, C, W, CO2, M_DEA, M_W

rows = lambda name: list(csv.DictReader((REF / name).open()))
water = lambda w: (1 - w) / M_W / (w / M_DEA)
p_water = lambda T: 1e3 * 10 ** (7.19621 - 1730.63 / (T - 39.724))  # Horstmann 2002 Table 2 water Antoine; pressure guess only
# Lal 2.0 kmol/m3 -> mass fraction: w * rho(w) = c M, rho linear between Weiland Table 2 unloaded 20 and 30 mass % (298 K).
rho = lambda w: 1.021 + (w - 0.20) * (1.035 - 1.021) / 0.10
w_lal = 0.2
for _ in range(50):
    w_lal = 2.0 * M_DEA / rho(w_lal)
order = iter(range(10_000))
def packet(name, source, values):
    out = [dict(observation_order=next(order), identity=f'{name}:{i}', source=json.dumps(r), **values(r)) for i, r in enumerate(source)]
    with (AN / f'inputs/{name}.csv').open('w') as f:
        writer = csv.DictWriter(f, list(out[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(out)
    return dict(path=f'inputs/{name}.csv', sha256=hashlib.sha256((AN / f'inputs/{name}.csv').read_bytes()).hexdigest())
def pressure(T, p, w, a):
    return dict(T=T, P=p + p_water(T), water=water(w), alpha=a, observed=p, weight=1 / (30 * 0.09 ** 2))
files = dict(
    lawson=packet('lawson-1976', rows('LawsonGarst1976_TableII_CO2.csv'), lambda r: pressure((float(r['T_F']) - 32) / 1.8 + 273.15, 133.322368 * float(r['p_CO2_mmHg']), 0.25, float(r['alpha_mol_CO2_per_mol_DEA']))),
    carson=packet('carson-2000', rows('Carson2000_Table2_DEA.csv'), lambda r: dict(T=298.15, P=101325.0, water=water(float(r['DEA_mass_fraction'])),
        alpha=float(r['x_CO2']) / (1 - float(r['x_CO2'])) * (1 + water(float(r['DEA_mass_fraction']))), observed=1e3 * float(r['solution_enthalpy_kJ_mol_CO2']),
        scale=0.02 * 1e3 * abs(float(r['solution_enthalpy_kJ_mol_CO2'])), weight=1 / 50)),
    seo=packet('seo-hong-1996', rows('SeoHong1996_Table1_DEA30.csv'), lambda r: pressure(float(r['T_C']) + 273.15, 1e3 * float(r['p_CO2_kPa']), 0.30, float(r['alpha_mol_CO2_per_mol_amine']))),
    lal=packet('lal-1985', rows('Lal1985_Table2_CO2.csv'), lambda r: pressure(float(r['T_C']) + 273.15, 1e3 * float(r['p_CO2_kPa']), w_lal, float(r['alpha_mol_CO2_per_mol_DEA']))),
    weiland=packet('weiland-1998', rows('Weiland1998_Table2_DEA_density.csv'), lambda r: dict(T=298.15, P=101325.0, water=water(float(r['DEA_mass_percent']) / 100),
        alpha=float(r['alpha_mol_CO2_per_mol_DEA']), observed=1e3 * float(r['density_g_per_mL']), scale=1.0, weight=1.0)),
    lawson8=packet('lawson-1976-viii', rows('LawsonGarst1976_TableVIII_CO2.csv'), lambda r: pressure((float(r['T_F']) - 32) / 1.8 + 273.15, 133.322368 * float(r['p_CO2_mmHg']),
        float(r['DEA_mass_percent']) / 100, float(r['alpha_mol_CO2_per_mol_DEA']))))
# Boettinger 2008 Table 4 true mole fractions at 2.5 MPa (cell 5-25 bar; per-row pressure not tabulated), one packet per measured quantity.
for q in ('x_DEA_plus_DEAH', 'x_DEACOO', 'x_HCO3'):
    files[q] = packet(f'bottinger-2008-{q[2:]}', rows('Bottinger2008_Table4_DEA_NMR.csv'), lambda r: dict(T=float(r['T_K']), P=2.5e6, water=water(float(r['DEA_mass_fraction'])),
        alpha=float(r['alpha_mol_CO2_per_mol_DEA']), observed=float(r[q]), scale=0.001, weight=1.0))

# Chemistry (D1): R1-R3 from the adopted MEA declarations; Bower 1962 Eq. 7 fixed; Aroua 1997 Eq. 14 inverse as the carbamate start.
mea = tomllib.loads((ROOT / 'analyses/solvent_specification_mea/declarations.toml').read_text())
shared = [dict(r, stoichiometry={k: v for k, v in r['stoichiometry'].items() if v}) for r in mea['chemistry']['reactions']['aqueous'] if r['name'] in ('R1', 'R2', 'R3')]
law = lambda a, b, d=0.0: dict(a=a, b=b, c=0.0, d=d, e=0.0, f=0.0, reference_temperature=313.15, standard_state_id='aqueous-molality-infinite-dilution-water-v1', temperature_min=293.15, temperature_max=393.15)
ln10 = math.log(10)
reactions = shared + [
    dict(name='DEA-dissociation', stoichiometry={H: -1.0, W: -1.0, DEA: 1.0, 'hydronium-cation': 1.0},
         correlation=law(-4.0302 * ln10, -1830.15 * ln10, 0.0043261 * ln10), reference=dict(reference_pressure_pa=100000.0, source_basis='CommonMolalityInfiniteDilution')),
    dict(name='carbamate-hydrolysis', stoichiometry={C: -1.0, W: -1.0, DEA: 1.0, 'bicarbonate-anion': 1.0},
         correlation=law(5.12 * ln10, -1781 * ln10), reference=dict(reference_pressure_pa=100000.0, source_basis='CommonMolalityInfiniteDilution'))]
L = [W, DEA, CO2, H, C, 'bicarbonate-anion', 'carbonate-anion', 'hydronium-cation', 'hydroxide-anion']
feed = lambda a: dict(basis='amounts', values={W: '$water', DEA: 1.0, CO2: a})
liquid = lambda a: dict(T='$T', P='$P', feed=feed(a), phases=[dict(name='L', kind='liquid', support=L)], reaction_set='aqueous', neutral_reference='aqueous', row_tolerance=1e-10)
templates = {'loaded-liquid': liquid('$alpha'), 'zero-liquid': liquid(0.0), 'loaded-bubble': dict(liquid('$alpha'), P=dict(free=True, guess='$P'), phases=[
    dict(name='L', kind='liquid', support=L), dict(name='V', kind='vapor', support=[W, DEA, CO2], amount=dict(status='pinned', value=0.0), composition_guess={W: 0.1, DEA: 1e-5, CO2: 0.9})])}
neutral = mea['chemistry']['neutral_references']['aqueous']
neutral['solute_molality_ratios'] = {k.replace('monoethanolamine', DEA): v for k, v in neutral['solute_molality_ratios'].items()}
columns = {k: k for k in ('observation_order', 'T', 'P', 'water', 'alpha', 'observed', 'weight')}
partial = dict(constructor='observation', kind='partial_pressure', template='loaded-bubble', arguments=dict(observed='$observed', form='log_ratio', phase='V', species=[CO2]), weight='$weight')
D = (293.15, 393.15)  # declared range of every reaction law (D1)
datasets = [
    dict(name='lawson-1976', group='Lawson', role='calibration', **files['lawson'], **partial, columns=columns, filter=dict(T=[300.0, 393.15]), temperature_domain=D),
    dict(name='lawson-1976-394K', group='Lawson-394K', role='comparison', **files['lawson'], **partial, columns=columns, filter=dict(T=[393.15, 400.0]), temperature_domain=D),
    dict(name='carson-2000', group='Carson', role='calibration', **files['carson'], template='loaded-liquid', initial='zero-liquid', final='loaded-liquid', constructor='addition_enthalpy',
         kind='pressure', columns=dict(columns, scale='scale'), arguments=dict(observed='$observed', form='difference', scale='$scale', feed={CO2: 1.0}, amount='$alpha', T='$T', P='$P', phase='vapor'),
         weight='$weight', filter={}, temperature_domain=D),
    dict(name='seo-hong-1996', group='SeoHong', role='comparison', **files['seo'], **partial, columns=columns, filter={}, temperature_domain=D),
    dict(name='lal-1985', group='Lal', role='comparison', **files['lal'], **partial, columns=columns, filter={}, temperature_domain=D),
    dict(name='weiland-1998', group='Weiland', role='comparison', **files['weiland'], template='loaded-liquid', constructor='observation', kind='phase_density', columns=dict(columns, scale='scale'),
         arguments=dict(observed='$observed', form='difference', scale='$scale', phase='L', mass_basis=True), weight='$weight', filter={}, temperature_domain=D),
    dict(name='lawson-1976-viii', group='Lawson-VIII', role='comparison', **files['lawson8'], **partial, columns=columns, filter={}, temperature_domain=D)] + [
    dict(name=f'bottinger-2008-{q[2:]}', group=f'Bottinger-{q[2:]}', role='comparison', **files[q], template='loaded-liquid', constructor='observation', kind='mole_fraction',
         columns=dict(columns, scale='scale'), arguments=dict(observed='$observed', form='difference', scale='$scale', phase='L', species=species, mass_basis=False),
         weight='$weight', filter={}, temperature_domain=D) for q, species in (('x_DEA_plus_DEAH', [DEA, H]), ('x_DEACOO', [C]), ('x_HCO3', ['bicarbonate-anion', 'carbonate-anion']))]
formulas = {CO2: dict(C=1, O=2, charge=0), W: dict(H=2, O=1, charge=0), 'bicarbonate-anion': dict(H=1, C=1, O=3, charge=-1), 'carbonate-anion': dict(C=1, O=3, charge=-2),
            'hydronium-cation': dict(H=3, O=1, charge=1), 'hydroxide-anion': dict(H=1, O=1, charge=-1), DEA: dict(C=4, H=11, N=1, O=2, charge=0),
            H: dict(C=4, H=12, N=1, O=2, charge=1), C: dict(C=5, H=10, N=1, O=4, charge=-1)}
analytical = {CO2: {CO2: 1}, DEA: {DEA: 1}, W: {W: 1}, H: {DEA: 1}, C: {DEA: 1, CO2: 1}, 'bicarbonate-anion': {CO2: 1, W: 1}, 'carbonate-anion': {CO2: 1, W: 1},
              'hydronium-cation': {W: 1}, 'hydroxide-anion': {W: 1}}
policy = dict(carbon_component=CO2, carbon_species=[CO2, 'bicarbonate-anion', 'carbonate-anion', C], neutral_species=[W, DEA, CO2], packing_fraction_threshold=0.1, ambiguity_interval=[0.05, 0.35])
toml = lambda v: json.dumps(v).replace('": ', '" = ')
text = '# #317 DEA declarations, generated by prepare.py from the design (comment 6836480110). Declaration data only.\n' + ''.join(
    f'{k} = {toml(v)}\n' for k, v in dict(templates=templates, chemistry=dict(reactions=dict(aqueous=reactions), neutral_references=dict(aqueous=neutral)),
                                           datasets=datasets, element_formulas=formulas, analytical_components=analytical, phase_policy=policy).items())
(AN / 'declarations.toml').write_text(text)
(AN / 'inputs/no-phase-states.json').write_text('[]\n')
(AN / 'results/preparation.json').write_text(json.dumps(dict(lal_mass_fraction=w_lal, lal_water_per_DEA=water(w_lal), water_per_DEA={'25': water(0.25), '30': water(0.30)},
    declarations_sha256=hashlib.sha256(text.encode()).hexdigest(), files=files), indent=1) + '\n')
