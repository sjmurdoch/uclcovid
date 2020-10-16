#!/usr/bin/env bash

cd /home/uclcovid/uclcovid
git pull
git add .
git commit -m "Automatic commit at $(date '+%Y-%m-%dT%H-%M-%S')"
git push
