# Preservation

This describes what the archive is for, what it can be shown to do, and where it falls short. It completes work begun on a `preservation` branch in May 2022 and finished in July 2026.

## Goals

A dataset that outlives its author's attention needs four things. These were the goals:

1. **Keep the primary sources, not just the derived tables.** The CSV and JSON files are an interpretation of UCL's web page; the snapshots are the evidence. Anyone who disagrees with the interpretation should be able to go back to the source.
2. **Make the derived data reproducible from those sources**, so that the numbers can be checked rather than trusted.
3. **Make the archive self-describing.** Where each file came from should be recorded inside the archive, not left implicit in a website that may not outlive it.
4. **Never mutate the archive while reading it.** A tool that reorganises data as a side effect of analysing it cannot be run twice with confidence.

## What was achieved

**The primary sources are preserved.** 6,140 hourly snapshots of UCL's confirmed-cases page (12 October 2020 – 29 July 2022) in `data/original/`, and 168 UCL COVID-19 update newsletters (9 March 2020 – 4 May 2022) in `data/updates/`. The newsletters begin roughly seven months before the case statistics and record the decisions behind the numbers.

**The published data is reproducible, and this has been verified rather than assumed.** Running

```bash
cd code
python snapshot_to_csv.py --snapshots ../data/original --data /tmp/out
```

regenerates `covid.csv`, `covid.json`, `covid_raw.csv` and `covid_raw.json` **byte-for-byte identically** to the published files. Verified 2026-07-21 with pandas 1.5.3.

**Provenance is recorded inside the archive.** `data/updates/manifest.csv` maps all 168 newsletters to their title and source URL — 168 entries, every one present on disk. This matters because the stored filenames encode only a date and issue number, and the sources live on email-campaign tracking domains (161 on `uclnews.org.uk`, 7 on `dmtrk.net`) of the kind that disappear when a contract lapses. `manifest-sha256.txt.gz` in the repository root records the SHA-256 of every snapshot, including 7,890 deduplicated ones deleted during archival.

**The tooling no longer fights the archive.** `snapshot_to_csv.py` takes its paths from the command line or the environment, never writes to the snapshot directory, and records unparseable files instead of aborting on them.

## Known limitations

**The data ends before the snapshots do.** UCL's page states "final update Thursday 12 May 2022" and the totals freeze at 1350 / 1239 / 3279 / 1614. The scraper carried on fetching an unchanging page for another two and a half months. The last row of published data is 2022-05-11; snapshots after that date add nothing.

**24 of 6,140 snapshots (0.4%) cannot be parsed.** They are listed on stderr at the end of every run. Nineteen are zero-length — UCL's site was failing when they were fetched, mostly during a 17-hour outage on 17–18 December 2020. Five are from 27–29 July 2022, when the page was restructured as it was decommissioned. No data is lost: the hourly cadence means an adjacent snapshot covers the same period.

**Two gaps in the data were never corrected.** No figures were published on 2021-03-31, which appears to have been 3 staff on-campus cases. Missing data over Easter 2022 was also never corrected. Both were noted by the original author and are reproduced here because they affect anyone using the series.

**The published `data/original-tables.html` is truncated.** It is missing its closing `</body></html>`, because the final production run aborted before writing them. The file is otherwise a byte-exact prefix of the regenerated version. Regenerating it produces a well-formed file 14 bytes longer, so it will not match the copy served from GitHub Pages.

**The code does not run on a current pandas.** `iteritems()` was removed in pandas 2.0 and `line_terminator` was renamed in 1.5. The pinned versions in `requirements.txt` are from 2020 and no longer build on current platforms. pandas 1.5.3 on Python 3.11 is the newest combination confirmed to work.

**`exportdata.py` must not be run against this archive.** It is the original live-scraper script, kept for the historical record. It *moves* any snapshot whose content matches the previous one into a `duplicates/` directory as a side effect of parsing, and it calls `sys.exit(1)` on the first malformed file. Use `snapshot_to_csv.py`.

**The newsletters are stored as raw email HTML**, roughly 42 KB of email-service template around perhaps 2 KB of text. Images are referenced remotely and were not captured, so they will break as those hosts age. No plain-text extraction was performed.

**One filename is ambiguous.** `covid-2020-10-25T01-34-01.html` exists in both the retained and deduplicated sets with different content: 25 October 2020 was the UK clock change, so 01:34 occurred twice and the second fetch reused the first filename. Snapshot filenames are therefore not a unique key.

## A resolved question

A `## TODO was it converted to float64?` comment asked whether dropping `dtype='float64'` from the dataframe constructor changed the result. It does not — the regenerated files are byte-identical, and every data column in the output is `float64` regardless, because the values are cast when the supplementary rows are concatenated.
