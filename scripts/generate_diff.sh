#!/usr/bin/env bash

# This shell script can generate the difference between two multi-file latex projects
# It contains two steps:
# 1. use 'latexpand' to merge multi-file latex projects into single latex files
# 2. use 'latexdiff' to generate the difference between the two single latex files

# Note:
# 1. To show the difference of figures, the new latex project should include a new
# figure file instead of replacing the original one. Also, the original figure file
# should not be deleted in the new latex project.
# 2. Showing the difference of tables is not well supported as decribed in the
# following link: https://github.com/ftilmann/latexdiff/issues/5

set -o nounset
set -o pipefail
set -o xtrace
set -o errexit

if [[ "$#" != 2 ]] ; then
    echo "Usage: $0 <old main tex file> <new main tex file>"
    exit
fi

readonly TMP=$(mktemp -d)

trap "rm -rf ${TMP}" EXIT

readonly OLD_MAIN_TEX_FILE=$1
readonly NEW_MAIN_TEX_FILE=$2
readonly OLD_MAIN_TEX_NAME=$(basename "${OLD_MAIN_TEX_FILE}")
readonly NEW_MAIN_TEX_NAME=$(basename "${NEW_MAIN_TEX_FILE}")
readonly OLD_MAIN_DIR=$(dirname "${OLD_MAIN_TEX_FILE}")
readonly NEW_MAIN_DIR=$(dirname "${NEW_MAIN_TEX_FILE}")
readonly OUTPUT_PATH="${NEW_MAIN_DIR}/tmp_diff_main.tex"

readonly OLD_TMP_TEX_FILE="${TMP}/old_artical.tex"
readonly NEW_TMP_TEX_FILE="${TMP}/new_artical.tex"

# merge multi-file latex project into one file with 'latexpand'
pushd "${OLD_MAIN_DIR}"
latexpand "${OLD_MAIN_TEX_NAME}" -o "${OLD_TMP_TEX_FILE}"
popd

pushd "${NEW_MAIN_DIR}"
latexpand "${NEW_MAIN_TEX_NAME}" -o "${NEW_TMP_TEX_FILE}"
popd

latexdiff "${OLD_TMP_TEX_FILE}" "${NEW_TMP_TEX_FILE}" > "${OUTPUT_PATH}"

pdflatex -synctex=1 -interaction=nonstopmode "${OUTPUT_PATH}"
