#!/usr/bin/env bash

cd /home/uclcovid/uclcovid/data
wget -qO original/covid-$(date '+%Y-%m-%dT%H-%M-%S').html https://www.ucl.ac.uk/coronavirus/testing-reporting-and-managing-cases/current-confirmed-cases-covid-19
cd /home/uclcovid/uclcovid/code
/home/uclcovid/pyvenv/uclcovid/bin/python3 exportdata.py
../code/autocommit.sh
