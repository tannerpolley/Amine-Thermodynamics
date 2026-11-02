# PZ source records, issues #237, #239 and #240

Public source assessments only. There are no Engine results, no parameter adoption, no copied measurement tables and no CESAR-1 rows, code or parameters. CESAR-1 (commit `f24611b`) was used only to list filenames and CSV header lines, to find papers.

- [Pure PZ PC-SAFT](pure-pz-pcsaft.md): one published 2B set (Razavi 2019); σ³ association convention; handbook-correlation fitting data; reproduction check defined, not run.
- [Solid phases](solid-phase.md): hexahydrate and anhydrous phase diagram, the loaded liquid window, and the Engine's lack of a solid phase.
- [Kamps 2003, its 2006 temperature correction, and Yi 2024](kamps-2003-yi-2024.md) (#239): total-pressure rows, precipitation, uncertainty, corrected temperatures, the MDEA + PZ blend rows, and the Yi eNRTL cross-check with its Supplementary Information hashes.
- [Derks 2005 and Hartono 2013](derks-2005-hartono-2013.md) (#240): the dilute CO2 partial-pressure rows and their role; PZ–water, AMP–water and AMP–PZ–water ebulliometer VLE; a hand comparison with Hilliard D.2 at 60 °C; Fosbøl 2011 SLE identity.
- `pdf-identities.json`: Zotero parent and PDF keys plus SHA-256 for every PDF read.
- Chemistry, constants and the Hamborg/Hetzer mapping: [chemistry](../chemistry.md). Data blocks: [data map](../data-map.md).

## Zotero additions under #237 (collection `8RZP275E`)

| Source | Parent | PDF | Status |
|---|---|---|---|
| Ermatchkov, Pérez-Salado Kamps & Maurer 2003, JCT 35, 1277 | `43ANFJEV` | `BBMLF2KZ` | added, 13 pages, read §§1–5 and Tables 1–5 |
| Freeman et al. 2010, IJGGC 4, 119 | `W6G2BPXW` | `EXYPAS6E` | added, read §§2–3.1, 3.5 |
| Hetzer, Robinson & Bates 1968, J. Phys. Chem. 72, 2081 | `XFC6H9KP` | `F3YWQANV` | added, read abstract, Eqs.1–4, Tables III and V |
| Ermatchkov et al. 2006, JCED 51, 1788 | `62PA5LDF` | `R3UZX4UN` | added, read methods, model, Tables 1–5 headers and Table 5 |
| Esmaeili et al. 2020, PSEP 141, 95 | `DTTAZ8N3` | `WTWA3L4H` | added, read §2.1 and Table 1 |
| Bishnoi & Rochelle 2000, CES 55, 5531 | `J54B28MY` | `HB9DN6UJ` | added, read abstract and Tables 1–2 |
| Razavi, Khoshsima & Shahriari 2019, IECR 58, 11038 | `FEVGI4LK` | `4L3HXHTI` | added, read abstract, Eq.7, the 2B statement, Table 1 and refs.100, 136 |
| Xu & Rochelle 2011, Energy Procedia 4, 117 | `8J4YS46U` | `HSYX9FUA` | already in the library ("existing" route); read §§2–3.1 and Table 1 |
| Pérez-Salado Kamps, Xia & Maurer 2003, AIChE J. 49, 2662 | `79R7VKJW` | none | metadata only; superseded by `H7EYIXSK` (below) and now in the Zotero trash |
| Derks et al. 2005, AIChE J. 51, 2311 | `ESTCE9HW` | none | metadata only; superseded by `PRYYEZ43` (below) and now in the Zotero trash |

## Zotero items under #239 (collection `8RZP275E`)

| Source | Parent | PDF | Status |
|---|---|---|---|
| Pérez-Salado Kamps, Xia & Maurer 2003, AIChE J. 49, 2662 | `H7EYIXSK` | `VSVC3FEB` | already in the library at the start of #239; all 9 pages read. `WJCXT6TT` is a byte-identical PDF (same SHA-256), now in the Zotero trash. A stray webpage item `VNC9XIW8` with the same title is still in the collection. |
| Yi et al. 2024, Sep. Purif. Technol. 350, 127924 | `SDKLQTBQ` | `3YP4GUWT` | already in the library at the start of #239; §§2–4, Tables 1–5 and the Supplementary Information (downloaded, not attached) read |
| Derks et al. 2005, AIChE J. 51, 2311 | `PRYYEZ43` | none | already in the library at the start of #239, with a saved web page only; merged into `7BYDJFRT` before #240 (below) |
| Hartono, Saeed, Ciftja & Svendsen 2013, Chem. Eng. Sci. 91, 151 | `5KUR8PRH` | `SEPZQIPE` | acquired (Connector); all 11 pages read under #240 |
| Hartono, Rafiq, Gondal & Svendsen 2021, Fluid Phase Equilib. 538, 112992 | `NVDXQ5NY` | `L5BIJ5I8` | acquired (the `elsevier-api` acquisition step of `cse-zotero acquire`); identity checked on page 1, not read |
| Nguyen, Hilliard & Rochelle 2010, IJGGC 4, 707 | `62762ZRK` | `ZA6SU36Z` | acquired (Connector); identity checked on page 1, not read |
| Chen, Caparanga, Soriano & Li 2010, J. Chem. Thermodyn. 42, 54 | `P3ZNCVRZ` | `M8B3RA3J` | acquired (Connector); identity checked on page 1, not read |

The last four are PZ data sources whose identity Yi 2024's SI resolved. Each closes an "identity not resolved" or "not acquired" entry in the data map.

## Zotero items under #240 (collection `8RZP275E`)

| Source | Parent | PDF | Status |
|---|---|---|---|
| Derks, Dijkstra, Hogendoorn & Versteeg 2005, AIChE J. 51, 2311 | `7BYDJFRT` | `MTKZ5MEF` | in the library at the start of #240 (`PRYYEZ43` was merged into it); 17 pages; read pp.2311–2322 (methods, Tables 1, 4–12, results, conclusions) |
| Hartono, Saeed, Ciftja & Svendsen 2013, Chem. Eng. Sci. 91, 151 | `5KUR8PRH` | `SEPZQIPE` | all 11 pages read |
| Kim, Svendsen & Børresen 2008, J. Chem. Eng. Data 53, 2521 | `97LARJKT` | `4SMCK4SC` | already in the library; apparatus and uncertainty paragraphs read (pp.2526, 2528) |
| Fosbøl, Neerup, Arshad, Tecle & Thomsen 2011, J. Chem. Eng. Data 56, 5088 | `BXZRGU3H` | `VVP244A8` | acquired (Connector); abstract, introduction and table titles read |

Existing items read: Hilliard 2008 thesis `DNQUPRMT`/`LB7LUETY` (§§5.3, 9.4.1, 14.3, 14.4 Table 14.4-2, 14.6 and App. D.2, D.5, F.4–F.5, G.3–G.4, H.1, I.1); Hamborg & Versteeg 2009 `D9KXSKLR`/`334KGLPV` (Eqs.6–21, Tables 9–11, 16); Dugas & Rochelle 2011 `NDJWMT4H`/`5H55QKVX` (methods, Table 2); and its correction `TINYKLZD`/`EJBAYJVP`. No deletions, merges, metadata edits, attachments of companions or bibliography refreshes were made. Under #240 the only Zotero write was the Fosbøl 2011 acquisition.

## Not read

- Derks 2005: Figs. 4–12 (not digitized), its nomenclature and literature-cited pages, and the companion kinetics paper (Derks et al. 2006, CES 61, 6837), which was not checked for N2O data.
- Hartono 2013 Supplementary Material (Figs. S1–S7): not obtained.
- Fosbøl 2011 Tables 1–3: not transcribed. Bishnoi & Rochelle 2002 (Ind. Eng. Chem. Res. 41, 604) and Bishnoi's 2000 dissertation, the SLE sources Fosbøl cites: not acquired.
- Wilson & Wilding 1994 (DIPPR 1990–1991 projects, pp.63–115; identity from Hartono 2013 p.161): not acquired.
- Kamps 2003 Figs. 1–7 (not digitized; Fig. 1's reaction scheme was not used to fix reaction directions).
- Yi 2024 SI figures other than S4, S10 and S11. Yi's GitHub model files (github.com/mijndertvanderspek/PZ-CESAR1-thermo-model) were not opened.
- Three PDFs acquired under #239 (Hartono 2021, Nguyen 2010, Chen 2010), beyond their first page. Hartono 2013 was read under #240.
- MDEA + PZ data cited by Kamps 2003 (Bishnoi & Rochelle 2002; Xu et al. 1998; Liu et al. 1999), and the AMP and AMP/PZ data indexed from Yi Tables 4–5.
- Freeman 2011 dissertation, Ma et al. 2012 crystallization, Nguyen 2011/2013 volatility, Chen 2010 PZ–water Cp, Liu and Hartono PZ absorption heat, and the primary publication of Kim's PZ heat data: not acquired, or identity unresolved.
- Hamborg 2009 Supporting Information (EMF data; possibly Eq.21 coefficients): not looked for.
- The primary data behind Razavi's PZ fit (Yaws handbook; Aspen HYSYS databank).
- Hilliard Chapter IX (H2O–PZ parameter fitting) beyond §9.4.1, and the NMR method behind App. F.
- Dugas & Rochelle 2009 (Zotero `B7T53U6N`): its overlap with Dugas 2011 is taken from the correction notice; it was not read.

The main-checkout `literature/` shelf has no PZ paper. It was read, not written. Mathpix was not used: every PDF read has a usable text layer. The local copies made with `pdftotext` were scratch files outside the repository.
