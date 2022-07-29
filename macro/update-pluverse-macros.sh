#!/usr/bin/env bash

set -o nounset
set -o pipefail
set -o errexit
set -o xtrace

readonly MACRO_FILES=( 
  "pluverse-preamble.tex"
  "pluverse-preamble-end.tex"
)
readonly BASE_URL="https://raw.githubusercontent.com/uw-pluverse/pluverse-latex-style-guide/master/macro/"
readonly CURRENT_TIME=$(date +%Y%m%d-%H%M%S)
for file in "${MACRO_FILES[@]}" ; do
  if [[ -f "${file}" ]] ; then
    mv "${file}" ".backup.${file}.${CURRENT_TIME}" 
  fi
  wget "${BASE_URL}/${file}"
done

