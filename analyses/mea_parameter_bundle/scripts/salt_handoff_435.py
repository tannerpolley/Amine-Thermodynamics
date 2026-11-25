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

from salt_publication_435 import (EXCLUDED, OPEN, RETAINED, figure_quantities, prose_quantity,
                                  publication_readback, table_quantity)

ROOT = Path(__file__).resolve().parents[3]
ME = Path('analyses/mea_parameter_bundle/results/salt-anchored-435')
LATEX = 'docs/scientific/latex'
STORY = '75c3ee525d9068a37197bbb1e915990f7a87b59a'
ROUND5 = '804811e44eadfb04f1e3a51a6be0a46a4c54ba00'
BASE = '50cbeaf006aa378ae212986c29caf1de9c1d42a5'
# A scientific-notation mantissa, base and exponent are one displayed value.
LITERAL = re.compile(
    r'(?<![\w.])[-+−]?(?:10\^\{[-+]?\d+\}|[eE][-+]?\d+|'
    r'(?:\d{1,3}(?:,\d{3})+|\d+|\.\d+)(?:\.\d+)?'
    r'(?:[eE][-+]?\d+|\\times\s*10\^\{[-+]?\d+\})?)(?!\w|\.\d)'
)
COUNT_WORD = re.compile(
    r'\b(?:zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)\b'
    r'(?=\s+(?:data sets?|temperatures?|pressures?|states?|liquids?|starts?|'
    r'parameters?|observations?|intervals?|compositions?|fits?|splits?|'
    r'coefficients?|moles?|measurements?|isobars?|searches|loadings?)\b)', re.I
)
INCLUDE = re.compile(r'\\(?:input|include)\s*\{([^{}]+)\}')
GRAPHIC = re.compile(r'\\includegraphics(?:\[[^\]]*\])?\{([^{}]+)\}')
NON_TEXT = re.compile(r'\\(?:cite\w*|\w*ref|label|url|href|includegraphics)(?:\[[^\]]*\])?\{[^{}]+\}'
                      r'|\\(?:multi(?:row|column))\{\d+\}'
                      r'|\\\\\[[^\]]+\]|\d+(?:\.\d+)?\\(?:linewidth|textwidth)'
                      r'|\b(?:Fig(?:ure)?\.|Eq(?:uation)?\.|Table|Section|Appendix|issue)\s*~?\s*[SA]?(?:\d+\.)*\d+'
                      r'|(?<=\()(?:19|20)\d{2}(?=\))|(?<= in )(?:19|20)\d{2}(?![.\w])|#[0-9]+|\b[0-9a-f]{12,}\b'
                      r'|\b\d+-amino-\d+-methyl-\d+-propanol\b'
                      r'|(?<=\^)\{?[−+-]?\d+\}?|(?<=_)\{?\d+\}?'
                      r'|\\setlength\{[^{}]+\}\{[^{}]+\}|\\begin\{tabular[^}]*\}.*')
UNIT = re.compile(r'(?:\s|\\,|~|\$|\})*(\\%|%|MPa|kPa|Pa|K|mol/kg|kg/m³|kJ/mol)(?=\W|$)')
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


def masked(line):
    scientific = [m.span() for m in LITERAL.finditer(line) if r'	imes' in m[0]]
    clean = NON_TEXT.sub(lambda m: m[0] if any(a <= m.start() < b for a, b in scientific)
                         else ' '*len(m[0]), line)
    return re.sub(r'--(?=\d)', '  ', clean)


def occurrences(closure, readback):
    buf = StringIO()
    fields = ('revision', 'entry_points', 'file', 'line', 'column', 'reported_quantity',
              'printed_token', 'rounding', 'display_unit', 'old_producer', 'old_source', 'old_field', 'disposition',
              'quantity', 'record', 'record_field', 'model', 'denominator', 'value', 'value_unit', 'producer', 'estimated_cost', 'note', 'printed_context')
    writer = csv.DictWriter(buf, fields, lineterminator='\n')
    writer.writeheader()
    counts = Counter()
    recomputations = Counter()
    figures = {}
    for path, (content, entries) in sorted(closure.items()):
        name = Path(path).stem
        table = '/tables/' in path or name == 'amp_reference_state'
        headings, block = [], ''
        in_document = r'\begin{document}' not in content
        for i, line in enumerate((active_text(content) if path.endswith('.tex') else content).splitlines(), 1):
            if r'\begin{document}' in line:
                in_document = True
            for figure in GRAPHIC.findall(line):
                figures.setdefault(figure, []).append(f'{path}:{i}')
            if INCLUDE.search(line):
                continue
            clean = masked(line)
            if table and (tag := re.search(r'\\textit\{([^{}]+)\}', line)) and r'\multicolumn' in line:
                block = tag[1]
            cells = re.split(r'(?<!\\)&', line)
            if table and len(cells) > 1 and not headings:
                headings = [cell.strip().replace(r'\toprule ', '') for cell in cells]
                header = True
            else:
                header = False
            # Count excluded source literals separately to keep the scan auditable.
            matches = list(LITERAL.finditer(line))
            selected = list(LITERAL.finditer(clean))
            counts[EXCLUDED] += sum(m.span() not in {x.span() for x in selected} for m in matches)
            words = list(COUNT_WORD.finditer(clean)) if not table else []
            for index, match in enumerate([*selected, *words]):
                token = match[0]
                col = len(re.split(r'(?<!\\)&', line[:match.start()])) - 1
                row = cells[0].strip()
                heading = headings[col] if len(cells) > 1 and col < len(headings) else 'Caption/notes'
                if (not in_document or header or re.match(r'\s*(?:postcode=|\\(?:vspace|draw|coordinate|pagestyle|usepackage)\b)', line)
                        or (name == 'graphical_abstract' and i not in range(17, 21))
                        or re.fullmatch(r'\d+(?:\.\d+)?(?:pt|mm|cm)', token)):
                    counts[EXCLUDED] += 1
                    continue
                if table:
                    position = sum(len(re.split(r'(?<!\\)&', line[:prior.start()])) - 1 == col
                                   for prior in selected[:index])
                    binding = table_quantity(name, i, col, block, row, heading, position)
                    label = f'{block + " / " if block else ""}{row} / {heading}'
                else:
                    binding = prose_quantity(name, i, index, token, line)
                    label = binding.get('old_field', 'Document identifiers')
                if binding['disposition'] == EXCLUDED:
                    counts[EXCLUDED] += 1
                    continue
                key = binding.get('quantity')
                if key:
                    value = readback['quantities'][key]
                    denominator = value['denominator'] if isinstance(value['denominator'], (str, int)) else f'{len(value["denominator"])} entries; see quantity record'
                    binding |= dict(record=value['source'], record_field=value['field'], value=value['value'],
                                    value_unit=value['unit'], model=value['model'], denominator=denominator)
                elif binding['disposition'] == RETAINED and not (ROOT / binding['record']).is_file():
                    raise ValueError(f'Absent #435 record for {path}:{i}: {binding}')
                if 'record' in binding and not key:
                    old = binding['record']
                    model = next((case for case, identity in readback['models'].items()
                                  if old.startswith(identity['path'].rsplit('/', 1)[0] + '/')), '')
                    if not model and old.startswith((str(ME) + '/MEA/',)):
                        model = 'MEA'
                    binding['model'] = model or 'See receiver identity or matched-row record'
                    binding['denominator'] = 'Declared observation, state or coefficient indicated by record_field'
                counts[binding['disposition']] += 1
                if binding['disposition'] == OPEN:
                    recomputations[binding['producer'], binding['estimated_cost'], binding['note']] += 1
                mantissa = re.split(r'[eE]|\\times', token)[0]
                unit = UNIT.match(line[match.end():])
                old_producer = binding['old_source'] if binding['old_source'].endswith('.py') else (
                    'final_rerun_tables.py / dea_displays.py' if table else 'Pinned prose; see old_source and old_field')
                writer.writerow(dict(revision=STORY, entry_points=' / '.join(entries), file=path, line=i,
                                     old_producer=old_producer,
                                     column=match.start()+1, reported_quantity=key or label,
                                     printed_token=token, rounding=('written count' if match in words else
                                         f'{len(mantissa.partition(".")[2])} decimal places in displayed mantissa'),
                                     display_unit=unit[1] if unit else '', printed_context=line.strip(), **binding))
    series = figure_quantities(figures)
    for entry in series:
        counts['figure series · ' + entry['disposition']] += 1
        if entry['disposition'] == OPEN:
            recomputations[entry['producer'], entry['estimated_cost'], entry['note']] += 1
    return buf.getvalue(), counts, recomputations, series


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


def render(closure, counts, recomputations, readback):
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
    values = readback['quantities']
    tie = readback['DEA absolute tie check']
    heat_replay = load(ME / 'MEA/F4/heat-replay.json')['rows']
    n_heat = sum(row['status'] == 'available' for row in heat_replay)
    q5 = load(ME / 'MEA/F4/q5.json')['result']
    activity = next(row for row in q5['rows'] if row['T_K'] == 313.15 and row['loading'] == 0.30 and row['symbol'] is None)
    binary_path = Path('analyses/mdea_mea_workflow/results/salt-anchored-435/campaign/binary-onset.json')
    fixed_path = binary_path.with_name('fixed-pressure.json.gz')
    binary = load(binary_path)['result']
    fixed = load(fixed_path)
    lines += ['', '## Publication numbers', '',
              f'Pinned #429 TeX commit `{STORY}`. All {len(closure)} active source files are present.', '',
              'Use the [occurrence map](number-occurrences.csv) to locate a printed value by file, line, row and column. '
              'The [quantity records](publication-quantities.json) give full-precision values, denominators, effective '
              'models and wheel. The [figure series map](figure-series.json) gives the plotted fields and retained input hashes.', '',
              'Scientific counts written as cardinal numbers before quantity nouns also enter the map. Structural numbers are excluded by rule. These include TeX dimensions and command arguments used for layout, '
              'citation keys and publication years in citations, section/equation/table/figure identifiers, issue numbers, '
              'hashes, chemical-name locants and math subscripts or exponents used as notation. '
              'Scientific-notation mantissa and exponent are recorded together. Model versions are tracked as provenance.', '',
              *[f'- {n:,} {disposition}.' for disposition, n in sorted(counts.items())], '',
              f"The old MEA objective 150.76 (307 rows, primary weights) becomes "
              f"{values['MEA/C']['value']:.2f}. The Cai share changes from 60.8% to "
              f"{values['MEA/Cai objective share']['value']:.1f}%.", '',
              f"DEA #413 absolute tie check. The saved starts differ by {tie['absolute_delta']:.6g}; "
              f"both tie at {tie['absolute_tolerance']:.0e} and {tie['chosen']} has the lower cost. "
              'The previously used relative rule gives the same labels for these saved costs.', '',
              '### Supplementary readbacks', '',
              '- Three MEA bubble checks agree to ten significant digits from two initial pressures. '
              + link(ME / 'MEA/F4/check-values.json', 'printed_digits_agree'),
              '- The temperature-band readback preserves the #409 role rules. The added heat replay '
              f'returned {n_heat} of {len(heat_replay)} predictions, with {len(heat_replay)-n_heat} above the calculation ceiling. '
              + link(ME / 'MEA/F4/bands.json') + ' · ' + link(ME / 'MEA/F4/heat-replay.json'),
              '- The source-pressure replay passes the common-basis and equal-pressure checks. '
              'Equality to the old F2 archived pressures fails for the changed parameters. '
              + link(ME / 'MEA/F4/q4.json', 'result.checks'),
              '- The activity grid retains the #432 historical pH check as false. The worked state at '
              f'313.15 K, 101325 Pa, 30 wt% MEA and loading 0.30 gives pH {activity["pH"]:.6f} on the common molality '
              'basis, and its R1 and R2 common-molality calculations agree. '
              + link(ME / 'MEA/F4/q5.json', 'result.rows'),
              f'- The MDEA CO₂-free onset readback took {binary["seconds"]:.1f} s. The three brackets have '
              'the same printed limits as #421. ' + link(binary_path, 'result.pressures'),
              f'- The MDEA loaded case at {fixed["P_Pa"]/1e6:.3f} MPa has outcome `{fixed["outcome"]}` under #435. '
              'The worked two-liquid composition, densities and curvature in the supplement belong to the older declaration. '
              + link(fixed_path, 'outcome, attempts'), '',
              '### Open publication items', '',
              '| Producer | Estimated effort | Needed evidence | Occurrences / series |', '| --- | --- | --- | ---: |',
              *([f'| {p} | {cost} | {why} | {n} |' for (p, cost, why), n in sorted(recomputations.items())]
                or ['| — | — | No current-value recomputation is assigned by the pinned occurrence map. | 0 |']), '',
              'Publication rendering remains open. Bind the #435 records in `final_rerun_tables.py`, '
              '`dea_displays.py`, `f2_figures.py` and `supplement_data_inventory.py` when revising the '
              'manuscript. Rendering is a readback, estimated at seconds to minutes after rebinding. '
              'Update labels and captions for the expanded AMP objective, linear-T salt laws and changed search outcomes, '
              'then run the document and generated-display checks.', '',
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
    if missing:
        raise ValueError(f'Incomplete manuscript snapshot: {missing}')
    readback = publication_readback()
    content, counts, recomputations, series = occurrences(closure, readback)
    handoff = render(closure, counts, recomputations, readback)
    notebook = handoff.split('## Calculations\n', 1)[1].split('## Publication numbers', 1)[0]
    notebook += '### Supplementary readbacks\n' + handoff.split('### Supplementary readbacks\n', 1)[1].split('### Open publication items', 1)[0]
    notebook = re.sub(r'\]\(([^)]+)\)',
                      lambda m: '](' + posixpath.normpath('results/salt-anchored-435/' + m[1]) + ')', notebook)
    paths = [('publication-quantities.json', json.dumps(dict(manuscript_commit=STORY, **readback), indent=2)+'\n'),
             ('figure-series.json', json.dumps(dict(manuscript_commit=STORY, series=series), indent=2)+'\n'),
             ('number-occurrences.csv', content), ('manuscript-handoff.md', handoff), ('calculation-summary.md', notebook.rstrip()+'\n')]
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
