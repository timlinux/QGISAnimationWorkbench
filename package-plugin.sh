#!/usr/bin/env bash

version=$(grep '^version=' animation_workbench/metadata.txt | cut -d '=' -f 2| tr -d '\n')
echo $version
version="1.2"
rm animation_workbench*.zip
cd animation_workbench
rm -rf __pycache__ core/__pycache__/ gui/__pycache__/
cd ..
zip -r animation_workbench-${version}.zip animation_workbench
cd ..
ls -lah animation_workbench-${version}.zip
