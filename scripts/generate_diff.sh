#! /bin/bash

set -o nounset
set -o pipefail
set -o xtrace
set -o errexit

if [[ "$#" != 2 ]] ; then
    echo "Usage: $0 <old main tex file> <new main tex file>"
    exit
fi

readonly TMP=$(mktemp -d)

readonly OLD_MAIN_TEX_FILE=$1
readonly NEW_MAIN_TEX_FILE=$2
readonly OLD_MAIN_TEX_NAME=$(basename "${OLD_MAIN_TEX_FILE}")
readonly NEW_MAIN_TEX_NAME=$(basename "${NEW_MAIN_TEX_FILE}")
readonly OLD_MAIN_DIR=$(dirname "${OLD_MAIN_TEX_FILE}")
readonly NEW_MAIN_DIR=$(dirname "${NEW_MAIN_TEX_FILE}")

# merge multi-file latex project into one file with 'latexpand'
pushd "${OLD_MAIN_DIR}"
latexpand "${OLD_MAIN_TEX_NAME}" -o "${TMP}/old_artical.tex"
popd

pushd "${NEW_MAIN_DIR}"
latexpand "${NEW_MAIN_TEX_NAME}" -o "${TMP}/new_artical.tex"
popd

latexdiff "${TMP}/old_artical.tex" "${TMP}/new_artical.tex" > "${NEW_MAIN_DIR}/tmp_diff_main.tex"

pdflatex -synctex=1 -interaction=nonstopmode "${NEW_MAIN_DIR}/tmp_diff_main.tex"

rm -rf "${TMP}"

