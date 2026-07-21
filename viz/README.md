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

### Verified

Rendered in headless Chrome from `file://`, with no network, and compared against the original page rendering with the CDN and GitHub Pages available. **The two screenshots are byte-identical** (`960a13a8…`, 1200×3200). The change is cosmetically null.

## Known limitations

**It renders unstyled.** The page links `../../theme/css/combined-min.css` and `../../theme/js/combined-min.js`, paths relative to the website root, and pulls the header image and social icons from `../../images/` and `../../theme/images/`. None of those resolve here. The result is plain but complete and entirely readable — every chart, control and paragraph is present. The theme was deliberately not vendored: it is the website's, not this project's, and copying it would preserve someone else's CSS rather than this dataset.

**Navigation links point at the website.** Sidebar links (`Publications`, `Talks`, and so on) are relative and will 404. They are left alone as part of the record of how the page was presented.

**It is a snapshot of one moment.** If the page on murdoch.is is later updated to say the project concluded, this copy will not follow.

**Note for the repository owner:** because GitHub Pages serves this repository, this directory is also published at `https://sjmurdoch.github.io/uclcovid/viz/` — where, unlike a local copy, it *does* render with data but still without the website's theme.
