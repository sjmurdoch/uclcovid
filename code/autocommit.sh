#!/usr/bin/env bash

cd /home/uclcovid/uclcovid
git pull -q
git add . 
git commit -q -m "Automatic commit at $(date '+%Y-%m-%dT%H-%M-%S')"
git push -q
