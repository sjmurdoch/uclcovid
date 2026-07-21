# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A **concluded archive**, not an active project: a scraper and dataset of UCL's published COVID-19 case statistics. UCL published to a web page that was overwritten with each update and kept no history; a cron job on a now-decommissioned machine fetched it hourly from October 2020 to July 2022 and parsed the numbers out. Published data runs 2020-10-09 to 2022-05-11; snapshots run to 2022-07-29.

Nothing here is under development. The purpose of any change is to make the archive easier to read or check, and the constraint on every change is that **the published data must keep regenerating byte-identically**. Treat `data/` as read-only evidence.

The repository sits at `home/uclcovid/` inside a working directory whose top level holds `ARCHIVE-PLAN.md` — a status document tracking the archival work, and the place to look for what has and has not been done. It is deliberately not committed.

## The one test

There is no test suite, no CI and no build. The regression check is byte-identical regeneration of the four published files:

```bash
cd code
python snapshot_to_csv.py --snapshots ../data/original --data "$TMPDIR/out"
for f in covid.csv covid.json covid_raw.csv covid_raw.json; do
    cmp "$TMPDIR/out/$f" "../data/$f" && echo "OK $f"
done
```

About 90 seconds over 6,140 snapshots. Unparseable files are listed on stderr at the end — 24 of them, which is expected. Paths may also come from `UCLCOVID_SNAPSHOTS` and `UCLCOVID_DATA`; the command line wins.

**Run this after any change to `code/`, and after any change to `data/`.** It is the only thing standing between an edit and a silently corrupted dataset.

### Environment

Needs **pandas 1.5.x** — `iteritems()` was removed in 2.0 and `line_terminator` renamed in 1.5. `code/requirements.txt` holds the 2020 pins and no longer builds. Create the environment with:

```bash
export UV_CACHE_DIR="$TMPDIR/uvcache"   # the default cache path is unwritable under the sandbox
uv venv "$TMPDIR/rvenv" --python 3.11
uv pip install --python "$TMPDIR/rvenv/bin/python" 'pandas==1.5.3' 'numpy<2' beautifulsoup4
```

Pushing to GitHub fails inside the sandbox (`nc: authentication method negotiation failed`) and needs `dangerouslyDisableSandbox`.

## Two parsers, and why both exist

`code/exportdata.py` and `code/snapshot_to_csv.py` implement the same parse and produce identical output. They are not redundant, and the difference matters:

| | `exportdata.py` | `snapshot_to_csv.py` |
|---|---|---|
| Role | The live scraper. Produced **every published figure** | The archival tool, written 2026 |
| On a bad snapshot | `sys.exit(1)` — bypasses exception handling, truncates the run | Records it in `skipped` and continues |
| On a duplicate | **Moves the file** into `data/duplicates/` | No dedup; reads only |
| Paths | Hardcoded | CLI or environment |

**Never run `exportdata.py` against `data/original/`.** Its dedup step mutates the archive as a side effect of parsing; during verification it moved the last snapshot in the collection out of `data/original/`. Use `snapshot_to_csv.py`.

**Never modify `exportdata.py`.** It is byte-identical to commit `cf8d91aa` and that property is deliberate — it is the artefact that produced the published data, including the author's original header notes, some of which describe corrections that were never made. Verify with `git show cf8d91aa:code/exportdata.py | cmp - code/exportdata.py`. If it must be run for a comparison, patch a scratch copy.

`snapshot_to_csv.py` has no such claim on it and can be changed, subject to the regression check.

## How the parse works

`snapshot_to_csv.py` reads snapshots in filename order and builds one dataframe, then derives two more:

1. `extract_df()` — parses each snapshot, **skipping any whose extracted data equals the previous one**, so one row is emitted per genuine update rather than per fetch. It also writes `data/original-tables.html` as it goes. A row whose file date repeats overwrites the previous row (`is_extra`) rather than appending.
2. `add_weekend()` → the smoothed frame. Until 2022-03-02 UCL published on weekdays only, so Monday's figure covers Saturday–Monday and is divided by three across those days; long vacation gaps are divided by their actual span (13, 18 and 12 days, hardcoded by date); from 2022-03-02 the weekly figure is divided by seven.
3. `main()` — computes the `*rolling7*` series with `rolling("7D", min_periods=5)`, concatenates, and exports.

`covid_raw.*` come from the raw frame; `covid.*` from the smoothed one plus the rolling columns.

**Per-date corrections live in two places, both keyed by literal dates**: `cleanup_value()` handles UCL's typos and stray footnote symbols in the HTML (a dagger on 2020-10-27, `41` that should be `414` on 2021-07-15, and others), and `extract_df()` splices in one row UCL sent by email and never published (2022-02-02). Both are load-bearing for byte-identical output.

**One boundary differs between the tools, latently.** The switch to weekly-only figures is `date(2022,3,3)` in `exportdata.py` but `datetime(2022,3,3,9,34)` in `snapshot_to_csv.py`. Only one snapshot exists that day, at 09:34:03, so they agree on the actual archive.

## Snapshot filenames are not what they look like

- **Europe/London local time, not UTC** — an hour is missing at each spring forward and repeats at each autumn back.
- **Not unique keys.** Two files genuinely share `covid-2020-10-25T01-34-01.html` with different content. Compare content hashes; never merge snapshot directories by name.
- **Snapshot counts are not the polling record.** Unchanged fetches were deduplicated away and deleted during archival; `manifest-sha256.txt.gz` is what records every fetch, including the 7,890 removed ones, and is the only evidence of collection frequency.

## Documentation structure

Deliberately two root documents plus one scoped to `viz/`. Keep it that way — it was four, and the same facts had drifted into contradictory versions across them.

| | |
|---|---|
| `README.md` | Sufficient to **use** the data. All caveats affecting interpretation go here, including anything discovered in the code |
| `PROVENANCE.md` | For **checking** it: how collection ran, the August 2021 corruption, what was discarded in 2026, verification results |
| `viz/README.md` | The self-contained chart page and what was changed to make it stand alone |

Data caveats belong in `README.md`, not in source comments — source comments should point at it. Claims in these files are expected to be checkable against the repository or the data; when adding one, verify it and say what verified it.

## viz/

`viz/index.html` is the rendered chart page from murdoch.is, made self-contained: libraries vendored into `viz/js/`, and the data supplied as `viz/js/covid-data.js`, which sets `window.dataSets`. **If `data/covid.json` is ever regenerated, regenerate `covid-data.js` too** — the procedure and a drift check are in `viz/README.md`. GitHub Pages serves this directory, so changes here are published.

## Branches

`main` only. `origin/rust` holds an abandoned reimplementation that never reached parity and produced none of the published data; it is retained unmerged on purpose and should stay off `main`.
