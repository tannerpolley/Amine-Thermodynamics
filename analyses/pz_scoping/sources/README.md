# PZ source records, issue #237

Public source assessments only. There are no Engine results, no parameter adoption, no copied measurement tables and no CESAR-1 rows, code or parameters. CESAR-1 (commit `f24611b`) was used only to list filenames and CSV header lines, to find papers.

- [Pure PZ PC-SAFT](pure-pz-pcsaft.md): one published 2B set (Razavi 2019); σ³ association convention; handbook-correlation fitting data; reproduction check defined, not run.
- [Solid phases](solid-phase.md): hexahydrate and anhydrous phase diagram, the loaded liquid window, and the Engine's lack of a solid phase.
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
| Pérez-Salado Kamps, Xia & Maurer 2003, AIChE J. 49, 2662 | `79R7VKJW` | none | metadata only; Wiley needs the owner's login with the VPN off (hand-off https://doi.org/10.1002/aic.690491019) |
| Derks et al. 2005, AIChE J. 51, 2311 | `ESTCE9HW` | none | metadata only; same Wiley hand-off (https://doi.org/10.1002/aic.10442) |

Existing items read: Hilliard 2008 thesis `DNQUPRMT`/`LB7LUETY` (§§5.3, 9.4.1, 14.3, 14.4 Table 14.4-2, 14.6 and App. D.2, D.5, F.4–F.5, G.3–G.4, H.1, I.1); Hamborg & Versteeg 2009 `D9KXSKLR`/`334KGLPV` (Eqs.6–21, Tables 9–11, 16); Dugas & Rochelle 2011 `NDJWMT4H`/`5H55QKVX` (methods, Table 2); and its correction `TINYKLZD`/`EJBAYJVP`. No deletions, merges, metadata edits, attachments of companions or bibliography refreshes were made.

## Not read

- Kamps 2003 and Derks 2005: PDFs unavailable (above). Their sizes and ranges are quoted from Ermatchkov 2006 Table 5 only.
- Bishnoi 2002 SLE, Freeman 2011 dissertation, Ma et al. 2012 crystallization, Nguyen 2011/2013 volatility, Hartono 2013 PZ–water VLE, Chen 2010 PZ–water Cp, Liu and Hartono PZ absorption heat, and the primary publication of Kim's PZ heat data: not acquired, or identity unresolved.
- Hamborg 2009 Supporting Information (EMF data; possibly Eq.21 coefficients): not looked for.
- The primary data behind Razavi's PZ fit (Yaws handbook; Aspen HYSYS databank).
- Hilliard Chapter IX (H2O–PZ model regression) beyond §9.4.1, and the NMR method behind App. F.
- Dugas & Rochelle 2009 (Zotero `B7T53U6N`): its overlap with Dugas 2011 is taken from the correction notice; it was not read.

The main-checkout `literature/` shelf has no PZ paper. It was read, not written. Mathpix was not used: every PDF read has a usable text layer. The local copies made with `pdftotext` were scratch files outside the repository.
