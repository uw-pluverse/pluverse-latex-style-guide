#!/usr/bin/env bash

set -o nounset
set -o pipefail
set -o errexit
set -o xtrace

readonly MACRO_FILES=( 
  "pluverse-preamble.tex"
)
readonly BASE_URL="https://github.com/uw-pluverse/pluverse-latex-style-guide/raw/master/"

