# Historical UCL COVID-19 statistics

**This project has concluded.** Between October 2020 and May 2022 UCL published statistics of COVID-19 cases among its staff and students on a web page that was overwritten with each update, keeping no history. This repository collected that page hourly and extracted the numbers, so the series could be read as a whole rather than a day at a time.

UCL's page recorded its "final update Thursday 12 May 2022" and was decommissioned that July. **The published data therefore runs 2020-10-09 to 2022-05-11**, and the snapshots run to 2022-07-29 — the scraper carried on fetching an unchanging page for two and a half months after the numbers stopped moving.

The original page is gone: its URL now redirects to a general campus-safety page. The [Internet Archive's capture of 28 January 2022](https://web.archive.org/web/20220128023651/https://www.ucl.ac.uk/coronavirus/testing-reporting-and-managing-potential-cases/current-confirmed-cases-covid-19) shows what was being read.

## What is here

| | |
|---|---|
| `data/covid.csv`, `data/covid.json` | The extracted series, smoothed. **Start here.** |
| `data/covid_raw.csv`, `data/covid_raw.json` | The same, unsmoothed |
| `data/original/` | 6,140 hourly snapshots of UCL's page, 2020-10-12 to 2022-07-29 — the evidence behind the numbers |
| `data/updates/` | 168 UCL COVID-19 update newsletters, 9 March 2020 to 4 May 2022, with `manifest.csv` recording each one's source URL |
| `manifest-sha256.txt.gz` | SHA-256 of every snapshot ever fetched, including 7,890 deduplicated ones no longer stored |
| `code/` | The scraper, the archival re-implementation, and the newsletter fetcher |
| `viz/` | The interactive charts from murdoch.is, self-contained — open `viz/index.html` |
| [`PRESERVATION.md`](PRESERVATION.md) | What the archive can be shown to do, and where it falls short |
| [`PROVENANCE.md`](PROVENANCE.md) | How the data was produced, on a machine that no longer exists |

The newsletters are worth knowing about. They begin seven months before the case statistics and record the decisions behind the numbers, which the statistics alone do not explain.

## The data

Four groups of four series, each covering staff (on campus), staff (off campus), students (on campus), students (off campus):

| Group | Series |
|---|---|
| Daily cases, as reported | `staff.on`, `staff.off`, `student.on`, `student.off` |
| Weekly cases, as reported | `staff7.on`, `staff7.off`, `student7.on`, `student7.off` |
| Total since start of Term 1, as reported | `stafftotal.on`, `stafftotal.off`, `studenttotal.on`, `studenttotal.off` |
| Weekly cases, recalculated from daily | `staffrolling7.on`, `staffrolling7.off`, `studentrolling7.on`, `studentrolling7.off` |

**Smoothing.** Before 2022-03-02 UCL published on weekdays, merging Saturday to Monday into Tuesday's figures; `covid.csv` and `covid.json` spread those over the three days they cover, to avoid a misleading Tuesday peak. From 2022-03-02 publication was weekly, and daily cases are the weekly count shared over seven days. Weekly and total figures need no such treatment, so Saturday and Sunday are simply omitted from them. The `covid_raw.*` files are unsmoothed.

**"On campus" does not mean infected on campus.** UCL's definition was someone who had visited UCL buildings for 15 minutes or more in the two days before symptoms began or a test was requested. Since exposure to symptoms typically takes four to five days, this identifies possible onward transmission, not the source of an infection.

**These are reported cases only.** They count what UCL was told about. Positive tests that were never reported to UCL do not appear, and asymptomatic infections largely went undetected, so the series is an underestimate by an unknown margin.

### Things that will otherwise look like errors

- **A jump of 89 cases on 2020-10-26.** A one-off addition of cases identified through UCL's own testing service that had not been reported to UCL. It appears in the totals but not in any day's reported cases, so consecutive totals do not difference to the daily figure across it.
- **Reported weekly totals disagree with a rolling 7-day sum of daily cases before November 2020.** 79 cases with incomplete information were incorrectly carried forward in the weekly figures. UCL resolved this as of 4 November 2020; daily and total figures were unaffected. This is why the `*rolling7*` series exist, and why the published charts use them for the earlier period.
- **Two gaps UCL never corrected.** No figures were published for 2021-03-31 — apparently 3 staff on-campus cases — and data missing over Easter 2022 was never restored.
- **A 50-hour hole in the snapshots**, 2021-08-21 to 2021-08-23, from a machine failure that also corrupted the git repository. No published data was lost; see [`PROVENANCE.md`](PROVENANCE.md).
- **`data/original-tables.html` is truncated**, missing its closing tags, because the run that produced it aborted partway. See [`PRESERVATION.md`](PRESERVATION.md).

The file formats were never guaranteed stable, and are now frozen by the project having ended.

## Reproducing and verifying

The published files can be regenerated from the snapshots:

```bash
cd code
python snapshot_to_csv.py --snapshots ../data/original --data /tmp/out
```

This produces `covid.csv`, `covid.json`, `covid_raw.csv` and `covid_raw.json` byte-identical to those in `data/`, which has been checked rather than assumed. It takes about 90 seconds and lists unparseable snapshots on stderr at the end. Paths may also be given as `UCLCOVID_SNAPSHOTS` and `UCLCOVID_DATA`; the command line wins.

The snapshots themselves can be checked against the manifest:

```bash
gzcat manifest-sha256.txt.gz | grep ' data/original/' | shasum -a 256 -c --quiet
```

The manifest's other half describes deduplicated files deleted during archival and will report as missing. That is expected.

**Do not run `code/exportdata.py` against this archive.** It is the original live scraper, kept for the record, and it *moves* snapshots into a `duplicates/` directory as a side effect of parsing them. Use `snapshot_to_csv.py`.

The code needs pandas 1.5.x; `iteritems()` was removed in pandas 2.0. The pins in `code/requirements.txt` date from 2020 and no longer build.

## Access over HTTPS

The JSON is served at [`https://sjmurdoch.github.io/uclcovid/data/covid.json`](https://sjmurdoch.github.io/uclcovid/data/covid.json), and the tables extracted from each snapshot at [`data/original-tables.html`](https://sjmurdoch.github.io/uclcovid/data/original-tables.html). Both depend on GitHub Pages remaining enabled; `viz/index.html` deliberately does not.

## Code

| | |
|---|---|
| `code/download.sh` | What cron ran: fetch, parse, commit, push. Paths are hardcoded for the machine it ran on |
| `code/exportdata.py` | The live parser that produced all published data. Read it, do not run it |
| `code/snapshot_to_csv.py` | The archival parser: same output, no side effects, survives bad input |
| `code/fetch_updates.py` | Downloads the newsletters and records where each came from |
| `code/parse-data.ipynb` | Notebook comparing reported weekly figures against a rolling 7-day sum — the analysis behind the 79-case discrepancy above |
| `code/experiments/rust/` | An abandoned attempt to reimplement the parser in Rust. Never reached parity |

A `rust` branch also exists, unmerged and left that way. It holds a 22 MB profiling artefact with no symbols to interpret it against; the source worth keeping was copied to `code/experiments/rust/`.

## Licence

The code and the extracted data are under the Apache License 2.0 — see [`LICENSE`](LICENSE). The original UCL pages in `data/original/` and the newsletters in `data/updates/` are not covered by it; they are UCL's, reproduced here as the evidence behind the extracted figures.

If you use this data, the author would like to hear what for: s.murdoch@ucl.ac.uk.
