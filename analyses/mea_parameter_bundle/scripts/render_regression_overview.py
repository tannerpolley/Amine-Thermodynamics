"""Render identified retained regression rows; never import or execute the EOS."""

import csv
import hashlib
import json
import math
import statistics
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from manuscript_style import apply_style
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures/regression_overview/output"
DATA = ROOT / "results/density-cp-160/D1-evidence"
PRESSURE = DATA / "pressure-figure-data.csv"
SPECIES_DATA = DATA / "species-figure-data.csv"
POOL = DATA / "pool-figure-data.csv"
WATER = ROOT / "results/density-cp-160/cp-124-assessment/water.csv"
NATIVE_FIT = DATA / "F1-A/native-fit.json"
PHYSICAL = DATA / "F1-A/parameters.json"
PARAM = ROOT / "results/selected-current-best-parameters.json"
QUALIFICATION = ROOT / "results/density-cp-160/common-wheel-48a639e7/qualification.json"
# Separate legacy diagnostic renderer reads this file; this notebook does not.
FIT = ROOT / "results/current-best-fit-residuals.csv"
HCO3_POOL_LABEL = "HCO3- + CO3^2-"
ENGINE_COMMIT = "D1 fit, wheel 28181e72"
COLORS = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9"]
SOURCES = ["Aronu2011", "Hilliard2008", "Idris2014", "Jou1995", "Mamun2005", "Xu2011"]
MARKERS = dict(zip(SOURCES, ["*", "o", "D", "^", "h", "v"], strict=True))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def ln_ratio(row):
    return math.log(float(row["predicted"]) / float(row["observed"]))


def positive(rows):
    return [
        r
        for r in rows
        if r["predicted"] and float(r["observed"]) > 0.0 and float(r["predicted"]) > 0.0
    ]


def ln_statistics(
    family, group_type, group, rows, engine=ENGINE_COMMIT
):
    valid = positive(rows)
    errors = [ln_ratio(r) for r in valid]
    rms_ln = math.sqrt(statistics.fmean(e * e for e in errors))
    return {
        "engine": engine,
        "family": family,
        "group_type": group_type,
        "group": group,
        "attempted": len(rows),
        "evaluated_positive": len(valid),
        "mean_ln_pred_over_obs": statistics.fmean(errors),
        "rms_ln_pred_over_obs": rms_ln,
        "rmse_log10": rms_ln / math.log(10.0),
        "rms_factor": math.exp(rms_ln),
        "aard_percent": 100.0
        * statistics.fmean(abs(math.exp(e) - 1.0) for e in errors),
        "mean_difference_native_unit": statistics.fmean(
            float(r["predicted"]) - float(r["observed"]) for r in valid
        ),
    }


def ln_label(rows):
    """n, AARD, bias and RMS ln of retained residual rows, for figure text."""
    stat = ln_statistics("", "", "", rows)
    return (
        f"n = {stat['evaluated_positive']} · AARD {stat['aard_percent']:.1f} % · "
        f"bias (mean ln) {stat['mean_ln_pred_over_obs']:+.2f} · RMS ln {stat['rms_ln_pred_over_obs']:.2f}"
    )


def species_label(rows):
    stat = ln_statistics("", "", "", rows)
    return (
        f"n = {stat['evaluated_positive']}, AARD {stat['aard_percent']:.0f} %, "
        f"RMS ln {stat['rms_ln_pred_over_obs']:.2f}"
    )


def short_label(rows):
    stat = ln_statistics("", "", "", rows)
    return f"n = {stat['evaluated_positive']}, AARD {stat['aard_percent']:.0f} %"


def save(fig, name):
    for ext in ("svg", "png", "pdf"):
        fig.savefig(
            OUT / f"{name}.{ext}",
            dpi=160,
            metadata={"Date": None}
            if ext == "svg"
            else {"CreationDate": None, "ModDate": None}
            if ext == "pdf"
            else {},
        )
    plt.close(fig)


def source_colors(pressure):
    present = [s for s in SOURCES if any(r["source"] == s for r in pressure)]
    return {s: COLORS[i] for i, s in enumerate(present)}


def render_isotherms(pressure, colors, title):
    fig, axes = plt.subplots(2, 3, figsize=(10, 6), layout="constrained")
    for ax, temperature in zip(axes.flat, (40, 60, 80, 100, 120)):
        group = [r for r in pressure if round(float(r['temperature_C'])) == temperature]
        for source, color in colors.items():
            sub = [r for r in group if r['source'] == source]
            ax.scatter([float(r['loading_mol_CO2_per_mol_MEA']) for r in sub],
                       [float(r['observed']) / 1000 for r in sub], marker=MARKERS[source],
                       facecolors='none', edgecolors=color, s=26, label=source)
        ax.scatter([float(r['loading_mol_CO2_per_mol_MEA']) for r in group],
                   [float(r['predicted']) / 1000 for r in group], marker='+', color='black', s=24)
        domain = 'calibration' if temperature <= 60 else 'comparison' if temperature == 80 else 'extrapolation'
        ax.set(title=f'{temperature} °C · {domain}', xlabel='CO₂ loading (mol/mol MEA)',
               ylabel='CO₂ partial pressure (kPa)', yscale='log')
        ax.text(.02, .98, short_label(group), transform=ax.transAxes, va='top', fontsize=8)
        ax.grid(alpha=.18)
    from matplotlib.lines import Line2D
    legend = axes.flat[-1]
    legend.set_axis_off()
    handles = [Line2D([], [], linestyle='none', marker=MARKERS[s], markerfacecolor='none',
                      markeredgecolor=c, label=s) for s, c in colors.items()]
    handles += [Line2D([], [], linestyle='none', marker='+', color='black', label='F1″ at observed loading')]
    legend.legend(handles=handles, loc='center', frameon=False, title='Observed (open) / calculated (+)')
    save(fig, 'pressure')


def render_parity(rows, colors, title, name='pressure-parity', unit='kPa', divisor=1000):
    values = [float(r[k]) / divisor for r in rows for k in ('observed', 'predicted')]
    low, high = min(values) / 1.6, max(values) * 1.6
    fig, ax = plt.subplots(figsize=(7, 6), layout='constrained')
    ax.plot([low, high], [low, high], color='black', lw=.8, label='Equality')
    for source, color in colors.items():
        sub = [r for r in rows if r['source'] == source]
        ax.scatter([float(r['observed']) / divisor for r in sub],
                   [float(r['predicted']) / divisor for r in sub], marker=MARKERS[source],
                   facecolors='none', edgecolors=color, s=24, label=f'{source}: {short_label(sub)}')
    ax.set(xscale='log', yscale='log', xlim=(low, high), ylim=(low, high),
           xlabel=f'Observed ({unit})', ylabel=f'Calculated ({unit})', title=title)
    ax.set_aspect('equal', adjustable='box')
    ax.text(.97, .03, 'All displayed: ' + short_label(rows), transform=ax.transAxes, ha='right', fontsize=8)
    ax.legend(loc='upper left', frameon=False, fontsize=8)
    ax.grid(alpha=.18)
    save(fig, name)


def render_residuals(rows, colors, title, name='pressure-residuals', species=False):
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True, layout='constrained')
    for ax, field, label in zip(axes, ('loading_mol_CO2_per_mol_MEA', 'temperature_C'),
                               ('CO₂ loading (mol/mol MEA)', 'Temperature (°C)')):
        for source, color in colors.items():
            sub = [r for r in rows if r['source'] == source]
            ax.scatter([float(r[field]) for r in sub],
                       [float(r['scaled_residual']) if species else ln_ratio(r) for r in sub],
                       marker=MARKERS[source], facecolors='none', edgecolors=color, s=24, label=source)
        ax.axhline(0, color='black', lw=.8)
        ax.set_xlabel(label)
        ax.grid(alpha=.18)
    axes[0].set_ylabel('(x calculated − x observed)/(0.1 x observed + 0.001)' if species
                       else 'ln(p calculated / p observed)')
    axes[1].legend(frameon=False, fontsize=8)
    fig.suptitle(title)
    save(fig, name)


def model_parts(species):
    return ('MEA', 'MEAH+') if species == 'MEA + MEAH+' else ('HCO3-', 'CO3^2-') if species == HCO3_POOL_LABEL else (species,)


def render_speciation(rows):
    labels = {'MEA': 'MEA', 'MEAH+': 'MEAH⁺', 'MEA + MEAH+': 'MEA + MEAH⁺',
              'MEACOO-': 'MEACOO⁻', 'HCO3-': 'HCO₃⁻ + CO₃²⁻'}
    species_colors = dict(zip(labels, COLORS))
    groups = [('Matin2012', 20)] + [('Bottinger2008', t) for t in (20, 40, 60, 80)]
    fig, axes = plt.subplots(2, 3, figsize=(11, 7), layout='constrained')
    for ax, (source, temperature) in zip(axes.flat, groups):
        group = [r for r in rows if r['source'] == source and round(float(r['temperature_C'])) == temperature]
        for species, color in species_colors.items():
            sub = [r for r in group if r['species'] == species]
            for fitted, marker in ((True, 'o'), (False, 's')):
                obs = [r for r in sub if r['fitted'] == fitted]
                ax.scatter([float(r['loading_mol_CO2_per_mol_MEA']) for r in obs],
                           [float(r['observed']) for r in obs], marker=marker,
                           facecolors='none', edgecolors=color, s=24)
            ax.scatter([float(r['loading_mol_CO2_per_mol_MEA']) for r in sub],
                       [float(r['predicted']) for r in sub], marker='+', color=color, s=24)
        ax.set(title=f'{source} · {temperature} °C', yscale='log',
               xlabel='CO₂ loading (mol/mol MEA)', ylabel='Species / aggregate mole fraction')
        ax.grid(alpha=.18)
    from matplotlib.lines import Line2D
    axes.flat[-1].set_axis_off()
    handles = [Line2D([], [], linestyle='none', marker='o', markerfacecolor='none', markeredgecolor=c, label=labels[s])
               for s, c in species_colors.items()]
    handles += [Line2D([], [], linestyle='none', marker=m, color='black',
                       markerfacecolor='none', label=l) for m, l in
                [('o', 'Observation, fitted'), ('s', 'Observation, not fitted'), ('+', 'F1″ at observed loading')]]
    axes.flat[-1].legend(handles=handles, loc='center', frameon=False)
    save(fig, 'speciation')


def render_pool(rows):
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), layout='constrained')
    ax = axes[0]
    ax.scatter([float(r['loading']) for r in rows], [float(r['observed']) for r in rows],
               marker='s', facecolors='none', edgecolors='#009E73', label='Matin observations')
    ax.scatter([float(r['loading']) for r in rows], [float(r['predicted']) for r in rows],
               marker='+', color='black', label='F1″ pool comparison')
    ax.set(xlabel='CO₂ loading (mol/mol MEA)', ylabel='HCO₃⁻ + CO₃²⁻ mole fraction',
           title='Matin pool · report-only · 20 °C')
    ax.legend(frameon=False)
    axes[1].scatter([float(r['loading']) for r in rows], [float(r['scaled_residual']) for r in rows],
                    marker='s', facecolors='none', edgecolors='#009E73')
    axes[1].axhline(0, color='black', lw=.8)
    axes[1].set(xlabel='CO₂ loading (mol/mol MEA)', ylabel='Scaled species residual',
                title='Excluded from the 94 fitted species targets')
    for ax in axes:
        ax.grid(alpha=.18)
    save(fig, 'matin-pool')


def render_water():
    rows = [r for r in read(WATER) if r['record'] == 'adopted' and r['grid'] != 'atmospheric-controls']
    fig, axes = plt.subplots(1, 3, figsize=(11, 4), layout='constrained')
    for ax, quantity, label in zip(axes, ('cp', 'saturated_liquid_rho', 'psat'),
                                    ('Liquid Cp error (%)', 'Saturated density error (%)', 'Saturation pressure error (%)')):
        for grid, marker, color in [('primary', 'o', COLORS[0]), ('staggered', 's', COLORS[1])]:
            sub = [r for r in rows if r['grid'] == grid]
            ax.scatter([float(r['T_K']) for r in sub], [100 * float(r[quantity + '_error_relative']) for r in sub],
                       marker=marker, facecolors='none', edgecolors=color, s=24, label=grid)
        ax.axhline(0, color='black', lw=.8)
        ax.set(xlabel='Temperature (K)', ylabel=label)
        ax.grid(alpha=.18)
    for limit in (-3, 3):
        axes[0].axhline(limit, color='grey', linestyle='--', lw=.8)
    axes[0].legend(frameon=False)
    axes[0].set_title('Cp at 0.300 MPa; ±3% limit')
    axes[1].set_title('Saturated liquid density')
    axes[2].set_title('Saturation pressure')
    save(fig, 'water-deviations')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    apply_style()
    plt.rcParams.update({'font.family': 'sans-serif', 'font.sans-serif': ['DejaVu Sans']})
    plt.rcParams['svg.hashsalt'] = 'mea-regression-overview'
    qualification = json.loads(QUALIFICATION.read_text())
    assert digest(PARAM) == qualification['inputs']['candidate_record_sha256']
    assert digest(PHYSICAL) == qualification['inputs']['physical_record_sha256']
    selected, physical = (json.loads(path.read_text()) for path in (PARAM, PHYSICAL))
    assert all(value == physical[key] for key, value in selected.items()
               if key not in {'document_id', 'purpose', 'empirical_density_correction'})
    fitted = set(json.loads(NATIVE_FIT.read_text())['targets'])
    pressure, species, pool = ([r for r in read(path) if r['problem'] == 'F1']
                               for path in (PRESSURE, SPECIES_DATA, POOL))
    for row in pressure + species:
        row.update(temperature_C=float(row['temperature_K']) - 273.15,
                   loading_mol_CO2_per_mol_MEA=row['loading'], fitted=row['target'] in fitted)
    assert {r['record_sha256'] for r in pressure + species + pool} == {digest(PHYSICAL)}
    assert [sum(r['fitted'] for r in rows) for rows in (pressure, species)] == [47, 94]
    assert {r['target'] for r in pressure + species if r['fitted']} == fitted
    assert len(positive(pressure + species)) == len(pressure + species)
    pool = [r for r in pool if r['source'] == 'Matin2012' and r['species'] == 'HCO3-']
    assert not any(r['target'] in fitted for r in pool)
    statistics_rows = []
    for family, rows in [('pressure', pressure), ('species', species), ('Matin pool', pool)]:
        statistics_rows.append(ln_statistics(family, 'displayed', 'all', rows))
        if family != 'Matin pool':
            sub = [r for r in rows if r['fitted']]
            statistics_rows.append(ln_statistics(family, 'fitted', 'all', sub))
            assert math.isclose(statistics_rows[-1]['aard_percent'],
                                qualification['cost_by_quantity'][family]['common_wheel_percent'], rel_tol=1e-10)
        statistics_rows += [ln_statistics(family, 'displayed source', s, [r for r in rows if r['source'] == s])
                            for s in sorted({r['source'] for r in rows})]
    with (OUT / 'statistics.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(statistics_rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(statistics_rows)
    for name, rows in [('pressure', pressure), ('speciation', species)]:
        with (OUT / f'{name}.csv').open('w', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator='\n')
            writer.writeheader()
            writer.writerows(rows)
    pressure_colors = source_colors(pressure)
    species_colors = {'Bottinger2008': COLORS[0], 'Matin2012': COLORS[2]}
    MARKERS.update(Bottinger2008='o', Matin2012='s')
    render_isotherms(pressure, pressure_colors, '')
    render_parity(pressure, pressure_colors, 'F1″ pressure · all 79 retained display rows')
    render_residuals(pressure, pressure_colors, 'F1″ pressure · all displayed rows by source')
    strict_species = [r for r in species if not (r['source'] == 'Matin2012' and r['species'] == 'HCO3-')]
    render_parity(strict_species, species_colors, 'F1″ species · Matin pool shown separately',
                  'species-parity', 'mole fraction / aggregate', 1)
    render_residuals(strict_species, species_colors, 'F1″ species · Matin pool shown separately',
                     'species-residuals', species=True)
    render_speciation(species)
    render_pool(pool)
    render_water()
    inputs = [PRESSURE, SPECIES_DATA, POOL, WATER, DATA / 'run-summary.json', PARAM, PHYSICAL, NATIVE_FIT, QUALIFICATION,
              Path(__file__), Path(__file__).with_name('manuscript_style.py')]
    (OUT / 'provenance.json').write_text(json.dumps({
        'inputs': {str(p.relative_to(ROOT)): digest(p) for p in inputs},
        'fit_figure_wheel_sha256': json.loads((DATA / 'run-summary.json').read_text())['wheel_sha256'],
        'current_wheel_qualification': qualification['engine'], 'model_executed': False,
        'series': 'Observed values are open points; model values are + markers at observed loadings. No model curves. Pressure CSV units: Pa; pressure axes: kPa. Matin HCO3- denotes the HCO3- + CO3^2- observation pool, excluded from F1 fitting.',
        'outputs': {p.name: digest(p) for p in sorted(OUT.iterdir())
                    if p.suffix in ('.csv', '.svg', '.pdf') and not p.name.startswith('heat')}
    }, indent=2) + '\n')
    for row in statistics_rows:
        print(f"{row['family']} · {row['group_type']} · {row['group']}: "
              f"n={row['evaluated_positive']}; AARD={row['aard_percent']:.6f}%")


if __name__ == '__main__':
    main()
