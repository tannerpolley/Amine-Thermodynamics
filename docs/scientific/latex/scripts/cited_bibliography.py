"""Copy the entries cited in builds/main.aux and builds/supplement.aux from the central Zotero export, except those kept in transfer_sources.bib.

Usage: python scripts/cited_bibliography.py [EXPORT] > references.bib
EXPORT defaults to ~/Zotero/exports/references.bib. Entries are copied verbatim,
except that local attachment ``file`` fields are dropped and handle eprints become ``url`` fields.
"""
import re
import sys
from pathlib import Path

export = Path(sys.argv[1] if len(sys.argv) > 1 else '~/Zotero/exports/references.bib').expanduser()
latex = Path(__file__).resolve().parents[1]
auxes = [latex / 'builds' / name for name in ('main.aux', 'supplement.aux')]  # other .aux files in builds/ belong to retired documents
cited = {k.strip() for aux in auxes for group in re.findall(r'\\citation\{([^}]*)\}', aux.read_text()) for k in group.split(',')}
cited -= set(re.findall(r'^@\w+\{([^,]+),', (latex / 'transfer_sources.bib').read_text(), re.M))  # entries kept in the companion file
entries = {m.group(1): m.group(0) for m in re.finditer(r'^@\w+\{([^,]+),.*?^\}\n', export.read_text(), re.S | re.M)}
missing = sorted(cited - entries.keys())
if missing:
    sys.exit(f'cited keys absent from {export}: {", ".join(missing)}')
for key in sorted(cited, key=str.lower):
    entry = re.sub(r'^  file = \{.*\},?\n', '', entries[key], flags=re.M)
    # The Elsevier style prints every eprint as arXiv; restore handle URLs that the export turned into eprints.
    entry = re.sub(r'^  eprint = \{(.*)\},\n  eprinttype = \{hdl\},\n', r'  url = {http://hdl.handle.net/\1},\n', entry, flags=re.M)
    # Crossref titles can carry publisher chemical-formula tags (<fc>...</fc>) that the export escapes as text.
    entry = re.sub(r'\{\$<\$\}/?fc\{\$>\$\}', '', entry, flags=re.I)
    # The export of Bower et al. (1962) carries a mis-encoded degree sign in its title.
    entry = re.sub(r'(from 0 to 50 ).*?(\{\$\^\\circ\$\}\{\{C\}\})', r'\1\2', entry)
    sys.stdout.write(entry + '\n')
