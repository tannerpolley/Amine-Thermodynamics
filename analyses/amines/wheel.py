"""Identity of the installed Engine from the locked wheel."""

from functools import cache
from hashlib import sha256
from importlib.util import find_spec
from os import getpid
from pathlib import Path
from zipfile import ZipFile
import tomllib

ROOT = Path(__file__).resolve().parents[2]


def verify():
    return _verify(getpid())


def locked_archive():
    with (ROOT / "uv.lock").open("rb") as lock:
        (package,) = (p for p in tomllib.load(lock)["package"] if p["name"] == "epcsaft")
    path = ROOT / package["source"]["path"]
    (entry,) = (w for w in package["wheels"] if w.get("filename") == path.name)
    return path, entry["hash"]


@cache
def _verify(pid):
    path, expected = locked_archive()
    digest = sha256(path.read_bytes()).hexdigest()
    if expected != f"sha256:{digest}":
        raise RuntimeError(f"Engine archive differs from uv.lock: {path}")
    module = find_spec("epcsaft")
    if module is None or module.origin is None:
        raise RuntimeError("Install the locked Engine with uv run --locked")
    installed = Path(module.origin).parent.parent
    with ZipFile(path) as archive:
        for name in archive.namelist():
            if name.startswith(("epcsaft/", "epcsaft.libs/")) and not name.endswith("/"):
                if archive.read(name) != (installed / name).read_bytes():
                    raise RuntimeError(f"Installed Engine differs from the locked wheel: {name}")
    return digest
