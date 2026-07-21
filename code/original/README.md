# The live pipeline, as it ran

These three files are the scraper as it actually ran on `hephaestus.cs.ucl.ac.uk` from October 2020 to July 2022. **They are here for reference, not for use.** None of them runs against this archive as-is, and one of them is actively unsafe to run against it.

To *reproduce* the published data, use `../snapshot_to_csv.py` — a 2026 reimplementation that produces byte-identical output without the hazards below. See the top-level [`README.md`](../../README.md).

| | |
|---|---|
| `download.sh` | The cron wrapper: `git pull`, `wget` the page, run `exportdata.py`, commit, push. Every path is hardcoded to `/home/uclcovid` on a machine that no longer exists, so it cannot run here |
| `exportdata.py` | The parser that produced **every published figure**. Dangerous to run — see below |
| `requirements.txt` | The 2020 dependency pins. They no longer build; the reproduction environment is pandas 1.5.x, documented in the top-level README |

## Why `exportdata.py` is kept, and frozen

It is the provenance of the entire dataset — the actual code the numbers came out of. That is worth more than its function, which `snapshot_to_csv.py` has entirely replaced. It is deliberately **byte-identical to commit `cf8d91aa`** and should stay that way; it is an artefact, not maintained code. Its original header notes, describing corrections that were never made, are part of what it records.

```bash
git show cf8d91aa:code/exportdata.py | cmp - exportdata.py    # must be identical
```

## Why it must not be run against `data/original/`

Two reasons, either one sufficient:

- **It mutates the archive.** It deduplicates by moving any snapshot whose bytes match the previous one into a `duplicates/` directory, as a side effect of parsing. During verification on a *scratch copy* it moved `covid-2022-07-29T11-34-03.html`, the last snapshot in the collection, out of `data/original/`.
- **It aborts on bad input.** It calls `sys.exit(1)` on a mismatched table label, which raises `SystemExit`, bypasses ordinary exception handling, and truncates the whole run over one malformed snapshot. This is why the published `data/original-tables.html` is truncated.

If you need to run it for a comparison, patch a throwaway copy — never this one. `snapshot_to_csv.py` does the same parse with neither behaviour.
