"""A selected pressure-table change must stop presentation before its renderer."""

import hashlib
from pathlib import Path
import shutil
import subprocess
import tempfile


def check_missing_or_modified_retained_input(tmp_path):
    snakemake = shutil.which("snakemake")
    assert snakemake, "Put the dedicated presentation interpreter on PATH"
    root = Path(__file__).resolve().parents[1]
    relative = Path("analyses/neutral_pcsaft_pressure_reference")
    source = root / relative
    target = tmp_path / relative
    target.mkdir(parents=True)
    for name in ("Snakefile", "retained-results.sha256"):
        shutil.copy2(source / name, target / name)
    originals = {}
    for line in (source / "retained-results.sha256").read_text().splitlines():
        digest, name = line.split("  ", 1)
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(root / name, path)
        originals[path] = (digest, path.read_bytes())
    scripts = target / "scripts"
    scripts.mkdir()
    view = tmp_path / "previous-view"
    (scripts / "render_figures.py").write_text(
        "from pathlib import Path\nPath('previous-view').write_bytes(b'rendered')\n"
    )
    command = [snakemake, "--cores", "1", "present"]
    completed = subprocess.run(command, cwd=target, capture_output=True, timeout=60)
    assert completed.returncode == 0, completed.stderr.decode()
    assert view.read_bytes() == b"rendered"
    assert all(hashlib.sha256(path.read_bytes()).hexdigest() == digest for path, (digest, _) in originals.items())
    changed = next(iter(originals))
    for failure in ("missing", "modified"):
        view.write_bytes(b"previous presentation")
        if failure == "missing":
            changed.unlink()
        else:
            changed.write_bytes(b"modified pressure table\n")
        completed = subprocess.run(command, cwd=target, capture_output=True, timeout=60)
        assert completed.returncode != 0
        assert view.read_bytes() == b"previous presentation"
        changed.write_bytes(originals[changed][1])
    assert all((root / path.relative_to(tmp_path)).read_bytes() == contents for path, (_, contents) in originals.items())


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as directory:
        check_missing_or_modified_retained_input(Path(directory))
    print("Missing/modified retained input refused; previous view and source values preserved")
