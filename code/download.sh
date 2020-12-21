#!/usr/bin/env bash

cd /home/uclcovid/uclcovid
git pull -q
cd /home/uclcovid/uclcovid/data
wget -qO original/covid-$(date '+%Y-%m-%dT%H-%M-%S').html https://www.ucl.ac.uk/coronavirus/testing-reporting-and-managing-cases/current-confirmed-cases-covid-19
cd /home/uclcovid/uclcovid/code
## Disable over Christmas to prevent issues when it restarts
#/home/uclcovid/pyvenv/uclcovid/bin/python3 exportdata.py
cd /home/uclcovid/uclcovid
git add --all .
git diff-index --quiet HEAD || git commit -q -m "Automatic commit at $(date '+%Y-%m-%dT%H-%M-%S')"
git push -q
