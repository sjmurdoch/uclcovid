# Historical UCL COVID-19 statistics

**This project has concluded.** Between October 2020 and May 2022 UCL published statistics of COVID-19 cases among its staff and students on a web page that was overwritten with each update, keeping no history. This repository collected that page hourly and extracted the numbers, so the series could be read as a whole rather than a day at a time.

UCL's page recorded its "final update Thursday 12 May 2022" and was decommissioned that July. **The published data therefore runs 2020-10-09 to 2022-05-11**, ending with cumulative totals of 1350 staff on campus, 1239 staff off campus, 3279 students on campus and 1614 students off campus. The snapshots run to 2022-07-29 — the scraper carried on fetching an unchanging page for two and a half months after the numbers stopped moving.

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
| [`PROVENANCE.md`](PROVENANCE.md) | Where the data came from, what was discarded, and what was verified |

The newsletters are worth knowing about. They begin seven months before the case statistics and record the decisions behind the numbers, which the statistics alone do not explain.

This README is meant to be enough to use the data. `PROVENANCE.md` is for checking it.

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
- **Reported weekly totals disagree with a rolling 7-day sum of daily cases before November 2020.** 79 cases with incomplete information were incorrectly carried forward in the weekly figures. UCL resolved this as of 4 November 2020; daily and total figures were unaffected. This is why the `*rolling7*` series exist, and why the published charts use them for the earlier period. **The two do not agree perfectly afterwards either** — see below.
- **A day UCL never refreshed: 2021-03-31.** The page served on Wednesday 31 March 2021 was identical to the previous day's, and there is a row for that date in the data — so this looks like a day with no cases rather than a day with no figures. It is the latter. The staff on-campus total then rises from 190 to 193 on 1 April, and the weekly figure reports 3, but no day's cases ever account for them. **Three staff on-campus cases exist only in the totals.** Never corrected.
- **A week UCL never published: Easter 2022.** There are weekly rows for 2022-03-30, 2022-04-06, 2022-04-20 and 2022-04-27, but none for 2022-04-13. The 41 staff on-campus cases reported on 2022-04-20 as "new cases in last 7 days" in fact cover the **14 days** from 6 April; the other three series are affected the same way. Totals reconcile across the gap, so nothing is lost from them, but that week's weekly figures understate the period they appear to describe. Never corrected.
- **A 50-hour hole in the snapshots**, 2021-08-21 to 2021-08-23, from a machine failure that also corrupted the git repository. No published data was lost — the gap fell across a weekend, when UCL was not publishing, and the totals reconcile across it. But anyone reasoning from *fetch* times rather than reported dates should know about it. See [`PROVENANCE.md`](PROVENANCE.md).
- **`data/original-tables.html` is truncated**, missing its closing `</body></html>`. This is not a transcription error: the run that produced it aborted at the first unparseable snapshot before reaching the line that writes the closing tags, and regenerating it reproduces the truncation byte for byte. A properly regenerated version is 14 bytes longer and so will not match the copy served from GitHub Pages.

### Comparing weekly against daily figures

Since a week's cases should equal the sum of that week's daily cases, the two published series can be checked against each other. Doing so is how the 79-case problem above was found, and anyone re-examining this data is likely to try it, so it is worth setting out what the comparison does and does not show.

**Sum five rows, not seven.** Until 2022-03-02 nothing was published at weekends, so the daily series has five rows per week. A seven-row window spans nine calendar days and will not match anything.

```python
import pandas as pd
df = pd.read_csv("data/covid_raw.csv", index_col="date", parse_dates=True)
daily  = ["staff.on", "staff.off", "student.on", "student.off"]
weekly = ["staff7.on", "staff7.off", "student7.on", "student7.off"]
rolling = df[daily].rolling(5).sum().dropna()
residual = df.loc[rolling.index, weekly].sub(rolling.values)
```

Against `covid_raw.csv`, that comparison gives a residual of zero on most days from 4 November 2020 onwards, confirming UCL's fix. It is **not** zero everywhere: 68 of the 308 days to 1 March 2022 differ. Almost all of the large ones are an artefact of the method rather than a fault in the data, because a five-row window spanning a vacation covers far more than seven days. The three worst clusters sit immediately after the three longest breaks in publication:

| Break in publication | Residual that follows |
|---|---|
| 18 days, 2020-12-17 → 2021-01-04 | up to −27 per series, 5–8 January |
| 13 days, 2021-12-21 → 2022-01-03 | up to −507 for students on campus, 3–7 January |
| Half term, February 2022 | up to −27, 18–23 February |

The remaining differences are of the order of one to six cases and scattered thinly.

This is also why the weekly chart on the [project page](https://murdoch.is/projects/covid/) switches from the recalculated series to UCL's reported weekly figures at 2021-01-05 — the first publication day after that 18-day Christmas break. **The comparison is only meaningful within a teaching term.** After 2022-03-02, when publication became weekly, it does not apply at all.

## Using the primary sources

The CSV and JSON files are an interpretation of UCL's web page. `data/original/` is the evidence, and is there so that anyone who disagrees with the interpretation can go back to it. Three things about it are not obvious.

**Snapshot filenames are Europe/London local time, not UTC.** They come from `date '+%Y-%m-%dT%H-%M-%S'` on the machine that fetched them, so an hour goes missing at each spring forward and repeats at each autumn back. All four UK clock changes fall inside the collection period.

**Snapshot filenames are therefore not unique keys.** Two files in the collection genuinely share a name with different content, from the October 2020 clock change — see [`PROVENANCE.md`](PROVENANCE.md). Compare content hashes, and do not merge snapshot directories by name.

Neither affects the published CSV and JSON, which are keyed by the date UCL reported, not by fetch time.

**24 of the 6,140 snapshots (0.4%) cannot be parsed**, and are listed on stderr at the end of every run. Nineteen are zero-length, from times when UCL's site was failing, mostly during a 17-hour outage on 17–18 December 2020. The rest are from 27–29 July 2022, when the page was restructured as it was decommissioned. No data is lost: the hourly cadence means an adjacent snapshot covers the same period.

The newsletters in `data/updates/` are stored as **raw email HTML** — roughly 42 KB of email-service template around perhaps 2 KB of text, with no plain-text extraction performed. Their images are referenced remotely and were not captured, so they will break as those hosts age. `data/updates/manifest.csv` records the source URL of each one, which the filenames do not.

The file formats were never guaranteed stable, and are now frozen by the project having ended.

## Reproducing and verifying

The published files can be regenerated from the snapshots:

```bash
cd code
python snapshot_to_csv.py --snapshots ../data/original --data /tmp/out
```

This produces `covid.csv`, `covid.json`, `covid_raw.csv` and `covid_raw.json` byte-identical to those in `data/` — checked rather than assumed, against both the published files and the original live scraper, as recorded in [`PROVENANCE.md`](PROVENANCE.md). It takes about 90 seconds and lists unparseable snapshots on stderr at the end. Paths may also be given as `UCLCOVID_SNAPSHOTS` and `UCLCOVID_DATA`; the command line wins.

The snapshots themselves can be checked against the manifest:

```bash
gzcat manifest-sha256.txt.gz | grep ' data/original/' | shasum -a 256 -c --quiet
```

The manifest's other half describes deduplicated files deleted during archival and will report as missing. That is expected.

**Do not run `code/exportdata.py` against this archive.** It is the original live scraper, kept for the record, and it *moves* any snapshot whose content matches the previous one into a `duplicates/` directory as a side effect of parsing. This is not theoretical: during verification on a scratch copy it moved `covid-2022-07-29T11-34-03.html`, the last snapshot in the collection, out of `data/original/`. It also calls `sys.exit(1)` on a mismatched table label, which raises `SystemExit` and so bypasses ordinary exception handling. Use `snapshot_to_csv.py`.

**The code needs pandas 1.5.x.** `iteritems()` was removed in pandas 2.0 and `line_terminator` was renamed in 1.5, so a current pandas will not run this without small changes to `to_json` and `export`. The pins in `code/requirements.txt` date from 2020 and no longer build; the verification was done with Python 3.11, pandas 1.5.3, numpy 1.26.4 and BeautifulSoup 4.

## Access over HTTPS

The JSON is served at [`https://sjmurdoch.github.io/uclcovid/data/covid.json`](https://sjmurdoch.github.io/uclcovid/data/covid.json), and the tables extracted from each snapshot at [`data/original-tables.html`](https://sjmurdoch.github.io/uclcovid/data/original-tables.html). Both depend on GitHub Pages remaining enabled; `viz/index.html` deliberately does not.

## Code

| | |
|---|---|
| `code/download.sh` | What cron ran: fetch, parse, commit, push. Paths are hardcoded for the machine it ran on |
| `code/exportdata.py` | The live parser that produced all published data. Read it, do not run it |
| `code/snapshot_to_csv.py` | The archival parser: same output, no side effects, survives bad input |
| `code/fetch_updates.py` | Downloads the newsletters and records where each came from |

An unmerged `rust` branch also exists, holding an abandoned attempt to reimplement the parser in Rust. It produced none of the published data and is not needed to understand or reproduce anything here; it is kept off `main` deliberately, for the reasons in [`PROVENANCE.md`](PROVENANCE.md).

## Licence

The code and the extracted data are under the Apache License 2.0 — see [`LICENSE`](LICENSE). The original UCL pages in `data/original/` and the newsletters in `data/updates/` are not covered by it; they are UCL's, reproduced here as the evidence behind the extracted figures.

If you use this data, the author would like to hear what for: s.murdoch@ucl.ac.uk.
