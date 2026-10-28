"""PDF units check and interim reaction-constant comparison, not a source correction."""
import hashlib
import json
import math
from pathlib import Path
import numpy as np

AN=Path(__file__).resolve().parents[1]

def write(name,x):
 (AN/'results'/name).write_text(json.dumps(x,indent=2)+'\n')

T=np.linspace(293.,423.,131)
a1,a2,a3,a4,a5,a6=-7.748e5,119.2,334.9,1585.,237.2,-734.7
# Printed right-hand side of Eq. 26 and its derivative.
f=a2+a3*(a4/T)/np.tanh(a4/T)-a5*(a6/T)*np.tanh(a6/T)+a1/T
cp_aly=a2+a3*((a4/T)/np.sinh(a4/T))**2+a5*((a6/T)/np.cosh(a6/T))**2
cp_literal=(cp_aly-f)/T
write('ideal-gas-units-check.json',dict(status='complete',source='Wangler2018, ZILDPWWE, PDF G7ZTAJZS p.4 printed p.18 Eq.26 and Table 3',pdf_sha256=hashlib.sha256(next((Path.home()/'Zotero/storage/G7ZTAJZS').glob('*.pdf')).read_bytes()).hexdigest(),render='inputs/wangler-equation-26.png',printed_equation='Hig/n = A2 + A3 (A4/T)coth(A4/T) - A5 (A6/T)tanh(A6/T) + A1/T',finding='PDF agrees with reading copy. RHS has Aly-Lee H/(nT) form if A2,A3,A5 carry J/mol/K and A1 carries J/mol. PDF does not print those coefficient units. Restoring T is the owner-adopted dimensional interpretation (2026-10-28), not an OCR repair.',literal_Cp_J_mol_K_range=[float(min(cp_literal)),float(max(cp_literal))],Aly_Lee_Cp_J_mol_K_range=[float(min(cp_aly)),float(max(cp_aly))],reason='Owner 2026-10-28 adopted restored factor T. Literal Cp violates 5R/2=20.79 J/mol/K. Cubic and zero h,s anchors retained.',rows=[dict(T_K=float(t),printed_rhs=float(q),literal_derivative=float(lit),Cp_if_enthalpy_is_T_times_RHS=float(cp)) for t,q,lit,cp in zip(T,f,cp_literal,cp_aly)]))
rows=[]
for t in (278.,293.15,298.15,313.15,368.):
 u=-83.491-819.7/t+10.976*math.log(t)
 j=-83.4914-819.7/t+10.9756*math.log(t)
 rows.append(dict(T_K=t,Uyan_lnKx=u,Jakobsen_printed_correlation=j,difference=j-u,Uyan_pKx=-u/math.log(10),Uyan_pKm=-(u+4.0165)/math.log(10)))
write('reaction-basis-interim.json',dict(status='blocked',missing='Kamps-Maurer 1996 DOI 10.1021/je960141+',sources=['Uyan2015 Table 1: -83.491, -819.7, 10.976, 0','Jakobsen2005 Table 1 and Eq.10: -83.4914, -819.7, 10.9756, 0'],basis='Uyan declares mole-fraction basis; this comparison does not establish the unavailable original source basis.',rows=rows,conclusion='Coefficients share lineage but do not give identical lnK at printed precision. At 298.15 K their difference is about -0.002679; no coefficient replacement authorized. Item (g) remains blocked.'))

# Owner adopts H/n = T times the printed RHS; derivative is Aly-Lee Cp.
T=np.linspace(293.,423.,1301)
cp=a2+a3*((a4/T)/np.sinh(a4/T))**2+a5*((a6/T)/np.cosh(a6/T))**2
polynomial=np.polynomial.Polynomial.fit(T,cp,3).convert()
error=100*abs(polynomial(T)/cp-1)
assert max(error)<=.5
record=json.loads((AN.parents[1]/'data/reference/MEA/thermal/physical-ideal-gas-calorics.json').read_text())
record['components'].pop('monoethanolamine')
record['components']={k:v for k,v in record['components'].items() if k in ('water','carbon-dioxide')}
record['components']['methyldiethanolamine']=dict(representation='cp_polynomial',coefficients=polynomial.coef.tolist(),range_k=[293.,423.],basis='ideal gas; Cp = a+b*T+c*T^2+d*T^3 in J/mol/K',source='Wangler 2018 Table 3 Eq.26 printed p.18 PDF G7ZTAJZS; restored factor T, owner decision 2026-10-28',enthalpy_entropy_anchor_k=313.15,anchor_basis='h=s=0 at 313.15 K, MEA amine convention')
(AN/'inputs/physical-ideal-gas-calorics.json').write_text(json.dumps(record,indent=2)+'\n')
def aly_cp(t,A2,A3,A4,A5,A6):
 return A2+A3*((A4/t)/np.sinh(A4/t))**2+A5*((A6/t)/np.cosh(A6/t))**2
# Independent EOS ideal part: Neumann et al. (2021), Eq.5 and Table 8, pp.10-11.
t=298.15; R=8.31446261815324
independent=R*(4+sum(m*(theta/t)**2*np.exp(theta/t)/np.expm1(theta/t)**2 for m,theta in [(31.94,800.),(29.98,2382.)]))
wangler=aly_cp(t,a2,a3,a4,a5,a6)
write('ideal-gas-polynomial.json',dict(status='complete',coefficients=polynomial.coef.tolist(),max_deviation_percent=float(max(error)),grid_step_K=.1,range_K=[293.,423.],anchor_K=313.15,h_anchor_J_mol=0.,s_anchor_J_mol_K=0.,lower_bound_J_mol_K=2.5*R,water_Cp_298_15=aly_cp(t,33.36,26.79,2611.,8.896,1169.),CO2_Cp_298_15=aly_cp(t,29.37,34.54,1428.,26.40,588.),independent_comparison=dict(source='Neumann, Baumhoegger, Span, Vrabec and Thol (2021), Thermodynamic Properties of Methyl Diethanolamine, DOI 10.1007/s10765-021-02933-7, Eq.5 Table 8 manuscript pp.10-11',url='https://www.static.tu.berlin/fileadmin/www/10002160/Publikationen/FEOS_MDEA.pdf',pdf_sha256='f077727a0b47bf53c8fdbdcd2676d8367780f6637c7df3193dd10759f54faa46',T_K=t,Cp_J_mol_K=independent,Wangler_Cp_J_mol_K=wangler,relative_difference_percent=100*(wangler/independent-1),limit='Independent EOS estimate, adjusted to liquid Cp and sound speed after Joback initialization; no measured ideal-gas Cp. Authors report Joback deviations up to 27% and cannot assign reliable ideal-Cp uncertainty.'),rows=[dict(T_K=float(t),source_Cp_J_mol_K=float(c),polynomial_Cp_J_mol_K=float(polynomial(t)),relative_deviation_percent=float(e)) for t,c,e in zip(T,cp,error)]))
