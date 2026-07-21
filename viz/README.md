# The visualisation

`index.html` is the interactive chart page from <https://murdoch.is/projects/covid/>, which was the public face of this dataset. It is here because it existed nowhere in this repository, and because the website that served it is maintained separately and on a different schedule.

Open it in a browser. No web server, no network connection.

## What this is, and what it is not

It is the **rendered** page as saved on 2026-07-14, which carries all 573 lines of charting logic inline. It is not the Pelican source — the Markdown and template that generated it live in the website repository. Nothing is lost by that: the source's only job was to produce this file.

The prose is the author's, written while the project was live, and has not been edited. It still says "This page shows data for the full period", which is true, and does not say the project has concluded, which by then it had.

## Changes made so that it survives

The page as served would eventually have broken in three ways, each of them silently — a blank chart, not an error message. Compare against the first commit of this file to see the changes; there are three, all small.

**The three JavaScript libraries are now stored in `js/`** rather than fetched from `cdn.jsdelivr.net`. They are byte for byte what that CDN served on 2026-07-21:

| File | Version | sha256 | Licence |
|---|---|---|---|
| `js/Chart.js` | chart.js 2.9.3 | `9d96b13c7036b806aaba2c634835f5f5398895b44d08eadfe473b5a07979a7bd` | MIT |
| `js/chartjs-plugin-annotation.min.js` | 0.5.7 | `3a59da8dfde8f647e4146968212c0fd53b252625940ddec86267c2f8674229de` | MIT |
| `js/moment.min.js` | moment 2.29.1 | `ab8c8dc9d3a670c207395adc9c8b03e9792aab00dc22fd646f498d0d2c1d501c` | MIT |

The originals were `https://cdn.jsdelivr.net/npm/chart.js@2.9.3/dist/Chart.js`, `…/chartjs-plugin-annotation@0.5.7/chartjs-plugin-annotation.min.js` and `…/moment@2.29.1/moment.min.js`. Chart.js 2.x has been end-of-life for years, so a CDN dropping it is a question of when.

**The data is now `js/covid-data.js`** instead of an `XMLHttpRequest` to `https://sjmurdoch.github.io/uclcovid/data/covid.json`. That URL only works while GitHub Pages is enabled on this repository, and a page opened from disk cannot fetch a file sitting next to it, so a plain relative URL would not have fixed it. The data therefore arrives as a script that sets `window.dataSets`.

`js/covid-data.js` is a copy of `data/covid.json` with a header comment, an assignment, and a semicolon around it. Confirm it has not drifted:

```bash
perl -0pe 's/^(?:.*\n){10}//; s/;\n\z//' viz/js/covid-data.js | shasum -a 256
shasum -a 256 data/covid.json
```

Both give `df22fb51…`. If `data/covid.json` is ever regenerated, regenerate this too:

```bash
{ echo "window.dataSets ="; cat data/covid.json; echo ";"; } > viz/js/covid-data.js
```
(then restore the header comment, or adjust the line count in the check above).

**Drawing now waits for `DOMContentLoaded`** rather than for the `XMLHttpRequest` to load, since there is no longer a request to wait for.

**The page has its own stylesheet, and the site chrome is gone.** It used to link `../../theme/css/combined-min.css` from murdoch.is, so on its own it rendered as unstyled browser defaults. That theme cannot be vendored: it depends on Advocate, Concourse and Triplicate, which are licensed commercial webfonts and not redistributable. What replaces it is about a hundred lines of self-contained CSS in system fonts — **a substitute, not a reproduction of the original design.**

The sidebar went with it. It was navigation into murdoch.is — publications, talks, teaching, social icons, a cover photo — none of which resolves here. A banner at the top now says what the page is instead. The two remaining site-relative links point at murdoch.is rather than 404ing.

**Two chart defects were fixed**, both present in the published page. The annotation labels on the total-cases and rolling-7-day charts sat close to the left edge and were clipped by the canvas, reading "ases added" and "ases reviewed"; both now carry an `xAdjust`. And the chart control rows have an inline `display: flex` with no wrapping, so five buttons needing 547px made the page scroll sideways on a phone.

### Verified

The dependency changes were checked before any restyling: rendered in headless Chrome from `file://` with no network, and compared against the original page rendering with the CDN and GitHub Pages available. **The two screenshots were byte-identical** (`960a13a8…`, 1200×3200), so vendoring the libraries and inlining the data changed nothing visible. The restyling was then checked the same way — all four charts and their controls, the text, both annotation labels reading in full, and no horizontal overflow at 500px.

One trap worth recording for anyone repeating this: Chart.js is still animating when the page finishes loading, so a screenshot taken then catches the lines partway up and the totals chart appears to stop short. Setting `Chart.defaults.global.animation.duration = 0` in a throwaway copy gives the settled page, whose totals reach 1350 / 1239 / 3279 / 1614 — what the DOM reports, and what UCL froze at on 12 May 2022.

## Known limitations

**It does not look like the original.** The typography and layout are a substitute, for the licensing reason above; the charts and text are unchanged. Anyone wanting the original appearance should consult the first commit of this file together with a capture of murdoch.is from the same period.

**It is a snapshot of one moment.** If the page on murdoch.is is later updated to say the project concluded, this copy will not follow.

**Note for the repository owner:** because GitHub Pages serves this repository, this directory is also published at `https://sjmurdoch.github.io/uclcovid/viz/` — where, unlike a local copy, it *does* render with data but still without the website's theme.
