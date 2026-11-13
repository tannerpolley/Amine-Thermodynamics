"""Stage #206's retained Part I manuscript evidence; never upload or reserve a DOI.

Use: stage (moves any old staging aside, copies Part I evidence), rebuild (compiles both PDFs from the
staged copy and compares them with the accepted PDFs), then seal (README, manifest, checksums).
"""
import csv
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

ROOT = Path(__file__).resolve().parents[1]
DEST = Path('/home/tnnrpolley21/Workspaces/External/mea-manuscript-deposit')
B = 'analyses/mea_parameter_bundle'
A = f'{B}/results/adoption-297'
E = f'{A}/paper-evidence'
L = 'docs/scientific/latex'
PARAMETER = 'f8f64820b161377a0d97d1e4ad4f6cea764cd0558dc63231d58e2096988eef97'
# The accepted PDFs were compiled on the real clock; rebuilds use this fixed time (main.pdf's creation instant).
SOURCE_DATE_EPOCH = '1794527621'
SOURCE = subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip()
NOTEBOOK = subprocess.check_output(['git', '-C', str(ROOT), 'log', '-1', '--format=%H', SOURCE, '--', f'{B}/notebook.qmd'], text=True).strip()
INVENTORY_COMMIT = '771410a94f7729915bfe6457bfe7a5a0746f1611'  # a7_presentation.py checks the table generator at this commit


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


def stage():
    receipt = json.loads((ROOT / L / 'builds/verification-receipt.json').read_text())
    accepted = {n: ROOT / L / f'builds/{n}.pdf' for n in ('main', 'supplement')}
    assert sha(accepted['main']) == receipt['pdf_sha256'], 'main.pdf does not match builds/verification-receipt.json'
    tracked = subprocess.check_output(['git', '-C', str(ROOT), 'ls-files'], text=True).splitlines()
    prefixes = [f'{A}/', f'{B}/results/uncertainty-307/', f'{B}/results/engine-3e83e19c-phase-search/run-2/',
                f'{B}/results/engine-3e83e19c-density-free/', f'{B}/results/engine-3e83e19c-refit-chain/',
                f'{B}/results/engine-3e83e19c-paper-evidence/', f'{B}/data/', f'{B}/scripts/', f'{B}/calibration-misfit/',
                'data/reference/MEA/', 'src/', f'{L}/']
    selected = {p for p in tracked if any(p.startswith(q) for q in prefixes)
                and '/builds/' not in p and '/submission/' not in p and not p.endswith('submission_metadata.yml')
                and 'mdea' not in p.lower()}  # MDEA files belong to Part II
    selected.update(['LICENSE', 'pyproject.toml', 'uv.lock', f'{B}/notebook.qmd',
                     f'{B}/results/selected-current-best-parameters.json',
                     f'{B}/results/temperature-reanchor-140/never-accessed-vle-admission.csv',
                     'scripts/stage_manuscript_deposit.py'])
    # Every file the table and figure generators read is named in their outputs.
    selected.update(json.loads((ROOT / L / 'figures/generated/provenance.json').read_text())['inputs'])
    for table in (ROOT / L / 'tables').glob('*.tex'):
        selected.update(re.findall(r'^% Input: (\S+) SHA256', table.read_text(), re.M))
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
    selected = {p for p in selected if not p.endswith('.whl')}
    for name in sorted(selected):  # check everything before copying, so a failure leaves no half-staged folder
        assert not any(q in name.lower() for q in ('cesar', 'a7-paper-evidence/', 'mdea')), name  # MDEA belongs to Part II
        assert not name.endswith('.pdf') or 'figures' in name, name  # generated figures only, never source papers
        assert (ROOT / name).is_file() and not (ROOT / name).is_symlink(), name
    if DEST.exists() and any(DEST.iterdir()):  # replace cleanly; the old staging stays for review
        stamp = datetime.date.fromtimestamp(DEST.stat().st_mtime).isoformat()
        DEST.rename(DEST.with_name(f'{DEST.name}-{stamp}-superseded'))
    DEST.mkdir(parents=True, exist_ok=True)
    for name in sorted(selected):
        (DEST / name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, DEST / name)
    (DEST / L / 'builds').mkdir()
    for name, pdf in accepted.items():
        shutil.copy2(pdf, DEST / L / f'builds/{name}.pdf')
    # Exact historical table source needed by the generator's Git provenance check.
    history = DEST / 'provenance'
    history.mkdir()
    (history / 'inventoried-table-generator.py').write_bytes(subprocess.check_output(
        ['git', '-C', str(ROOT), 'show', f'{INVENTORY_COMMIT}:{L}/scripts/final_rerun_tables.py']))
    write('provenance/source.json', dict(manuscript_commit=SOURCE, mea_notebook_commit=NOTEBOOK, source_date_epoch=int(SOURCE_DATE_EPOCH)))
    subprocess.run(['uv', 'export', '--frozen', '--no-dev', '--no-emit-project',
                    '--no-emit-package', 'epcsaft', '--no-emit-package', 'pcsaft',
                    '--format', 'requirements-txt', '--output-file',
                    str(history / 'presentation-requirements.txt')], cwd=ROOT,
                   stdout=subprocess.DEVNULL, check=True)
    print(f'Staged {len(selected)} source files at {DEST}')


def rebuild():
    """Compile both PDFs from the staged copy only, as a reader of the README would, and compare with the accepted PDFs."""
    with tempfile.TemporaryDirectory() as tmp:
        shutil.copytree(DEST / L, Path(tmp) / 'latex', ignore=shutil.ignore_patterns('builds'))
        work = Path(tmp) / 'latex'
        env = {**os.environ, 'SOURCE_DATE_EPOCH': SOURCE_DATE_EPOCH, 'FORCE_SOURCE_DATE': '1', 'TEXINPUTS': './styles//:'}
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


def seal():
    paths = dict(density=f'{E}/density.csv', phase_states=f'{E}/phase-family.csv',
                 ideal_gas_calorics=f'{E}/source-only/physical-ideal-gas-calorics.json')
    for path in paths.values():
        assert (DEST / path).is_file(), path
    with (DEST / paths['density']).open() as stream:
        assert len(list(csv.DictReader(stream))) == 210
    with (DEST / paths['phase_states']).open() as stream:
        phase = list(csv.DictReader(stream))
    adopted = {(r['engine_wheel_sha256'], r['parameter_sha256']) for r in phase if r['record'] == 'adopted #255 candidate'}
    comparison = {(r['engine_wheel_sha256'], r['parameter_sha256']) for r in phase if r['record'] == 'comparison'}
    assert len(phase) == 324 and sum(r['record'] == 'comparison' for r in phase) == 162 and len(adopted) == len(comparison) == 1
    parameter = sha(DEST / B / 'results/selected-current-best-parameters.json')
    assert parameter == PARAMETER
    records = load(f'{L}/figures/generated/provenance.json')['records']
    engine, historical = records['reported']['engine'], records['comparison']
    assert (engine['wheel_sha256'], parameter) in adopted
    assert (historical['engine']['wheel_sha256'], historical['parameter_sha256']) in comparison
    rebuilt = load('provenance/rebuild-check.json')
    pdfs = {}
    for name, pages in [('main', 24), ('supplement', 22)]:
        path = DEST / L / f'builds/{name}.pdf'
        assert pdf_pages(path) == pages == rebuilt[name]['pages'] and sha(path) == rebuilt[name]['accepted_sha256']
        pdfs[name] = dict(pages=pages, sha256=sha(path))
    readme = f'''# MEA manuscript deposit, Part I: preparation only

Nothing has been uploaded or published. No DOI has been reserved. This staging represents manuscript commit `{SOURCE}` (Part I, main 24 pages, supplement 22 pages). Owner review and all publication actions remain separate gates. The MDEA evidence belongs to Part II and is not included.

Scientific basis: the adopted MEA notebook at `{NOTEBOOK}`. Notebook text and historical receipts retain their status at authoring. No calculations were rerun in preparing this deposit.

- Adopted MEA parameters: `{B}/results/selected-current-best-parameters.json`, SHA-256 `{parameter}`.
- Adopted-record Engine source: `{engine['commit']}`; immutable wheel `{Path(engine['wheel_path']).name}`, SHA-256 `{engine['wheel_sha256']}`. This wheel produced every adopted result and the 162 adopted phase states.
- Historical comparison fit (the fit without a phase-stability requirement, parameter SHA-256 `{historical['parameter_sha256']}`): Engine source `{historical['engine']['commit']}`; wheel SHA-256 `{historical['engine']['wheel_sha256']}`. Only its comparison calculations and its 162 comparison phase states need this second wheel.

Both wheels are omitted. Referee access to the compiled library is to be arranged by the corresponding author. HSL MA57 is separately licensed and is not redistributed. No source-paper PDFs or private CESAR-1 material are included. Analysis code is supplied under the MIT license (`LICENSE`); third-party measurements retain their source terms.

## Data the manuscript says the deposit supplies

| Statement in the manuscript | Deposited file |
|---|---|
| complete 210-observation density table (supplement) | `{paths['density']}` |
| complete 162-state table for both fits (supplement); the `record` column names the fit and `engine_wheel_sha256` its wheel | `{paths['phase_states']}` |
| neutral ideal-gas caloric coefficients (main text) | `{paths['ideal_gas_calorics']}` |

Other same-named records in the repository are provenance or intermediate records, not alternate mappings.
'''
    figure_names = sorted({name for source in (DEST / L).rglob('*.tex')
                           for name in re.findall(r'\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}', source.read_text())
                           if name.endswith('.pdf')})
    for name in figure_names:
        assert (DEST / L / 'figures/generated' / name).is_file(), name
    readme += '\nLaTeX figure filenames resolve as follows:\n\n' + ''.join(
        f'- `{name}`: `{L}/figures/generated/{name}`\n' for name in figure_names)
    readme += f'''
## Contents and limits

`{A}/` holds the adopted record's retained evidence: the 307-row replay, the 162-state phase searches of the adopted and comparison fits, conditional uncertainty, the paper-evidence tables and the retained wheel and input identities (`wheel.json`, `input-identity.json`, `inventory.json`). `{B}/results/uncertainty-307/` holds the covariance, profiles and prediction bands. The `engine-3e83e19c-*` directories under `{B}/results/` retain the historical comparison fit and its phase search. The phase searches are numerical verification and conditional calibration, not independent physical validation or a global stability proof.

`data/reference/MEA/` retains processed measurements, provenance, source locators and data-role declarations. Current tables, vector figure PDFs, PNG previews and rendering code are under `{L}/` and `{B}/scripts/`. Application calculation code is under `src/`. The obsolete `a7-paper-evidence/` package is excluded.

## Reproduction

Start at the deposit root. Run `sha256sum -c SHA256SUMS` before doing anything else. Preserve an untouched copy because generators overwrite displays and receipts. Python 3.13 is required. `pyproject.toml` and `uv.lock` are byte-identical snapshots of the manuscript environment; the adopted wheel path is intentionally unresolved until supplied through referee access.

For rendering retained values, only matplotlib and its dependencies are required. Exact package pins are recorded in `uv.lock`. The table generator also checks a historical source using `git show`. In a copied deposit, obtain that Git object with:

```bash
git init
git fetch --depth=1 https://github.com/tannerpolley/Amine-Thermodynamics.git {INVENTORY_COMMIT}
```

The matching historical source is also retained as `provenance/inventoried-table-generator.py`. This Git fetch is a reproduction prerequisite, not a publication action.

```bash
uv venv --python 3.13 .venv-presentation
uv pip sync --python .venv-presentation/bin/python provenance/presentation-requirements.txt
nice -n 10 .venv-presentation/bin/python docs/scientific/latex/scripts/final_rerun_tables.py
nice -n 10 .venv-presentation/bin/python analyses/mea_parameter_bundle/scripts/render_manuscript_figures.py
```

Build both PDFs using pdfLaTeX/latexmk and BibTeX, with the supplied CAS class and styles, after installing the TeX packages named in the preamble. The two documents read each other's cross-references, so build main, supplement, main, supplement. From `{L}/`:

```bash
mkdir -p builds
for name in main supplement main supplement; do
  SOURCE_DATE_EPOCH={SOURCE_DATE_EPOCH} FORCE_SOURCE_DATE=1 TEXINPUTS='./styles//:' nice -n 10 latexmk -g -pdf -interaction=nonstopmode -halt-on-error -outdir=builds $name.tex
done
```

The PDFs in `{L}/builds/` are the accepted builds, compiled on the real clock. A rebuild with the command above from this deposit alone gave the same page counts, text and rendered pages (`provenance/rebuild-check.json`); only the creation date and file identifier differ, so its SHA-256 differs.

For calculation replay, obtain the matching wheels and the licensed solver first. Place each wheel at the path identified by its retained runtime receipt, relative to a fresh copy of this deposit. The adopted wheel uses the path in `pyproject.toml`; run `uv sync --locked`, then use `UV_NO_SYNC=1 uv run python` for the retained scripts. `{B}/scripts/adoption_297.py` records the qualification sequence and command options (`f1`, `f2`, `f3`, `evidence`, `extras`, `phase-export`, `f5`); see its retained execution logs under `{A}/logs/`. These are expensive calculation reruns, separate from rendering retained results, and were not attempted for this deposit because the wheels and HSL are omitted.

## Build identities and inventories

- Main PDF: SHA-256 `{pdfs['main']['sha256']}` (24 pages).
- Supplement PDF: SHA-256 `{pdfs['supplement']['sha256']}` (22 pages).

`manifest.json` lists each payload file's role, byte size and SHA-256, plus manuscript, parameter, Engine and PDF identities. It excludes itself and `SHA256SUMS` to avoid a recursive checksum. `SHA256SUMS` covers all final files except itself, including the manifest. `provenance/verification.json` records the data-file and wheel-label checks. These checks establish file identity and staging completeness; they add no new scientific result.
'''
    (DEST / 'README.md').write_text(readme)
    write('provenance/verification.json', dict(deposited_data=paths, density_rows=210, phase_state_rows=324,
          adopted_wheel_labels=sorted(adopted), comparison_wheel_labels=sorted(comparison), mea_parameter_sha256=parameter, pdfs=pdfs))
    files = sorted(p for p in DEST.rglob('*') if p.is_file() and p not in (DEST / 'manifest.json', DEST / 'SHA256SUMS'))
    entries = [dict(path=str(p.relative_to(DEST)), role=('manuscript source or display' if str(p.relative_to(DEST)).startswith(L) else 'retained data, provenance, environment or application code'), bytes=p.stat().st_size, sha256=sha(p)) for p in files]
    write('manifest.json', dict(publication='preparation only; nothing published', manuscript_commit=SOURCE, mea_notebook_commit=NOTEBOOK,
          mea_parameter_sha256=parameter, adopted_engine=engine, comparison_engine=historical, pdfs=pdfs, files=entries))
    files = sorted(p for p in DEST.rglob('*') if p.is_file() and p != DEST / 'SHA256SUMS')
    (DEST / 'SHA256SUMS').write_text(''.join(f'{sha(p)}  {p.relative_to(DEST)}\n' for p in files))
    print(json.dumps(dict(path=str(DEST), files=len(files)+1, bytes=sum(p.stat().st_size for p in files)+(DEST/'SHA256SUMS').stat().st_size)))


if __name__ == '__main__':
    steps = dict(stage=stage, rebuild=rebuild, seal=seal)
    if len(sys.argv) != 2 or sys.argv[1] not in steps:
        raise SystemExit('Use: stage, then rebuild, then seal.')
    steps[sys.argv[1]]()
