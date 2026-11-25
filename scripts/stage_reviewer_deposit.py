"""Stage the #440 evidence and three worked calculations for referee round 9."""
import argparse
import gzip
import json
from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory

from check_private_source import path_is_blocked, scan
from stage_manuscript_deposit import AMP, B, DEA, MDEA, ROOT, declared_inputs, sha

STUDY = 'analyses/fixed_reaction_reference'
RESULTS = f'{STUDY}/results'
BASE = '5023dbc44885be4675820dea8812576da58c570d'
WORKED_HEAT_REVISION = '13d133739cedc422449491ad8214db8b18e85c99'
WHEELS = (
    ('05e94210fa64cf69725e45babc0411d32139df5a', '1.3.1',
     'c9fbf898b14d004f915f01ed77675867908dd30d77dc28544b2860e9195c80bb'),
    ('391dfe5d64ede5036bf160bc6ae037ad5e14af32', '1.3.0',
     '0962e21d2fa7a8ba1ed4622f1110b3e8053bacd878fa41c999d85e8b9afab66b'),
)
TABLE_8 = {
    'MEA': ('MEA', 'MEA, MEA-fitted shared set',
            f'{B}/results/paper-evidence-341/paper-evidence/reported-parameters.json', []),
    'DEA': ('DEA', 'DEA, 30-pressure Lawson–Garst fit',
            f'{DEA}/results/salt-anchored-435/campaign/selection.json.gz', ['chosen', 'parameters']),
    'MDEA': ('MDEA', 'MDEA, fit with MEA weights',
             f'{MDEA}/results/salt-anchored-435/campaign/selection.json.gz', ['point']),
    'AMP': ('AMP_free', 'AMP, earlier carbamate inputs',
            f'{AMP}/results/salt-anchored-435/free/selection.json.gz', ['point']),
}


def read(path):
    data = (ROOT / path).read_bytes()
    return json.loads(gzip.decompress(data) if path.endswith('.gz') else data)


def selected_files():
    tracked = set(subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT, text=True).rstrip('\0').split('\0'))
    prefixes = (
        f'{STUDY}/', 'analyses/round_7/', 'analyses/round_8/',
        'analyses/solvent_specification_mea/inputs/', 'analyses/solvent_specification_mdea/inputs/',
        f'{B}/data/', f'{B}/scripts/', f'{B}/calibration-misfit/',
        f'{B}/results/adoption-297/historical-spec/', f'{B}/results/reference-states-428/',
        f'{B}/results/salt-anchored-435/', f'{B}/results/carbonate-ions-282/',
        f'{B}/results/paper-evidence-341/same-data-comparison/',
        f'{B}/results/paper-evidence-341/stability/candidate/',
        f'{DEA}/inputs/part-ii-346/', f'{DEA}/results/salt-anchored-435/',
        f'{MDEA}/scripts/', f'{MDEA}/results/salt-anchored-435/',
        f'{MDEA}/results/shared-bicarbonate-417/',
        f'{AMP}/inputs/retransfer-344/phase-2/', f'{AMP}/results/salt-anchored-435/',
        'data/reference/', 'src/', 'scripts/deposit_examples/',
    )
    producer_dirs = ('analyses/round_3/', 'analyses/round_5/', 'analyses/solvent_specification_mea/',
                     'analyses/solvent_specification_mdea/', f'{DEA}/', f'{AMP}/')
    selected = {p for p in tracked if p.startswith(prefixes) or
                (p.endswith('.py') and p.startswith(producer_dirs))}
    selected.update({
        'LICENSE', 'pyproject.toml', 'uv.lock', 'analyses/part_ii.py',
        'analyses/reference_states_428.py', 'analyses/r4_shift_tables_426.py',
        'analyses/permittivity_temperature_loading/dielectric_volume.py',
        'analyses/solvent_specification_mea/declarations.toml',
        f'{B}/results/adoption-340/part-ii-shared-values.json',
        f'{B}/results/paper-evidence-341/paper-evidence/model-curves/heat.csv',
        f'{B}/results/split-cause-342/figure-contributions.csv',
        f'{B}/results/density-cp-160/D1-evidence/F1-A/native-fit.json',
        f'{B}/results/engine-3e83e19c-refit-chain/a6/spec.json',
        f'{B}/results/stable-refit-255/evidence/final/carbonate-share.csv',
        f'{MDEA}/inputs/bounded-binary-411.json', f'{AMP}/source-admission.md',
        'analyses/round_3/results/q1.json',
        *(path for _, _, path, _ in TABLE_8.values()),
        *(f'{AMP}/inputs/{name}' for name in (
            'hartono-2021-table-7.csv', 'tong-2012-table-4.csv', 'hartono-2013-table-3.csv',
            'pure-amp.csv', 'amp-document.json', 'amp-pure-endpoint.json',
        )),
    })
    for path in (
        f'{B}/results/adoption-297/historical-spec/MEA.toml',
        f'{DEA}/inputs/part-ii-346/f2-carbamate-413-route.json',
        f'{MDEA}/inputs/bounded-binary-411.json',
        f'{AMP}/inputs/retransfer-344/phase-2/AMP-05e94210.json',
    ):
        # MDEA uses retained curve predictions in place of the older curve rows.
        selected.update(declared_inputs(path, overridden=('curve_rows',) if path.endswith('411.json') else ()))

    for quantity in read(f'{STUDY}/manuscript-handoff.json')['quantities'].values():
        for record in (quantity.get('old_contributor'), *quantity['new_contributors']):
            if record and record.get('sha256'):
                path = record['path']
                if sha(ROOT / path) != record['sha256']:
                    raise ValueError(f'#440 contributor changed: {path}')
                selected.add(path)
    for name in sorted(selected):
        path = ROOT / name
        if path_is_blocked(name):
            raise ValueError('Private-source identifier in deposit path')
        if name not in tracked or path.is_symlink() or not path.is_file():
            raise ValueError(f'Invalid deposit input: {name}')
    return selected


def model_index():
    models = {}
    for label, (design, old_label, old_path, fields) in TABLE_8.items():
        selection = read(f'{RESULTS}/{design}/selection.json')
        path = f"{RESULTS}/{design}/{selection['selected']}.json.gz"
        if read(path)['endpoint_fingerprint'] != selection['endpoint_fingerprint']:
            raise ValueError(f'#440 selection disagrees with {path}')
        models[label] = dict(path=path, fields=['endpoint'], reaction_reference='fixed at 100 kPa')
        models[old_label] = dict(path=old_path, fields=fields, reaction_reference='system pressure for R1–R3')
    return models


def stage(dest, wheel_dir):
    failures = scan(ROOT)
    if failures:
        raise SystemExit('\n'.join(failures))
    files = selected_files()
    dest.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=dest.parent) as tmp:
        package = Path(tmp) / dest.name
        package.mkdir()
        for name in sorted(files):
            target = package / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)
        engines = []
        for commit, version, digest in WHEELS:
            suffix = Path(f'main-{commit}/epcsaft-{version}-cp313-cp313-manylinux_2_39_x86_64.whl')
            source = wheel_dir / suffix
            if sha(source) != digest:
                raise ValueError(f'Engine wheel SHA-256 mismatch: {source}')
            target = package / 'build/engine-wheels' / suffix
            target.parent.mkdir(parents=True)
            shutil.copyfile(source, target)
            engines.append(dict(path=target.relative_to(package).as_posix(), version=version,
                                engine_commit=commit, sha256=digest))
        (package / 'provenance.json').write_text(json.dumps(dict(
            adopted_fit_commit=BASE, worked_heat_revision=WORKED_HEAT_REVISION, engines=engines,
            table_8_models=model_index(),
        ), indent=2) + '\n')
        shutil.copyfile(ROOT / 'scripts/deposit_examples/README.md', package / 'README.md')
        subprocess.run(['uv', 'export', '--frozen', '--no-dev', '--no-emit-project',
                        '--no-emit-package', 'epcsaft', '--no-emit-package', 'pcsaft',
                        '--format', 'requirements-txt', '--output-file', str(package / 'requirements.txt')],
                       cwd=ROOT, stdout=subprocess.DEVNULL, check=True)
        # uv records the command and temporary path in its banner.
        requirements = package / 'requirements.txt'
        requirements.write_text(''.join(line for line in requirements.read_text().splitlines(keepends=True)
                                        if not line.startswith('#')))
        payload = sorted(p for p in package.rglob('*') if p.is_file())
        manifest = package / 'SHA256SUMS'
        manifest.write_text(''.join(f'{sha(p)}  {p.relative_to(package).as_posix()}\n' for p in payload))
        if dest.exists():
            if sha(dest / manifest.name) != sha(manifest):
                raise FileExistsError(f'{dest} has a different manifest. Choose a new --output.')
            subprocess.run(['sha256sum', '--check', '--quiet', manifest.name], cwd=dest, check=True)
        else:
            package.rename(dest)
        print('# Round 9 reproducibility package\n')
        print(f'- Directory {dest.relative_to(ROOT) if dest.is_relative_to(ROOT) else dest.name}')
        print(f'- Size {sum(p.stat().st_size for p in dest.rglob("*") if p.is_file()):,} bytes')
        print(f'- SHA-256 manifest SHA256SUMS covers {len(payload):,} files')
        print(f'- SHA-256 of SHA256SUMS {sha(dest / manifest.name)}\n')
        print('Top-level entries\n')
        for path in sorted(dest.iterdir()):
            print(f'- {path.name}{"/" if path.is_dir() else ""}')


def main(args=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--wheel-dir', type=Path, default=ROOT / 'build/engine-wheels',
                        help='Directory holding the main-COMMIT subdirectories for both wheels')
    parser.add_argument('--output', type=Path, default=ROOT / 'build/referee-packet-r9/reproducibility')
    options = parser.parse_args(args)
    stage(options.output.resolve(), options.wheel_dir.resolve())
