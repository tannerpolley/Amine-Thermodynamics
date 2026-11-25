"""Recover public optimized trial identities from a deterministic Q7 replay."""
from pathlib import Path
from tempfile import TemporaryDirectory
from time import monotonic

from amp import DECLARATION, ENDPOINTS, Q7
from amp_stability import bank_hash
from common import RESULTS, fingerprints, save
from part_ii import Route, stable
from refit_404 import TRIAL_SHA, trial_bank


class TrialAttribution(Route):
    short_rows = True

    def branch_counts(self, row):
        branches = super().branch_counts(row)
        trials = row.get('supplied_trials', [])
        excluded = {tuple(t['support']) for t in row.get('not_applicable_supplied_trials', [])}
        key = frozenset(excluded)
        if key not in self.applicable_ids:
            self.applicable_ids[key] = [i for i,t in enumerate(self.bank) if tuple(t['support']) not in excluded]
        indices = self.applicable_ids[key]
        if len(trials) != len(indices):
            return dict(branches, supplied_attribution=dict(attempted=len(indices), returned=len(trials),
                        refusal=row.get('supplied_error','No ordered trial results available')))
        evaluated = [(i,t) for i,t in zip(indices,trials,strict=True) if t['evidence']=='evaluated']
        descending = [(i,t) for i,t in evaluated if stable.supplied_negative(t)]
        first = next(iter(descending),None)
        least = min(evaluated,key=lambda t:t[1]['quantities']['tpd_over_rt'],default=None)
        def describe(candidate):
            if candidate is None:
                return None
            i, trial = candidate
            return dict(bank_index=i, initial=self.bank[i], evaluated=trial)
        return dict(branches, supplied_attribution=dict(attempted=len(indices), returned=len(trials),
                    evaluated=len(evaluated), descending_bank_indices=[i for i,_ in descending],
                    first_descending=describe(first), least_tpd=describe(least)))


def calculate(work):
    started = monotonic()
    path = ENDPOINTS/'main/parameters.json'
    route = TrialAttribution(DECLARATION,work)
    bank = trial_bank(route)
    assert bank_hash(bank)==TRIAL_SHA
    route.bank = bank['trials']
    route.applicable_ids = {}
    point = stable.read(path)
    spec = route.bind(point)
    archive = {r['key']: r for r in stable.read(Q7)}
    states = route.states(spec)
    assert archive.keys() == {s['key'] for s in states}
    duplicates = route.same_calculations(point, states)
    canonical = [s for s in states if s['key'] not in duplicates]
    replay = stable.grid(point, canonical, route.bank, route=route, capture=True)
    by_key = {r['key']:r for r in replay}
    out = []
    for state in states:
        key = state['key']
        row = by_key[duplicates.get(key, key)]
        optimized = row.get('optimized_trials', [])
        descents = [t for t in optimized if t['resolved_descent']]
        measured_tpd = [t for t in optimized if t['evidence'] in ('evaluated', 'no_resolved_descent') and 'tpd_over_rt' in t['quantities']]
        least = min(measured_tpd, key=lambda t:t['quantities']['tpd_over_rt'], default=None)
        out.append(dict(row,key=key,same_calculation_as=duplicates.get(key), attempted_public_trials=len(optimized),
                        converged_public_trials=sum(t['optimizer_success'] for t in optimized),
                        descending_public_trials=[t['seed'] for t in descents],
                        first_public_descending_trial=descents[0]['seed'] if descents else None,
                        least_public_trial=least,
                        archived_descent=archive[key]['outcome']=='resolved descent',
                        has_descent=bool(descents)))
    overlap = {name:sum((r['has_descent'], r['supplied_branch'] in ('liquid','vapor','mixed','unresolved'))==values for r in out)
               for name,values in [('both',(True,True)),('native_only',(True,False)),
                                   ('supplied_only',(False,True)),('neither',(False,False))]}
    bank_record = RESULTS/'A/search-free-supplied-full-final-bank.json.gz'
    save('records/AMP-public-trials.json.gz', dict(rows=out, original_states=len(states), distinct_calculations=len(canonical),
         archive_descents=sum(r['archived_descent'] for r in out), replay_descents=sum(r['has_descent'] for r in out),
         native_supplied_overlap=overlap, supplied_bank_sha256=TRIAL_SHA,
         supplied_bank_record=bank_record.relative_to(RESULTS).as_posix(),
         changed=[r['key'] for r in out if r['archived_descent'] != r['has_descent']],
         no_public_trace='Internal optimizer initial iterates and their order are unavailable in 1.3.1. Returned trial seed labels and converged compositions are retained.',
         inputs=fingerprints(path,Q7,DECLARATION,bank_record)), start=started)


if __name__ == '__main__':
    with TemporaryDirectory() as directory:
        calculate(Path(directory))
