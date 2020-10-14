# Historical UCL COVID-19 statistics

UCL publishes [daily statistics](https://www.ucl.ac.uk/coronavirus/testing-reporting-and-managing-potential-cases/current-confirmed-cases-covid-19) of COVID-19 cases
for UCL staff and students. This repository contains this data for previous days, so as to better understand any trends present.

## Data

Hourly snapshots of the original data can be found in `data/`. These files are processed to extract the underlying data in [JSON](data/covid.json) and [CSV](data/covid.csv) formats.
The file format is not guaranteed to remain stable.
The JSON file is also available over HTTPS, suitable for plotting on web pages, at
[`https://sjmurdoch.github.io/uclcovid/data/covid.json`](https://sjmurdoch.github.io/uclcovid/data/covid.json).

For the latest data and important caveats on how it should be interpreted, see the [official UCL webpage](https://www.ucl.ac.uk/coronavirus/testing-reporting-and-managing-potential-cases/current-confirmed-cases-covid-19).

## Code

The code for downloading the webpage and processing it to extract data can be found in `code/`. For now, this is a Jupyter Notebook for Python 3.6.
Once the processing has been finalised, this will be converted to a Python script designed to be run automatically.

## Visualisation

A simple plot of the data can be found on [my personal webpage](https://murdoch.is/projects/covid/).
