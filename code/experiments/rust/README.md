# Abandoned Rust parser experiment (Feb–May 2022)

An attempt to reimplement `code/exportdata.py` in Rust to see whether it would be faster. It was abandoned in May 2022 and **never reached parity with the Python**, which produced all published data.

These files are kept as a record of the approach, not as working code. They are extracted from the `rust` branch, which is retained but deliberately left unmerged. The `.toml.txt` extensions are deliberate, so `cargo` does not treat this directory as a workspace.

## What is here

| File | |
|---|---|
| `parse_covid.rs` | Serial prototype |
| `parse_covid_par.rs` | Parallel variant using rayon |
| `Cargo_serial.toml.txt` | Dependencies for the serial version (glob, scraper) |
| `Cargo_par.toml.txt` | Dependencies for the parallel version (adds lazy_static, rayon) |

## How far it got

Both versions glob `data/original/covid-*.html`, extract `th`/`td` cells with a CSS selector, and print rows to stdout when the values change. That is roughly where it stopped. There is no CSV or JSON output, no Tuesday smoothing, no rolling-7 calculation, and no deduplication — perhaps 5% of what `exportdata.py` does.

The CSS selector is the same one used at `code/exportdata.py:134`, so nothing here is needed to understand the parsing.

## Known defects

`parse_covid_par.rs` is **incorrect**, not merely incomplete. Change detection is stateful across files via the `last` array, but `par_chunks(10)` resets that state at every chunk boundary, so its output differs from the serial version. The `println!` calls from rayon threads also interleave nondeterministically. Its `lazy_static! SELECTOR` is dead code — `parse_chunk` builds its own local selector instead of using it.

## Was it faster?

Unknown. The branch carried a 22 MB `perf.data` profile, but no binary or `target/` directory was committed alongside it, so there were no symbols to resolve it against and it was unreadable. No benchmark figures were recorded anywhere.

That profile, along with 1.5 MB of duplicated program output, remains on the `rust` branch and was deliberately not merged here — it accounts for 3.6 MiB of packed repository, and none of it is interpretable.
