"""Retained source populations and reductions for the round-7 comparisons."""
import csv
from collections import Counter, defaultdict
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
CANONICAL_VLE = ROOT/'data/reference/MEA/observations/vapor_liquid_equilibrium/Canonical_VLE_Observations.csv'
MDEA_RESULTS = ROOT/'analyses/mdea_mea_workflow/results'
MDEA_SALT = MDEA_RESULTS/'salt-anchored-435/campaign'

sys.path.insert(0, str(ROOT/'src'))
from MEA.common.deviation_statistics import deviation_statistics  # noqa: E402


def off_window_population():
    with CANONICAL_VLE.open(newline='') as stream:
        rows = [q for q in csv.DictReader(stream) if q['CO2_pressure'] and q['MEA_weight_fraction']
                and q['temperature_reported_C'] and (
            (q['source_key']=='Jou1995' and float(q['temperature_reported_C'])<40 and float(q['MEA_weight_fraction'])==.30)
            or (q['source_key']=='Aronu2011' and float(q['MEA_weight_fraction']) in (.15,.45)))]
    assert Counter(q['source_key'] for q in rows)=={'Jou1995':14,'Aronu2011':70}, 'Off-window MEA source population changed'
    assert len({q['observation_id'] for q in rows})==len(rows)
    assert len({(q['source_file'],q['source_row']) for q in rows})==len(rows)
    return rows


def mdea_deviations(observations, joins):
    groups = defaultdict(list)
    for row in observations:
        groups[row['group'],row['role'],row['unit']].append(row)
    reductions = []
    for (group,role,unit), rows in sorted(groups.items(),key=lambda item:str(item[0])):
        fixed = {q['identity']: [t for t in joins.get(q['identity'],[]) if t['historical']['bubble_multiplier'] is None]
                 for q in rows}
        eligible = {identity: [t for t in attempts if t['completed_without_descent'] and t['below_bubble_salt'] is False]
                    for identity,attempts in fixed.items()}
        admitted = [q for q in rows if eligible[q['identity']]]
        reduction = dict(group=group,role=role,unit=unit,
                         admitted_observations=[q['identity'] for q in admitted],
                         fixed_pressure_search_attempts=sum(map(len,fixed.values())),
                         admitted_search_attempts=sum(map(len,eligible.values())))
        for label,pool in (('all',rows),('resolved_fixed_pressure_subset',admitted)):
            pairs = [(x['observed'],x['value']) for x in pool if x['status']=='Available' and x.get('requested_tolerance_met')]
            reduction[label] = dict(attempted=len(pool),available=len(pairs),
                                    scores=deviation_statistics(pairs,unit) if pairs else None)
        reductions.append(reduction)
    return reductions


def kuranov_82(observations, extra, source):
    rows = [q for q in observations if q['group'] in ('Kuranov', 'Kuranov-binary', 'Kuranov-413K')]
    assert sorted(int(q['row']['source_row']) for q in rows) == source['matched_rows']
    assert (int(extra['row']['source_row']), extra['observed']) == (72, source['row']['p_exp'])
    available = [q for q in [*rows, extra] if q['status']=='Available' and q['requested_tolerance_met']]
    assert all(q['unit']=='Pa' for q in available)
    stats = deviation_statistics([(q['observed'], q['value']) for q in available], 'Pa')
    return dict(available=len(available), AARD_percent=stats['AARD_percent'] if len(available)==82 else None)
