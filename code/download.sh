#!/usr/bin/env bash

cd /home/uclcovid/uclcovid/data
wget -qO covid-$(date '+%Y-%m-%dT%H-%M-%S').html https://www.ucl.ac.uk/coronavirus/testing-reporting-and-managing-cases/current-confirmed-cases-covid-19
../code/autocommit.sh
