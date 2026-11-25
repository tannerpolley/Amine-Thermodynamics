"""Inventory #435 evidence and pinned manuscript occurrences, without solving."""
import argparse
from collections import Counter
import csv
import gzip
import hashlib
from io import StringIO
import json
import os
from pathlib import Path
import posixpath
import re

ROOT = Path(__file__).resolve().parents[3]
ME = Path('analyses/mea_parameter_bundle/results/salt-anchored-435')
LATEX = 'docs/scientific/latex'
STORY = '75c3ee525d9068a37197bbb1e915990f7a87b59a'
ROUND5 = '804811e44eadfb04f1e3a51a6be0a46a4c54ba00'
BASE = '50cbeaf006aa378ae212986c29caf1de9c1d42a5'
LITERAL = re.compile(r'(?<![A-Za-z0-9])[-+−]?(?:\d+\.\d+|\.\d+|\d+)(?:[eE]([-+]?\d+))?(?![A-Za-z0-9])')
INCLUDE = re.compile(r'\\(?:input|include)\s*\{([^{}]+)\}')
NON_TEXT = re.compile(r'\\(?:cite\w*|ref|eqref|label|includegraphics)(?:\[[^\]]*\])?\{[^{}]+\}')
UNIT = re.compile(r'(?:\s|\\,|~|\$)*(\\%|%|MPa|kPa|Pa|K|mol/kg|kg/m³|kJ/mol)(?=\W|$)')
REFERENCE = {'reaction_equilibrium_constants.tex', 'supplement_reaction_coefficients.tex'}
HISTORICAL = {'mdea-shared-control.tex', 'dea-binary-tradeoff.tex', 'choice_cost.tex'}
SOURCE_SNAPSHOTS = {'429': (STORY, f'{LATEX}/builds/429-story-pass-number-sources.md'),
                    '434': (ROUND5, 'analyses/round_5/manuscript-handoff.md')}


def pinned_sources(commit):
    return load(ME/'pinned-manuscript-sources.json.gz')[commit]


def snapshot():
    available = pinned_sources(STORY)
    roots = ('main.tex', 'supplement.tex', 'submission/graphical_abstract.tex',
             'submission/cover_letter.md', 'submission/highlights.txt', 'submission/chemrxiv.md')
    closure, missing = {}, []
    for entry in roots:
        pending, seen = [f'{LATEX}/{entry}'], set()
        while pending:
            path = pending.pop()
            if path in seen:
                continue
            seen.add(path)
            if path not in available:
                missing.append((entry, path))
                continue
            doc = closure.setdefault(path, [available[path], []])
            doc[1].append(entry)
            for child in INCLUDE.findall(active_text(doc[0])):
                child = posixpath.normpath(f'{LATEX}/{child}')
                pending.append(child if child.endswith('.tex') else child+'.tex')
    return closure, missing


def active_text(content):
    return '\n'.join(re.split(r'(?<!\\)%', line, maxsplit=1)[0] for line in content.splitlines())


def occurrences(closure):
    buf = StringIO()
    writer = csv.writer(buf, lineterminator='\n')
    writer.writerow(('revision', 'entry_points', 'file', 'line', 'column', 'section_or_table',
                     'printed_token', 'printed_decimal_places', 'local_unit', 'old_source',
                     'new_source_or_disposition', 'printed_context'))
    counts = Counter()
    for path, (content, entries) in sorted(closure.items()):
        name = Path(path).name
        section = name
        for i, line in enumerate((active_text(content) if path.endswith('.tex') else content).splitlines(), 1):
            if re.search(r'\\(?:sub)*section\{|\\caption\{|^#+ ', line):
                section = line.strip()
            if INCLUDE.search(line):
                continue
            stripped = NON_TEXT.sub(lambda m: ' '*len(m[0]), line)
            for match in LITERAL.finditer(stripped):
                state = 'reference source law' if name in REFERENCE else 'historical endpoint' if name in HISTORICAL else 'unresolved'
                mantissa = re.split('[eE]', match[0])[0]
                unit = UNIT.match(line[match.end():])
                writer.writerow((STORY, ' / '.join(entries), path, i, match.start()+1, section, match[0],
                                 len(mantissa.partition('.')[2]), unit[1] if unit else '',
                                 f'{STORY}:{path}:{i}', state, line.strip()))
                counts[state] += 1
    return buf.getvalue(), counts


def load(path):
    path = ROOT / path
    if not path.is_file():
        return None
    return json.loads(gzip.decompress(path.read_bytes()) if path.suffix == '.gz' else path.read_bytes())


def link(path, field=''):
    name = os.path.relpath(path, ME)
    return f'[{Path(path).name}]({name})' + (f' `{field}`' if field else '')


def ledger(lines):
    for issue, (revision, path) in SOURCE_SNAPSHOTS.items():
        source = pinned_sources(revision)[path]
        selected = [i for i, line in enumerate(source.splitlines(), 1)
                    if line.startswith('| ') and not line.startswith('| ---')]
        url = f'https://github.com/tannerpolley/Amine-Thermodynamics/blob/{revision}/{path}'
        lines += [f'## Pinned #{issue} ledger', '',
                  'Each source row below retains its printed value, source field and stated check. '
                  'Results from the original declarations remain historical. '
                  'Occurrences that still need a current-model replacement are open in the occurrence inventory.', '',
                  '| Source row | Pinned content |', '| --- | --- |']
        for i in selected:
            line = source.splitlines()[i-1].strip('| ').replace('|', '&#124;')
            lines.append(f'| [{i}]({url}#L{i}) | {line} |')
        lines.append('')


def render(closure, missing, counts):
    lines = ['# Salt-anchored parameter handoff', '',
             'Issue #435. This inventory records numerical evidence and open manuscript replacements. '
             'Parameter promotion requires delivered-evidence review.', '',
             f'TeX source revision `{STORY}`; Round 5 source revision `{ROUND5}`; post-#434 implementation base `{BASE}`.', '',
             '## Calculations', '', '| Quantity | Value | Source |', '| --- | --- | --- |']
    p = ME / 'salt/summary.json'
    salt = load(p)['result']
    for name, score in salt['scores'].items():
        lines.append(f"| {name} osmotic coefficient AARD | {score['aard_percent']:.8g}% on {score['n']} available rows | {link(p, 'result.scores.'+name)} |")
    for name, law in salt['laws'].items():
        lines.append(f"| Water–{name} $k(T)$ | $a_0={law['a0']:.16g}$ at {law['t_ref']} K, $a_1={law['a1']:.16g}$ K⁻¹ | {link(p, 'result.laws.'+name)} |")
    for label in ('F2-control', 'F2', 'F4'):
        p = ME / f'MEA/{label}' / ('replay.json' if label == 'F2-control' else 'fit-summary.json')
        if fit := load(p):
            lines.append(f"| MEA {label} cost | {fit['cost']!r} | {link(p, 'cost')} |")
        p = ME / f'MEA/{label}/search-summary.json'
        if record := load(p):
            for family in ('grid', 'offset', 'census'):
                s = record[family]
                count = s.get('available', s['states']-s.get('incomplete', 0))
                lines.append(f"| MEA {label} {family} | {count}/{s['states']} available, {s['descent']} descents | {link(p, family)} |")
    outputs = {'MEA': ME / 'MEA/selection.json',
               'DEA': Path('analyses/dea_transfer/results/salt-anchored-435/campaign/selection.json.gz'),
               'MDEA': Path('analyses/mdea_mea_workflow/results/salt-anchored-435/campaign/selection.json.gz'),
               **{f'AMP {family}': Path(f'analyses/amp_transfer/results/salt-anchored-435/{family}/selection.json.gz')
                  for family in ('free', 'fixed')}}
    for model, p in outputs.items():
        record = load(p)
        choice = record.get('chosen', record) if record else None
        state = repr(choice['cost']) if choice else 'Unresolved'
        lines.append(f"| {model} selected objective | {state} | {link(p) if record else 'No selected endpoint record'} |")
    if (selection := load(outputs['MEA'])) and (point := selection['chosen']):
        p = ME / f"MEA/{point['label']}/fit-summary.json"
        for group, metric in point['metrics'].items():
            lines.append(f"| MEA {group} | {metric['aard_percent']:.6g}% AARD on {metric['n']} fitted rows | {link(p, 'metrics.'+group)} |")
        p = p.with_name('reference-state.json')
        if state := load(p):
            lines.append(f"| MEA reference addition heat | {state['heat_kJ_mol']:.8g} kJ/mol CO₂ at {state['T_K']} K"
                         f" and {state['P_Pa']/1e6:.4g} MPa | {link(p, 'heat_kJ_mol')} |")
    lines += ['', '### Computation time', '', '| Step | Projection (s) | Elapsed (s) | Source |', '| --- | --- | --- | --- |']
    for p in sorted((ROOT / ME / 'MEA').glob('*/*-timing.json')):
        record = load(p)
        lines.append(f"| {p.parent.name} {p.stem.removesuffix('-timing')} | {record.get('projection_s', '—')} | "
                     f"{record.get('elapsed_s', '—')} | {link(p.relative_to(ROOT))} |")
    for p in sorted((ROOT / ME).glob('*-runtime.json')):
        record = load(p)
        elapsed = record.get('elapsed_s', record.get('seconds'))
        lines.append(f"| {p.stem.removesuffix('-runtime')} | {record['projection_s']} | {elapsed:.3f} "
                     f"(exit {record['returncode']}) | {link(p.relative_to(ROOT))} |")
    for model, p in outputs.items():
        case = model.split()[0]
        for name in ('deviations.json.gz', f'{case}/information.json.gz', f'{case}/contributions.csv.gz',
                     'search-outcome.json.gz', 'native/search-outcome.json.gz', 'supplied/search-outcome.json.gz'):
            candidate = p.parent / name
            if (ROOT / candidate).is_file():
                lines.append(f'\n{model} {link(candidate)}')
    lines += ['\n### Matched observations and worked states', '']
    evidence = [ME/'receiver-law-verification.json', ME/'MEA/hong-matched-pressure.json',
                ME/'MEA/baygi-matched-pressure.json', ME/'MEA/F4/reference-state.json',
                ME/'MEA/evidence/F4/retained-raw-files.json', ME/'MEA/controls/readback.json']
    for owner in ('dea_transfer', 'mdea_mea_workflow', 'amp_transfer'):
        directory = Path('analyses') / owner / 'results/salt-anchored-435'
        for pattern in ('matched-deviations-*.json', 'kuranov-matched-pressure.json.gz', 'common-pressure.json',
                        'hydrolysis/shift.json', 'campaign/fixed-pressure.json.gz'):
            evidence.extend(p.relative_to(ROOT) for p in sorted((ROOT/directory).glob(pattern)))
    lines += [f'- {link(p)}' for p in evidence if (ROOT/p).is_file()]
    lines += ['', '## Manuscript occurrence inventory', '',
              f"{len(closure)} source files in the input closure. The [occurrence ledger](number-occurrences.csv) "
              'records the printed token and locator, with current-model replacements left unresolved wherever support is incomplete.', '',
              *[f'- {disposition}: {n} source occurrences.' for disposition, n in sorted(counts.items())],
              *[f'- Missing include from {entry}: `{path}`.' for entry, path in missing], '',
              'The ledger covers source tokens. Rendered numbering, macro expansion and display readback still require reconciliation.', '',
              '### Retained point and declaration hashes', '', '| File | SHA-256 |', '| --- | --- |']
    point_files = sorted({p for output in outputs.values() for location in (output.parent, output.parent.parent)
                          for p in (ROOT/location).glob('curve-data.json*')})
    point_files += sorted((ROOT/ME/'MEA/evidence').glob('*/model-curves/*.csv'))
    for p in (*outputs.values(), *point_files, ME/'pinned-manuscript-sources.json.gz'):
        path = ROOT/p
        if path.is_file():
            lines.append(f"| {link(path.relative_to(ROOT))} | `{hashlib.sha256(path.read_bytes()).hexdigest()}` |")
    lines.append('')
    ledger(lines)
    return '\n'.join(lines)


def main(check):
    closure, missing = snapshot()
    content, counts = occurrences(closure)
    handoff = render(closure, missing, counts)
    notebook = handoff.split('## Calculations\n', 1)[1].split('## Manuscript occurrence inventory', 1)[0]
    notebook = re.sub(r'\]\(([^)]+)\)',
                      lambda m: '](' + posixpath.normpath('results/salt-anchored-435/' + m[1]) + ')', notebook)
    paths = [('number-occurrences.csv', content), ('manuscript-handoff.md', handoff), ('calculation-summary.md', notebook.rstrip()+'\n')]
    for name, value in paths:
        path = ROOT/ME/name
        if check:
            if path.read_bytes() != value.encode():
                raise SystemExit(f'{path} is stale')
        else:
            path.write_bytes(value.encode())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    main(parser.parse_args().check)
