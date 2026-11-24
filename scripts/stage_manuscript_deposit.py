"""Stage #206's retained evidence for the merged manuscript; never upload or reserve a DOI.

Use: stage (moves any old staging aside, copies the manuscript evidence), rebuild (compiles both PDFs from the
staged copy and compares them with the accepted PDFs), then seal (README, manifest, checksums).
"""
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib

ROOT = Path(__file__).resolve().parents[1]
DEST = Path('/home/tnnrpolley21/Workspaces/External/mea-manuscript-deposit')
B = 'analyses/mea_parameter_bundle'
A = f'{B}/results/adoption-297'
E = f'{A}/paper-evidence'
L = 'docs/scientific/latex'
DEA = 'analyses/dea_transfer'
MDEA = 'analyses/mdea_mea_workflow'
AMP = 'analyses/amp_transfer'
DEA_RESULTS = f'{DEA}/results/refit-413'
MDEA_RESULTS = f'{MDEA}/results/bounded-binary-411'
AMP_RESULTS = f'{AMP}/results/retransfer-412-f2-05e94210'
F2 = f'{B}/results/paper-evidence-341'
REDUCED = f'{B}/results/reduced-refit'
STRIPPER = f'{B}/results/stripper-temperature-409'
FIGURE_INPUTS = f'{L}/builds/347-figure-hashes.json'
SOURCE = subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip()
NOTEBOOK = subprocess.check_output(['git', '-C', str(ROOT), 'log', '-1', '--format=%H', SOURCE, '--', f'{B}/notebook.qmd'], text=True).strip()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads((DEST / path).read_text())


def write(path, value):
    (DEST / path).write_text(json.dumps(value, indent=2) + '\n')


def pdf_pages(pdf):
    return int(re.search(r'Pages:\s+(\d+)', subprocess.check_output(['pdfinfo', str(pdf)], text=True))[1])


def pdf_content(pdf):
    """Text plus the hash of every rendered page: equal when two builds differ only in dates and file ID."""
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(['pdftoppm', '-r', '60', '-png', str(pdf), f'{tmp}/p'], check=True)
        pages = [sha(p) for p in sorted(Path(tmp).glob('p-*.png'))]
    return subprocess.check_output(['pdftotext', str(pdf), '-'], text=True), pages


def metadata():
    import yaml

    return yaml.safe_load((ROOT / L / 'submission_metadata.yml').read_text())


def pdf_identities(meta):
    return {
        name: dict(pages=meta[prefix + 'pdf_pages'], sha256=meta[prefix + 'pdf_sha256'])
        for name, prefix in [('main', ''), ('supplement', 'supplement_')]
    }


def check_parameters(root, records):
    for record in records:
        assert sha(root / record['path']) == record['sha256'], record['path']


def declared_inputs(name, base=None, *, overridden=()):
    """Follow hashed data records and specification files read by the fit declarations."""
    path = ROOT / name
    base = path.parent if base is None else base
    document = tomllib.loads(path.read_text()) if path.suffix == '.toml' else json.loads(path.read_text())
    for key in overridden:
        del document[key]
    yield name

    def visit(node):
        if isinstance(node, dict):
            if 'path' in node and 'sha256' in node:
                dependency = Path(os.path.abspath(base / node['path']))
                relative = dependency.relative_to(ROOT).as_posix()
                assert sha(dependency) == node['sha256'], relative
                if dependency.suffix == '.toml':
                    yield from declared_inputs(relative, base)
                else:
                    yield relative
            for value in node.values():
                yield from visit(value)
        elif isinstance(node, list):
            for value in node:
                yield from visit(value)

    if isinstance(document, dict) and 'specification' in document:
        spec = Path(os.path.abspath(base / document['specification']))
        yield from declared_inputs(spec.relative_to(ROOT).as_posix())
        if changes := document.get('dataset_changes'):
            yield from declared_inputs((base / changes['path']).relative_to(ROOT).as_posix(), spec.parent)
    yield from visit(document)


def selected_files(tracked, records):
    prefixes = [
        f'{A}/', f'{B}/results/uncertainty-307/', f'{B}/results/engine-3e83e19c-phase-search/run-2/',
        f'{B}/results/engine-3e83e19c-density-free/', f'{B}/results/engine-3e83e19c-refit-chain/',
        f'{B}/results/engine-3e83e19c-paper-evidence/', f'{B}/data/', f'{B}/scripts/', f'{B}/calibration-misfit/',
        'data/reference/MEA/', 'src/', f'{L}/sections/', f'{L}/styles/', f'{L}/thumbnails/',
        f'{L}/figures/generated/', f'{DEA_RESULTS}/', f'{MDEA_RESULTS}/', f'{AMP_RESULTS}/', f'{STRIPPER}/',
        f'{F2}/', f'{REDUCED}/F0/', f'{B}/results/wheel-recheck-05e94210/',
        *(f'{MDEA}/results/shared-bicarbonate-417/{name}/' for name in ('mea', 'mdea', 'reported-mdea')),  # the three MDEA fits of main-text Table 8 and the two MEA refits behind them
        f'{B}/results/born-diameter-sensitivity-405/', f'{B}/results/same-data-comparison/hong-2027/',
        f'{B}/results/same-data-comparison/part1/published/',
    ]
    selected = {p for p in tracked if p.startswith(tuple(prefixes))}
    selected.update([
        'LICENSE', 'pyproject.toml', 'uv.lock', '.gitignore', f'{B}/notebook.qmd',
        f'{B}/results/selected-current-best-parameters.json',
        f'{B}/results/temperature-reanchor-140/never-accessed-vle-admission.csv',
        'analyses/part_ii.py', 'analyses/wheel_recheck_391.py',
        'analyses/solvent_specification_mea/inputs/endpoint.json',
        f'{B}/results/adoption-340/part-ii-shared-values.json',
        f'{REDUCED}/split-registry.json', f'{REDUCED}/split-trials.json', f'{REDUCED}/README.md',
        f'{REDUCED}/F2/parameters.json', f'{REDUCED}/F2/replay.json', f'{REDUCED}/F2/information.json',
        f'{B}/results/adoption-340/candidate/replay.json',
        *(f'{REDUCED}/evidence/F2/{name}' for name in (
            'state-targets.csv', 'heat.csv', 'cp.csv', 'kim2007-heat-pathways/kim-heat.csv',
            'heat-capacity-264.json', 'density-268/density.json',
        )),
        f'{B}/results/split-cause-342/figure-contributions.csv',
        f'{B}/results/split-cause-342/final-supplied-F2.json.gz',
        f'{B}/results/same-data-comparison/matched-score.json',
        f'{L}/.latexmkrc', f'{L}/main.tex', f'{L}/supplement.tex',
        f'{L}/chemistry_macros.tex', f'{L}/references.bib', f'{L}/transfer_sources.bib',
        f'{L}/submission/highlights.txt',
        *(f'{L}/scripts/{name}.py' for name in ('final_rerun_tables', 'f2_figures', 'dea_displays')),
        *(f'{DEA}/{name}.py' for name in ('f2_carbamate', 'rerun', 'present_current')),
        *(f'{AMP}/{name}.py' for name in (
            'fit_412', 'probe_412', 'classify_descents', 'refit_404', 'retain_404', 'pure_binary_on_05e94210',
        )),
        *(f'{MDEA}/scripts/{name}.py' for name in ('bounded_binary_411', 'retransfer_343')),
        f'{DEA}/inputs/part-ii-346/f2-carbamate-413-parameter-table-declarations.json',
        f'{DEA}/inputs/part-ii-346/parameter-table-declarations.json',
        f'{DEA}/inputs/part-ii-346/README.md', f'{AMP}/source-admission.md',
        f'{AMP}/results/retransfer-344-05e94210/data-rows.json',
        f'{AMP}/results/retransfer-344-05e94210/campaign/new-witnesses.json.gz',
        f'{AMP}/results/retransfer-344-05e94210/campaign/start-0/retreat-disposition.json',
        f'{AMP}/results/retransfer-344-05e94210/campaign/start-0/unpenalized/stage-0/parameters.json',
        *(f'{AMP}/inputs/{name}' for name in ('pure-amp.csv', 'amp-pure-endpoint.json', 'hartono-2013-table-3.csv', 'amp-document.json')),
        f'{AMP}/results/pure/summary.json', f'{AMP}/results/binary-dielectric.json',
        f'{MDEA}/inputs/retransfer-343-binary-penalty.json',
        *(f'{MDEA}/results/retransfer-343/binary-penalty/{name}' for name in (
            'split-record.json', 'post-binary/data-rows.json', 'summary-row.json', 'curves/curve-rows.json',
            'parameter-table.json', 'published-pressure-comparisons.json',
        )),
        f'{MDEA}/results/retransfer-343/reaction-ranges.json',
        *(record['path'] for record in records),
    ])
    for declaration in (
        f'{DEA}/inputs/part-ii-346/f2-carbamate-413-route.json',
        f'{DEA}/inputs/part-ii-346/route-current.json',
        f'{AMP}/inputs/retransfer-344/phase-2/AMP-05e94210.json',
        'analyses/solvent_specification_mea/MEA.toml',
        f'{A}/historical-spec/MEA.toml',
        f'{B}/results/adoption-340/historical-spec/MEA.toml',
    ):
        selected.update(declared_inputs(declaration))
    # The bounded-fit producer substitutes the retained pressure-figure curve rows.
    selected.update(declared_inputs(f'{MDEA}/inputs/bounded-binary-411.json', overridden=('curve_rows',)))

    # The checked transfer displays record every file they read, including the older measured-point rows.
    sources = f'{L}/tables/number-sources.json'
    selected.update((sources, FIGURE_INPUTS))
    for inputs in (json.loads((ROOT / sources).read_text()), json.loads((ROOT / FIGURE_INPUTS).read_text())['files']):
        for name, digest in inputs.items():
            assert sha(ROOT / name) == digest, name
            selected.add(name)
    # Root tables include the current generators' auxiliary display files.
    for table in (ROOT / L / 'tables').glob('*.tex'):
        selected.add(table.relative_to(ROOT).as_posix())
        selected.update(re.findall(r'^% Input: (\S+) SHA256', table.read_text(), re.M))
    # Preserve the existing MEA evidence and its original figure receipt.
    selected.update(json.loads((ROOT / L / 'figures/generated/provenance.json').read_text())['inputs'])
    # Keep the actual file dependencies of retained fit declarations, not whole retired studies.
    pending = [p for p in selected if p.endswith('spec.json')]
    seen = set()
    def references(value):
        if isinstance(value, dict):
            for key, item in value.items():
                yield from references(key)
                yield from references(item)
        elif isinstance(value, list):
            for item in value:
                yield from references(item)
        elif isinstance(value, str) and value.startswith(('analyses/', 'data/')) and not any(c.isspace() or c == ':' for c in value):
            if (ROOT / value).is_file() and 'a7-paper-evidence/' not in value:
                yield value
    while pending:
        name = pending.pop()
        if name in seen:
            continue
        seen.add(name)
        for dependency in references(json.loads((ROOT / name).read_text())):
            selected.add(dependency)
            if dependency.endswith('.json'):
                pending.append(dependency)
    return {p for p in selected if not p.endswith('.whl')}


def stage():
    from check_private_source import PUBLISHED_LINE_HASH, PUBLISHED_PATH, path_is_blocked, scan

    failures = scan(ROOT)
    if failures:
        raise SystemExit('\n'.join(failures))
    meta = metadata()
    accepted = pdf_identities(meta)
    for name, identity in accepted.items():
        pdf = ROOT / L / f'builds/{name}.pdf'
        assert sha(pdf) == identity['sha256'] and pdf_pages(pdf) == identity['pages'], pdf.name
    check_parameters(ROOT, meta['parameter_records'])
    tracked = set(subprocess.check_output(['git', '-C', str(ROOT), 'ls-files'], text=True).splitlines())
    selected = selected_files(tracked, meta['parameter_records'])
    for name in sorted(selected):
        assert not path_is_blocked(name), "private-source identifier in deposit path"
        assert name in tracked and (ROOT / name).is_file() and not (ROOT / name).is_symlink(), name
        assert 'a7-paper-evidence/' not in name, name
        assert not name.endswith('.pdf') or 'figures' in name, name  # generated figures only
    if DEST.exists() and any(DEST.iterdir()):  # replace cleanly; the old staging stays for review
        stamp = datetime.datetime.fromtimestamp(DEST.stat().st_mtime).strftime('%Y-%m-%dT%H%M%S')
        DEST.rename(DEST.with_name(f'{DEST.name}-{stamp}-superseded'))
    DEST.mkdir(parents=True, exist_ok=True)
    for name in sorted(selected):
        (DEST / name).parent.mkdir(parents=True, exist_ok=True)
        if name == PUBLISHED_PATH:
            # The repository scan allows an obsolete, nonprinting bibliography keyword field.
            lines = (ROOT / name).read_bytes().splitlines(keepends=True)
            (DEST / name).write_bytes(b''.join(
                line for line in lines if hashlib.sha256(line.rstrip(b'\r\n')).hexdigest() != PUBLISHED_LINE_HASH
            ))
        else:
            shutil.copy2(ROOT / name, DEST / name)
    for name in accepted:
        pdf = Path(L) / f'builds/{name}.pdf'
        shutil.copy2(ROOT / pdf, DEST / pdf)
    history = DEST / 'provenance'
    history.mkdir()
    info = subprocess.check_output(['pdfinfo', '-isodates', str(ROOT / L / 'builds/main.pdf')], text=True)
    creation_date = re.search(r'^CreationDate:\s+(\S+)', info, re.M)[1]
    write('provenance/source.json', dict(
        deposit_commit=SOURCE, manuscript_commit=meta['pdf_commit'], mea_notebook_commit=NOTEBOOK,
        source_date_epoch=int(datetime.datetime.fromisoformat(creation_date).timestamp()),
    ))
    subprocess.run(['uv', 'export', '--frozen', '--no-dev', '--no-emit-project',
                    '--no-emit-package', 'epcsaft', '--no-emit-package', 'pcsaft',
                    '--format', 'requirements-txt', '--output-file',
                    str(history / 'presentation-requirements.txt')], cwd=ROOT,
                   stdout=subprocess.DEVNULL, check=True)
    # The earlier accepted MEA figures carry this renderer version in their PDF metadata.
    (history / 'matplotlib-3.11.2-linux-x86_64.txt').write_text(
        'matplotlib==3.11.2 --hash=sha256:1944895967f87c84c9b4bad29a707b31f5b36df4a3a2339ea1f8ea3ce5105539\n'
    )
    print(f'Staged {len(selected)} source files at {DEST}')


def rebuild():
    """Compile both PDFs from the staged copy only, as a reader of the README would, and compare with the accepted PDFs."""
    identity = load('provenance/source.json')
    assert identity['deposit_commit'] == SOURCE
    with tempfile.TemporaryDirectory() as tmp:
        shutil.copytree(DEST / L, Path(tmp) / 'latex', ignore=shutil.ignore_patterns('builds'))
        work = Path(tmp) / 'latex'
        env = {**os.environ, 'SOURCE_DATE_EPOCH': str(identity['source_date_epoch']), 'FORCE_SOURCE_DATE': '1', 'TEXINPUTS': './styles//:'}
        for name in ('main', 'supplement', 'main', 'supplement'):  # each file reads the other's cross-references
            subprocess.run(['latexmk', '-g', '-pdf', '-interaction=nonstopmode', '-halt-on-error', '-outdir=builds', f'{name}.tex'],
                           cwd=work, env=env, check=True, stdout=subprocess.DEVNULL)
        result = {}
        for name in ('main', 'supplement'):
            new, old = work / f'builds/{name}.pdf', DEST / L / f'builds/{name}.pdf'
            text_new, pages_new = pdf_content(new)
            text_old, pages_old = pdf_content(old)
            result[name] = dict(pages=pdf_pages(new), text_identical=text_new == text_old, rendered_pages_identical=pages_new == pages_old,
                                byte_identical=sha(new) == sha(old), rebuilt_sha256=sha(new), accepted_sha256=sha(old))
            assert pdf_pages(new) == pdf_pages(old) and result[name]['text_identical'] and result[name]['rendered_pages_identical'], result
    write('provenance/rebuild-check.json', result)
    print(json.dumps(result, indent=2))


def write_software_index(meta, identity):
    display_base = load(FIGURE_INPUTS)['commit']
    engines = '\n'.join(
        f"| {record['scope']} | {record['version']} | `{record['engine_commit']}` | `{record['engine_wheel_sha256']}` |"
        for record in meta['engines']
    )
    (DEST / 'software-index.md').write_text(f'''# Software and commands

## Engine identities

| Calculation | epcsaft version | Engine commit | Wheel SHA-256 |
|---|---|---|---|
{engines}

Use CPython 3.13. The wheels are supplied through the corresponding author.
Verify each wheel against the table and install the wheel for the calculation
in its own environment. HSL MA57 requires a separate licence. The locked
Python dependencies are listed in `uv.lock`. The current `pyproject.toml`
binds version 1.3.1 at its expected repository-relative wheel path. For
version 1.3.0 use the path suffix starting at `build/engine-wheels/` in
`{F2}/wheel.json`, relative to the scratch checkout.

## Displays and PDFs

Work in a copy because the generators write displays and receipts.
`final_rerun_tables.py` and `f2_figures.py` check the archived numerical inputs
against a Git snapshot. From the deposit root:

```bash
git init
git fetch --depth=1 https://github.com/tannerpolley/Amine-Thermodynamics.git {display_base}
uv venv --python 3.13 .venv-presentation
uv pip sync --python .venv-presentation/bin/python provenance/presentation-requirements.txt
mkdir -p {L}/builds
.venv-presentation/bin/python {L}/scripts/final_rerun_tables.py --check
.venv-presentation/bin/python {L}/scripts/dea_displays.py --check
.venv-presentation/bin/python {L}/scripts/f2_figures.py
```

The locked Matplotlib 3.10.9 reproduces the checked transfer displays and
five MEA figures. The accepted `density-curves.pdf`, `mea-water.pdf` and
`split-energy.pdf` use Matplotlib 3.11.2. Regenerate those three in a
second scratch copy using the same commands, with this additional install
after `uv pip sync` and before calling `f2_figures.py`:

```bash
uv pip install --python .venv-presentation/bin/python --no-deps --require-hashes -r provenance/matplotlib-3.11.2-linux-x86_64.txt
```

Build with pdfLaTeX, latexmk and BibTeX. The two documents read each other's
cross-references. The accepted LaTeX inputs and vector figures are ready for
this build directly, with no Python environment required.

```bash
cd {L}
for name in main supplement main supplement; do
  SOURCE_DATE_EPOCH={identity['source_date_epoch']} FORCE_SOURCE_DATE=1 TEXINPUTS='./styles//:' \\
    latexmk -g -pdf -interaction=nonstopmode -halt-on-error -outdir=builds "$name.tex"
done
```

## Numerical reproduction

Run the commands below from the repository root in a scratch checkout at the
recorded source, with the matching wheel installed. Several producers verify
Git provenance and compare against historical baselines. The deposited
records support the paper and display generation directly. Use the named
historical Git inputs for the original numerical campaigns.

```bash
export AGENT_HEAVY_CORES=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=src
```

**MEA (1.3.0).** The calibration campaign and reductions use
`{B}/scripts/reduced_refit_338.py`. See the command sequence in
`{REDUCED}/README.md` and the F2 evidence recipe in `{F2}/README.md`.

```bash
python {B}/scripts/reduced_refit_338.py campaign
for action in replay evidence uncertainty comparison weights shared checks stability; do
  python {B}/scripts/paper_evidence_341.py "$action"
done
python {B}/scripts/stripper_temperature_409.py table
python {B}/scripts/stripper_temperature_409.py replay /path/to/f7e09b9ec-export
python {B}/scripts/hong_2027.py /path/to/scratch-hong-results
```

The stripper heat replay uses the exact producer from Git commit
`f7e09b9ec` as described in `{STRIPPER}/README.md`. The retained heat
replay is sufficient to regenerate the band table. The 1.3.1 wheel recheck
uses `python analyses/wheel_recheck_391.py part-i ACTION RUN_DIRECTORY`;
see that script's action and comparison commands.

**DEA (1.3.1).** The preflight uses `selection.json` and `paper-data.csv`
from the earlier `{DEA}/results/retransfer-398/` in the Git checkout.

```bash
run={DEA}/results/runs/413-reproduce
python {DEA}/f2_carbamate.py prepare
python {DEA}/f2_carbamate.py run "$run"
python {DEA}/present_current.py "$run" "$run-paper" "$run-replay-398" \\
  F2-carbamate F0-carbamate 413 inputs/part-ii-346/f2-carbamate-413-parameter-table-declarations.json
```

**MDEA (1.3.1).** The bounded campaign reuses the earlier starts, trial bank
and measured-point locations included as individual inputs.

```bash
for action in critical fit unbounded report search retain; do
  python {MDEA}/scripts/bounded_binary_411.py "$action"
done
```

**AMP (1.3.1).** The free-slope comparison supplies the warm start for the
reported fixed-slope model. The historical F0 diagnostics and the final
`fit_412.py retain -150` reduction also read earlier comparison rows from
`{AMP}/results/retransfer-404-05e94210/main/` in the Git checkout.

```bash
export PYTHONPATH=src:analyses
python {AMP}/fit_412.py reference
python {AMP}/fit_412.py -125 -150 -175
python {AMP}/fit_412.py confirm -150
python {AMP}/probe_412.py f2
```
''')


def seal():
    meta = metadata()
    identity = load('provenance/source.json')
    assert identity['deposit_commit'] == SOURCE
    check_parameters(DEST, meta['parameter_records'])
    rebuilt = load('provenance/rebuild-check.json')
    pdfs = pdf_identities(meta)
    for name, pdf in pdfs.items():
        path = DEST / L / f'builds/{name}.pdf'
        assert pdf['pages'] == pdf_pages(path) == rebuilt[name]['pages']
        assert pdf['sha256'] == sha(path) == rebuilt[name]['accepted_sha256']
        assert rebuilt[name]['text_identical'] and rebuilt[name]['rendered_pages_identical']

    readme = f'''# Data and code for the aqueous amine ePC-SAFT manuscript

The accepted main text and supplement are in `{L}/builds/`. Their source
commit is `{identity['manuscript_commit']}`. The deposit was staged from
`{SOURCE}`. This is local preparation for Zenodo.

| Model | Reported evidence |
|---|---|
| MEA | `{F2}/`, including the density, carbonate share and stability evidence. The 16-parameter comparison is under `{REDUCED}/F0/`. |
| MEA at stripper temperatures | `{STRIPPER}/`, including observation-level results and band reductions. |
| DEA | `{DEA_RESULTS}/`, including the selected fit, property comparisons and stability summary. |
| MDEA | `{MDEA_RESULTS}/`, including the bounded fit, its comparison and the search outcomes. |
| AMP | `{AMP_RESULTS}/slope-150/` is the reported model. `{AMP_RESULTS}/main/` is the comparison with the temperature slope fitted. |
| MDEA, shared water--bicarbonate interaction | `{MDEA}/results/shared-bicarbonate-417/`: `mdea/` holds the MDEA refits at 0.1325 and 1.0, `mea/` the MEA refits at those values and `reported-mdea/` the reported MDEA model on the same observations (main-text Table 8). |

The parameter record paths and SHA-256 hashes are in `manifest.json`.
The MEA ideal-gas caloric coefficients are in
`{E}/source-only/physical-ideal-gas-calorics.json`.
The numerical observations retain their published source terms. The supplied
analysis code uses the MIT license in `LICENSE`.
The staged bibliography removes a nonprinting keyword field.

`SHA256SUMS` covers every deposited file except itself. Run
`sha256sum -c SHA256SUMS` from the root before making changes.
`manifest.json` gives the payload file sizes and hashes.
`provenance/rebuild-check.json` gives the accepted PDF hashes and the page,
text and render comparisons. See `software-index.md` for reproduction commands.

## Package versions and linear solvers

The MEA calculations were made with version 1.3.0 of the epcsaft package, and
the DEA, MDEA and AMP calculations with version 1.3.1. Recalculated with
version 1.3.1 at the reported parameters, the fitted MEA quantities differ from
the reported values by less than 2.1e-12 in relative terms, and all 2646
phase-stability searches again finish without a detected instability. Version
1.3.2 is public (https://github.com/tannerpolley/epcsaft, release v1.3.2).
Built from that source for Linux and Python 3.13 with the separately licensed
HSL MA57 linear solver, it reproduces the reported predictions of all four
amines at the reported parameters: the fitted MEA quantities differ by less
than 2.1e-12 in relative terms, all 2646 MEA searches again finish without a
detected instability, and five searches that did not finish with version
1.3.1, one for DEA and four for MDEA, now finish without a detected
instability, while every search that finished before still finishes. The conda
package uses the MUMPS linear solver and does not require MA57; checked on MEA
only, its 307 fitted MEA predictions agree with those of the MA57 build within
1.4e-12 in relative terms. The MEA fit and the refits near the bound were not
repeated with version 1.3.1, and no fit was repeated with version 1.3.2.
'''
    (DEST / 'README.md').write_text(readme)
    write_software_index(meta, identity)
    files = sorted(p for p in DEST.rglob('*') if p.is_file() and p not in (DEST / 'manifest.json', DEST / 'SHA256SUMS'))
    entries = [dict(path=str(p.relative_to(DEST)), role=('manuscript source or display' if str(p.relative_to(DEST)).startswith(L) else 'retained data, provenance, environment or application code'), bytes=p.stat().st_size, sha256=sha(p)) for p in files]
    write('manifest.json', dict(**identity, engines=meta['engines'], parameter_records=meta['parameter_records'],
                                pdfs=pdfs, files=entries))
    files = sorted(p for p in DEST.rglob('*') if p.is_file() and p != DEST / 'SHA256SUMS')
    (DEST / 'SHA256SUMS').write_text(''.join(f'{sha(p)}  {p.relative_to(DEST)}\n' for p in files))
    print(json.dumps(dict(path=str(DEST), files=len(files)+1, bytes=sum(p.stat().st_size for p in files)+(DEST/'SHA256SUMS').stat().st_size)))


if __name__ == '__main__':
    steps = dict(stage=stage, rebuild=rebuild, seal=seal)
    if len(sys.argv) != 2 or sys.argv[1] not in steps:
        raise SystemExit('Use: stage, then rebuild, then seal.')
    steps[sys.argv[1]]()
