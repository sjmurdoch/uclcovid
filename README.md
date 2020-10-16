# Historical UCL COVID-19 statistics

UCL publishes [daily statistics](https://www.ucl.ac.uk/coronavirus/testing-reporting-and-managing-potential-cases/current-confirmed-cases-covid-19) of COVID-19 cases
for UCL staff and students. This repository contains this data for previous days, so as to better understand any trends present.

## Data

Hourly snapshots of the original data can be found in `data/`. These files are processed to extract the underlying data in [JSON](data/covid.json) and [CSV](data/covid.csv) formats.
The file format is not guaranteed to remain stable.
The JSON file is also available over HTTPS, suitable for plotting on web pages, at
[`https://sjmurdoch.github.io/uclcovid/data/covid.json`](https://sjmurdoch.github.io/uclcovid/data/covid.json).

Data is only published during weekdays, with cases from Saturday to Monday being merged into the results reported on Tuesday.
Daily cases reported on Tuesday are shared equally over Saturday, Sunday, and Monday to avoid a misleading weekly peak.
Weekly and total cases don't need such smoothing, so data for Saturday and Sunday are simply omitted.

For the latest data and important caveats on how it should be interpreted, see the [official UCL webpage](https://www.ucl.ac.uk/coronavirus/testing-reporting-and-managing-potential-cases/current-confirmed-cases-covid-19).

## Code

The code for downloading the webpage and processing it to extract data can be found in `code/`. For now, this is a Jupyter Notebook for Python 3.6.
Once the processing has been finalised, this will be converted to a Python script designed to be run automatically.

## Visualisation

A simple plot of the data can be found on [my personal webpage](https://murdoch.is/projects/covid/).
