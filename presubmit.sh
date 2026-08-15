#!/usr/bin/env bash

# Runs every check that must pass before a change is committed.
#
# Usage:
#   ./presubmit.sh          run all checks
#   ./presubmit.sh -v       run all checks, verbose test output
#
# Set PYTHON to pick a specific interpreter, e.g. PYTHON=python3.11 ./presubmit.sh

set -o errexit
set -o nounset
set -o pipefail

readonly REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PYTHON="${PYTHON:-python3}"

VERBOSE=""
if [[ "$#" -gt 0 ]] ; then
  case "$1" in
    -v|--verbose) VERBOSE="-v" ;;
    -h|--help) sed -n '3,8p' "${BASH_SOURCE[0]}" | sed 's/^# \?//' ; exit 0 ;;
    *) echo "unknown argument: $1" >&2 ; exit 1 ;;
  esac
fi

cd "${REPO_ROOT}"

failures=0

announce() {
  echo
  echo "=============================================================="
  echo "$1"
  echo "=============================================================="
}

check() {
  local name="$1"
  shift
  if "$@" ; then
    echo "PASS: ${name}"
  else
    echo "FAIL: ${name}" >&2
    failures=$((failures + 1))
  fi
}

if ! command -v "${PYTHON}" > /dev/null ; then
  echo "error: ${PYTHON} not found; set PYTHON to a Python 3 interpreter" >&2
  exit 1
fi

announce "Python interpreter"
"${PYTHON}" --version

announce "Byte-compiling the formatter"
check "compile bin/pluverse-format.py" \
  "${PYTHON}" -m py_compile bin/pluverse-format.py test/test_pluverse_format.py

announce "Unit tests"
# The suite also formats every .tex file in the repository and asserts that the
# comment-stripped token stream is unchanged, so the checks below stay honest.
check "test/test_pluverse_format.py" \
  "${PYTHON}" -m unittest discover -s test ${VERBOSE}

announce "Formatter self-check"
# Reports which .tex files are not formatted.  This is advisory: the templates
# in this repository are deliberately left in their original form, so a
# non-clean result here does not fail the presubmit.
if "${PYTHON}" bin/pluverse-format.py --check macro template ; then
  echo "PASS: all .tex files are formatted"
else
  echo "NOTE: some .tex files are not formatted (advisory, not a failure)"
  echo "      run '${PYTHON} bin/pluverse-format.py --diff macro template' to preview"
fi

announce "Summary"
if [[ "${failures}" -ne 0 ]] ; then
  echo "${failures} check(s) FAILED"
  exit 1
fi
echo "all checks passed"
