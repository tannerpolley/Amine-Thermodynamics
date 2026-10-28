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
write('ideal-gas-units-check.json',dict(status='incomplete',source='Wangler2018, ZILDPWWE, PDF G7ZTAJZS p.4 printed p.18 Eq.26 and Table 3',pdf_sha256=hashlib.sha256(next((Path.home()/'Zotero/storage/G7ZTAJZS').glob('*.pdf')).read_bytes()).hexdigest(),render='inputs/wangler-equation-26.png',printed_equation='Hig/n = A2 + A3 (A4/T)coth(A4/T) - A5 (A6/T)tanh(A6/T) + A1/T',finding='PDF agrees with reading copy. RHS has Aly-Lee H/(nT) form if A2,A3,A5 carry J/mol/K and A1 carries J/mol. PDF does not print those coefficient units. Multiplication by T is an interpretation, not an OCR repair.',literal_Cp_J_mol_K_range=[float(min(cp_literal)),float(max(cp_literal))],Aly_Lee_Cp_J_mol_K_range=[float(min(cp_aly)),float(max(cp_aly))],reason='No adopted dimensional interpretation or separately cited polynomial. No polynomial promoted and no h,s anchors or 0.5% reproduction criterion claimed.',rows=[dict(T_K=float(t),printed_rhs=float(q),literal_derivative=float(lit),Cp_if_enthalpy_is_T_times_RHS=float(cp)) for t,q,lit,cp in zip(T,f,cp_literal,cp_aly)]))
rows=[]
for t in (278.,293.15,298.15,313.15,368.):
 u=-83.491-819.7/t+10.976*math.log(t)
 j=-83.4914-819.7/t+10.9756*math.log(t)
 rows.append(dict(T_K=t,Uyan_lnKx=u,Jakobsen_printed_correlation=j,difference=j-u,Uyan_pKx=-u/math.log(10),Uyan_pKm=-(u+4.0165)/math.log(10)))
write('reaction-basis-interim.json',dict(status='blocked',missing='Kamps-Maurer 1996 DOI 10.1021/je960141+',sources=['Uyan2015 Table 1: -83.491, -819.7, 10.976, 0','Jakobsen2005 Table 1 and Eq.10: -83.4914, -819.7, 10.9756, 0'],basis='Uyan declares mole-fraction basis; this comparison does not establish the unavailable original source basis.',rows=rows,conclusion='Coefficients share lineage but do not give identical lnK at printed precision. At 298.15 K their difference is about -0.002679; no coefficient replacement authorized. Item (g) remains blocked.'))
