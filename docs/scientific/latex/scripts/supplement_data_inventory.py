"""Generate the reviewed 34-entry table from the corrected source manifest.

Usage: python scripts/supplement_data_inventory.py MANIFEST [ZOTERO_BIB]
Output: tables/supplement_data_inventory.tex. No observations are admitted.
"""
import csv
import hashlib
import re
import sys
from pathlib import Path

SELECTED = '''Wong2015 Idris2014 Amundsen2009 Fan2009 Jou1995 Aronu2011
Wagner2013 Park2002 Mamun2005 Tong2012 Dugas2011 Dugas2009 Xu2011
Hilliard2008 Bottinger2008 Jakobsen2005 Matin2012 Wong2016 Yamada2012
Kim2007 Kim2014 Mathonat1998 Arcis2011 Vinjarapu2024 Han2012 Hartono2014
Jayarathna2013 Weiland1998 Weiland1997 Ganesan2026 Concepcion2023
Karunarathne2020 Won16c Sob16b'''.split()
SALT = {'Wong2015', 'Wong2016', 'Won16c'}
manifest = Path(sys.argv[1]).resolve()
bib = Path(sys.argv[2] if len(sys.argv) > 2 else '~/Zotero/exports/references.bib').expanduser()
entries = {m.group(1): m.group(0) for m in re.finditer(
    r'^@\w+\{([^,]+),.*?^\}\s*$', bib.read_text(), re.S | re.M)}

def field(entry, name):
    m = re.search(r'^\s*' + name + r'\s*=\s*\{(.*?)\},?\s*$', entry, re.M)
    return m.group(1) if m else ''

def doi(value):
    return re.sub(r'^https?://(?:dx\.)?doi.org/', '', value.strip().lower())

by_doi = {}
for key, entry in entries.items():
    value = doi(field(entry, 'doi'))
    if value:
        by_doi.setdefault(value, []).append(key)

with manifest.open(newline='') as handle:
    rows = list(csv.DictReader(handle))
lookup = {r['source_key']: r for r in rows}
assert len(SELECTED) == len(set(SELECTED)) == 34
assert len(lookup) == len(rows)
assert sum(r['evidence_level'] == 'discovery_metadata_only' for r in rows) == 88

# Plain-language readings of the inventory status codes.
ACCESS = {
    'PDF_in_Zotero': 'Full text available',
    'open_access_primary_PDF_web_accessible;not_in_Zotero': 'Open-access full text',
    'primary_PDF_web_accessible;not_in_Zotero': 'Full text available online',
    'NIST_ThermoML_machine_readable;PDF_not_obtained;not_in_Zotero': 'NIST ThermoML record; full text not obtained',
    'not_found_in_Zotero': 'Original full text not obtained'}
EVIDENCE = {
    'primary_passage_or_table_verified': 'Checked against a primary passage or table',
    'primary_database_metadata_verified': 'Checked against a primary database record',
    'main_method_verified_SI_numerical_basis_unverified':
        'Method checked against the article; numerical values not checked against the supporting tables'}
EXTRACTION = {
    'not_extracted': 'Values not extracted',
    'extracted': 'Values extracted',
    'extracted_digitized': 'Values digitized from figures',
    'extracted_physical_CO2_solubility': 'Physical CO2 solubility values extracted',
    'extracted_all_density_viscosity_tables': 'All density and viscosity tables extracted',
    'extracted_VLE_partially_speciation': 'VLE values extracted; speciation values partly extracted',
    'extracted_near_30wt_source_tables_no_admission': 'Near-30 wt% source tables extracted; not fitted',
    'partially_extracted_speciation': 'Speciation values partly extracted',
    'partially_extracted_total_pressure': 'Total-pressure values partly extracted',
    'partially_extracted_diagnostic_only': 'Values partly extracted',
    'partially_extracted_VLE;NMR_and_Cp_not_extracted': 'VLE values partly extracted; NMR and heat-capacity values not extracted',
    'Table_2_state_coverage_complete_no_new_admission': 'All Table 2 states extracted; not fitted',
    '30wt_Table_4_measured_state_coverage_complete_no_new_admission': 'All 30 wt% Table 4 measured states extracted; not fitted',
    'MEA_Tables_1_to_3_complete_source_archive_duplicate_linked_no_admission':
        'MEA Tables 1-3 extracted; rows linked to the same retained states; not fitted',
    '30wt_paired_VLE_and_heat_source_tables_complete_duplicate_heat_linked_no_admission':
        '30 wt% paired VLE and heat tables extracted; heat rows linked to the same retained values; not fitted',
    'pure_aqueous_baseline_Tables_4_and_5_complete_duplicate_linked_no_admission':
        'Pure aqueous baseline Tables 4 and 5 extracted; rows linked to the same retained values; not fitted',
    'numeric_Tables_1_and_2_extracted_integral_loading_curves_figure_only':
        'Numeric Tables 1 and 2 extracted; integral loading curves given only as figures'}
assert all(lookup[k]['access_status'] in ACCESS and lookup[k]['evidence_level'] in EVIDENCE
           and lookup[k]['repo_extraction_status'] in EXTRACTION for k in SELECTED)

# Zotero item keys (eight upper-case letters and digits) are library handles, not locators.
ZOTERO_KEY = r'\b(?=[A-Z0-9]*\d)(?=[A-Z0-9]*[A-Z])[A-Z0-9]{8}\b'

def locator(value):
    keep = []
    for part in value.split(';'):
        part = re.sub(r'hash-verified literature/\S+\.md', '', part)
        part = re.sub(r'(?:\b(?:Zotero|live|PDF) )*' + ZOTERO_KEY + r'(?:/[A-Z0-9]{8}\b)? ?', '', part)
        # Repository holdings and search tools are not places in the source.
        if part.strip() and not part.strip().startswith('retained') and 'Undermind' not in part:
            keep.append(part)
    return ';'.join(keep)

PROPERTY = {
    'VLE': 'VLE', 'speciation': 'speciation', 'pH': 'pH', 'density': 'density',
    'unloaded_density': 'unloaded density', 'heat_capacity': 'heat capacity',
    'absorption_heat': 'heat of absorption', 'total_pressure': 'total pressure',
    'derived_VLE': 'derived CO2 pressure', 'derived_carbamate_constants': 'derived carbamate constants',
    'calorimetry_derived_solubility': 'solubility derived from calorimetry',
    'physical_CO2_solubility': 'physical CO2 solubility'}
assert all(t in PROPERTY for k in SELECTED for t in lookup[k]['property_family'].split(';'))

def properties(row):
    return '; '.join(PROPERTY[t] for t in row['property_family'].split(';'))

def derived(row):
    return 'Derived quantity.' if 'derived' in row['property_family'] else ''

def units(value):
    # 40C, 99.75 degC -> 40 °C; 372.9K -> 372.9 K. 13C NMR is carbon-13, not a temperature.
    value = re.sub(r'(\d)\s?(?:degC|C)\b(?!\s*NMR)', '\\1 °C', value)
    return re.sub(r'(\d)(K|MPa|kPa|Pa|bar)\b', r'\1 \2', value)

def tex(value):
    # Escape without rewriting source wording or whitespace. URLs own their breaks.
    replacements = {'\\': r'\textbackslash{}', '&': r'\&', '%': r'\%',
                    '$': r'\$', '#': r'\#', '{': r'\{', '}': r'\}',
                    '_': r'\_', '~': r'\textasciitilde{}', '^': r'\textasciicircum{}', '°': r'\textdegree{}'}
    result = []
    for part in re.split(r'(https?://[^\s;]+)', value):
        if part.startswith(('http://', 'https://')):
            result.append(r'\url{' + part + '}')
            continue
        for token in re.split(r'(\s+)', part):
            long_token = len(token) > 12 and any(c in token for c in '/_.-')
            for char in token:
                result.append(replacements.get(char, char))
                if char in ';,:' or (long_token and char in '/_.-'):
                    result.append(r'\allowbreak{}')
    return ''.join(result)

# Curation-workflow notes in the inventory fields become plain statements of what is known.
PLAIN = [(r'exact scope pending basis review', 'exact scope not determined'),
         (r'visual reader count provisional', 'count read from the figure'),
         (r'Raman scope requires separate review', 'Raman scope not determined'),
         (r'source species basis verify', 'source species basis not determined'),
         (r'numerical legacy packet\s?20\s?°?\s?C not source verified', 'calculated here at 20 °C'),
         (r'\bpending\b', 'not determined'),
         (r'\bunverified\b', 'not determined')]

def plain(value):
    for pattern, replacement in PLAIN:
        value = re.sub(pattern, replacement, value, flags=re.I)
    return value

def paragraphs(parts):
    return r'\par '.join(tex(plain(p)) for p in parts if p)

caption = (r'Published measurements near 30 wt\% aqueous MEA: 34 publications whose near-30 wt\% scope is '
           r'confirmed from a primary passage, table or database record. Mass fraction, molality '
           r'(per kg water or solution), and molarity remain distinct reported bases; no equivalence '
           r'is assumed. The three marked Wong studies contain sodium perchlorate reference salt; '
           r'NMR dilution and additives can change the final liquid composition. Derived quantities are '
           r'marked; counts are not additive across publications or properties. ``Not determined'' marks a field that '
           r'could not be established from the source; it never means zero. Temperature '
           r'envelopes are in K; reported property-specific temperatures retain their stated units. '
           r'The per-source notes, including campaign overlap and reused states, are in the '
           r'public inventory file \nolinkurl{data/reference/MEA/manifests/source_status_manifest.csv}.')
# "Retained" counts what was extracted from each source, not what this work fitted.
COUNTS = [('Near-30 wt% published: ', 'near_30wt_point_count'),
          ('Extracted for this work: ', 'retained_point_count'),
          ('Published values: ', 'published_point_count'),
          ('Count basis: ', 'point_count_scope')]
headers = ['Reference', 'Quantity and method', 'MEA composition', 'Temperature / K',
           'Loading and pressure', 'Observation counts', 'Evidence and extraction', 'Locator and caveats']
head = ' & '.join(r'\textbf{' + h + '}' for h in headers) + r' \\'
output = [
    '% Generated by scripts/supplement_data_inventory.py; do not hand-edit values.',
    '% Source manifest SHA-256: ' + hashlib.sha256(manifest.read_bytes()).hexdigest(),
    '% Requires longtable, pdflscape, array, booktabs, xurl and a citation package.',
    r'\begin{landscape}', r'\begingroup', r'\fontsize{7}{8.4}\selectfont',
    r'\setlength{\tabcolsep}{2pt}', r'\setlength{\LTcapwidth}{24.5cm}', r'\renewcommand{\arraystretch}{1.08}',
    r'\begin{longtable}{@{}' + ''.join(r'>{\raggedright\arraybackslash}p{' + str(w) + 'cm}'
                                      for w in [2.0, 3.0, 3.3, 2.6, 3.2, 3.6, 2.2, 3.7]) + r'@{}}',
    r'\caption{' + caption + r'}\label{tab:s4-data-inventory}\\',
    r'\toprule', head, r'\midrule', r'\endfirsthead',
    r'\multicolumn{8}{l}{\tablename~\thetable{} (continued)}\\',
    r'\toprule', head, r'\midrule', r'\endhead',
    r'\midrule\multicolumn{8}{r}{Continued on next page}\\', r'\endfoot',
    r'\bottomrule', r'\endlastfoot']
missing = []
for source in SELECTED:
    r = lookup[source]
    candidates = by_doi.get(doi(r['doi']), []) if r['doi'] else []
    key = r['citation_key'] if r['citation_key'] in candidates else (candidates[0] if candidates else '')
    # Hilliard's dissertation has no DOI: check its supplied key against the title.
    if not r['doi'] and r['citation_key'] in entries:
        normalize = lambda s: re.sub(r'[^a-z0-9]', '', s.lower())
        if normalize(field(entries[r['citation_key']], 'title')) == normalize(r['title']):
            key = r['citation_key']
    if not key:
        missing.append(source)
    label = {'Won16c': 'Wong 2016', 'Sob16b': 'Sobrino 2016'}.get(
        source, re.sub(r'(?<=[A-Za-z])(?=\d{4}$)', ' ', source))
    reference = tex(label) + (r' \cite{' + key + '}' if key else r' (citation key unavailable)')
    if r['doi']:
        reference += r'\par DOI: \url{' + r['doi'] + '}'
    if source in SALT:
        reference += r'\par\textbf{Salt-containing study}'
    temperatures = r['temperature_min_K'] + ('--' + r['temperature_max_K']
                    if r['temperature_max_K'] != r['temperature_min_K'] else '')
    cells = [reference,
             paragraphs([properties(r), r['measurement_method']]),
             paragraphs([r['concentration_reported'], 'Basis: ' + r['concentration_basis']]),
             paragraphs([temperatures + ' K' if r['temperature_min_K'] else 'Not determined',
                         'Reported: ' + units(r['temperature_reported'])]),
             paragraphs(['Loading: ' + units(r['loading_range_reported'] or 'not determined'),
                         'Pressure: ' + units(r['pressure_range_reported'] or 'not determined')]),
             paragraphs([units(label + (r[column] or 'not determined')) for label, column in COUNTS]),
             paragraphs([ACCESS[r['access_status']], EVIDENCE[r['evidence_level']],
                         EXTRACTION[r['repo_extraction_status']]]),
             paragraphs([locator(r['evidence_locator']), derived(r)])]
    output += ['% Entry: ' + source, ' & '.join(cells) + r' \\', r'\addlinespace']
output += [r'\end{longtable}', r'\endgroup', r'\end{landscape}', '']
target = Path(__file__).resolve().parents[1] / 'tables/supplement_data_inventory.tex'
target.write_text('\n'.join(output))
print(f'{target}: {len(SELECTED)} entries; missing citation keys: {", ".join(missing) or "none"}')
