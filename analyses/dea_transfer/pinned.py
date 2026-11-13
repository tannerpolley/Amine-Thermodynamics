"""#317 DEA transfer: pinned Engine wheel, shared paths and species names."""
import hashlib, json, sys, zipfile
from pathlib import Path
import epcsaft

AN = Path(__file__).resolve().parent
ROOT = AN.parents[1]
REF = ROOT / 'data/reference/DEA'
WHEEL = ROOT / 'build/engine-wheels/main-391dfe5d64ede5036bf160bc6ae037ad5e14af32/epcsaft-1.3.0-cp313-cp313-manylinux_2_39_x86_64.whl'
SHA = '0962e21d2fa7a8ba1ed4622f1110b3e8053bacd878fa41c999d85e8b9afab66b'
MEA = ROOT / 'analyses/mea_parameter_bundle/results/selected-current-best-parameters.json'
MEA_SHA = 'f8f64820b161377a0d97d1e4ad4f6cea764cd0558dc63231d58e2096988eef97'
DEA, H, C, W, CO2 = 'diethanolamine', 'protonated-diethanolamine', 'carbamate-anion', 'water', 'carbon-dioxide'
SHARED = (W, CO2, 'bicarbonate-anion', 'carbonate-anion', 'hydronium-cation', 'hydroxide-anion')
M_DEA, M_W = 0.105137, 0.01801528
sys.path.insert(0, str(ROOT / 'src'))


def verify_wheel():
    assert hashlib.sha256(WHEEL.read_bytes()).hexdigest() == SHA
    assert hashlib.sha256(MEA.read_bytes()).hexdigest() == MEA_SHA
    with zipfile.ZipFile(WHEEL) as archive:
        for name in archive.namelist():
            if name.startswith('epcsaft/') and not name.endswith('/'):
                assert archive.read(name) == (Path(epcsaft.__file__).parent.parent / name).read_bytes(), name


def save(path, value):
    text = json.dumps(value, indent=1, default=float) + '\n'
    (AN / path).parent.mkdir(parents=True, exist_ok=True)
    (AN / path).write_text(text)
    return hashlib.sha256(text.encode()).hexdigest()
