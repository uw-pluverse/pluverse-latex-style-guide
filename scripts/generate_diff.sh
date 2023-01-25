#!/use/bin/env bash

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
