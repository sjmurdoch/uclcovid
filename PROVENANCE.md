# Provenance

Where this data came from, and what was done to it.

**To use the data, read [`README.md`](README.md).** Everything that affects how the figures should be read is there. This file is for checking the archive rather than reading it: how the collection ran, what went wrong along the way, what was discarded in 2026, and what was verified rather than assumed.

## The collection

The data was produced on a machine that no longer exists: the `uclcovid` service account on `hephaestus.cs.ucl.ac.uk`, a UCL Computer Science host.

The account's crontab, complete and verbatim. Three lines, and every one of them matters:

```
MAILTO=smurdoch
MAILFROM=smurdoch
#34 11,23 * * * /home/uclcovid/uclcovid/code/download.sh
```

**The line is commented out.** That single `#` is how the project ended, on or shortly after 29 July 2022. UCL had decommissioned the page being fetched, so `exportdata.py` began failing; with `MAILTO` set, every failure was emailed twice a day. Commenting out the line stopped the mail.

**The schedule shown is the final one** — twice daily at 11:34 and 23:34. For most of the project the job ran hourly at minute 34; it changed around 16 May 2022, which the snapshot filenames show and `code/original/exportdata.py`'s mtime of that date corroborates.

`download.sh` fetched the page with `wget`, ran `exportdata.py` to parse it into the CSV and JSON files, then committed and pushed — one automatic commit per run, about 6,500 of them. Commit timestamps run roughly three minutes behind the snapshot filenames, which is the download and parse time.

### What `data/original/` actually contains

Not one copy of each distinct page. `exportdata.py` compared each fetch against **only the immediately preceding one**, moving it aside if the bytes matched, so what survived is *fetches that differed from their predecessor*. Content that recurred non-adjacently was kept, and a great deal did:

| | |
|---|---|
| Files | 6,140 |
| Distinct contents among them | **3,066** |
| Files sharing content with another file in the directory | **3,990 (65%)** |

The page alternated between states rather than simply changing. On 5–6 April 2022, ten byte-identical fetches survive with different pages interleaved between them; the adjacent-only check could not see past its one-file window.

So **snapshot counts are not a record of the schedule, and not a count of page updates either.** Fewer files in a month does mean UCL was changing the page less often, but the count overstates the number of changes, because an A→B→A oscillation is counted twice. `manifest-sha256.txt.gz` is what records the polling itself.

Only sixteen adjacent duplicates escaped the move. Fifteen fall inside a single run of sixteen zero-length files during the December 2020 outage — the emptiness test returns before the hash test, so empty files were never eligible to be moved at all. The sixteenth is `covid-2022-07-29T11-34-03.html`, the last snapshot in the collection, byte-identical to the fetch before it because the cron line was commented out before `exportdata.py` ran again. **It is the one fetch that was never processed**, and it is kept: what a snapshot records is that the page was fetched at that moment, which is unique to it whatever the bytes say.

**The earliest snapshots were collected elsewhere.** The first substantive command in the account was:

```
scp -r smurdoch@tails:/cs/research/infosec/home0/smurdoch/UCL .
```

This is why the data starts on 12 October 2020 although the repository's first commit is 13 October. Those files were fetched by hand on another machine before the cron job existed.

## The August 2021 corruption

Around 21 August 2021 the working repository's `.git` was corrupted. This is worth knowing about because the repair left permanent marks on the history that would otherwise look like tampering.

The account's shell history recorded the repair as:

```
mv .git/index ~          # index corrupt; moving it aside did not help
mv .git ~/gitold         # give up on the existing .git entirely
git init                 # start over
git add . ; git commit -m 'Recover from .git corruption'
git remote add origin git@github.com:sjmurdoch/uclcovid.git
git merge -s ours origin/main    # graft the published history back on
git branch -m master main
```

**The merge base is therefore artificial**, and `git blame` and `git log --follow` behave oddly across it. That is a recovery artefact, not evidence that data was rewritten.

Do not take this file's word for it. Most of the incident is visible in the repository itself:

```bash
git rev-list --max-parents=0 HEAD    # two root commits: 56549283 and c30b745a
git diff --stat ec035475 4acef1b7    # empty — the merge took 'ours' wholesale
git diff --stat 1edb69da ec035475    # what the recovered tree added
```

Two root commits in one repository is the anomaly; `56549283` is literally titled "Recover from .git corruption", dated 2021-08-23, and `ec035475` is the merge that grafted the published line back on. The third command is the reassuring one: relative to the last published commit before the corruption, the recovered tree **added** four snapshots and the files derived from them, and removed nothing. The `-s ours` merge discarded no history.

### What it cost

**Fetching stopped completely for 50 hours**, from `covid-2021-08-21T08-34-02` to `covid-2021-08-23T10-34-02`. This is not a deduplication artefact: `manifest-sha256.txt.gz` records every fetch including the deduplicated ones, and 22 August 2021 has **zero** entries in it.

So the failure was of the machine, not of the scraper. Fetching resumed at 10:34 on 23 August but the repository was not repaired until 12:12, so data was being collected for nearly two hours before anyone noticed git was broken.

**No published data was lost.** The gap fell across a weekend, and UCL published on weekdays only at that time. `data/covid_raw.csv` runs 2021-08-20 → 2021-08-23 unbroken and the cumulative totals reconcile across it: staff on-campus 240 → 242, matching the 2 daily cases reported on the 23rd. What was lost is 50 hours of the polling record.

The abandoned `~/gitold` was examined in July 2026 before being deleted. `git fsck` reported *empty* objects and null-SHA refs; every object still readable was already present in the live repository, and its HEAD commit `5cc745e8` is intact there. Empty objects are the usual signature of an unclean shutdown rather than of software error, which fits a 50-hour machine outage — but that is inference. Nothing recorded what actually happened, only what was done about it.

## The one duplicated filename

Snapshot filenames are Europe/London local time and are not unique keys; the README says so, because it affects anyone using `data/original/`. This is the incident behind that warning.

All four UK clock changes fell inside the collection period:

| Date | | What happened |
|---|---|---|
| 2020-10-25 | back | 01:34 occurred twice. **Both fetches produced `covid-2020-10-25T01-34-01.html`** — see below |
| 2021-03-28 | forward | No 01:34 snapshot exists; that local hour never happened. Harmless |
| 2021-10-31 | back | 01:34 occurred twice, but the fetches took 2 and 3 seconds, giving `01-34-02` and `01-34-03`. Distinct names, both preserved |
| 2022-03-27 | forward | No 01:34 snapshot. Harmless |

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

## Archival, July 2026

This completed work begun on a `preservation` branch in May 2022, and was shaped by four intentions:

1. **Keep the primary sources, not just the derived tables.** The CSV and JSON files are an interpretation of UCL's web page; the snapshots are the evidence. Anyone who disagrees with the interpretation should be able to go back to the source.
2. **Make the derived data reproducible from those sources**, so the numbers can be checked rather than trusted.
3. **Make the archive self-describing.** Where each file came from should be recorded inside the archive, not left implicit in a website that may not outlive it.
4. **Never mutate the archive while reading it.** A tool that reorganises data as a side effect of analysing it cannot be run twice with confidence.

The fourth is why `snapshot_to_csv.py` exists and why the README warns against running `exportdata.py`.

### What was removed, and on what evidence

Archival reduced the working copy from **1.5 GB to 283 MB**. Since most of that was deletion, the reasoning is recorded here rather than left to be inferred from an absence.

**7,890 deduplicated snapshots were deleted** — 698 MB across two copies of the same tree, one extracted from a `duplicates.tar.gz` made in May 2022. Every file in them was byte-identical to one kept in `data/original/`: SHA-256 over both sides gave 1,395 distinct contents among the duplicates, 3,066 among the originals, and **zero** duplicate-side hashes absent from the original side.

Their *filenames* were not redundant, though, and that is why `manifest-sha256.txt.gz` exists. Each name records an hour at which the page was fetched and found unchanged, so the set of names is the polling record — the only evidence of how often the page was checked against how often it actually changed. Deleting the tree without the manifest would have destroyed that. It has since earned its keep twice: it is what proves the 50-hour outage above was real rather than an artefact of deduplication, and it is now the sole record of the duplicated filename.

The manifest was verified complete before anything was deleted — 7,890 + 6,140 = 14,030 entries, matching disk exactly, with `shasum -a 256 -c` returning exit 0 over all of them.

**Also deleted:** the corrupted `.git` directory described above (54 MB); a Linux virtualenv (114 MB, unusable on any other platform, and `code/original/requirements.txt` holds the pins); a pip cache; a second full clone of this repository, confirmed byte-identical by `diff -rq`; and the deploy key, which was tested against GitHub, found already revoked, and destroyed.

Nothing that was deleted is needed to reproduce any published figure, and nothing deleted was ever on GitHub except the `preservation` branch, whose commits were merged first.

### Branches

The `preservation` branch, carrying the newsletters and the first version of `snapshot_to_csv.py`, was merged into `main` — 171 files, 28,389 insertions, **0 deletions** — verified contained in `main` before its remote branch was deleted.

A `rust` branch holding an abandoned reimplementation of the parser is deliberately **retained and unmerged**. It never reached parity with the Python and produced none of the published data. Of the 24 MB it adds, about 4 KB is source and the rest is a profiling artefact with no binary or symbols committed to interpret it against. Its source was briefly copied to `code/experiments/rust/` on `main` and then removed again, on the grounds that code which never worked earns no place in the front of an archive. It remains on the branch, and in this repository's history.

### What was discarded from the account, and what that costs

Nothing from the `uclcovid` account is archived as a file. The crontab and the commands quoted above are reproduced from the originals verbatim; everything else they showed is either recorded here or independently checkable in the repository.

- **`.bash_history`** — 398 lines, perhaps a dozen of them informative and the rest `ls`, `cd`, `git status` and `vim`.
- **`crontab`** — quoted complete above, so keeping the file added three lines and a directory.
- **`.gitconfig`** — `Steven Murdoch <s.murdoch@ucl.ac.uk>` and `push.default = simple`. This looks like provenance and is not: 6,569 of the repository's 6,579 commits already carry that identity, so `git log --format='%an <%ae>'` states it more precisely, and also shows the one thing the file cannot — that the identity changed, the first nine commits (13–16 October 2020) being `Steven Murdoch (uclcovid)`.
- **`.bashrc`, `.bash_profile`, `.emacs`** — stock distribution skeleton files, unmodified. Cron does not source them, so they had no effect on anything here.
- **`.viminfo`, `.lesshst`** — trivia that may hold incidental fragments of unrelated files.
- **The deploy key** (`~/.ssh/id_ed25519`) — tested, revoked, deleted, as above.

Be clear about what the trade costs. The corruption account can be verified against git without the shell history, and the tarball that became `data/duplicates/` against the manifest. **The `scp` line cannot be checked against anything** — this file is now its only record, and you are trusting a summary rather than reading evidence. It is a small claim and the dates support it, but it is an assertion.

Dates here are inferred from what commands did and from commit and file times. The shell history carried no timestamps: `HISTTIMEFORMAT` was never set.

## What was verified

Performed 2026-07-21 with Python 3.11, pandas 1.5.3, numpy 1.26.4 and BeautifulSoup 4. The pinned versions in `requirements.txt` are from 2020 and no longer build; 1.5.3 is the newest pandas confirmed to run this code. The commands for repeating any of this are in the README.

### The published data reproduces, three ways

Three independent sources of the same four files were compared:

| Source | |
|---|---|
| **Published** | `data/covid.csv` etc. as committed by the cron job in 2022 |
| **Archival tool** | `snapshot_to_csv.py` run over `data/original/` |
| **Live scraper** | `exportdata.py` run over a *copy* of `data/original/` |

`covid.csv`, `covid.json`, `covid_raw.csv` and `covid_raw.json` are **byte-for-byte identical across all three**. The regenerated `original-tables.html` is also identical between the two tools.

To compare the two engines on equal terms, `exportdata.py` had to be patched — on the scratch copy only, never in this repository — to record parse failures instead of aborting. Without that it cannot process the archive at all.

### The newsletter manifest is complete

`data/updates/manifest.csv` maps all 168 newsletters to their title and source URL — 168 entries, none missing in either direction. This matters because the stored filenames encode only a date and issue number, and the sources live on email-campaign tracking domains (161 on `uclnews.org.uk`, 7 on `dmtrk.net`) of the kind that disappear when a contract lapses.

### A difference between the two tools that is not a disagreement

The archival tool skips **24** snapshots; the live scraper reports only **4** parse errors. The gap is entirely accounted for:

- **19** are zero-length. Both tools skip them, by different tests — `st_size == 0` in the archival tool, `len(data) == 0` in the live scraper — and the live scraper does so silently.
- **1** is `covid-2022-07-29T11-34-03.html`, which is byte-identical to the preceding `covid-2022-07-28T23-34-02.html` (both `e7ab46e9…`). The live scraper hashes each file against the previous one and moves duplicates aside *before* parsing, so it never reaches the parser. The archival tool has no dedup step, so it attempts the file and records the failure.
- **4** genuinely fail to parse in both.

### Two smaller questions closed

**The two tools disagree on one boundary, latently.** The switch to weekly-only figures is `date(2022,3,3)` in `exportdata.py` but `datetime(2022,3,3,9,34)` in `snapshot_to_csv.py`. Only one snapshot exists on that date, taken at 09:34:03, so both treat it identically and the outputs agree. Had a snapshot been taken earlier that morning the two would have parsed it differently. The archival tool's boundary is the more precise of the two.

**A `## TODO was it converted to float64?` comment** in the source asked whether dropping `dtype='float64'` from the dataframe constructor changed the result. It does not — the regenerated files are byte-identical, and every data column in the output is `float64` regardless, because the values are cast when the supplementary rows are concatenated.
