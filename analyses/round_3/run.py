"""Run the fixed-parameter calculations for issue #432."""
import argparse
import hashlib
import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from time import monotonic


def receipt():
    from part_ii import ROOT, SHA, WHEEL

    executed = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                for module in tuple(sys.modules.values())
                if (file := getattr(module, '__file__', None)) and (p := Path(file).resolve()).is_relative_to(ROOT)
                and '.venv' not in p.parts and p.suffix == '.py'}
    return dict(wheel_sha256=SHA, engine_commit=WHEEL.parent.name.removeprefix('main-'), executed_files=executed)


def save(question, start, **record):
    from part_ii import jsonable

    result = dict(seconds=monotonic()-start, **receipt(), **record)
    path = Path(__file__).with_name('results') / f'{question}.json'
    path.write_text(json.dumps(jsonable(result), indent=2, allow_nan=False)+'\n')
    print(question, result['seconds'], flush=True)


if __name__ == '__main__':
    from recall import DECLARATION
    from part_ii import Route

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('question', choices=('q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q8'),
                        help='q1 also writes q2; recall.py writes q7')
    question = parser.parse_args().question
    with TemporaryDirectory() as directory:
        work = Path(directory)
        Route(DECLARATION, work/'verify')
        if question in ('q1', 'q2'):
            from phases import amp_rows
            amp_rows(work/question, save, save_q1=question=='q1')
        elif question == 'q3':
            from phases import mdea_rows
            mdea_rows(work/question, save)
        elif question == 'q8':
            from records import reductions
            reductions(work, save)
        elif question == 'q6':
            from phases import worked, certificate
            worked(work/question, save, certificate)
        else:
            from mea import sensitivity, activity_grid
            (sensitivity if question=='q4' else activity_grid)(save)
