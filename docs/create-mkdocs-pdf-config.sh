#!/usr/bin/env bash

# This script will assemble a mkdocs.yml
# file with plugins section suitable for 
# PDF site generation.

# This script is used both in manual
# site compilation (via build-docs-html.sh)
# and via the github workflow for 
# publishing the site to github pages
# .github/workflows/CompileMKDocsToPDF.yml

cat mkdocs-base.yml > mkdocs.yml
cat mkdocs-pdf.yml >> mkdocs.yml
cat mkdocs.yml > mkdocs-overview.yml
cat mkdocs-pdf-overview.yml >> mkdocs-overview.yml
cat mkdocs.yml > mkdocs-users.yml
cat mkdocs-pdf-users.yml >> mkdocs-users.yml
cat mkdocs.yml > mkdocs-administrators.yml
cat mkdocs-pdf-administrators.yml >> mkdocs-administrators.yml
cat mkdocs.yml > mkdocs-developers.yml
cat mkdocs-pdf-developers.yml >> mkdocs-developers.yml
cat mkdocs.yml > mkdocs-devops.yml
cat mkdocs-pdf-devops.yml >> mkdocs-devops.yml
# This is a kludge: I could not figure out 
# how to reference image resources using a relative path in the scss...
cat templates/styles.scss.templ | sed "s?\[BASE_FOLDER\]?$PWD?g" > templates/styles.scss
cat templates/graphics.scss.templ | sed "s?\[BASE_FOLDER\]?$PWD?g" > templates/graphics.scss
