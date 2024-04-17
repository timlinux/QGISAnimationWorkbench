#!/usr/bin/env bash
cd animation_workbench
rm -rf __pycache__ core/__pycache__/ gui/__pycache__/
zip -qq -r ../animation_workbench.zip *
cd ..
ls -lah animation_workbench.zip
