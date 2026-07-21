# Preservation

This describes what the archive is for, what it can be shown to do, and where it falls short. It completes work begun on a `preservation` branch in May 2022 and finished in July 2026.

## Goals

A dataset that outlives its author's attention needs four things. These were the goals:

1. **Keep the primary sources, not just the derived tables.** The CSV and JSON files are an interpretation of UCL's web page; the snapshots are the evidence. Anyone who disagrees with the interpretation should be able to go back to the source.
2. **Make the derived data reproducible from those sources**, so the numbers can be checked rather than trusted.
3. **Make the archive self-describing.** Where each file came from should be recorded inside the archive, not left implicit in a website that may not outlive it.
4. **Never mutate the archive while reading it.** A tool that reorganises data as a side effect of analysing it cannot be run twice with confidence.

## What was achieved

**The primary sources are preserved.** 6,140 hourly snapshots of UCL's confirmed-cases page (12 October 2020 – 29 July 2022) in `data/original/`, and 168 UCL COVID-19 update newsletters (9 March 2020 – 4 May 2022) in `data/updates/`. The newsletters begin roughly seven months before the case statistics and record the decisions behind the numbers.

**Provenance is recorded inside the archive.** `data/updates/manifest.csv` maps all 168 newsletters to their title and source URL — 168 entries, none missing in either direction. This matters because the stored filenames encode only a date and issue number, and the sources live on email-campaign tracking domains (161 on `uclnews.org.uk`, 7 on `dmtrk.net`) of the kind that disappear when a contract lapses. `manifest-sha256.txt.gz` in the repository root records the SHA-256 of every snapshot, including 7,890 deduplicated ones deleted during archival.

**The tooling no longer fights the archive.** `snapshot_to_csv.py` takes its paths from the command line or the environment, never writes to the snapshot directory, and records unparseable files instead of aborting on them.

**The published data is reproducible, and this was verified rather than assumed.** See below.

## Verification

Performed 2026-07-21 with Python 3.11, pandas 1.5.3, numpy 1.26.4 and BeautifulSoup 4. The pinned versions in `requirements.txt` are from 2020 and no longer build; 1.5.3 is the newest pandas confirmed to run this code.

### Three-way agreement

Three independent sources of the same four files were compared:

| Source | |
|---|---|
| **Published** | `data/covid.csv` etc. as committed by the cron job in 2022 |
| **Archival tool** | `snapshot_to_csv.py` run over `data/original/` |
| **Live scraper** | `exportdata.py` run over a *copy* of `data/original/` |

`covid.csv`, `covid.json`, `covid_raw.csv` and `covid_raw.json` are **byte-for-byte identical across all three**. The regenerated `original-tables.html` is also identical between the two tools.

To compare the two engines on equal terms, `exportdata.py` had to be patched — on the scratch copy only, never in this repository — to record parse failures instead of aborting. Without that it cannot process the archive at all.

### Reproducing it

```bash
cd code
python snapshot_to_csv.py --snapshots ../data/original --data /tmp/out
# then compare /tmp/out/covid.csv etc. against ../data/
```

Paths may also be given as `UCLCOVID_SNAPSHOTS` and `UCLCOVID_DATA`; the command line wins. A full pass takes about 90 seconds and prints the skipped snapshots to stderr at the end.

To check the snapshots themselves against the SHA-256 manifest:

```bash
gzcat manifest-sha256.txt.gz | grep ' data/original/' | shasum -a 256 -c --quiet
```

The `data/duplicates/` half of that manifest refers to files deleted during archival and will report as missing. That is expected.

### A difference between the two tools that is not a disagreement

The archival tool skips **24** snapshots; the live scraper reports only **4** parse errors. The gap is entirely accounted for and does not indicate a parsing disagreement:

- **19** are zero-length. Both tools skip them, by different tests — `st_size == 0` in the archival tool, `len(data) == 0` in the live scraper — and the live scraper does so silently.
- **1** is `covid-2022-07-29T11-34-03.html`, which is byte-identical to the preceding `covid-2022-07-28T23-34-02.html` (both `e7ab46e9…`). The live scraper hashes each file against the previous one and moves duplicates aside *before* parsing, so it never reaches the parser. The archival tool has no dedup step, so it attempts the file and records the failure.
- **4** genuinely fail to parse in both.

## Known limitations

**The data ends before the snapshots do.** UCL's page states "final update Thursday 12 May 2022" and the totals freeze at 1350 / 1239 / 3279 / 1614. The scraper carried on fetching an unchanging page for another two and a half months. The last row of published data is 2022-05-11; snapshots after that date add nothing.

**24 of 6,140 snapshots (0.4%) cannot be parsed.** They are listed on stderr at the end of every run. Nineteen are zero-length — UCL's site was failing when they were fetched, mostly during a 17-hour outage on 17–18 December 2020. The rest are from 27–29 July 2022, when the page was restructured as it was decommissioned. No data is lost: the hourly cadence means an adjacent snapshot covers the same period.

**Two gaps in the data were never corrected.** No figures were published on 2021-03-31, which appears to have been 3 staff on-campus cases. Missing data over Easter 2022 was also never corrected. Both were noted by the original author and are reproduced here because they affect anyone using the series.

**The published `data/original-tables.html` is truncated.** It is missing its closing `</body></html>`. This is not a transcription error: running the unmodified `exportdata.py` against the archive reproduces the published file *byte for byte*, including the truncation, because it aborts at the first unparseable snapshot on 2022-07-27 with `AttributeError: 'NoneType' object has no attribute 'string'` — before reaching the line that writes the closing tags. Regenerating the file properly yields a well-formed version 14 bytes longer, which will therefore not match the copy served from GitHub Pages.

**`exportdata.py` must not be run against this archive.** It is the original live-scraper script, kept for the historical record. Running it moves any snapshot whose content matches the previous one into `duplicates/` as a side effect of parsing. This is not theoretical: in the verification run it moved `covid-2022-07-29T11-34-03.html`, the last snapshot in the archive, out of `data/original/`. It also calls `sys.exit(1)` on a mismatched table label, which raises `SystemExit` and so bypasses ordinary exception handling entirely. Use `snapshot_to_csv.py`.

**The two tools disagree on one boundary, latently.** The switch to weekly-only figures is `date(2022,3,3)` in `exportdata.py` but `datetime(2022,3,3,9,34)` in `snapshot_to_csv.py`. Only one snapshot exists on that date, taken at 09:34:03, so both treat it identically and the outputs agree. Had a snapshot been taken earlier that morning the two would have parsed it differently. The archival tool's boundary is the more precise of the two.

**The code does not run on a current pandas.** `iteritems()` was removed in pandas 2.0 and `line_terminator` was renamed in 1.5. Anyone reviving this will need either a pinned old environment or small changes to `to_json` and `export`.

**The newsletters are stored as raw email HTML**, roughly 42 KB of email-service template around perhaps 2 KB of text. Images are referenced remotely and were not captured, so they will break as those hosts age. No plain-text extraction was performed.

**One filename is ambiguous.** See the next section — snapshot filenames are not a unique key.

## Timestamps, and the one duplicated filename

Snapshots are named from `date '+%Y-%m-%dT%H-%M-%S'` on the machine that fetched them, which ran on **Europe/London local time, not UTC**. The archive shows this directly: local hours go missing at each spring forward and repeat at each autumn back. That makes the filenames ambiguous twice a year, and in one case actively collide.

All four UK clock changes fell inside the collection period:

| Date | | What happened |
|---|---|---|
| 2020-10-25 | back | 01:34 occurred twice. **Both fetches produced `covid-2020-10-25T01-34-01.html`** — see below |
| 2021-03-28 | forward | No 01:34 snapshot exists; that local hour never happened. Harmless |
| 2021-10-31 | back | 01:34 occurred twice, but the fetches took 2 and 3 seconds, giving `01-34-02` and `01-34-03`. Distinct names, both preserved |
| 2022-03-27 | forward | No 01:34 snapshot. Harmless |

### Why the 2020 collision did not lose data

Two files share the name `covid-2020-10-25T01-34-01.html` with different content. `wget -O` truncates its target, so the second fetch should simply have overwritten the first. It did not, because of an interaction with the deduplication step. Reconstructed from the manifest:

| SHA-256 | Path |
|---|---|
| `ef1093cb…` | `data/duplicates/covid-2020-10-25T00-34-01.html` |
| `ef1093cb…` | `data/duplicates/covid-2020-10-25T01-34-01.html` |
| `64b58820…` | `data/original/covid-2020-10-25T01-34-01.html` |
| `ef1093cb…` | `data/original/covid-2020-10-25T02-34-01.html` |

1. **01:34 BST** — fetched, content `ef1093cb`, written to `data/original/`.
2. `exportdata.py` ran, found it identical to the 00:34 snapshot, and **moved it to `data/duplicates/`**.
3. **01:34 GMT**, an hour later by the clock but the same local time — fetched, content `64b58820`, written to the now-vacant `data/original/` filename.
4. `exportdata.py` ran, found it differed, and kept it.

The first copy survived only because the dedup step had moved it out of the way seconds earlier. **Had it not been a duplicate, it would have stayed in `data/original/` and been silently overwritten** — no error, no trace, one snapshot gone. The archive escaped that by luck rather than design, and the same luck held in 2021 only because two fetches happened to take different numbers of seconds.

This is the **only** duplicated filename in the collection, confirmed across all 14,030 manifest entries. Since `data/duplicates/` was deleted during archival, `manifest-sha256.txt.gz` is now the sole record that the collision occurred.

### What this means for using the archive

- **Do not treat snapshot filenames as unique identifiers**, and do not merge snapshot directories by name. Compare content hashes.
- **Do not parse filenames as UTC.** They are Europe/London local time, so an hour is missing each spring and repeated each autumn.
- Neither affects the published CSV/JSON, which are keyed by the date UCL reported, not by fetch time.

## A resolved question

A `## TODO was it converted to float64?` comment asked whether dropping `dtype='float64'` from the dataframe constructor changed the result. It does not — the regenerated files are byte-identical, and every data column in the output is `float64` regardless, because the values are cast when the supplementary rows are concatenated.
