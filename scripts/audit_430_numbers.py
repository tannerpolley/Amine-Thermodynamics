"""Index the records read by the display renderer against manuscript number occurrences."""

import argparse
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


def displayed_number(token):
    scientific = SCIENTIFIC.fullmatch(token)
    if scientific:
        mantissa, exponent = scientific.group('mantissa', 'exponent')
        return Decimal(mantissa).scaleb(int(exponent)), len(mantissa.partition('.')[2]) - int(exponent)
    if token.lower() in CARDINAL:
        return Decimal(CARDINAL[token.lower()]), 0
    if d.NUMERAL.fullmatch(token):
        value = Decimal(token)
        return value, -value.as_tuple().exponent
    return None, None


def classification(text, start, stop):
    rules = (
        ('year', r'(?:\bin |\(\s*)(?P<value>(?:19|20)\d{2})(?=\s*\)|\s+when\b)'),
        ('condition', r'\\SI\{(?P<value>100)\}\{\\kilo\\pascal\}'),
        ('condition', r'(?:nominal |unloaded )(?P<value>30)(?=\s*wt)'),
        ('definition', r'(?P<value>[Tt]wo)(?=-(?:liquid|phase|site)\b)'),
        ('version', r'python=(?P<value>3\.13)(?=\s)'),
    )
    for reason, rule in rules:
        if any(match.span('value') == (start, stop) for match in re.finditer(rule, text)):
            return reason
    return None


def occurrences(collisions):
    for path in d.manuscript_sources():
        source = d.manuscript_body(path.read_text())
        masked = d.mask_syntax(source)
        # Keep the exponent in a typed scientific number while hiding equation indices elsewhere.
        for scientific in SCIENTIFIC.finditer(source):
            start, stop = scientific.span()
            if masked[start:scientific.end('mantissa')].strip():
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
                row = dict(file=path.relative_to(d.ROOT).as_posix(), line=i, column=match.start()+1,
                           token=match[0], sentence=sentence,
                           reason=classification(source[start:stop], offset+match.start()-start, offset+match.end()-start))
                for entry in collisions:
                    if entry['file'] == row['file'] and entry['token'] == row['token'] and any(
                        context.start() <= match.start() and match.end() <= context.end()
                        for context in re.finditer(re.escape(entry['context']), raw)
                    ):
                        row.update(reason=entry['reason'], collision=True)
                yield row
            offset += len(raw) + 1


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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    collisions = json.loads((d.ROOT / 'analyses/amines/number-collisions.json').read_text())
    rows = list(occurrences(collisions))
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
        paths = {path.relative_to(d.ROOT).as_posix() for path in d.manuscript_sources()}
        for entry in collisions:
            if entry['file'] not in paths:
                out.write(json.dumps(dict(entry, status='collision'), ensure_ascii=False) + '\n')


if __name__ == '__main__':
    main()
