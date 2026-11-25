"""Join retained observation, calibration, and phase-search records for issue #434."""
from collections import Counter, defaultdict
import csv
from time import monotonic
import math

from amp import Q7
from common import ROOT, fingerprints, save
from objective import BOUNDED, OBJECTIVES
from part_ii import deviation_statistics, stable

BUNDLE = OBJECTIVES.parents[1]
CASE421 = BOUNDED.parent / 'phase-search-421'
ROUND3 = ROOT / 'analyses/round_3/results'


def read_csv(path):
    with path.open() as stream:
        return list(csv.DictReader(stream))


def heat_capacity():
    start = monotonic()
    fit_path = OBJECTIVES / 'MEA/information.json.gz'
    source_path = BUNDLE / 'heat-capacity-264/sources.csv'
    newer = BUNDLE / 'results/adoption-297/paper-evidence/heat-capacity-264.json'
    older = BUNDLE / 'results/same-data-comparison/part1/published/heat-capacity-264.json'
    fitted = [r for r in stable.read(fit_path)['result']['rows'] if r['group'] == 'Cp']
    assert len(fitted) == 4
    source = [r for r in read_csv(source_path) if r['source'] == 'Hilliard2008' and r['role'] == 'probe-fit']
    source_by_basis = {(float(r['T_K']), float(r['loading']), float(r['cp_kJ_kg_K'])): r for r in source}
    assert len(source_by_basis) == len(source) == 51
    matched, versions, duplicates = {}, {}, {}
    for label, path in (('published', older), ('current', newer)):
        broad = [r for r in stable.read(path)['rows'] if r['group'] == 'broad Cp']
        duplicates[label] = [key for key, n in Counter(r['identity'] for r in broad).items() if n > 1]
        assert len(broad) == 51
        ids = {}
        for r in broad:
            source_row = source_by_basis[r['T_K'], r['loading'], r['observed_kJ_kg_K']]
            ids[r['T_K'], r['loading'], r['observed_kJ_kg_K']] = r['identity']
            r.update(stock_molality=float(source_row['MEA_molality']), source_locator=source_row['locator'], unit='kJ/(kg K)')
        versions[label] = broad
        matched[label] = {r['identity']: ids[r['row']['T_K'], r['row']['source_loading'], r['row']['source_observed_kJ_kg_K']]
                          for r in fitted}
    assert matched['published'] == matched['current'] and not any(duplicates.values())
    save('records/Hilliard-Cp.json', dict(fitted=fitted, broad=versions, intersection=matched, duplicate_IDs=duplicates,
         current_broad_roles=dict(fitted=len(matched['current']), outside=len(source)-len(matched['current'])),
         S7_printed_fit_count=2, inputs=fingerprints(fit_path, source_path, newer, older)), start=start)


def pressure_sources():
    start = monotonic()
    pairs = BUNDLE / 'results/stripper-temperature-409/points.csv'
    band_file = pairs.with_name('band-table.csv')
    data, ref = read_csv(pairs), read_csv(band_file)
    bands = {}
    for band, expected in (('absorber', 69), ('stripper', 66)):
        rows = [dict(r, csv_line=i) for i, r in enumerate(data, 2) if (r['property'],r['role'],r['band']) == ('CO2 partial pressure','not fitted',band)]
        stats = deviation_statistics([(float(r['observed']), float(r['predicted'])) for r in rows], 'Pa')
        target, = [r for r in ref if (r['property'],r['role'],r['band'],r['cohort']) ==
                   ('CO2 partial pressure','not fitted',band,'all')]
        assert len(rows) == expected == int(target['n'])
        assert math.isclose(stats['AARD_percent'], float(target['AARD_percent']), rel_tol=1e-12)
        assert math.isclose(stats['bias_percent'], float(target['mean_signed_relative_percent']), rel_tol=1e-12)
        bands[band] = dict(rows=rows, statistics=stats, displayed_AARD=f"{stats['AARD_percent']:.2f}")
    assert not {r['csv_line'] for r in bands['absorber']['rows']} & {r['csv_line'] for r in bands['stripper']['rows']}
    save('records/S8-pressure-bands.json', dict(bands=bands, inputs=fingerprints(pairs, band_file)), start=start)

    start = monotonic()
    models = {'reported': BOUNDED / 'data-rows.json'}
    models.update({p.parent.name.split('-')[1]: p for p in (BOUNDED.parent / 'shared-bicarbonate-417/mdea').glob('*/data-rows.json.gz')})
    out = {}
    for name, path in models.items():
        rows = [r for r in stable.read(path) if r['group'] in ('Ermatchkov','Xiao')]
        groups = defaultdict(list)
        for r in rows:
            groups[r['group'], r['T_K']].append(r)
            groups[r['group'], None].append(r)
        stats = {}
        for (source, T), rr in groups.items():
            available = [r for r in rr if r['status'] == 'Available']
            differences = deviation_statistics([(r['observed'], r['value']) for r in available], 'Pa') if available else {}
            stats[source, T] = dict(source=source, T_K=T, total=len(rr), **differences,
                                    missing=[r['identity'] for r in rr if r not in available],
                                    worst=max(available, key=lambda r: abs(r['value']/r['observed']-1), default=None))
        assert (stats['Ermatchkov', None]['total'], stats['Xiao', None]['total']) == (101, 20)
        common = [r for r in rows if r['status'] == 'Available']
        overall = deviation_statistics([(r['observed'], r['value']) for r in common], 'Pa')
        summed = math.fsum(stats[g,None]['AARD_percent']*stats[g,None]['rows'] for g in ('Ermatchkov','Xiao'))/len(common)
        assert math.isclose(overall['AARD_percent'], summed, rel_tol=1e-12)
        out[name] = dict(rows=rows, source_and_isotherm=list(stats.values()), combined=overall, count_weighted_AARD=summed)
    save('C/partial-pressures.json.gz', dict(endpoints=out, inputs=fingerprints(*models.values())), start=start)


def mdea_records():
    start = monotonic()
    q8_path = ROUND3 / 'q8.json'
    kuranov = BOUNDED.parent / 'kuranov-published-422/kuranov-rows.json'
    historical = BOUNDED.parent / 'refit-298/README.md'
    q8 = stable.read(q8_path)
    rows = [r for r in stable.read(kuranov) if r['source_row'] in (28, 72)]
    assert len(rows) == 2 and rows[1] == q8['kuranov']['added_row']
    save('records/Kuranov-R2.json', dict(historical_selector_upper_K=393.15, measured_MDEA_dissociation_upper_K=368.,
         rows=[dict(r, over_historical_R2_limit_K=round(r['T']-393.15,2)) for r in rows],
         inputs=fingerprints(q8_path, kuranov, historical)), start=start)

    start = monotonic()
    coverage, measured, observation, errors, data = [CASE421 / f'{n}.json' for n in
        ('coverage','measured-phase','observation-crosswalk','property-deviations','coverage-counts')]
    observation_rows = {r['identity']: r for r in stable.read(BOUNDED / 'data-rows.json')}
    failures = [dict(r, fitted_status=observation_rows.get(r.get('observation'), {}).get('role')) for r in stable.read(coverage) if not r['complete']]
    expected = {(r['tier'],r['stage']): r['count'] for r in stable.read(data)['stages']}
    found = Counter((r['tier'],r['stage']) for r in failures)
    assert found == expected and len(failures) == 1099
    crosswalk = defaultdict(list)
    for r in stable.read(observation):
        crosswalk[r['canonical']].append(r)
    states = []
    for r in stable.read(measured):
        p = r['pressure_basis']
        p_bubble = p.get('model_bubble_pressure_Pa')
        P = p.get('search_pressure_Pa')
        linked = crosswalk[r['key']]
        source_pressures = {float(o['observation']['row']['pressure_MPa'])*1e6 for o in linked
                            if o['observation']['row'].get('pressure_MPa') is not None}
        states.append(dict(r, assigned_or_imposed_Pa=P, source_pressures_Pa=sorted(source_pressures),
                           pressure_deficit_Pa=p_bubble-P if P is not None and p_bubble is not None else None,
                           source_pressure_explicit=bool(source_pressures), linked_observations=linked))
    assert len(states) == 27 == len({r['key'] for r in states})
    save('records/MDEA-coverage.json.gz', dict(incomplete_record_count=len(failures), records=failures, distinct_keys=len({r['key'] for r in failures}),
         groups=[dict(tier=t, stage=s, count=n) for (t,s), n in found.items()], property_states=states,
         property_errors=stable.read(errors), Q8= q8['phase_counts'],
         inputs=fingerprints(coverage, measured, observation, errors, data, q8_path, BOUNDED / 'data-rows.json')), start=start)


def native_attribution():
    start = monotonic()
    summary = Q7.with_name('q7-summary.json')
    records = stable.read(Q7)
    assert len(records) == 666
    fields = ('key','outcome','value','uncertainty','native_branch','witnesses','archived_search_Pa','pressure_matched','same_calculation_as')
    save('records/AMP-native-starts.json.gz', dict(states=[{k:r.get(k) for k in fields} for r in records], summary=stable.read(summary),
         missing='Q7 compact rows retain descending witnesses without native per-start initial iterates or counts. A public trial replay is required for visible trial identities.',
         inputs=fingerprints(Q7, summary)), start=start)


if __name__ == '__main__':
    heat_capacity()
    pressure_sources()
    mdea_records()
    native_attribution()
