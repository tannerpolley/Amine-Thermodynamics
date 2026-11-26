"""Index the records read by the display renderer against manuscript number occurrences."""

import argparse
import ast
import collections
import gzip
from heapq import nsmallest
import math
import re
import sys
from decimal import Decimal
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from analyses.amines import displays as d  # noqa: E402

SMALL = (
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen "
    "fifteen sixteen seventeen eighteen nineteen"
).split()
TENS = "twenty thirty forty fifty sixty seventy eighty ninety".split()
CARDINAL = {word: n for n, word in enumerate(SMALL)}
CARDINAL.update({f"{word}{'-' + unit if n else ''}": 10 * t + n
                 for t, word in enumerate(TENS, 2) for n, unit in enumerate(SMALL[:10])})
WORDS = re.compile(r"\b(?:" + "|".join(sorted(CARDINAL, key=len, reverse=True)) +
                   r"|hundred|thousand|million)\b", re.I)
SCIENTIFIC = d.SCIENTIFIC
TOKEN = re.compile(rf"{SCIENTIFIC.pattern}|{d.NUMERAL.pattern}|{WORDS.pattern}", re.I)
TERMS = re.compile(r"[A-Za-z][A-Za-z0-9]+")
EQUATIONS = re.compile(r"\\begin\{equation\*?\}.*?\\end\{equation\*?\}", re.S)
CAPTION = re.compile(r"\\caption\b(?:\[[^]]*\])?\s*\{")


def displayed_number(token):
    scientific = SCIENTIFIC.fullmatch(token)
    if scientific:
        mantissa, exponent = scientific['mantissa'] or '1', scientific['exponent']
        return Decimal(mantissa).scaleb(int(exponent)), len(mantissa.partition('.')[2]) - int(exponent)
    if token.lower() in CARDINAL:
        return Decimal(CARDINAL[token.lower()]), 0
    if d.NUMERAL.fullmatch(token):
        value = Decimal(token)
        return value, -value.as_tuple().exponent
    return None, None


def classification(text, start, stop):
    rules = (
        ('year', r'(?:\bin |\(\s*)(?P<value>(?:19|20)\d{2})\b'),
        ('citation', r'\b(?:Eq\.|Fig\.|Table|row|run)\s*~?\s*S?(?P<value>\d+)(?=[^\d.]|\.(?!\d)|$)'),
        ('condition', r'\\SI\{(?P<value>100)\}\{\\kilo\\pascal\}|(?P<plain>100)\s+kPa(?:\b|\\)'),
        ('condition', r'(?:nominal |unloaded )(?P<value>\d+(?:\.\d+)?)(?=\s*wt)'),
        ('constant', r'P\^\\circ\s*=?\s*\\SI\{(?P<value>0\.1)\}\{\\mega\\pascal\}'),
        ('definition', r'(?P<value>[Tt]wo)(?=-(?:liquid|phase|site|sided)\b)'),
        ('definition', r'(?P<value>[Oo]ne)(?=-sided\b| Gibbs energy\b| donor\b| acceptor\b| induced-association\b)'),
        ('definition', r'(?P<value>four)(?=-site chain\b| standard contributions\b)'),
        ('definition', r'(?P<value>\d+)-parameter (?:calibration|form|model|fit)\b'),
        ('equation', r'(?P<value>\d+)(?=\\(?:pi|eta|rho)\b)'),
        ('version', r'python=(?P<value>3\.13)(?=\s)'),
    )
    for reason, rule in rules:
        if any(any(match.span(name) == (start, stop) for name in match.groupdict())
               for match in re.finditer(rule, text)):
            return reason
    recipe = text.lstrip().lower()
    if recipe.startswith(('the grid spans ', 'each temperature--loading pair uses ',
                          'the mea liquid--vapor search contains ',
                          'for mea, the liquid grid contains ', 'a second liquid grid, offset from the first,')):
        return 'condition'
    if any(begin <= start < stop <= end for begin, end in
           (match.span() for match in re.finditer(r"\b2-amino-2-methyl-1-propanol\b", text))):
        return 'definition'
    return None


def occurrences(collisions):
    for path in d.manuscript_sources():
        source = d.manuscript_body(path.read_text())
        masked = d.mask_syntax(source)
        equations = [match.span() for match in EQUATIONS.finditer(source)]
        captions = []
        for command in CAPTION.finditer(source):
            depth = 1
            for brace in re.finditer(r"(?<!\\)[{}]", source[command.end():]):
                depth += 1 if brace[0] == "{" else -1
                if not depth:
                    captions.append((command.end(), command.end() + brace.start()))
                    break
        relative = path.relative_to(d.ROOT).as_posix()
        reviewed_spans = [(match.span(), entry) for entry in collisions if entry['file'] == relative
                          for match in d.collision_contexts(source, entry['context'])]
        # Keep the exponent in a typed scientific number while hiding equation indices elsewhere.
        for scientific in SCIENTIFIC.finditer(source):
            start, stop = scientific.span()
            if masked[start:scientific.end('base')].strip():
                masked = masked[:start] + scientific[0] + masked[stop:]
        boundary = re.compile(r'[.!?](?=\s|$)|\n\s*\n|\\\\(?=\n|$)')
        stops = iter([*(match.end() for match in boundary.finditer(source)), len(source)])
        start, stop = 0, next(stops)
        offset = 0
        for i, (raw, filtered) in enumerate(zip(source.splitlines(), masked.splitlines(), strict=True), 1):
            for match in TOKEN.finditer(filtered):
                while stop <= offset + match.start():
                    start, stop = stop, next(stops)
                sentence = ' '.join(source[start:stop].split())
                begin, end = offset + match.start(), offset + match.end()
                reason = classification(source[start:stop], begin-start, end-start)
                if not reason and path.name == 'nomenclature.tex':
                    reason = 'definition'
                if not reason and any(a <= begin and end <= b for a, b in equations):
                    reason = 'equation'
                row = dict(file=relative, line=i, column=match.start()+1,
                           token=match[0], sentence=sentence, reason=reason)
                if any(a <= begin and end <= b for a, b in captions):
                    row["display_text"] = True
                for (a, b), entry in reviewed_spans:
                    if entry['token'] == row['token'] and a <= begin and end <= b:
                        row.update(reason=entry['reason'], collision=True, context=entry['context'])
                yield row
            offset += len(raw) + 1


def display_text(collisions):
    path = Path(d.__file__)
    file = path.relative_to(d.ROOT).as_posix()
    labels = {"label", "xlabel", "ylabel", "title", "notes"}
    seen = set()
    for call in ast.walk(ast.parse(path.read_text())):
        if not isinstance(call, ast.Call):
            continue
        parts = [part.value for part in call.keywords if part.arg in labels]
        if isinstance(call.func, ast.Name) and call.func.id == 'table' and len(call.args) > 1:
            parts.append(call.args[1])
        for part in parts:
            for node in ast.walk(part):
                if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
                    continue
                if node in seen:
                    continue
                seen.add(node)
                text = node.value
                for match in TOKEN.finditer(d.mask_syntax(text)):
                    row = dict(file=file, line=node.lineno, token=match[0], sentence=text,
                               reason=classification(text, *match.span()), display_text=True)
                    for entry in collisions:
                        if entry['file'] == file and entry['token'] == match[0] and any(
                            m.start() <= match.start() and match.end() <= m.end()
                            for m in d.collision_contexts(text, entry['context'])
                        ):
                            row.update(reason=entry['reason'], collision=True, context=entry['context'])
                    yield row


def number_fields(data, prefix):
    if isinstance(data, dict):
        for key, value in data.items():
            yield from number_fields(value, (*prefix, key))
    elif isinstance(data, list):
        for i, row in enumerate(data):
            yield from number_fields(row, (*prefix, i))
    elif type(data) in (float, int):
        if math.isfinite(data):
            yield prefix, data
    elif isinstance(data, str) and d.NUMERAL.fullmatch(data.strip()):
        value = float(data)
        if math.isfinite(value):
            yield prefix, value


def searchable_records():
    d.verify()
    d.register_records(json.loads((d.ROOT / 'analyses/amines/sources.json').read_text()))
    manifest = json.loads((d.TABLES / 'number-sources.json').read_text())
    for record, entry in manifest.items():
        if entry['read']:
            yield record, d.read(record)
    for source in ('fit', 'phase', 'properties'):
        name = f'analyses/amines/results/shared/{source}/display-summary.json.gz'
        for record in d.read(name)['inputs']:
            if record in manifest and not manifest[record]['read']:
                path = d.ROOT / record
                if path.suffix in {'.json', '.gz'}:
                    yield record, json.loads(gzip.decompress(path.read_bytes()) if path.suffix == '.gz' else path.read_bytes())


def index(targets):
    by_precision = collections.defaultdict(set)
    for value, precision in targets:
        by_precision[precision].add(float(value))
    found = collections.defaultdict(dict)
    for record, data in searchable_records():
        for fields, value in number_fields(data, ()):
            for precision, values in by_precision.items():
                rounded = round(value, precision)
                if rounded not in values:
                    continue
                key = tuple('[]' if isinstance(field, int) else field for field in fields)
                candidates = found[rounded, precision]
                candidates.setdefault((record, key), dict(record=record, key=list(fields)))
    return found


def ranking(words, record, key):
    fields = [part for part in key if isinstance(part, str)]
    match = lambda s: len(set(TERMS.findall(s.lower())) & words)
    return 3 * match(' '.join(fields)) + match(record)


def mdea_descent_findings():
    record = d.PHASE_SUMMARY
    counts = d.read(record)['mdea_descent_counts']
    names = {
        'optimized_result_available': 'mdea-descents-optimized-result-available',
        'supplied_trial_optimized_result_unavailable': 'mdea-descents-supplied-trial-optimized-result-unavailable',
    }
    evidence = [dict(name=name, value=counts[key], record=record, key=f'mdea_descent_counts.{key}')
                for key, name in names.items()]
    available, supplied = (counts[key] for key in names)
    interpretation = (f'{supplied} of the {available + supplied} descents came from supplied trial compositions '
                      'whose optimized result was unavailable. The count of searches reported as finished '
                      f'covers {available} descents.')
    for path in d.manuscript_sources():
        for line, sentence in d.sentences(path.read_text()):
            if r'\res{mdea-descents-all-transfer-search}' in sentence or r'\res{mdea-descents-all-supplement}' in sentence:
                yield dict(file=path.relative_to(d.ROOT).as_posix(), line=line, sentence=sentence,
                           status='finding', interpretation=interpretation, evidence=evidence,
                           retained_source='analyses/fixed_reaction_reference/results/MDEA/screen/selected/declared/summary.json.gz',
                           retained_keys=['rows[].descent', 'rows[].available', 'rows[].optimized_available',
                                          'rows[].supplied_available', 'rows[].supplied_trial_evidence'])


def kuranov_pressure_finding():
    tracking_record = 'analyses/round_8/results/literature-populations.json.gz'
    reported_record = d.STUDY + 'results/MDEA/property-comparisons/A.json.gz'
    tracking = d.read(tracking_record)['quantities']['kuranov']['readback']
    reported = d.read(reported_record)['additional_Kuranov_72']
    if tracking['identity'] != reported['identity'] or tracking['observed'] != reported['observed']:
        raise ValueError('Different observations in the Kuranov row comparison')
    path = d.LATEX / 'supplement.tex'
    for line, sentence in d.sentences(path.read_text()):
        if r'\res{mdea-kuranov-row-72-tracking-reference-pressure}' in sentence:
            yield dict(
                file=path.relative_to(d.ROOT).as_posix(), line=line, sentence=sentence, status='finding',
                interpretation=(
                    'The printed pressure comes from the system-pressure-reference endpoint. '
                    'The 100 kPa reported endpoint predicts a different pressure at the same observation on S.'
                ),
                evidence=[
                    dict(record=tracking_record, key='quantities.kuranov.readback.value',
                         value=tracking['value'], unit='Pa'),
                    dict(record=reported_record, key='additional_Kuranov_72.value',
                         value=reported['value'], unit='Pa'),
                    dict(record=reported_record, key='additional_Kuranov_72.observed',
                         value=reported['observed'], unit='Pa'),
                ],
            )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    collisions = json.loads((d.ROOT / 'analyses/amines/number-collisions.json').read_text())
    rows = [*occurrences(collisions), *display_text(collisions)]
    targets = {displayed_number(row['token']) for row in rows if row['reason'] is None} - {(None, None)}
    candidates = index(targets)
    with args.output.open('w') as out:
        for row in rows:
            value, precision = displayed_number(row['token'])
            matches = candidates.get((float(value), precision), {}).values() if value is not None else ()
            words = set(TERMS.findall(row['sentence'].lower()))
            row['matches'] = len(matches)
            row['proposals'] = nsmallest(12, matches, key=lambda item: -ranking(words, **item))
            row['status'] = ('collision' if row.get('collision') else 'non-result' if row['reason'] else 'unclassified')
            out.write(json.dumps(row, ensure_ascii=False) + '\n')
        detected_collisions = {(row['file'], row['context'], row['token']) for row in rows if row.get('collision')}
        for entry in collisions:
            if (entry['file'], entry['context'], entry['token']) not in detected_collisions:
                out.write(json.dumps(dict(entry, status='collision'), ensure_ascii=False) + '\n')
        for finding in mdea_descent_findings():
            out.write(json.dumps(finding, ensure_ascii=False) + '\n')
        for finding in kuranov_pressure_finding():
            out.write(json.dumps(finding, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    main()
