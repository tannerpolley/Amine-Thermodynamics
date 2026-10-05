"""Reuse the retained #147 driver with the successor wheel and separate outputs."""
import os
from pathlib import Path

OUT = Path(__file__).resolve().parent
original = OUT.parent / 'qualify.py'
source = original.read_text()
replacements = {
    'HERE = Path(__file__).resolve().parent': 'HERE = Path(__file__).resolve().parent.parent',
    'ePC-SAFT-build-717a2990': 'ePC-SAFT-build-9c31cb9a',
    '717a2990e443423e051fc0569f25209d04007543': '9c31cb9a89b6fb42fd386ca44de2331601b4751c',
    '9e6a76cf59d4e2fef3347d895bf3a966ecced01f13dc6e0caec74c3c3d618dc4': os.environ['EPCSAFT_147_WHEEL_SHA256'],
    "RAW = BUNDLE / 'results/runs/temperature-heat-147'": "RAW = BUNDLE / 'results/runs/temperature-heat-147/qualification-9c31cb9a'",
    'pa.save(HERE /': 'pa.save(OUT /',
    'pa.table(HERE /': 'pa.table(OUT /',
    "'build_jobs': len(os.sched_getaffinity(0))": "'build_jobs': 1",
    'budget_s=180, limits=s.EvaluationLimits(180, 180)': 'budget_s=175, limits=s.EvaluationLimits(175, 175)',
    "'identity': rec['identity'], 'target':": "'module_origin': probe.epcsaft.__file__, 'identity': rec['identity'], 'target':",
    "path = HERE / f'calorimetry-": "path = OUT / f'calorimetry-",
    "if __name__ == '__main__':": "pa.save(OUT / 'installed-record-check.json', pa.verify(RAW.parent / '.venv-9c31cb9a'))\nif __name__ == '__main__':",
}
for old, new in replacements.items():
    assert old in source, old
    source = source.replace(old, new)
exec(compile(source, str(original), 'exec'), globals())
