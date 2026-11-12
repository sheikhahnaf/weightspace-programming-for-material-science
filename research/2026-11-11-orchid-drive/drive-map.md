# ORCHID shared drive: map for a (table image -> Opus extraction) dataset

Date: 2026-11-11. Read-only reconnaissance through the Google Drive connector. Nothing in the drive was created,
edited, moved or shared. Drive: `2026_ORCHID_Project` (id given `0AP-TnVrOcJ7sUk9PVA`).

Evidence levels used below: **READ** = I opened the file; **LISTED** = seen in a folder listing (name, size, id);
**STATED** = a README in the drive says so; **INFERRED** = my conclusion, not checked.

## 0. Bottom line

- The **inputs exist**: 1,418 assessment-paper PDFs sit loose in `01_Primary_Sources/Assessment_Papers` (STATED count,
  LISTED sample). No per-table crop PNGs of journal tables are on the drive (INFERRED from two title searches and
  from the code README, which says crops and caches are not included).
- The **labels exist only in merged form**: per-table record stores (`master/` for invariant tables, `records/` for
  general tables), one JSONL per table, named by PDF, table label and page. They hold the consensus observations and
  list which readers agreed. The **raw per-reader answers (the Opus JSON for each crop) and the crop PNGs are in
  `gemini-cache/` and `claude-reads/done/` on the PI's Mac Studio, not on the drive** (STATED in the pipeline README).
- The **crop is reproducible**: the cropping code, DPI and rule are in the code snapshot, and the exact prompt and
  JSON schema the reader received are there too. So pairs can be rebuilt as (re-rendered crop, consensus rows that
  list `claude-opus-5.5` among their readers).
- **Everything usable as input is restricted**: publisher PDFs and anything rendered from them are drive-only.

## 1. Layout as the authors describe it (READ: README.md, CURRENT_PROJECT_INDEX, ORCHID_PROJECT_OVERVIEW)

| Folder | Id | Content |
|---|---|---|
| 00_README_and_Index | `12CawGiRVzd4Kfs4T05KqvbRLuXVxbfMH` | README, manifests, restricted list, overview, knowledge base |
| 01_Primary_Sources | `1OcQj_SyLxG9LEO2lCvVeY7KX-3GIx3pY` | TDB files, hull snapshots, Assessment_Papers, Cited_Original_Sources, Handbooks, ILL scans |
| 02_Raw_Extractions | `1uSOKHTLXe7c1At2K1q_QOj-nKu8nb2BT` | Okamoto handbook run h only; `Tables_Invariant_and_General` is empty |
| 03_Processed_Data | `1Sec1smnYeTULK8QpOR3irT52EVje9IwF` | Invariant_Reactions, Thermochemical_Tables, data release v2026.10, private candidate, hulls, figures |
| 04_Review_and_Audits | `1ZLNHy0kgGfJ1Uj2hhV1-sxbfId9eY_Mi` | expert answers, adjudicator decisions, re-verification, audits A1-A6 |
| 04_Review | `1PtwP50-oMdpj6C-lTYA9U3oL1ri35cOs` | `precision_review` (human review kit, student reviews, supplement) |
| 06_Code_Snapshots | `1NgQ7-n-9hTMmpWvSLPDLNyxKvX5WCK2r` | code exports; `orchid-pipeline` holds the table readers |
| 08_Documentation | `1ebrqKKK57De_JHmNSOlpQij0zKUjTIiT` | project memory 00-12, receipts, figure-extraction handover |

Key index files in 00: `README.md` `1SFMD7Az-fzglGMXc-kJHdDf-0fMyTLhd`, `ORCHID_PROJECT_OVERVIEW.md`
`1gHx9gu7MVmTQi252J5TaQEo1vf652Nl-`, `CURRENT_PROJECT_INDEX_2026-10-26.md` `1PzHtxAWAfQ9cxBqDjNrk_2MEcpxiGlcX`,
`ORCHID_KNOWLEDGE_BASE.md` `1AljzH86LIM3YY1GeqNdrc0X1AztVFdKN` (109 kB, not read), `MANIFEST.tsv`
`16BiogABktzctt2X1lHjmGF7IXIUVqCMb` (2.2 MB: path, bytes, sha256 of every file), `MANIFEST_FLAGS.tsv`
`1WtMjmgoaNDBAAMhgoRt2n4SWpHPsmMyR` (adds the restricted flag), `RESTRICTED_LOCAL_ONLY.tsv`
`1EtFLWwq0zgqTH4U_XiI9qa-Owd2eWokN`, `PACKED_GROUPS.tsv` `1KOqRj-S2dyUOaT35roU5hdpiA7066nsz`.

Drive size (STATED, 2026-10-24 snapshot): 13,554 files, 7.54 GB packed; 9,145 restricted files, 6.42 GB. Many
small-file groups are packed as `<group>__packed_20261024.tar.zst` with an `INDEX.tsv.gz` beside them.

Release numbers (STATED, overview of 2026-10-28): ORCHID-Values 73,542 records from 1,321 papers; 66,551 accepted;
11,161 ESPEI-ready; 1,892 certified.

## 2. Source PDFs and images (01_Primary_Sources)

| Subfolder | Id | Content | Count / size (STATED) |
|---|---|---|---|
| Assessment_Papers | `13HttJBpTX4dwseQtLciFlpsmY_1pO9ZB` | publisher PDFs, loose | 1,418 files, 1.89 GB |
| Assessment_Papers/inter-library_ILL_scans | `13J66J1LszwTLIp8cZHkuyFPjP3SXcoNl` | scanned papers | 158 files, 1.13 GB |
| Cited_Original_Sources | `16-dDF3RxPDfBRzYGciFSkI32bQlgbyN2` | `elsevier`, `publishers`, `_reference_lists` | 1,165 + 1,822 PDFs, 2.19 GB |
| Handbooks | `1mCgVlS8LdqD5W66gK--gWDiwJch4g5Hu` | Okamoto desk handbook PDF (81 MB), one Springer book | 2 PDFs + 1 book |
| Handbooks/Okamoto_page_images_and_crops_run-h | `1bGyuaRAZF_vq0j2gKdY19cynR7Ur8jMp` | `pages/`, `systems/` | 4,556 images, 1.08 GB |
| ILL_Get_It_For_Me | `1THwX_7QjLlF28sB0mGJyHkhv8sHNh2ZI` | not opened | - |

- **Naming** (LISTED): `<NNNN>_<doi with "/" replaced by "_">.pdf`, e.g. `1895_10.1016_j.calphad.2004.09.002.pdf`
  (id `1FBojyJQr8230tRJdHhrG1t9Z1J7QbVnY`, 955 kB). The record stores refer to the same file as
  `references/pdfs/1895_10.1016_j.calphad.2004.09.002.pdf`, so the join is by file name.
- Typical PDF size 0.1-1.5 MB, a few near 9 MB (LISTED, first 50).
- **Per-page images or table crops of journal papers: none found.** The only page images and crops on the drive are
  the Okamoto handbook ones (phase-diagram drawings, not tables). The pipeline README says the original run used a
  private local corpus of about 5,700 PDFs, more than the drive's 1,418 + 2,987.

## 3. Extraction outputs

### 3.1 Where they are

`02_Raw_Extractions` holds only the handbook annotation run (`okamoto-annotation-run-20261021h`); its
`Tables_Invariant_and_General` folder lists as empty. The table extractions are under `03_Processed_Data`:

| Store | Folder id | Loose files | Packed archive (id, size) | Unpacked (STATED) |
|---|---|---|---|---|
| Invariant-reaction tables | `1xQlh1RuiuqxWlYsgjuW71oQvHuogUNSQ` | `master/` `1aLYwnPSiZZbqiH30tah8EgMUHfquA1V3` (per-table JSONL, at least 5 loose) | `master__packed_20261024.tar.zst` `1J2KAE9wp5I8LPq4ZphrmU9t2fDvho-zr`, 7.3 MB; index `1QToL1aRqTytL0y2aeQnj2ptjrOkqwLvz` | 1,449 files, 238 MB |
| General thermochemical tables | `1peaf92klAoWZuGip1y9mCZHyQxMTpJM8` | `quarantine/`, `second-reader-requests/`, `awaiting-reader/`, `sr2-finalize/`, `structures/` | `records__packed_20261024.tar.zst` `1UiJ5kOmR3Dhq82iJq3I9ZLQfiNLl1lHC`, 7.6 MB; index `1PSNORP2gyjCuZ_rdfsPh9I44tMjqXVnH` | 2,293 files, 325 MB |
| Same folder | | `flash_tables.jsonl` `1b8M-Y16hewICehnK3BXerPefWceUypF3`, 8.7 MB (not read: JSONL is not readable through the connector's text reader; likely the Gemini Flash table inventory, INFERRED) | | |
| Public release (merged) | `15G9slwtaw_nh_n39SkPUkMWQ53mwCLqw` | README, NOTICE, LICENSES | `literature__packed_20261024.tar.zst` `1et-ji5qi5o4bNtWh18n0ZCUCd_VVLiH8`, 25.6 MB; index `1TyeEyakIer45Sm-iHZfms4ZaWkW2ZJbt` | contains `orchid-literature.jsonl.gz`, `systems/*.json`, `papers.json` |
| Newer private candidate | `1Qaya3KuMlpwyVB6-nDBCysHSmnyIuu6d` | not opened | - | 2026-10-26 build |

**Table-level counts** (READ, `sr2-finalize/counts_after.json` `1e39_sKYyLMi4-RCmDEnmA6WpcZP8Lek5`): general tables
`final_tables` 3,060 with `final_observations` 47,099. Invariant store: 1,449 files (one per table, INFERRED from
naming). So about **4,500 table-level files** in total.

### 3.2 File naming and back-pointers

Per-table file name: `references-pdfs-<NNNN>-<doi-slug>-pdf.table-<label>.p<page>.jsonl`
(e.g. `references-pdfs-1895-10-1016-j-calphad-2004-09-002-pdf.table-3.p6.jsonl`). A record points back by:

- `asset`: `doi:10.1016/j.calphad.2004.09.002/p6/tab-3` (paper DOI, PDF page, table label)
- `id` / row id: `obs:artifact:10-1016-j-calphad-2004-09-002:p6:table-3:row-00:p0`
- `pid`: `doi:.../p6/tab-3/r01#equilibrium_property`
- `readings`: one id per reader, e.g. `reading:artifact:...:row-00:claude-opus-5-5`, `...:gemini-3-8-flash`, `...:text-layer`

There are **no bounding boxes and no crop file names in the observation record** I read. The crop recipe
(`crop_box_pdf_points`, `dpi`, renderer, `crop_png_sha256`) is written into the `_meta` of each cached reader
answer, which lives in the Mac Studio cache (READ in `gemini_table_reader.py`). Whether the packed per-table JSONL
also carries the `reading` records with that `_meta` was not checked (the archives are binary); the file sizes
(37-314 kB per table) suggest they hold more than the observations.

### 3.3 One real record (READ, `quarantine/…calphad-2004-09-002-pdf.table-3.p6.jsonl`, id `159Y-owRLlSvHAhnkLc6Urzu7Pun9Chsj`, abridged)

```json
{"record_type": "observation", "schema_version": 3,
 "id": "obs:artifact:10-1016-j-calphad-2004-09-002:p6:table-3:row-00:p0",
 "asset": "doi:10.1016/j.calphad.2004.09.002/p6/tab-3",
 "system": ["O", "ZR"], "component": "ZRO2",
 "observation_type": "equilibrium_property", "quantity": "CPM",
 "printed_quantity": "Heat capacity", "value": 50.33, "unit": "unknown",
 "uncertainty": {"basis": "printed", "value": 0.33},
 "conditions": {"T_K": 298.0, "T_basis": "printed", "P_Pa": 101325, "P_basis": "unstated_assumed"},
 "phases": [{"printed_label": "monoclinic ZrO2"}],
 "origin": "experimental", "origin_basis": "cited_work_before_1980_assumed_experimental",
 "quality": {"checks": [{"check": "multi_reader_consensus",
   "detail": {"agreement": "unanimous", "readers": ["gemini-3.8-flash", "claude-opus-5.5", "text_layer"]}}],
   "status": {"extraction_accepted": true, "reader_tier": "preliminary_flash+claude"}},
 "_tool_release": "tools-release-v2.1.18"}
```

This is a normalised observation, not the reader's raw transcription. The release schema
(`literature_SCHEMA.md`, id `1Jr7LOYlBF5iPl1mCXwvDS_f76SSr09ME`, READ) adds `value_printed`, `unit_printed`,
`temperature_printed`, `locator {artifact, label, caption, page, row}`, `readers`, `reader_agreement`
(`multi_reader`, `single_reader`, `single_reader_text_layer`), `flags.extraction_accepted`, `tool_release`.

### 3.4 Which model and prompt

- Readers (READ): `gemini-3.8-flash` first, `claude-opus-5.5` second, a blind `claude-opus-5.5#2` where needed,
  `gemini-3.1-pro-preview` as tie-break, plus the PDF text layer. Opus ran as Claude Code subagents through a file
  broker, not through the API.
- Prompt versions: `inv-table-v5` (invariant tables), `thermo-table-v5` -> `v6-units` -> `v7-structures` ->
  `v7.1-sites` (general tables). A job file records it, e.g. `"prompt_version": "thermo-table-v7.1-sites"`,
  `"reader_model": "claude-opus-5.5"` (READ, `second-reader-requests/…jnucmat-2014-03-044-pdf.table-1.p2.json`,
  id `1eY3R-OcgoIGm43xIV8oozYOfz4DUKCGl`).
- **Opus is one of two or three readers, so the stored value is a consensus, not Opus alone.** Rows where Opus
  disagreed with Flash went to a judge or stayed unsettled.

## 4. Verified / audited subsets (04_*)

| Item | Where | Size | Result (STATED) |
|---|---|---|---|
| Human precision review, 6 student packets | `04_Review/precision_review/ORCHID_precision_review_kit` `1XbxMRdIESr6zh7stdnjATPpy28ntNxVX`; each packet is one HTML (~200 kB) + README; packet 1 HTML `13KDpqgbz4vrLcyfKcKBOx26xIo-_RNHo` | 300-record frozen random sample, 60 per packet; 240 responses on 210 distinct records | value correct 95.6 %; all five criteria 81.5 % (176/216). Preliminary, not a population estimate |
| Student responses | `ORCHID_student_reviews` `12BELUKx4fnIgxrs4zPmR4RX-z8j_gdxl` (not opened) | 4 JSON packets | - |
| Adjudication of flagged records | summarised in `08_Documentation/03_REVIEW_EVIDENCE.md` `1BUu59PWkHGabWq9dy02jsKlvUUgBPYgy` and `HUMAN_REVIEW_EVIDENCE_20261026.md` `11M-MentnIxkNyrRA5OOe1XCrT1ffKga8`; ledger itself is in a Dropbox path, not seen on the drive | 81 records: 36 defect, 17 mixed, 10 display, 11 supported, 7 unresolved | AI-assisted, not a second human review; 31 field corrections on 19 records |
| Adversarial AI audits A1-A6 | `ORCHID_AUDIT_2026-10-24` `1sn-k3uBqtWeGuhULVxgPb6Ql0hqv7RGz`, `Reverification_2026-10-24` `1eaT0u9_NtxGRDHNPEKD_sSivsSgMn9BK`, `orchid-pipeline-AUDIT.md` `1CCmBCekVem0Tj7beFxAqf1jCszqgE0dX` (not opened) | random samples against the printed page | wrong value or state: records 3.6 % -> 1.8 %, phase names 3.0 % -> 0.3 %, thermochemistry 10.9 % -> 9.1 % |
| Codex independent check | overview only | 200 ESPEI-ready records | 189/200 safe to fit (94.5 %); value, composition, phases, property, class 200/200 |
| Expert answers / adjudicator decisions | `Expert_Answers_Tables/decisions.jsonl` `15WGWfG6QNpV1ExU3Ig2stcJheArx5x5S` (27 kB), `Adjudicator_Decisions_Tier4`, `Expert_Answers_Tier5` | small | not read |

The human review judges **individual values** (value, unit, evidence class, phases, citation) against the paper,
not whole-table transcriptions. It gives about 210 human-checked values with DOI, page and table/row, which is a
ground-truth test set at cell level, not at table level.

## 5. Code: how crops were made and what the reader got (06_Code_Snapshots/orchid-pipeline)

Folder `1PA6XkgI6ae6Qn9aTMPNCWyXMfLTXX4iL`; pipeline README `1LHecPS_yCUpa705p-uX9RwYTLfNvekp7` (READ). Tool release
folder `tools-release-v2.1.18` id `13VEgoqBblj8T2TeAWX0DYFT04dloSdto`.

| File | Id | What it shows |
|---|---|---|
| `gemini_table_reader.py` | `1L0luBv0tS3-b4oAdnMnFPTnNSN-rF7wr` | crop rule and renderer, cache key, invariant prompt and schema (READ) |
| `thermo_table_reader.py` | `1PeKMdcTS-JTXshDlrFl-nvt_vyeCX8nU` | general-table prompts and schemas v5 to v7.1 (READ) |
| `invariant_reader.py` | `1j0mvSMaCPTrlXAj-8a0Q2HZusG9bcVJA` | invariant-table driver (not read) |
| `reader_cli.py` | `1LxJ1g6tQQ8JR7Y9VDektdoZt8vYIxmyf` | claim / answer / release broker commands (not read) |
| `crop_index.py` | `1Awe8anadte-ymvGGgnlGTvSOIoRgYRDX` | sha256 -> cached crop PNG lookup; cache was ~1,400 PNGs / 240 MB (READ) |
| `claude-reads/READER_INSTRUCTIONS_table_v71.md` | `1gc51C-LkdrAvrJ1pk8gP1G6o2khMxTn5` | what the blind Opus reader was told (READ) |
| `claude-reads/run-20261022/BRIEF.md` | `12InxxntGzQjgP4C7dzsP2HTW7xLb7e7E` | full-run brief and pilot lessons (READ) |
| `db-v2.1/orchid-v3.schema.json` | not located by id | record schema v3 |

**Crop rule** (READ): locate the table caption box with pdfplumber; crop the **full page width** from 6 pt above the
caption down to the next "Table/Fig." caption on the same side of the page, else the page bottom; render at
**160 dpi** with pdfplumber `Page.crop().to_image` (PDFium); a vertical caption means a landscape table, so the whole
page is taken and rotated upright; fall back to a whole-page `pdftoppm` render; a table continuing on the next page
is a two-page stack. The crop needs `caption_box`, which comes from an upstream table-routing step whose output is
not on the drive.

**What the reader received** (READ): the crop PNG plus a text prompt holding the caption, up to 8 sentences of the
paper that cite the table, and up to 80 lines of the PDF text layer for the same region (flagged as possibly
garbled). Instruction: the image is authoritative; one output row per printed row; values, units, phase names and
reactions exactly as printed; never convert, compute, complete or correct; keep ranges, bounds, `±` and citations in
their own fields; leave empty rather than guess.

**Output schema** (READ): `{table_kind, system[], temperature_unit, composition_basis, rows[], notes}`; each row has
`row_label`, `temperature` (+ `_unit`, `_printed`, `_bound`, `_max`, `_uncertainty`, `_role`),
`overall_composition[]`, `phases_present[]`, `reaction`, `transition_kind`, `phase_compositions[]`,
`properties[] {quantity, quantity_kind, value, unit, uncertainty, phase, component, reference_state}`, `method`,
`source` (6-way enum), `source_label`, `citations[]`; v7 adds `structure` (space group, Pearson symbol, lattice),
v7.1 adds Wyckoff `sites`, expressions, calculation settings, `printed` strings. `table_kind` has 11 values
(invariant_reactions, phase_compositions, thermochemical_properties, crystallographic, model_parameters, ...).

## 6. Recipe for 200-500 (table image -> Opus extraction) pairs

Target of the pair: the consensus rows of a table that list `claude-opus-5.5` among `readers`, regrouped per table.

1. Download the two indexes first (small): `records__packed_20261024.INDEX.tsv.gz` `1PSNORP2gyjCuZ_rdfsPh9I44tMjqXVnH`
   and `master__packed_20261024.INDEX.tsv.gz` `1QToL1aRqTytL0y2aeQnj2ptjrOkqwLvz`. They list every per-table file
   with its PDF number, table label and page.
2. Download the two record archives: `records__packed_20261024.tar.zst` `1UiJ5kOmR3Dhq82iJq3I9ZLQfiNLl1lHC` (7.6 MB)
   and `master__packed_20261024.tar.zst` `1J2KAE9wp5I8LPq4ZphrmU9t2fDvho-zr` (7.3 MB). Unpack; check whether
   `reading` records with `_meta.crop_recipe` are inside. If they are, the Opus reading and crop box come for free.
3. Pick 300-500 tables: settled rows only, `multi_reader` agreement, Opus in `readers`, single page, stratified
   over `table_kind`. Keep whole papers together and split by paper (the release already defines `fold_lpo`).
4. Download only the PDFs those tables need from `Assessment_Papers` `13HttJBpTX4dwseQtLciFlpsmY_1pO9ZB` (match
   `<NNNN>_<doi>.pdf`; about 0.5 MB each, so 150-300 PDFs is 100-200 MB). Use `MANIFEST.tsv`
   `16BiogABktzctt2X1lHjmGF7IXIUVqCMb` to get paths and hashes.
5. Re-render crops with the snapshot's `gemini_table_reader.crop_png` (160 dpi). If no crop box is stored, find the
   caption on the stated page by the table label and reuse `table_extent`.
6. For a human-checked test set, take the 300-value sample from the six review packets and the student responses;
   map each value to its table through `pid`.
7. Read `LICENSES.md` `1H7cYdvAq9nhK4X30yIGfD5nq0JvNS8P6` and `NOTICE.md` `12G5Sz8icCKELc3hwLnLgOxbxPqosYJFI` of
   the release before any redistribution decision.

**Missing, to ask the PI for:**
- the raw reader answers and crop PNGs (`~/projects/open-tdb/build/sgte-corpus/gemini-cache/` and
  `claude-reads/done/` on the Mac Studio); these are the true (crop, Opus JSON) pairs, with crop hash and recipe;
- the table-routing output that gives each table's `caption_box`, caption text and context sentences;
- the adjudication ledger (`ledger.json`), which is referenced by a Dropbox path;
- PDFs of the wider ~5,700-paper corpus if the selected tables point outside `Assessment_Papers`.

Practical limit of the connector: PDFs, PNGs, JSON and Markdown can be read; `.jsonl`, `.tar.zst` and `.gz` come
back only as base64 through `download_file_content`, so the archives (7-26 MB) need a normal Drive download or
Drive for desktop, not this connector.

## 7. Licence and confidentiality (READ)

- Publisher PDFs, ILL scans, handbook pages and crops, and reader text with publisher quotes are flagged
  `restricted = 1` and are **drive-only**: never copied to GitHub, Pages, Zenodo, Hugging Face, PyPI, R2 or the
  website, and folder links are not shared outside the team. The PI's ruling of 2026-10-24 treats the shared drive
  as local storage. Anything rendered from a PDF (page image, table crop) inherits the restriction.
- Derived data: CC BY 4.0, citing ORCHID and the original sources. Quotes are capped at 500 characters and stay
  under publisher copyright. SGTE, Materials Project and OQMD data keep their own licences.
- Source-page images and student responses are internal evidence and are not to go into public archives.
- The drive is a working archive; the 2026-10-26 candidate is explicitly not a published release.
- Consequence for this project: a (crop, extraction) dataset built from these PDFs can be used locally for
  training and evaluation, but the crops cannot be pushed to a public repository or model hub. Whether adapter
  weights trained on restricted crops may be released is not addressed in anything I read; that is a question for
  the PI.

## 8. Not covered

`ORCHID_KNOWLEDGE_BASE.md` (109 kB), `THERMO_EXTRACTOR_BENCHMARK.md` (`1KL0eeyEVTIz_FZ03az1YGfcxr-gNKDJz`, 22 kB,
may hold reader accuracy figures), the audit folders, `05_Reports*`, `90_Archive`, `07_Teaching`, `to_kyryl`,
`_superseded_2026-10-24c`, and the contents of every packed archive were not opened.
