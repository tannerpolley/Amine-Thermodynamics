"""Issue 223 merged-wheel preparation: fixed-density checks; no equilibrium solve or fitting."""
import copy
import csv
import hashlib
import json
import math
from pathlib import Path
import zipfile

import epcsaft
from epcsaft import equilibrium as eq

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
MAIN = Path('/home/tnnrpolley21/Workspaces/Engineering/Amine-Thermodynamics')
W, M, C, MH, B, D, H, OH = IDS = ('water', 'methyldiethanolamine', 'carbon-dioxide',
    'protonated-methyldiethanolamine', 'bicarbonate-anion', 'carbonate-anion', 'proton', 'hydroxide-anion')
EXPECTED_WHEEL = 'ca7093ca721fdc80226c74d018a582f31705684c6995e80b0492c193334dd5d5'
ENGINE_COMMIT = 'd513820994a78bfe628d42fffd55b2eeab6f89bd'

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def write(name, obj):
    content=json.dumps(obj, indent=2, allow_nan=False)+'\n'
    if name in ('sources.json','inventory.json','declaration.json') and (OUT/name).exists():
        assert (OUT/name).read_text()==content, f'{name} changed: return the frozen input change to Design'
    (OUT/name).write_text(content)

def val(v, unit):
    return dict(magnitude=v, unit=unit)

def coefficient(identity, v, unit):
    return dict(identity=identity, value=val(v, unit))

# Bülow Tables 1–2; masses are bookkeeping, with H+ rather than H3O+.
VALUES = [(.01801528,0,1.2046,None,353.94),(.1191622,0,3.6750,3.5630,228.71),
          (.0440095,0,2.0729,2.7852,169.21),(.12017014,1,1,3.5630,228.71),
          (.06101684,-1,1,2.9296,70.00),(.0600089,-2,1,2.4422,249.26),
          (.00100794,1,1,3.4654,500.00),(.01700734,-1,1,2.0177,650.00)]
REACTIONS = [dict(name='water-dissociation', stoichiometry={W:-1,H:1,OH:1}, c=[132.899,-13445.9,-22.4773], si_row='Ka,1', printed_reference=1, delta_nu_solute=2, pK_check=14.00, rounding_tolerance=.005),
 dict(name='MDEAH-dissociation', stoichiometry={MH:-1,M:1,H:1},c=[-83.491,-819.7,10.9756],si_row='Ka,5',printed_reference=4,delta_nu_solute=1,pK_check=8.551,rounding_tolerance=.0005),
 dict(name='CO2-hydration',stoichiometry={C:-1,W:-1,B:1,H:1},c=[231.465,-12092.1,-36.7816],si_row='Ka,2',printed_reference=2,delta_nu_solute=1,pK_check=6.359,rounding_tolerance=.0005),
 dict(name='bicarbonate-dissociation',stoichiometry={B:-1,D:1,H:1},c=[216.049,-12431.7,-35.4819],si_row='Ka,3',printed_reference=3,delta_nu_solute=1,pK_check=10.333,rounding_tolerance=.0005)]

def declaration():
    doc=dict(schema='epcsaft.parameters',schema_version=1,document_id='mdea-bulow-2021-issue-223',document_version=1,
      purpose='Fixed published parameters; issue 223 D1–D5; pending Engine 896 grammar',components=[],correlations=[],pairs=[],
      model_families=[dict(kind='base',choice='pc-saft'),dict(kind='association',choice='general-site'),
       dict(kind='electrolyte',choice='born',c_shell=0.,c_dielectric=0.,ionic_dispersion='exclude-same-sign-ion-pairs'),
       dict(kind='permittivity',choice='pending-engine-896-solvent-mole-weighting',normalization='none',solvents=[W,M],provenance='D1 literal Eq.19; D3 Hsieh Eq.3/Table 3')],
      model_coefficients=[dict(family='ionic_region_relative_permittivity',**coefficient('model/ionic_region_relative_permittivity',1.,'dimensionless'))],
      topology=dict(sites=[],edges=[],no_cross_association=[dict(component_id_a=M,component_id_b=C,provenance='Issue 223 water-only induced association interpretation')]),reaction_correlations=[])
    for cid,(mass,z,m,sigma,u) in zip(IDS,VALUES):
        coeffs=[('segment_count',m,'dimensionless'),('dispersion_energy_over_k',u,'kelvin'),('solvation_factor',1.,'dimensionless')]
        if sigma is not None: coeffs.append(('segment_diameter',sigma,'angstrom'))
        if z: coeffs += [('packing_diameter',.88*sigma,'angstrom'),('debye_huckel_diameter',sigma,'angstrom'),('born_diameter',sigma,'angstrom')]
        doc['components'].append(dict(component_id=cid,provenance='Bülow Tables 1–2; ion packing Held 2014 Eq.21 via ref.26',fixed=dict(molar_mass=dict(value=val(mass,'kilogram / mole')),charge_number=dict(value=val(z,'elementary-charge'))),coefficients=[dict(family=f,**coefficient(f'component/{cid}/{f}',v,unit)) for f,v,unit in coeffs]))
    prefix='component/water/segment_diameter'
    doc['correlations'].append(dict(component_id=W,correlation_id=prefix,family='segment_diameter',form='constant-plus-sum-of-exponentials',constant=coefficient(prefix+'/constant',2.7927,'angstrom'),terms=[dict(amplitude=coefficient(prefix+f'/{i}/amplitude',a,'angstrom'),exponent_coefficient=coefficient(prefix+f'/{i}/exponent',b,'1 / kelvin')) for i,(a,b) in enumerate([(10.11,-.01775),(-1.417,-.01146)])]))
    for cid,cs in [(W,[249.21,-.79069,.00072997]),(M,[44.1399,-.046824,-.0000882158])]:
        p=f'component/{cid}/relative_permittivity'
        doc['correlations'].append(dict(component_id=cid,correlation_id=p,family='relative_permittivity',form='constant-plus-polynomial-in-temperature',reference_temperature=val(0.,'kelvin'),constant=coefficient(p+'/constant',cs[0],'dimensionless'),terms=[dict(power=i,coefficient=coefficient(p+f'/a{i}',cs[i],['dimensionless','1 / kelvin','1 / kelvin ** 2'][i])) for i in (1,2)],provenance='Hsieh 2007 Eq.3/Table 3; MDEA 303.15–328.15 K; water 273.15–373.15 K'))
    kij={(W,M):[-.118,-.000759,-.0000132,.000000125],(W,C):[-.0021,.000453],(W,H):[.25],(W,OH):[-.25],(W,D):[-.25]}
    for i,a in enumerate(IDS):
        for b in IDS[i+1:]:
            if VALUES[i][1]*VALUES[IDS.index(b)][1]>0: continue
            p=f'pair/{a}/{b}/k_ij'; cs=kij.get((a,b),[0.])
            c=coefficient(p,cs[0],'dimensionless') if len(cs)==1 else dict(identity=p,temperature_law=dict(form='polynomial-plus-reciprocal-temperature',reference_temperature=val(298.15,'kelvin'),terms=[dict(power=k,coefficient=coefficient(p+f'/a{k}',v,['dimensionless','1 / kelvin','1 / kelvin ** 2','1 / kelvin ** 3'][k])) for k,v in enumerate(cs)]))
            doc['pairs'].append(dict(component_id_a=a,component_id_b=b,provenance='Bülow Table 3/Eq.26; all other unlike pairs zero',coefficients=[dict(family='k_ij',**c)]))
    for cid,n,e,v in [(W,1,2425.6,.045),(M,2,2046.6,.1238),(C,1,0.,.045)]:
        doc['topology']['sites'] += [dict(component_id=cid,site_id=s,site_role=r,multiplicity=n) for s,r in [('a','donor'),('b','acceptor')]]
        doc['topology']['edges'].append(dict(endpoint_a=dict(component_id=cid,site_id='a'),endpoint_b=dict(component_id=cid,site_id='b'),source=dict(kind='explicit',provenance='Bülow Table 1 printed volume'),energy_over_k=coefficient(f'association/{cid}/energy',e,'kelvin'),volume=coefficient(f'association/{cid}/volume',v,'dimensionless')))
    for a,b in [(W,M),(W,C)]:
        for donor,acceptor in [(a,b),(b,a)]:
            doc['topology']['edges'].append(dict(endpoint_a=dict(component_id=donor,site_id='a'),endpoint_b=dict(component_id=acceptor,site_id='b'),source=dict(kind='combining-rule',rule_id='wolbach-sandler',provenance='Bülow Eqs. 23 and 25',inputs=dict(energy_over_k=[f'association/{a}/energy',f'association/{b}/energy'],volume=[f'association/{a}/volume',f'association/{b}/volume']))))
    doc['reaction_correlations']=[dict(reaction_id=r['name'],stoichiometry=r['stoichiometry'],c1_c2_c3_c4=r['c']+[0.],basis='aqueous-mole-fraction-infinite-dilution-water-v1') for r in REACTIONS]
    return doc


def sources():
    records=[]
    for name,parent,key,locator in [('Bulow2021','B74UQB9E','E48WQBPB','Eqs.1–4,12–26; Tables 1–3, pp.6328–6331'),('Bulow2021-SI','B74UQB9E','5KCVQBVL','Tables S1 and S3'),('Austgen1991','NL4W5CA6','UNTA6KIT','Table V p.547; hydronium form'),('Hsieh2007','U3L9K37G','8X653CVB','Eq.3/Table 3 p.621'),('Kamps-Maurer1996','THBMMB2G','HRGBIYIW','Eq.8 p.1508; Eq.12 p.1509, 278–368 K'),('Kuranov1996','9F6UM7M4','QB5PV62N','Table 2 p.1960')]:
        pdf=next((Path.home()/'Zotero/storage'/key).glob('*.pdf'))
        records.append(dict(source=name,zotero_parent_key=parent,pdf_attachment_key=key,path=str(pdf),sha256=sha(pdf),locator=locator))
    paths=['data/reference/MDEA/Kuranov_1996_CO2_MDEA_total_pressure.csv','data/reference/MDEA/Hsieh_2007_MDEA_relative_permittivity.csv','data/reference/MDEA/Hsieh2007_stage1.csv']
    return dict(pdfs=records,tables=[dict(path=p,sha256=sha(ROOT/p)) for p in paths],reaction_assignment=REACTIONS,
      si_errors='SI S1 labels and reference numbers preserved above: Ka,2 is carbon hydration, not MDEA; Ka,3 bicarbonate; Ka,5 MDEA, not H2S. SI references 2 and 4 are also interchanged for carbon/MDEA.',
      excluded_si_row=dict(label='Ka,4',c=[214.582,-12995.4,-33.5471],printed_reference=3,assignment='H2S dissociation; excluded'),
      evidence='Austgen Table V identifies carbon and H2S; Kamps–Maurer Eq.12 identifies MDEA after scale transfer. Edwards 1978 and Vahidi 2013 unread.')


def inventory():
    groups=[]
    for nominal,t,lo,hi,target in [(19,313,1,11,42.21),(19,333,12,18,24.69),(19,373,19,27,10.54),(19,393,29,34,14.78),(32.3,313,42,51,63.06),(32.3,333,52,60,42.86),(32.3,373,61,68,14.78),(32.3,393,70,76,17.77)]:
        groups.append(dict(nominal_wt_percent=nominal,nominal_T_K=t,source_rows=list(range(lo,hi+1)),N=hi-lo+1,SI_S3_percent=target,interval_percent=[round(target-3,2),round(target+3,2)]))
    rows=list(csv.DictReader((ROOT/'data/reference/MDEA/Kuranov_1996_CO2_MDEA_total_pressure.csv').open()))
    primary=[i for g in groups for i in g['source_rows']]
    assert len(primary)==len(set(primary))==67
    assert all(float(r['m_CO2_mol_per_kg_H2O'])>0 for r in rows if int(r['source_row']) in primary)
    assert all(float(r['m_CO2_mol_per_kg_H2O'])==0 for r in rows if int(r['source_row']) in [28,69])
    return dict(table_path='data/reference/MDEA/Kuranov_1996_CO2_MDEA_total_pressure.csv',isotherms=groups,primary_count=67,zero_loading_diagnostic_rows=[28,69],excluded='413 K rows',feed='Actual row temperature and molalities; 1 kg initial water',pressure_conversion_to_Pa=1e5,primary_observable='total pressure',diagnostics=['zero-loading rows separately and in alternative 69-row comparison','y_CO2 * P versus measured total pressure; no measured partial pressure inferred','vapor composition'],window_basis='Issue 126 working allowance ±3 percentage points; not experimental uncertainty',retain='Near replicates, non-monotone rows and loadings above 1.2')


def main():
    wheel,digest=epcsaft.provenance()
    assert digest==EXPECTED_WHEEL and not isinstance(wheel,str)
    with zipfile.ZipFile(wheel) as z:
        assert all((Path(epcsaft.__file__).parent.parent/n).read_bytes()==z.read(n) for n in z.namelist() if n.startswith('epcsaft/') and not n.endswith('/'))
    doc=declaration()
    write('sources.json',sources())
    write('inventory.json',inventory())
    doc['preparation'] = dict(source_record_sha256=sha(OUT/'sources.json'),inventory_sha256=sha(OUT/'inventory.json'),reaction_reference=dict(solvent=W,water='pure-liquid',solutes='all other species, including MDEA and CO2, infinite dilution in water',source_basis='RawMoleFractionInfiniteDilution',pressure='system pressure'),pending_engine_issue='tannerpolley/ePC-SAFT#896',rule_grammar='Descriptive declaration; map to the merged Engine spelling without changing the scientific choice',interpretation='D1–D5 frozen; no sensitivity calculation or convention selection',same_sign_dispersion='All same-sign pairs including self excluded; omitted unlike-pair records are inactive',units='K, mol/m3, Pa; component diameters angstrom')
    write('declaration.json',doc)
    assert sha(OUT/'declaration.json') == '8e4aa8461e0cc8d3daf9d53a16118225b89fe4d79afc5ecd3341f5ea26915494'
    placeholder=copy.deepcopy(doc)
    placeholder.pop('preparation')
    placeholder['model_families'][-1]=dict(kind='permittivity',choice='solvent-mole-weighting',normalization='unnormalized',solvents=[W,M],provenance='D1 literal Eq.19; D3 Hsieh Eq.3/Table 3')
    comparison=copy.deepcopy(placeholder)
    comparison['preparation']=doc['preparation']
    comparison['model_families'][-1]=doc['model_families'][-1]
    assert comparison == doc
    write('run-document.json',placeholder)
    params=epcsaft.Parameters.from_mapping(placeholder)
    model=epcsaft.Mixture(params)
    checks={}
    # Fixed-density states, independent of the 67-row campaign.
    states={'neutral':[.88,.10,.02,0,0,0,0,0], 'charged':[.847,.10,.02,.015,.014,.001,.002,.001]}
    T,rho=333.15,30000.
    x=states['charged']; s=model.state(T,rho=rho,x=x)
    e,kB,eps0=1.602176634e-19,1.380649e-23,8.8541878128e-12
    expected=-e*e/(4*math.pi*eps0*kB*T)*(1-1/s.bulk_relative_permittivity)*sum(xi*v[1]**2/(v[3]*1e-10) for xi,v in zip(x,VALUES) if v[1])
    err=abs(s.born/expected-1)
    assert err<1e-9
    checks['born']=dict(status='pass',T_K=T,rho_mol_m3=rho,x=x,epsilon=s.bulk_relative_permittivity,native=s.born,Eq20=expected,relative_error=err,tolerance=1e-9,criterion='Floating point agreement; CODATA epsilon0 rounding')
    thermal=[]
    for t in [298.15,333.15,393.15]:
        sigma=2.7927+10.11*math.exp(-.01775*t)-1.417*math.exp(-.01146*t)
        theta=t-298.15
        km=-.118-.000759*theta-.0000132*theta**2+.000000125*theta**3
        kc=-.0021+.000453*theta
        constant=copy.deepcopy(placeholder)
        constant['correlations']=[c for c in constant['correlations'] if c['family']!='segment_diameter']
        constant['components'][0]['coefficients'].append(dict(family='segment_diameter',**coefficient('water/sigma/check',sigma,'angstrom')))
        for pair in constant['pairs']:
            if (pair['component_id_a'],pair['component_id_b']) in [(W,M),(W,C)]:
                expected_k=km if pair['component_id_b']==M else kc
                pair['coefficients']=[dict(family='k_ij',**coefficient('pair/check/'+pair['component_id_b'],expected_k,'dimensionless'))]
        replay=epcsaft.Mixture(epcsaft.Parameters.from_mapping(constant)).state(t,rho=rho,x=x)
        native=model.state(t,rho=rho,x=x)
        error=abs(replay.residual_helmholtz-native.residual_helmholtz)
        assert error<1e-12
        thermal.append(dict(T_K=t,water_sigma_A=sigma,k_water_MDEA=km,k_water_CO2=kc,native_a_res=native.residual_helmholtz,constant_input_a_res=replay.residual_helmholtz,absolute_error=error))
    for case in thermal:
        t=case['T_K']; pure=[]
        for cid,expected_eps in [(W,249.21-.79069*t+.00072997*t*t),(M,44.1399-.046824*t-.0000882158*t*t)]:
            eps=model.state(t,rho=1000.,x={cid:1.}).bulk_relative_permittivity
            assert abs(eps-expected_eps)<1e-12
            pure.append(dict(component=cid,native_epsilon=eps,polynomial_epsilon=expected_eps))
        case['Hsieh_pure_laws']=pure
    checks['temperature_laws']=dict(status='pass',cases=thermal,tolerance_absolute=1e-12,method='Native temperature laws versus independent Table 1 footnote/Eq.26 evaluation supplied as constants; all other Table 3 pairs admitted as printed constants')
    association=[]
    for label,composition in [('MDEA-CO2',[0,.9,.1,0,0,0,0,0]),('water-CO2',[.9,0,.1,0,0,0,0,0])]:
        state=model.state(T,rho=1000.,x=composition)
        co2sites=[state.site_fractions[i] for i,site in enumerate(params.site_ids) if site[0]==C]
        assert all(v==1 for v in co2sites) if label=='MDEA-CO2' else all(v<1 for v in co2sites)
        association.append(dict(binary=label,T_K=T,rho_mol_m3=1000.,x=composition,CO2_site_fractions=co2sites))
    # Explicit Eqs. 23 and 25 cross strength as independent partner/energy/volume check.
    explicit=copy.deepcopy(placeholder)
    sigma=2.7927+10.11*math.exp(-.01775*T)-1.417*math.exp(-.01146*T)
    for i,edge in enumerate(explicit['topology']['edges']):
        if edge['source']['kind']!='combining-rule': continue
        other=edge['endpoint_b']['component_id'] if edge['endpoint_a']['component_id']==W else edge['endpoint_a']['component_id']
        other_sigma=3.563 if other==M else 2.7852
        energy=(2425.6+(2046.6 if other==M else 0))/2
        volume=math.sqrt(.045*(.1238 if other==M else .045))*(math.sqrt(sigma*other_sigma)/((sigma+other_sigma)/2))**3
        edge['source']=dict(kind='explicit',provenance='Bülow Eqs. 23 and 25 independent arithmetic check')
        edge['energy_over_k']=coefficient(f'cross/{i}/energy',energy,'kelvin')
        edge['volume']=coefficient(f'cross/{i}/volume',volume,'dimensionless')
    replay=epcsaft.Mixture(epcsaft.Parameters.from_mapping(explicit)).state(T,rho=rho,x=x)
    cross_error=abs(replay.association-s.association)
    assert cross_error<1e-12
    assert all(site[0] in (W,M,C) for site in params.site_ids)
    checks['association']=dict(status='pass',site_ids=params.site_ids,binary_checks=association,CO2_water_energy_K=1212.8,explicit_cross_association_absolute_error=cross_error,tolerance_absolute=1e-12,ion_sites=0)
    deriv=[]
    for name,x in states.items():
        s=model.state(T,rho=rho,x=x)
        ht=.001
        aT=(model.state(T+ht,rho=rho,x=x).residual_helmholtz-model.state(T-ht,rho=rho,x=x).residual_helmholtz)/(2*ht)
        native_aT=(-s.residual_entropy/epcsaft.GAS_CONSTANT_J_PER_MOL_K-s.residual_helmholtz)/T
        h=.01
        fd=(model.state(T,rho=rho+h,x=x).pressure-model.state(T,rho=rho-h,x=x).pressure)/(2*h)
        items=[dict(quantity='da_res/dT',native=native_aT,finite_difference=aT,step=ht),dict(quantity='dP/drho',native=s.pressure_density_derivative,finite_difference=fd,step=h)]
        # d(n*a_res)/dn_i at constant T,V equals native mu_res/(RT).
        h=1e-5
        for i in range(8):
            if x[i]==0: continue
            direction=[0.]*8; direction[i]=1.
            if VALUES[i][1]:
                j=7 if VALUES[i][1]>0 else 6
                direction[j]=-VALUES[i][1]/VALUES[j][1]
            vals=[]
            for sign in [-1,1]:
                n=[xi+sign*h*di for xi,di in zip(x,direction)]; total=sum(n)
                vals.append(total*model.state(T,rho=rho*total,x=[ni/total for ni in n]).residual_helmholtz)
            items.append(dict(quantity=f'mu_res_RT_direction/{IDS[i]}',direction=direction,native=sum(di*mu for di,mu in zip(direction,s.residual_chemical_potential_over_rt) if di),finite_difference=(vals[1]-vals[0])/(2*h),step=h))
        for item in items:
            item['relative_error']=abs(item['finite_difference']/item['native']-1)
            item['status']='pass' if item['relative_error']<=1e-5 else 'fail'
        deriv.append(dict(state=name,T_K=T,rho_mol_m3=rho,x=x,checks=items))
    checks['derivatives']=dict(status='pass' if all(c['status']=='pass' for r in deriv for c in r['checks']) else 'fail',tolerance_relative=1e-5,states=deriv,repeat_on_896=True)
    rx=[]
    for r in REACTIONS:
        c1,c2,c3=r['c']; t=298.15
        lnx=c1+c2/t+c3*math.log(t); lnm=lnx-r['delta_nu_solute']*math.log(.01801528)
        pk=-lnm/math.log(10)
        ref=eq.ReactionReference(eq.ReferenceSourceBasis.RawMoleFractionInfiniteDilution)
        assert ref.reference_pressure_pa is None # Native optional unset means system pressure.
        law=eq.ReactionLogPolynomial(c1+c3*math.log(298.15),c2,c3,0.,298.15,273.,498.,'aqueous-mole-fraction-infinite-dilution-water-v1')
        rx.append(eq.Reaction(r['stoichiometry'],name=r['name'],correlation=law,reference=ref))
        checks[r['name']]=dict(status='pass' if abs(pk-r['pK_check'])<=r['rounding_tolerance'] else 'fail',ln_K_x=lnx,ln_K_m=lnm,pK_m=pk,expected=r['pK_check'],tolerance=r['rounding_tolerance'],delta_nu_solute=r['delta_nu_solute'],ln_Mw_m0=math.log(.01801528))
    prob=eq.Problem(T=T,P=1e5,feed=eq.Amounts({W:55.5084350618,M:2.,C:1.}),phases=[eq.Phase('L',support=IDS,kind='liquid')],reactions=rx,neutral_reference=eq.NeutralReference(solvent=W,standard_molality_mol_per_kg=1.,solute_molality_ratios={M:.125,C:.125,MH:.125,H:.125,B:.125,OH:.0625,D:.03125}))
    compiled=eq.compile_problem(model,prob)
    checks['admission']=dict(status='pass',species=list(params.component_ids),reaction_count=len(rx),charge_rows=compiled.charge_row_count,has_ions=compiled.has_ions,has_reaction=compiled.has_reaction,reference_basis='RawMoleFractionInfiniteDilution',reference_pressure_pa=None,meaning='System-pressure reference; native compile only, no solve',compiled_type=type(compiled).__name__)
    dielectric=[]
    for mode,expected in [('unnormalized',58.),('solvent-normalized',72.5)]:
        for masses in [(0.018,0.119),(0.061,0.019)]:
            refdoc=copy.deepcopy(placeholder)
            refdoc['model_families'][-1]['normalization']=mode
            refdoc['correlations']=[c for c in refdoc['correlations'] if c['family']!='relative_permittivity']
            for i,epsilon in enumerate([80.,20.]):
                refdoc['components'][i]['fixed']['molar_mass']['value']['magnitude']=masses[i]
                refdoc['components'][i]['coefficients'].append(dict(family='relative_permittivity',**coefficient(f'reference/{i}/epsilon',epsilon,'dimensionless')))
            refmodel=epcsaft.Mixture(epcsaft.Parameters.from_mapping(refdoc))
            for density in [1000.,20000.]:
                composition=[.7,.1,0,.1,.1,0,0,0]
                epsilon=refmodel.state(300.,rho=density,x=composition).bulk_relative_permittivity
                assert abs(epsilon-expected)<=1e-12
                dielectric.append(dict(normalization=mode,molar_masses=masses,rho_mol_m3=density,x=composition,native=epsilon,expected=expected))
            for cid,epsilon in [(W,80.),(M,20.)]:
                assert abs(refmodel.state(300.,rho=1000.,x={cid:1.}).bulk_relative_permittivity-epsilon)<=1e-12
            try:
                refmodel.state(300.,rho=1000.,x={MH:.5,B:.5})
            except ValueError as error:
                dielectric.append(dict(normalization=mode,zero_solvent_refusal=str(error)))
            else:
                raise AssertionError('Charged zero-solvent state was admitted')
    checks['dielectric']=dict(status='pass',tolerance_absolute=1e-12,cases=dielectric,pure_solvent_limits='80 and 20')
    write('repeat-checks.json',dict(engine_commit=ENGINE_COMMIT,wheel_path=str(wheel),wheel_sha256=digest,module=epcsaft.__file__,installed_files_byte_identical=True,declaration_sha256=sha(OUT/'declaration.json'),run_document_sha256=sha(OUT/'run-document.json'),document_diff_assertion='pass: only permittivity entry and removed preparation block',checks=checks,reproduction_run=False,fitting=False))
    assert all(r['status']=='pass' for r in checks.values()), checks
    print(json.dumps(checks,indent=2))

if __name__=='__main__': main()
