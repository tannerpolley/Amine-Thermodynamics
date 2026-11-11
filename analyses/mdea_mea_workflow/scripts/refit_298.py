"""Issue 298 retained replay, pool and input-identity operations."""
import os
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
import concurrent.futures as futures
import gzip
import hashlib
import json
import multiprocessing
from pathlib import Path
import zipfile
from datetime import datetime, timezone

AN = Path(__file__).resolve().parents[1]
ROOT = AN.parents[1]
OUT = AN / 'results/refit-298'
ADOPTION = ROOT / 'analyses/mea_parameter_bundle/results/adoption-297'
SHA = '0962e21d2fa7a8ba1ed4622f1110b3e8053bacd878fa41c999d85e8b9afab66b'
WHEEL = ROOT / 'build/engine-wheels/main-391dfe5d64ede5036bf160bc6ae037ad5e14af32/epcsaft-1.3.0-cp313-cp313-manylinux_2_39_x86_64.whl'

def read(path):
    path = Path(path)
    return json.loads(path.read_bytes() if path.exists() else gzip.decompress(path.with_suffix(path.suffix+'.gz').read_bytes()))

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def write(name, value):
    path = OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    raw=(json.dumps(value, indent=2, allow_nan=False)+'\n').encode()
    if len(raw)>5_000_000:
        path.with_suffix(path.suffix+'.gz').write_bytes(gzip.compress(raw,mtime=0))
        path.unlink(missing_ok=True)
    else:
        path.write_bytes(raw)

def pool(fn, jobs):
    with futures.ProcessPoolExecutor(max_workers=min(int(os.environ['AGENT_HEAVY_CORES']), len(jobs)), mp_context=multiprocessing.get_context('fork')) as executor:
        return list(executor.map(fn, jobs))

def predict(i):
    try:
        pred = s.reg.predict(s.model, ITEMS[i])
        return dict(index=i, meta=META[i], **{k:s.p.shared._jsonable(getattr(pred,k)) for k in ('value','unit','status','message','residual','requested_tolerance_met')})
    except Exception as error:
        return dict(index=i,meta=META[i],value=None,residual=None,status=type(error).__name__,message=str(error),requested_tolerance_met=False)

def identities():
    expected = {'shared-bicarbonate-water.json':'1858e768c0eea431dc8cfb749c8acbf65022834b337df630cd5ae35b4bb5ddf6',
                'shared-R2.json':'1b2b51e77924e7d01f43eebe80e02c7094644ef7a5a5e6ac211ac60dc5673471',
                'shared-R2-declaration.json':'05faae944ed26746a292389368ccd6b712849c92ed1de9822288523d009963fd'}
    hashes={str(ADOPTION/name):sha(ADOPTION/name) for name in expected}
    assert all(sha(ADOPTION/name)==value for name,value in expected.items())
    selected=ROOT/'analyses/mea_parameter_bundle/results/selected-current-best-parameters.json'
    assert sha(selected)=='f8f64820b161377a0d97d1e4ad4f6cea764cd0558dc63231d58e2096988eef97'
    assert sha(WHEEL)==SHA
    import epcsaft
    with zipfile.ZipFile(WHEEL) as archive:
        for name in archive.namelist():
            if name.startswith(('epcsaft/','epcsaft.libs/')) and not name.endswith('/'):
                assert archive.read(name)==(Path(epcsaft.__file__).parent.parent/name).read_bytes(),name
    sources=read(ROOT/'data/reference/MDEA/stage1-sources.json')
    for source in sources['sources']:
        pdf=next((Path.home()/'Zotero/storage'/source['pdf_attachment_key']).glob('*.pdf'))
        assert sha(pdf)==source['pdf_sha256']
        for record in source['files']:
            assert sha(ROOT/record['path'])==record['sha256']
            hashes[record['path']]=sha(ROOT/record['path'])
    for path in [AN/'inputs/probe-reaction-reference.json',AN/'results/diagnosis-unloaded-cp/summary.json',AN/'results/item-l/declaration.json'] + [AN/f'results/stage2-capped/{label}/{name}.json' for label in ('A3','B1') for name in ('endpoint','fit','declaration')]:
        hashes[str(path.relative_to(ROOT))]=sha(path)
    write('identity.json',dict(time_utc=datetime.now(timezone.utc).isoformat(),wheel=str(WHEEL.relative_to(ROOT)),wheel_sha256=SHA,installed_files_byte_identical=True,selected_sha256=sha(selected),inputs=hashes))
