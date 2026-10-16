"""Xu 2018 Eq.1 with Versteeg 1988 Eqs.4-5; source constants stay explicit."""
import csv
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
# Existing stage-2 parameter document: component molar_mass, kg/mol.
M_MEA, M_WATER = 0.06108, 0.01801528


def convert(row):
    result = dict(row)
    T = round(float(row['temperature_reported']) + (273.15 if row['temperature_reported_unit'] == 'degC' else 0), 2)
    composition = float(row['mea_composition_reported'])
    if row['mea_composition_basis'].startswith('mole fraction'):
        w = composition*M_MEA/(composition*M_MEA + (1-composition)*M_WATER)
    else:
        w = composition
    unit_factor = {'Pa m3 mol-1': 1, 'kPa m3 mol-1': 1000}[row['H_N2O_reported_unit']]
    H = float(row['H_N2O_reported'])*unit_factor
    U = float(row['U_H_N2O_reported'])*unit_factor
    # The source HE is c/p. Our H is p/c, hence H_CO2/H_N2O = HE_N2O/HE_CO2.
    HE_CO2 = 3.54e-7*math.exp(2044/T)
    HE_N2O = 1.17e-7*math.exp(2284/T)
    ratio = HE_N2O/HE_CO2
    assert 290 < T < 394 and 0 < w < 1 and H > 0 and 0 < ratio < 1
    near = .24 <= w <= .37
    result.update(temperature_K=T, mea_mass_fraction=w,
        H_N2O_Pa_m3_per_mol=H, H_CO2_physical_Pa_m3_per_mol=H*ratio,
        H_CO2_over_H_N2O=ratio, U_H_CO2_from_N2O_only_Pa_m3_per_mol=U*ratio,
        H_CO2_using_Eq6_Pa_m3_per_mol=H*math.exp(240/T)/3.04,
        conversion_equations='Xu18 Eq.1 p.2708; Versteeg1988 Eqs.4-5 p.30',
        conversion_pdf_key='RBJRWHQZ',
        conversion_pdf_sha256='a844567b8aa74a75f2c4cb81f80215a4e8920e65ccf9fc6d4692793addd0bdc5',
        analogy_assumption='CO2/N2O physical concentration-solubility ratio in unloaded MEA-water equals that in water',
        analogy_uncertainty='not quantified; propagated expanded uncertainty covers N2O measurement only',
        proposed_role='near-30mass calibration candidate' if near else 'concentration-transfer comparison candidate',
        water_correlation_domain='291-359.4 K common measured water span; highest Hartono row 360.25 K is slight extrapolation',
        admission='candidate; independent source/data and design review required')
    return result


if __name__ == '__main__':
    rows = []
    for name in ('Hartono_2014_N2O_solubility.csv', 'Xu_2018_N2O_solubility.csv'):
        with (ROOT/name).open(newline='') as handle:
            rows.extend(convert(r) for r in csv.DictReader(handle))
    assert len(rows) == len({r['record_id'] for r in rows}) == 23
    # Catch an inverted Henry convention and a kPa/Pa error at a printed water reference.
    assert math.isclose(3.54e-7*math.exp(2044/298), 3.37e-4, rel_tol=.005)
    assert 3200 < rows[0]['H_CO2_physical_Pa_m3_per_mol'] < 3600
    with (ROOT/'CO2_physical_from_N2O.csv').open('w',newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    print(f'{len(rows)} analogy-derived CO2 Henry constants; no model evaluations or fits')
