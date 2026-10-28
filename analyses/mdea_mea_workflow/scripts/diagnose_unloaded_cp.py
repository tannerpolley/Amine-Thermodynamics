"""Issue 222 diagnosis: unloaded MDEA-water heat capacity at the A1 endpoint. Nothing is fitted."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
import copy,csv,importlib.util,json,math
from math import comb
from pathlib import Path
import numpy as np
from scipy.optimize import brentq
AN=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('joint',AN/'scripts/fit_mdea.py');j=importlib.util.module_from_spec(spec);spec.loader.exec_module(j)
p,d,reg=j.p,j.d,j.reg
M,W=p.M,p.W
OUT='results/diagnosis-unloaded-cp'
R=p.epcsaft.GAS_CONSTANT_J_PER_MOL_K
MASS={M:.1191622,W:.01801528}
A1=json.loads((AN/'results/joint-fit/A1/endpoint.json').read_text())
KIM=json.loads((AN/'results/kim-prefit/summary.json').read_text())['primary']
CALORICS=json.loads((AN/'inputs/physical-ideal-gas-calorics.json').read_text())
# IAPWS-95 liquid water at 101325 Pa (chemicals 1.5.2), retained by the MEA bundle.
IAPWS={float(r['T_K']):float(r['cp_kJ_kg_K']) for r in csv.DictReader((AN.parent/'mea_parameter_bundle/results/density-cp-160/cp-124-assessment/iapws95-reference.csv').open()) if r['grid']=='atmospheric-controls'}
# Concepcion et al. 2023 (Zotero V6XIU3SE, PDF YBQI572A) Table 6, 0.100 MPa column, kJ/kg/K; Ur(cp)=0.010 (k=2).
CONCEPCION={.1001:{293.15:4.065,313.15:4.126,333.15:4.096,353.15:4.179},.2001:{293.15:3.880,313.15:3.987,333.15:4.051,353.15:4.098},
    .2998:{313.15:3.890,333.15:3.965,353.15:4.057},.4001:{293.15:3.601,313.15:3.727,333.15:3.810,353.15:3.897}}
WEILAND={float(r['MDEA_mass_fraction']):float(r['Cp_J_g_K']) for r in csv.DictReader((p.DATA/'Weiland1997_stage1.csv').open()) if float(r['loading'])==0.}

def pair_edit(doc,k=None,slope=None):
    q=next(q for q in doc['pairs'] if {q['component_id_a'],q['component_id_b']}=={M,W})
    for c in q['coefficients']:
        if c['family']=='k_ij' and k is not None:c['value']['magnitude']=k
        if c['family']=='k_ij_reciprocal_temperature_slope' and slope is not None:c['value']['magnitude']=slope
def edge(doc):return next(e for e in doc['topology']['edges'] if e['endpoint_a']['component_id']==M and e['endpoint_b']['component_id']==M)
def scale_energy(doc,f):edge(doc)['energy_over_k']['value']['magnitude']*=f
def kappa(doc,v):edge(doc)['volume']['value']['magnitude']=v
def cross_off(doc):
    t=doc['topology'];t['edges']=[e for e in t['edges'] if {e['endpoint_a']['component_id'],e['endpoint_b']['component_id']}!={M,W}]
    t['no_cross_association'].append(dict(component_id_a=M,component_id_b=W,provenance='issue 222 unloaded-Cp diagnosis only'))

def neumann_ideal_cp(T):
    # Neumann et al. 2022 (Zotero CA5R9QN8) Eq. 5, Table 8.
    return R*(4+sum(m*(t/T)**2*math.exp(t/T)/math.expm1(t/T)**2 for m,t in [(31.94,800.),(29.98,2382.)]))
NEUMANN_CUBIC=np.polynomial.polynomial.polyfit(np.arange(293.,423.05,.1),[neumann_ideal_cp(t) for t in np.arange(293.,423.05,.1)],3)

def caloric(params,mdea_cp=None):
    # Same construction as admission_probe.caloric_record, with an optional MDEA cubic substituted.
    intervals=[[] for _ in params.component_ids]
    for cid,src in CALORICS['components'].items():
        if cid not in params.component_ids:continue
        if src['representation']=='cp_polynomial':
            c0=src['enthalpy_entropy_anchor_k'];cp=list(mdea_cp) if mdea_cp is not None else src['coefficients']
            form=p.epcsaft.IdealPolynomial([sum(a*comb(i,k)*c0**(i-k) for i,a in enumerate(cp) if i>=k) for k in range(4)],c0,0.,0.)
        else:form=p.epcsaft.IdealShomate(src['coefficients'],src['formation_enthalpy_j_per_mol'])
        intervals[list(params.component_ids).index(cid)]=[p.epcsaft.IdealInterval(*src['range_k'],True,True,p.epcsaft.IdealCorrelation(form,1e5))]
    return p.epcsaft.ThermochemistryRecord(1e5,intervals)

def build(edit=None,mdea_cp=None):
    doc=copy.deepcopy(A1)
    if edit:edit(doc)
    params=p.epcsaft.Parameters.from_mapping(doc,components=[M,W])
    return p.epcsaft.Mixture(params,thermochemistry=caloric(params,mdea_cp)),doc

def composition(w):
    if w>=1:return {M:1.}
    if w<=0:return {W:1.}
    nw=j.water(w);return {M:1/(1+nw),W:nw/(1+nw)}
def molar_mass(x):return sum(MASS[c]*v for c,v in x.items())

TERMS=('hard_chain','dispersion','association')
def decompose(model,T,x,P=101325.):
    """Ideal Cp plus per-term residual Cv (additive) and the non-additive Cp-Cv coupling, at the liquid root."""
    s=model.state(T,P=P,x=x,phase='liquid',derived_properties=True);rho=s.molar_density
    hT,hr=.05,1e-4*rho
    a={(i,k):model.state(T+i*hT,rho=rho+k*hr,x=x) for i in (-1,0,1) for k in (-1,0,1)}
    out=dict(T_K=T,x_MDEA=x.get(M,0.),molar_density_mol_m3=rho,mass_density_kg_m3=rho*molar_mass(x),molar_mass_kg_mol=molar_mass(x),
        Cp_total_J_mol_K=s.total_isobaric_heat_capacity,Cp_ideal_J_mol_K=s.ideal_isobaric_heat_capacity,Cp_residual_engine_J_mol_K=s.residual_isobaric_heat_capacity,Cv_residual_engine_J_mol_K=s.residual_isochoric_heat_capacity)
    dPdT,dPdr=rho*R,R*T
    for t in TERMS:
        f=lambda i,k:getattr(a[(i,k)],t)
        aT=(f(1,0)-f(-1,0))/(2*hT);aTT=(f(1,0)-2*f(0,0)+f(-1,0))/hT**2
        ar=(f(0,1)-f(0,-1))/(2*hr);arr=(f(0,1)-2*f(0,0)+f(0,-1))/hr**2;arT=(f(1,1)-f(1,-1)-f(-1,1)+f(-1,-1))/(4*hT*hr)
        out[f'Cv_{t}_J_mol_K']=-R*(2*T*aT+T*T*aTT)
        # P = rho R T (1 + rho a_rho): per-term additive pressure derivatives.
        out[f'dPdT_{t}_Pa_K']=R*rho*rho*(ar+T*arT);dPdT+=out[f'dPdT_{t}_Pa_K']
        dPdr+=R*T*(2*rho*ar+rho*rho*arr)
    out['dPdT_total_Pa_K']=dPdT;out['dPdrho_total_Pa_m3_mol']=dPdr;out['dPdrho_engine_Pa_m3_mol']=s.pressure_density_derivative
    out['Cp_minus_Cv_J_mol_K']=T*dPdT**2/(rho*rho*dPdr)
    out['Cp_minus_Cv_minus_R_J_mol_K']=out['Cp_minus_Cv_J_mol_K']-R
    out['Cv_residual_sum_J_mol_K']=sum(out[f'Cv_{t}_J_mol_K'] for t in TERMS)
    out['Cp_residual_sum_J_mol_K']=out['Cv_residual_sum_J_mol_K']+out['Cp_minus_Cv_minus_R_J_mol_K']
    out['closure_relative']=out['Cp_residual_sum_J_mol_K']/s.residual_isobaric_heat_capacity-1
    out['Cp_total_J_g_K']=s.total_isobaric_heat_capacity/molar_mass(x)/1000
    return out

def cp_mass(model,T,w,P=101325.):
    x=composition(w);s=model.state(T,P=P,x=x,phase='liquid',derived_properties=True)
    return s.total_isobaric_heat_capacity/molar_mass(x)/1000,s.molar_density*molar_mass(x)

# --- Neumann et al. 2022 pure-MDEA reference EOS (Tables 8-11), verified against Table 11 test values.
NTC,NRC=741.,2720.
POL=[(0.050010681,1,4),(1.629696,.24,1),(-2.307822,.98,1),(-.6606441,1.18,2),(.2677026,.38,3)]
EXP=[(-1.858733,2.9,1,2),(-1.686275,3.03,3,2),(.3534702,.67,2,1),(-2.007864,3.,2,2),(-.038263920,.72,7,1)]
GBS=[(4.058964,1.63,1,1.22,1.02,1.4,.846),(-.009984452,2.1,1,19.6,1000.,1.08,.93),(-.2906544,1.91,3,1.5,1.3,1.38,.98),(-.6089361,1.92,2,1.36,1.3,1.19,.699),(-.6822699,2.,2,1.6,1.19,1.02,.698)]
def alpha_r(dl,tau):
    return (sum(n*dl**dd*tau**t for n,t,dd in POL)+sum(n*dl**dd*tau**t*math.exp(-dl**l) for n,t,dd,l in EXP)
        +sum(n*dl**dd*tau**t*math.exp(-eta*(dl-eps)**2-beta*(tau-gam)**2) for n,t,dd,eta,beta,gam,eps in GBS))
def neumann(T,rho):
    dl,tau,h=rho/NRC,NTC/T,1e-4
    f=lambda i,k:alpha_r(dl+i*h,tau+k*h)
    ad=(f(1,0)-f(-1,0))/(2*h);add=(f(1,0)-2*f(0,0)+f(-1,0))/h**2;att=(f(0,1)-2*f(0,0)+f(0,-1))/h**2
    adt=(f(1,1)-f(1,-1)-f(-1,1)+f(-1,-1))/(4*h*h)
    cv=neumann_ideal_cp(T)/R-1-tau*tau*att;num=(1+dl*ad-dl*tau*adt)**2;den=1+2*dl*ad+dl*dl*add
    return dict(p_Pa=rho*R*T*(1+dl*ad),cp_J_mol_K=R*(cv+num/den),cv_J_mol_K=R*cv,w_m_s=math.sqrt(R*T/.1191622*(den+num/cv)))
NEUMANN_TABLE11=[(300,8.8,34.24192443746,1678.19027898),(450,.002,.00744871480506,179.208847600),(450,8.,48.7244808160,1340.61678442),(650,.15,.734093733106,195.867090294),(700,5.5,9.1216579481,448.771720946)]

def main():
    out=AN/OUT;out.mkdir(parents=True,exist_ok=True)
    base,_=build()
    kim,_=build(lambda doc:pair_edit(doc,*KIM))
    # 1. Reproduction: neutral frozen Cp, and A1's fitted (equilibrium) prediction from fit.json.
    fit=json.loads((AN/'results/joint-fit/A1/fit.json').read_text());meta,_,_=j.objective(p.epcsaft.Parameters.from_mapping(A1))
    fitted={float(m['row']['MDEA_mass_fraction']):fit['predictions'][i] for i,m in enumerate(meta) if m['group']=='Cp' and float(m['row']['loading'])==0.}
    rows=[]
    for label,model in (('A1',base),('item-k pre-fit',kim)):
        for w,obs in sorted(WEILAND.items()):
            cp,rho=cp_mass(model,298.15,w);x=composition(w)
            eqm=fitted[w]/molar_mass(x)/1000 if label=='A1' and w in fitted else None
            rows.append(dict(model=label,source='Weiland 1997 Table 1',T_K=298.15,MDEA_mass_fraction=w,observed_J_g_K=obs,frozen_J_g_K=cp,frozen_relative=cp/obs-1,fitted_equilibrium_J_g_K=eqm,fitted_relative=eqm/obs-1 if eqm else None,in_fit=w<=.5,density_kg_m3=rho))
        for w,series in CONCEPCION.items():
            for T,obs in series.items():
                cp,rho=cp_mass(model,T,w)
                rows.append(dict(model=label,source='Concepcion 2023 Table 6 (0.1 MPa)',T_K=T,MDEA_mass_fraction=w,observed_J_g_K=obs,frozen_J_g_K=cp,frozen_relative=cp/obs-1,fitted_equilibrium_J_g_K=None,fitted_relative=None,in_fit=False,density_kg_m3=rho))
    write_csv(out/'reproduction.csv',rows)
    # 2. Term decomposition: pure liquids and the Weiland states.
    states=[('pure water',0.),('30 wt%',.3),('40 wt%',.4),('50 wt%',.5),('pure MDEA',1.)]
    dec=[]
    for label,model in (('A1',base),('item-k pre-fit',kim)):
        for name,w in states:dec.append(dict(model=label,state=name,**decompose(model,298.15,composition(w))))
    assert max(abs(r['closure_relative']) for r in dec)<1e-5,max(abs(r['closure_relative']) for r in dec)
    write_csv(out/'decomposition.csv',dec)
    # Excess Cp across composition (ideal mixing of the model's own pure liquids), per term.
    pure={w:decompose(base,298.15,composition(w)) for w in (0.,1.)}
    keys=['Cp_total_J_mol_K','Cp_ideal_J_mol_K']+[f'Cv_{t}_J_mol_K' for t in TERMS]+['Cp_minus_Cv_minus_R_J_mol_K']
    excess=[]
    for xm in [0.,.01,.02,.04,.0608,.0916,.1,.1313,.15,.2,.3,.4,.5,.6,.7,.8,.9,.95,1.]:
        x={M:xm,W:1-xm} if 0<xm<1 else ({M:1.} if xm else {W:1.});r=decompose(base,298.15,x)
        excess.append(dict(x_MDEA=xm,**{k.replace('_J_mol_K','_excess_J_mol_K'):r[k]-xm*pure[1.][k]-(1-xm)*pure[0.][k] for k in keys},Cp_total_J_mol_K=r['Cp_total_J_mol_K']))
    write_csv(out/'excess-cp-composition.csv',excess)
    # 3. Pure MDEA: Neumann reference EOS (fitted to Zhang 2002 Cp) against the model.
    checks=[dict(T_K=T,rho_mol_dm3=rh,p_MPa=neumann(T,rh*1000)['p_Pa']/1e6,p_table=pt,w_m_s=neumann(T,rh*1000)['w_m_s'],w_table=wt) for T,rh,pt,wt in NEUMANN_TABLE11]
    worst=max(max(abs(c['p_MPa']/c['p_table']-1),abs(c['w_m_s']/c['w_table']-1)) for c in checks);assert worst<1e-5,worst
    pure_rows=[]
    for T in (298.15,313.15,333.15,353.15):
        rho=brentq(lambda r:neumann(T,r)['p_Pa']-101325.,8200.,9500.);n=neumann(T,rho)
        m=base.state(T,P=101325.,x={M:1.},phase='liquid',derived_properties=True)
        pure_rows.append(dict(T_K=T,neumann_rho_kg_m3=rho*.1191622,model_rho_kg_m3=m.molar_density*.1191622,neumann_cp_J_mol_K=n['cp_J_mol_K'],neumann_ideal_cp_J_mol_K=neumann_ideal_cp(T),neumann_residual_cp_J_mol_K=n['cp_J_mol_K']-neumann_ideal_cp(T),
            model_cp_J_mol_K=m.total_isobaric_heat_capacity,model_ideal_cp_J_mol_K=m.ideal_isobaric_heat_capacity,model_residual_cp_J_mol_K=m.residual_isobaric_heat_capacity,model_relative=m.total_isobaric_heat_capacity/n['cp_J_mol_K']-1))
    # 5. Water against IAPWS-95.
    water_rows=[]
    for T in sorted(IAPWS):
        s=base.state(T,P=101325.,x={W:1.},phase='liquid',derived_properties=True);cp=s.total_isobaric_heat_capacity/MASS[W]/1000
        water_rows.append(dict(T_K=T,model_cp_J_g_K=cp,iapws95_cp_J_g_K=IAPWS[T],relative=cp/IAPWS[T]-1,model_ideal_J_mol_K=s.ideal_isobaric_heat_capacity,model_residual_J_mol_K=s.residual_isobaric_heat_capacity))
    write_csv(out/'water-iapws.csv',water_rows)
    p.write(f'{OUT}/pure-mdea.json',dict(neumann_table11_check=checks,neumann_table11_max_relative=worst,rows=pure_rows,
        reference='Neumann, Baumhoegger, Span, Vrabec, Thol 2022, Int. J. Thermophys. 43:10 (Zotero CA5R9QN8, PDF 4V38X73R), Eqs. 5-7, Tables 8-11; its liquid Cp is fitted to Zhang et al. 2002 (DSC, 2 % stated) and represents the seven literature Cp sets within about 4 % (section 5.4).',
        limit='The Neumann EOS is a correlation of the measurements, not a measurement; none of the primary pure-MDEA Cp sources is in Zotero.',
        missing_sources=dict(Zhang2002='10.1006/jcht.2002.0937',Chiu1999='10.1021/je980217x',Chen2001='10.1021/je0000367',Maham1997='10.1039/a607568a',MundhwaHenni2007='10.1021/je0604232',Hawrylak2006='Zh. Khim. Termodin. Termokhim. 38 (2006) 988-1007 (Wangler 2018 ref. 60); no DOI located')))
    # 4. One-change sensitivities of frozen Cp and density at the Weiland unloaded states.
    k0=next(c['value']['magnitude'] for q in A1['pairs'] if {q['component_id_a'],q['component_id_b']}=={M,W} for c in q['coefficients'] if c['family']=='k_ij')
    cases=[('A1 endpoint',None,None),('ideal-gas Cp: Neumann 2022',None,NEUMANN_CUBIC),
        ('MDEA association energy x0.9',lambda doc:scale_energy(doc,.9),None),('MDEA association energy x1.1',lambda doc:scale_energy(doc,1.1),None),
        ('kappa unconverted 0.123858',lambda doc:kappa(doc,.123858),None),
        ('k(MDEA-water) slope 0 (k0 kept)',lambda doc:pair_edit(doc,slope=0.),None),(f'k(MDEA-water) slope Kim {KIM[1]:.2f} K (k0 kept)',lambda doc:pair_edit(doc,slope=KIM[1]),None),
        ('k(MDEA-water) item-k pre-fit (both)',lambda doc:pair_edit(doc,*KIM),None),
        ('MDEA-water cross-association off (diagnostic)',cross_off,None),
        ('two-change: slope 0 (k0 kept) + Neumann ideal-gas Cp',lambda doc:pair_edit(doc,slope=0.),NEUMANN_CUBIC)]
    sens=[]
    for name,edit,cp in cases:
        model,_=build(edit,cp)
        for w in (.3,.4,.5,.6,1.):
            x=composition(w);r=decompose(model,298.15,x)
            sens.append(dict(case=name,MDEA_mass_fraction=w,observed_J_g_K=WEILAND.get(w),Cp_J_g_K=r['Cp_total_J_g_K'],relative=r['Cp_total_J_g_K']/WEILAND[w]-1 if w in WEILAND else None,density_kg_m3=r['mass_density_kg_m3'],
                Cp_ideal_J_mol_K=r['Cp_ideal_J_mol_K'],**{f'Cv_{t}_J_mol_K':r[f'Cv_{t}_J_mol_K'] for t in TERMS},Cp_minus_Cv_minus_R_J_mol_K=r['Cp_minus_Cv_minus_R_J_mol_K']))
    write_csv(out/'sensitivity.csv',sens)
    # Consequences of the k(MDEA-water) settings: excess Cp at the Weiland states, Concepcion T trend, Sobrino density, Kim bubble pressure. Evaluation only.
    settings=[('A1',None),('slope 0 (A1 k0 kept)',lambda doc:pair_edit(doc,slope=0.)),('item-k pre-fit',lambda doc:pair_edit(doc,*KIM)),('slope 0 (item-k k0 kept)',lambda doc:pair_edit(doc,KIM[0],0.))]
    neu298=pure_rows[0]['neumann_cp_J_mol_K'];water298=IAPWS[298.15]*MASS[W]*1000
    excess_rows,trend,dens,kim_rows=[],[],[],[]
    sobrino=[r for r in csv.DictReader((p.DATA/'Sobrino2016_stage1.csv').open()) if float(r['pressure_MPa'])==.1]
    for name,edit in settings:
        model,doc=build(edit);pure_m=decompose(model,298.15,{M:1.})['Cp_total_J_mol_K'];pure_w=decompose(model,298.15,{W:1.})['Cp_total_J_mol_K']
        for w,obs in sorted(WEILAND.items()):
            x=composition(w);mm=molar_mass(x);cp=model.state(298.15,P=101325.,x=x,phase='liquid',derived_properties=True).total_isobaric_heat_capacity
            excess_rows.append(dict(setting=name,MDEA_mass_fraction=w,x_MDEA=x[M],apparent_measured_excess_J_mol_K=obs*mm*1000-x[M]*neu298-x[W]*water298,model_excess_J_mol_K=cp-x[M]*pure_m-x[W]*pure_w,model_relative=cp/(obs*mm*1000)-1))
        for w,series in CONCEPCION.items():
            for T,obs in series.items():
                cp,_=cp_mass(model,T,w);trend.append(dict(setting=name,MDEA_mass_fraction=w,T_K=T,observed_J_g_K=obs,model_J_g_K=cp,relative=cp/obs-1))
        res=[]
        for r in sobrino:
            x=composition(float(r['MDEA_mass_fraction']));s=model.state(float(r['temperature_K']),P=1e5,x=x,phase='liquid');res.append(s.molar_density*molar_mass(x)-float(r['density_kg_m3']))
        dens.append(dict(setting=name,rows=len(res),mean_kg_m3=float(np.mean(res)),max_abs_kg_m3=float(np.max(np.abs(res))),frozen_cost=float(sum(.5*10*(v/.5)**2 for v in res))))
        k0s,slope=[next(c['value']['magnitude'] for q in doc['pairs'] if {q['component_id_a'],q['component_id_b']}=={M,W} for c in q['coefficients'] if c['family']==f) for f in ('k_ij','k_ij_reciprocal_temperature_slope')]
        params,binary=j.k.binary_model((k0s,slope));logs=[]
        for r in j.k.ROWS:
            item=reg.observation(params,'pressure',j.k.bubble(r),observed=float(r['total_pressure_kPa'])*1000,form='log_ratio');pred=reg.predict(binary,item)
            logs.append(math.log(pred.value/item.observed) if pred.status.name=='Available' else float('nan'))
        kim_rows.append(dict(setting=name,k_ij=k0s,slope_K=slope,rows=len(logs),available=sum(v==v for v in logs),AARD_percent=100*float(np.nanmean([abs(math.expm1(v)) for v in logs])),cost=float(.5*np.nansum(np.square(logs)))))
    write_csv(out/'excess-at-weiland.csv',excess_rows);write_csv(out/'concepcion-trend.csv',trend)
    p.write(f'{OUT}/k-setting-consequences.json',dict(sobrino_unloaded_density=dens,kim_bubble_pressure=kim_rows,basis='Frozen (no reaction) liquid at 0.1 MPa for density; Kim rows replayed through the item-(k) binary bubble problem; nothing refitted. Apparent measured excess uses Neumann 2022 pure-MDEA Cp and IAPWS-95 water at 298.15 K.'))
    p.write(f'{OUT}/summary.json',dict(A1_MDEA_water_k=[k0,next(c['value']['magnitude'] for q in A1['pairs'] if {q['component_id_a'],q['component_id_b']}=={M,W} for c in q['coefficients'] if c['family']=='k_ij_reciprocal_temperature_slope')],
        item_k_prefit_k=KIM,neumann_cubic=NEUMANN_CUBIC.tolist(),neumann_cubic_max_relative=float(max(abs(np.polynomial.polynomial.polyval(t,NEUMANN_CUBIC)/neumann_ideal_cp(t)-1) for t in np.arange(293.,423.05,.1))),
        decomposition_max_closure=max(abs(r['closure_relative']) for r in dec),finite_difference_steps=dict(T_K=.05,rho_relative=1e-4),runtime=json.loads((AN/'inputs/runtime.json').read_text())))
    print('done',flush=True)

def write_csv(path,rows):
    with path.open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)

if __name__=='__main__':main()
