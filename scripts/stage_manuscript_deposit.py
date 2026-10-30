"""Stage #206's retained manuscript evidence; never upload or reserve a DOI."""
import csv
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
DEST = Path('/home/tnnrpolley21/Workspaces/External/mea-manuscript-deposit')
B = 'analyses/mea_parameter_bundle'
E = f'{B}/results/engine-3e83e19c-paper-evidence'
P = f'{B}/results/engine-3e83e19c-phase-search/run-2'
M = 'analyses/mdea_mea_workflow'
L = 'docs/scientific/latex'
SOURCE = subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'c84ef77'], text=True).strip()
NOTEBOOK = subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'f138561'], text=True).strip()
MDEA_NOTEBOOK = subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', '209da68'], text=True).strip()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads((DEST / path).read_text())


def write(path, value):
    (DEST / path).write_text(json.dumps(value, indent=2) + '\n')


def stage():
    # Rebuild only in an empty destination; preserve any existing staging for review.
    DEST.mkdir(parents=True, exist_ok=True)
    assert not list(DEST.iterdir()), 'Destination must be empty; do not overwrite an existing deposit.'
    tracked = subprocess.check_output(['git', '-C', str(ROOT), 'ls-files'], text=True).splitlines()
    prefixes = [f'{E}/', f'{P}/', f'{B}/results/engine-3e83e19c-density-free/',
                f'{B}/results/engine-3e83e19c-refit-chain/', f'{B}/data/', f'{B}/scripts/',
                f'{B}/calibration-misfit/', f'{M}/inputs/', f'{M}/scripts/',
                f'{M}/results/stage2-capped/', f'{M}/results/item-l/',
                f'{M}/results/stage2-density/', f'{M}/results/dielectric/', f'{M}/results/context-sources/',
                'data/reference/MEA/', 'data/reference/MDEA/', 'src/', f'{L}/']
    selected = {p for p in tracked if any(p.startswith(q) for q in prefixes)
                and '/builds/' not in p and '/submission/' not in p}
    selected.update(['LICENSE', 'pyproject.toml', 'uv.lock', f'{B}/notebook.qmd',
                     f'{M}/notebook.qmd', f'{M}/README.md',
                     f'{B}/results/selected-current-best-parameters.json',
                     f'{B}/results/temperature-reanchor-140/never-accessed-vle-admission.csv',
                     'scripts/stage_manuscript_deposit.py'])
    selected.update(json.loads((ROOT / E / 'input-hashes.json').read_text()))
    selected.update(e['path'] for e in json.loads((ROOT / E / 'inventory.json').read_text())['entries'])
    selected.update(p for p in tracked if p.startswith(f'{M}/results/') and len(Path(p).parts) == 5)
    # Shared fitting code imports these declarations; keep their application-owned sources.
    selected.update(p for p in tracked if p.startswith(f'{B}/') and p.endswith(('.py', '.py.txt')))
    # Keep the actual file dependencies of retained fit declarations, not whole retired studies.
    pending = [p for p in selected if p.endswith('spec.json') or p.startswith(f'{M}/inputs/') and p.endswith('.json')]
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
    for name in sorted(selected):
        assert not any(q in name.lower() for q in ('cesar', 'a7-paper-evidence/'))
        assert not name.endswith('.whl')
        assert not name.endswith('.pdf') or name.startswith(f'{L}/figures/generated/')
        source = ROOT / name
        assert source.is_file() and not source.is_symlink(), name
        target = DEST / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    # Exact historical table source needed by the generator's Git provenance check.
    history = DEST / 'provenance'
    history.mkdir()
    (history / 'inventoried-table-generator.py').write_bytes(subprocess.check_output(
        ['git', '-C', str(ROOT), 'show', f'771410a94f7729915bfe6457bfe7a5a0746f1611:{L}/scripts/final_rerun_tables.py']))
    # Save source versions without requiring a wheel installation for presentation.
    write('provenance/source.json', dict(manuscript_commit=SOURCE, mea_notebook_commit=NOTEBOOK,
          mdea_notebook_commit=MDEA_NOTEBOOK, source_date_epoch=1792750003))
    subprocess.run(['uv', 'export', '--frozen', '--no-dev', '--no-emit-project',
                    '--no-emit-package', 'epcsaft', '--no-emit-package', 'pcsaft',
                    '--format', 'requirements-txt', '--output-file',
                    str(history / 'presentation-requirements.txt')], cwd=ROOT,
                   stdout=subprocess.DEVNULL, check=True)
    print(f'Staged {len(selected)} source files at {DEST}')


def seal():
    mapping = {name: f'{P}/{name}' for name in ('split-confirmations.csv', 'reference-pressures.csv')}
    mapping['carbonate-share.csv'] = f'{E}/carbonate-share.csv'
    mapping['source-only/physical-ideal-gas-calorics.json'] = f'{E}/source-only/physical-ideal-gas-calorics.json'
    cited = set()
    for source in (DEST / L).rglob('*.tex'):
        cited.update(re.findall(r'\\path\{([^}]+\.(?:csv|json|py|qmd))\}', source.read_text()))
    assert cited == set(mapping), (cited, mapping)
    for path in mapping.values():
        assert (DEST / path).is_file(), path
    parameter = sha(DEST / B / 'results/selected-current-best-parameters.json')
    assert parameter == '00e77608a8489fc9e03a7d2a86c08cb5ff782bb441368a62fa6390b8bfe9cc91'
    engine = load(f'{L}/figures/generated/provenance.json')['records']['reported']['engine']
    mdea = load(f'{M}/results/stage2-capped/authority.json')['runtime']
    endpoints = {v: sha(DEST / M / f'results/stage2-capped/{v}/endpoint.json') for v in ('A3', 'B1')}
    selected = load(f'{M}/results/stage2-capped/selection.json')
    assert endpoints == {v['label']: v['endpoint_sha256'] for v in selected.values()}
    pdfs = {}
    for name, pages in [('main', 25), ('supplement', 20)]:
        path = DEST / L / f'builds/{name}.pdf'
        info = subprocess.check_output(['pdfinfo', str(path)], text=True)
        assert int(re.search(r'Pages:\s+(\d+)', info)[1]) == pages
        pdfs[name] = dict(pages=pages, sha256=sha(path))
    with (DEST / mapping['carbonate-share.csv']).open() as stream:
        carbonate = list(csv.DictReader(stream))
    readme = f'''# MEA manuscript deposit: preparation only

Nothing has been uploaded or published. No DOI has been reserved. This staging represents manuscript commit `{SOURCE}` (main 25 pages, supplement 20 pages). Owner review and all publication actions remain separate gates.

Scientific basis: the adopted MEA notebook at `{NOTEBOOK}` and the owner-promoted MDEA #222 notebook at `{MDEA_NOTEBOOK}`. Notebook text and historical receipts retain their status at authoring; the owner's later promotion is the authority for S12 use. No calculations were rerun in preparing this deposit.

- MEA selected parameters: `{B}/results/selected-current-best-parameters.json`, SHA-256 `{parameter}`.
- MEA Engine source: `{engine['commit']}`; immutable wheel SHA-256 `{engine['wheel_sha256']}`; package versions `{engine['packages']}`.
- MDEA Engine source: `{mdea['engine_commit']}`; immutable wheel SHA-256 `{mdea['wheel_sha256']}` (epcsaft 1.0.0).
- MDEA A3 endpoint SHA-256 `{endpoints['A3']}`; B1 endpoint SHA-256 `{endpoints['B1']}`. Selection and runtime receipts are under `{M}/results/stage2-capped/`.

Both wheels are omitted. Referee access to the compiled library is to be arranged by the corresponding author. HSL MA57 is separately licensed and is not redistributed. No source-paper PDFs or private CESAR-1 material are included. Analysis code is supplied under the MIT license (`LICENSE`); third-party measurements retain their source terms.

## Names cited in the manuscript

Each cited name resolves to exactly one deposited file below. Other same-named records are provenance or intermediate records, not alternate mappings.

| Cited name | Deposited file |
|---|---|
'''
    readme += ''.join(f'| `{name}` | `{path}` |\n' for name, path in mapping.items())
    figure_names = sorted({name for source in (DEST / L).rglob('*.tex')
                           for name in re.findall(r'\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}', source.read_text())
                           if name.endswith('.pdf')})
    for name in figure_names:
        assert (DEST / L / 'figures/generated' / name).is_file(), name
    readme += '\nLaTeX figure filenames resolve as follows:\n\n' + ''.join(
        f'- `{name}`: `{L}/figures/generated/{name}`\n' for name in figure_names)
    readme += f'''
S12 cites no additional filenames. Its retained basis is `{M}/results/stage2-capped/`: `selection.json`, `reported-statistics.json`, `equal-cost-starts.json`, the A3/B1 endpoint, fit, assessment and saturation-cap records, and compressed phase evidence. `transfer-test.csv` and `transfer-test.png` give its pressure comparison. Inputs and code retain repository-relative paths.

## Contents and limits

The MEA current evidence directory `{E}/` supplies processed observations, retained predictions, 307 objective rows, 210 densities, {len(carbonate)} carbonate comparisons, uncertainty tables and five model-curve families. The phase mapping above uses run-2: 54 reference pressures, 162 states per fit. The wider-bound fit has 54 resolved-descent states and the reported fit has zero in that finite search. This is numerical verification and conditional calibration, not independent physical validation or a global stability proof.

`data/reference/MEA/` and `data/reference/MDEA/` retain processed measurements, provenance, source locators and data-role declarations. Current tables, vector figure PDFs, PNG previews and rendering code are under `{L}/` and `{B}/scripts/`. Application calculation code is under `src/` and the analysis script directories. Source-only and historical input records preserve declared starts, affine scaling, fixed caloric inputs and qualification; their identities do not replace the selected MEA or MDEA records. The obsolete `a7-paper-evidence/` package is excluded.

## Reproduction

Start at the deposit root. Run `sha256sum -c SHA256SUMS` before doing anything else. Preserve an untouched copy because generators overwrite displays and receipts. Python 3.13 is required. `pyproject.toml` and `uv.lock` are byte-identical snapshots of the manuscript environment; the MEA wheel path is intentionally unresolved until supplied through referee access. The MDEA wheel must be installed in a separate environment; do not replace the MEA pin.

For rendering retained MEA values, only matplotlib and its dependencies are required. Exact package pins are recorded in `uv.lock`. The existing table generator also checks a historical source using `git show`. In a copied deposit, obtain that Git object with:

```bash
git init
git fetch --depth=1 https://github.com/tannerpolley/Amine-Thermodynamics.git 771410a94f7729915bfe6457bfe7a5a0746f1611
```

The matching historical source is also retained as `provenance/inventoried-table-generator.py` and checked against the retained inventory. This Git fetch is a reproduction prerequisite, not a publication action.

```bash
uv venv --python 3.13 .venv-presentation
uv pip sync --python .venv-presentation/bin/python provenance/presentation-requirements.txt
nice -n 10 .venv-presentation/bin/python docs/scientific/latex/scripts/final_rerun_tables.py
nice -n 10 .venv-presentation/bin/python analyses/mea_parameter_bundle/scripts/render_manuscript_figures.py
nice -n 10 .venv-presentation/bin/python analyses/mdea_mea_workflow/scripts/summarize_capped.py
```

The MDEA summary refresh rewrites its notebook from retained numbers; preserve the promoted source copy. S12 is authored LaTeX, with values retained in `reported-statistics.json` and the cap records.

Build both PDFs using pdfLaTeX/latexmk and BibTeX, with the supplied CAS class and styles, after installing the TeX packages named in the preamble. From `{L}/`:

```bash
SOURCE_DATE_EPOCH=1792750003 FORCE_SOURCE_DATE=1 TEXINPUTS='./styles//:' nice -n 10 latexmk -g -pdf -interaction=nonstopmode -halt-on-error -outdir=builds supplement.tex
SOURCE_DATE_EPOCH=1792750003 FORCE_SOURCE_DATE=1 TEXINPUTS='./styles//:' nice -n 10 latexmk -g -pdf -interaction=nonstopmode -halt-on-error -outdir=builds main.tex
```

For calculation replay, obtain the two matching wheels and licensed solver first. Place each wheel at the path identified by its retained runtime receipt, relative to a fresh copy of this deposit. MEA uses the wheel path in `pyproject.toml`; run `uv sync --locked`, then use `UV_NO_SYNC=1 uv run python` for the retained scripts. `{B}/scripts/association_volume_refit_chain.py`, `engine_3e83e19c_refits.py`, `paper_displays_215.py` and the phase/model-curve scripts record the original calculation sequence and command options; see their retained execution receipts and READMEs. For example, recompute the five retained MEA model-curve families with:

```bash
UV_NO_SYNC=1 nice -n 10 uv run python analyses/mea_parameter_bundle/scripts/model_curves.py
```

These are expensive calculation reruns, separate from rendering retained results.

For MDEA, create a separate Python 3.13 environment with the d5138209 wheel, numpy and scipy; use that interpreter with `-I` for `{M}/scripts/refit_capped.py`, then `assess_capped.py` and `compare_capped_starts.py`. Their input declarations and precondition receipts are retained under `inputs/`, `results/item-l/` and `results/stage2-density/`. These scripts refit and overwrite results; use a disposable copy. Native calculation replay was not attempted here because the wheels and HSL are omitted. Retained unavailable comparisons remain unavailable.

## Build identities and inventories

- Main PDF: SHA-256 `{pdfs['main']['sha256']}` (25 pages).
- Supplement PDF: SHA-256 `{pdfs['supplement']['sha256']}` (20 pages).

`manifest.json` lists each payload file's role, byte size and SHA-256, plus manuscript, parameter, Engine and PDF identities. As in the earlier staging approach, it excludes itself and `SHA256SUMS` to avoid a recursive checksum. `SHA256SUMS` covers all final files except itself, including the manifest. `provenance/verification.json` records the cited-name and endpoint checks. These checks establish file identity and staging completeness; they add no new scientific result.
'''
    (DEST / 'README.md').write_text(readme)
    write('provenance/verification.json', dict(cited_name_mapping=mapping, cited_names_complete=True,
          mea_parameter_sha256=parameter, mdea_endpoint_sha256=endpoints, pdfs=pdfs))
    files = sorted(p for p in DEST.rglob('*') if p.is_file() and p not in (DEST / 'manifest.json', DEST / 'SHA256SUMS'))
    entries = [dict(path=str(p.relative_to(DEST)), role=('manuscript source or display' if str(p.relative_to(DEST)).startswith(L) else 'retained data, provenance, environment or application code'), bytes=p.stat().st_size, sha256=sha(p)) for p in files]
    write('manifest.json', dict(publication='preparation only; nothing published', manuscript_commit=SOURCE,
          mea_notebook_commit=NOTEBOOK, mdea_notebook_commit=MDEA_NOTEBOOK,
          mea_parameter_sha256=parameter, mea_engine=engine, mdea_engine=mdea, pdfs=pdfs, files=entries))
    files = sorted(p for p in DEST.rglob('*') if p.is_file() and p != DEST / 'SHA256SUMS')
    (DEST / 'SHA256SUMS').write_text(''.join(f'{sha(p)}  {p.relative_to(DEST)}\n' for p in files))
    print(json.dumps(dict(path=str(DEST), files=len(files)+1, bytes=sum(p.stat().st_size for p in files)+(DEST/'SHA256SUMS').stat().st_size)))


if __name__ == '__main__':
    if sys.argv[1:] == ['stage']:
        stage()
    elif sys.argv[1:] == ['seal']:
        seal()
    else:
        raise SystemExit('Use stage (empty destination), then render PDFs there, then seal.')
