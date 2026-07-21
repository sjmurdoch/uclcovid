# Provenance

How this dataset was produced, on a machine that no longer exists: the `uclcovid` service account on `hephaestus.cs.ucl.ac.uk`, a UCL Computer Science host.

Everything from that account has been read and summarised here. None of the original files are archived — see the last section for what was discarded and what that costs.

## The job

The account's crontab, complete and verbatim. Three lines, and every one of them matters:

```
MAILTO=smurdoch
MAILFROM=smurdoch
#34 11,23 * * * /home/uclcovid/uclcovid/code/download.sh
```

**The line is commented out.** That single `#` is how the project ended, on or shortly after 29 July 2022. UCL had decommissioned the page being fetched, so `exportdata.py` began failing; with `MAILTO` set, every failure was emailed twice a day. Commenting out the line stopped the mail.

**The schedule shown is the final one** — twice daily at 11:34 and 23:34. For most of the project the job ran hourly at minute 34; it changed around 16 May 2022, which the snapshot filenames show and `code/exportdata.py`'s mtime of that date corroborates.

`download.sh` fetched the page with `wget`, ran `exportdata.py` to parse it into the CSV and JSON files, then committed and pushed — one automatic commit per run, about 6,500 of them. Commit timestamps run roughly three minutes behind the snapshot filenames, which is the download and parse time.

Note that snapshot counts per month are not a record of the schedule. Unchanged fetches were deduplicated away, so fewer snapshots means UCL updated the page less often, not that the job ran less often.

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

## Two other things the shell history settled

**The earliest snapshots were collected on a different machine.** The first substantive command in the account was:

```
scp -r smurdoch@tails:/cs/research/infosec/home0/smurdoch/UCL .
```

This is why the data starts on 12 October 2020 although the repository's first commit is 13 October. Those files were fetched by hand elsewhere before the cron job existed.

**The deduplicated snapshots were archived deliberately, not lost.** `tar -czvf ~/duplicates.tar.gz duplicates/` is the origin of the `duplicates/` tree that survived until archival in 2026, when it was deleted after every file in it was proven byte-identical to one retained in `data/original/`. `manifest-sha256.txt.gz` now stands in for it, and is what makes the 50-hour outage above provable.

## What was discarded, and what that costs

Nothing from the account is archived as a file. The crontab and the commands quoted above are reproduced from the originals verbatim; everything else they showed is either recorded here or independently checkable in the repository.

- **`.bash_history`** — 398 lines, perhaps a dozen of them informative and the rest `ls`, `cd`, `git status` and `vim`.
- **`crontab`** — quoted complete above, so keeping the file added three lines and a directory.
- **`.gitconfig`** — `Steven Murdoch <s.murdoch@ucl.ac.uk>` and `push.default = simple`. This looks like provenance and is not: 6,569 of the repository's 6,579 commits already carry that identity, so `git log --format='%an <%ae>'` states it more precisely, and also shows the one thing the file cannot — that the identity changed, the first nine commits (13–16 October 2020) being `Steven Murdoch (uclcovid)`.
- **`.bashrc`, `.bash_profile`, `.emacs`** — stock distribution skeleton files, unmodified. Cron does not source them, so they had no effect on anything here.
- **`.viminfo`, `.lesshst`** — trivia that may hold incidental fragments of unrelated files.
- **The deploy key** (`~/.ssh/id_ed25519`) — tested against GitHub, found already revoked, and deleted.

Be clear about what the trade costs. The corruption account can be verified against git without the history, and the tarball claim against the manifest. **The `scp` line cannot be checked against anything** — this file is now its only record, and you are trusting a summary rather than reading evidence. It is a small claim and the dates support it, but it is an assertion.

Dates here are inferred from what commands did and from commit and file times. The shell history carried no timestamps: `HISTTIMEFORMAT` was never set.
