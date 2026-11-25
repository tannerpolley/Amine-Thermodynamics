"""Profile the AMP slope under the original and expanded pressure declarations."""
from pathlib import Path
from tempfile import TemporaryDirectory
from time import monotonic

from amp import DECLARATION, ENDPOINTS, ExpandedPressure, SLOPE, fixed_slope
from common import RESULTS, fingerprints, save
from objective import information
from part_ii import Route, stable

PROFILE_ARCHIVE = ENDPOINTS / 'diagnosis/f2-scan.json'
TARGET_INCREMENT = 3.84146


def calculate(work, design, *, endpoint=None, retain=save, extra_slopes=()):
    started = monotonic()
    if design == 'expanded':
        source = endpoint or RESULTS / 'A/expanded-free.json.gz'
        archived = stable.read(source)
        point = archived['point'] if endpoint is None else archived['selected'][2]
        route = ExpandedPressure(DECLARATION, work)
    else:
        source = ENDPOINTS / 'main/parameters.json'
        point = stable.read(source)
        route = Route(DECLARATION, work)
    lower, upper = next(q['bounds'] for q in point['coordinates'] if q['identity'] == 'AMPH-water-slope')
    center = stable.s.parameter_values(point['parameters'])[SLOPE]
    info = information(route, point)
    base = info['objective']
    delta = .5 * info['stage_variance'] * TARGET_INCREMENT
    data = dict(design=design, center=center, minimum=base, stage_variance=info['stage_variance'],
                delta_cutoff=delta, points={}, brackets={}, projection_minutes=[6, 15],
                inputs=fingerprints(source, PROFILE_ARCHIVE, DECLARATION))
    retain(f'A/profile-{design}-information.json.gz', info)
    knots = {float(k): v for k, v in stable.read(PROFILE_ARCHIVE).items()}
    scheduled = {k for k in (*knots, *extra_slopes) if lower <= k <= upper}
    data['outside_bounds'] = sorted(set(extra_slopes)-scheduled)
    seeds = {center: point}
    points = data['points']
    elapsed = []
    retain(f'A/profile-{design}.json', data, start=started)

    def evaluate(slope):
        if slope in points:
            return points[slope]['cost']
        tick = monotonic()
        seed = min(seeds, key=lambda k: abs(k - slope))
        pc = seeds[seed]
        # The unrestricted endpoint defines the free-coordinate list at every fixed slope.
        if seed != center:
            q = next(q for q in point['coordinates'] if q['identity'] == 'AMPH-water-slope')
            pc = dict(pc, coordinates=[*pc['coordinates'], dict(q, origin=seed)])
        trial_point = fixed_slope(pc, slope)
        name = f'profile-{design}-{slope:g}'
        report = stable.stage_fit(name, 0, None, trial_point, {}, [], route=route)
        endpoint = route.out / name / 'stage-0/parameters.json'
        mapping = stable.read(endpoint) if endpoint.is_file() else None
        cost = report.get('endpoint_replay_cost')
        usable = cost is not None and report['status'] == 'converged'
        if usable:
            seeds[slope] = mapping
        elapsed.append(monotonic() - tick)
        retain(f'A/{name}.json.gz', dict(point=mapping, report=report, seed_slope_K=seed, starting_point=trial_point,
             replay=route.result(f'{name}/stage-0/replay.json') if mapping else None), start=tick)
        points[slope] = dict(cost=cost if usable else None, status=report['status'], seconds=elapsed[-1],
                             increase=cost-base if cost is not None else None, record=f'{name}.json.gz')
        retain(f'A/profile-{design}.json', data, start=started)
        return points[slope]['cost']

    if design == 'original':
        for slope, entry in knots.items():
            points[slope] = dict(cost=entry['fit']['cost'], increase=entry['fit']['cost'] - base, record=str(PROFILE_ARCHIVE.relative_to(RESULTS.parents[2])))
    else:
        for slope in sorted(scheduled, key=lambda k: abs(k-center)):
            if len(elapsed) >= 2 and (monotonic()-started + max(elapsed) * (len(scheduled)-len(elapsed)+2)) >= 1800:
                data['stop'] = 'Adjacent conditional fits projected over twice the profile allowance'
                break
            evaluate(slope)
        # Removing the slope coordinate at the unrestricted optimum holds the fitted value exactly.
        points[center] = dict(cost=base, increase=0., record=source.name)
    for direction, limit in ((-1, lower), (1, upper)):
        this_side = sorted(((k, v['cost']) for k, v in points.items() if (k-center)*direction > 0 and v['cost'] is not None),
                           key=lambda p: abs(p[0] - center))
        inside = center
        outside = None
        for k, cost in this_side:
            if cost - base > delta:
                outside = k
                break
            inside = k
        while not data.get('stop') and (outside is None or abs(inside-outside) > .5):
            if monotonic()-started + max(elapsed, default=1) >= 1800:
                data['stop'] = 'Profile elapsed time plus a timed conditional fit reached twice the 15-minute upper projection'
                break
            if outside is None and inside == limit:
                break
            candidate = ((inside+outside)/2 if outside is not None else
                         center + direction*min(abs(limit-center), max(25., 2*abs(inside-center))))
            cost = evaluate(candidate)
            if cost is None:
                break
            if cost - base > delta:
                outside = candidate
            else:
                inside = candidate
        data['brackets'][str(direction)] = dict(within=inside, beyond=outside, closed=outside is not None and abs(inside-outside) <= .5)
        retain(f'A/profile-{design}.json', data, start=started)


if __name__ == '__main__':
    import sys

    with TemporaryDirectory() as directory:
        calculate(Path(directory), sys.argv[1])
