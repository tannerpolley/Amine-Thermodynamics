"""Refuse to run unless the installed epcsaft is byte-identical to the pinned Engine wheel e6dae5c7."""
import hashlib, zipfile
from pathlib import Path
import epcsaft
WHEEL = Path('/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT/build/wheels/main-e6dae5c7/epcsaft-1.2.0-cp313-cp313-manylinux_2_39_x86_64.whl')
SHA256 = '83ede7d2722d3581603f6e4139c614b8bbfc903ce90609c90b802d46eea77dd6'
assert hashlib.sha256(WHEEL.read_bytes()).hexdigest() == SHA256
with zipfile.ZipFile(WHEEL) as z:
    assert all(z.read(n) == (Path(epcsaft.__file__).parents[1] / n).read_bytes() for n in z.namelist() if n.startswith('epcsaft/') and not n.endswith('/'))
