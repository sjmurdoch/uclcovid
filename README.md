Historical UCL COVID-19 statistics
----------------------------------

UCL publishes [daily statistics](https://www.ucl.ac.uk/coronavirus/testing-reporting-and-managing-potential-cases/current-confirmed-cases-covid-19) of COVID-19 cases
for UCL staff and students. This repository contains this data for previous days, so as to better understand any trends present.

# Data

Hourly snapshots of the original data can be found in `data/original/`. These files are processed to extract the underlying data in [JSON](data/covid.json) and [CSV](data/covid.csv) formats. Data reported on Tuesday covers Saturday, Sunday and Monday so the daily statistics share these values over these three days. Versions are also available without the smoothing, in [JSON](data/covid_raw.json) and [CSV](data/covid_raw.csv). Weekly and total cases don't need such smoothing, so data for Saturday and Sunday are simply omitted. The file format is not guaranteed to remain stable.

The JSON file is also available over HTTPS, suitable for plotting on web pages, at
[`https://sjmurdoch.github.io/uclcovid/data/covid.json`](https://sjmurdoch.github.io/uclcovid/data/covid.json).

The actual tables extracted from the HTML files can be found at [`https://sjmurdoch.github.io/uclcovid/data/original-tables.html`](https://sjmurdoch.github.io/uclcovid/data/original-tables.html) for verification.

For the latest data and important caveats on how it should be interpreted, see the [official UCL webpage](https://www.ucl.ac.uk/coronavirus/testing-reporting-and-managing-potential-cases/current-confirmed-cases-covid-19).

# Code

The code for downloading the webpage and processing it to extract data can be found in `code/`.

# Visualisation

A simple plot of the data can be found on [my personal webpage](https://murdoch.is/projects/covid/).
