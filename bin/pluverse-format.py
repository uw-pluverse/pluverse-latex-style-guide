#!/usr/bin/env python3
"""A diff-minimizing line formatter for LaTeX sources.

The formatter only ever *splits* an existing line; it never joins lines and
never reflows text into a following line.  A line that is already acceptable is
reproduced byte for byte.  The goal is that reformatting an existing paper
produces the smallest git diff that still guarantees "no line exceeds the
width", rather than producing evenly filled paragraphs.

Two properties are maintained by construction:

  * A break is only ever placed on whitespace that already exists in the
    source.  In LaTeX a newline and a space are the same token, so turning a
    space into a newline cannot change the typeset output.  Nothing is ever
    broken at a position that would have to *insert* a space, which is what
    protects constructions such as ``foo---bar``.

  * Regions where a newline is illegal or meaningful -- verbatim-like
    environments, ``\\verb`` arguments, and control symbols such as ``\\ `` --
    are never broken.

Run with --help for the command line interface.
"""

from __future__ import annotations

import argparse
import dataclasses
import difflib
import re
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path

DEFAULT_WIDTH = 80
BACKUP_ROOT_NAME = ".pluverse-format-backups"
MANIFEST_NAME = "MANIFEST.tsv"

# Break-point quality; lower is preferred.
TIER_SENTENCE = 0
TIER_CLAUSE = 1
TIER_PLAIN = 2
TIER_MATH = 3

# A forced break is allowed to leave a line this empty only if no better-tier
# candidate sits further to the right.  Without it, a comma in the third column
# would drag every following word onto its own line.
MIN_FILL_RATIO = 0.5

# Bodies of these environments are copied through untouched.
VERBATIM_ENVIRONMENTS = frozenset(
    {
        "verbatim",
        "verbatim*",
        "Verbatim",
        "Verbatim*",
        "BVerbatim",
        "LVerbatim",
        "lstlisting",
        "minted",
        "alltt",
        "comment",
        "semiverbatim",
        "filecontents",
        "filecontents*",
        "tcblisting",
        "asy",
        "sagesilent",
        "pycode",
    }
)

# Commands whose argument is scanned verbatim, so a newline inside it is either
# illegal or changes the output.
VERBATIM_COMMANDS = frozenset(
    {
        "\\verb",
        "\\lstinline",
        "\\mintinline",
        "\\url",
        "\\path",
        "\\href",
        "\\nolinkurl",
    }
)

# The formatter reflows prose.  A line that opens with one of these commands is
# a definition, a piece of package setup, or a structural directive: its
# argument is code or a fixed label rather than running text, so the line is
# left exactly as written even when it is over-long.  Names are matched as
# whole control words, never as prefixes.
NOBREAK_LINE_COMMANDS = frozenset(
    {
        # Environment delimiters and their option lists.
        "begin", "end",
        # Macro and environment definitions.
        "newcommand", "renewcommand", "providecommand", "DeclareRobustCommand",
        "DeclareMathOperator", "DeclarePairedDelimiter", "def", "gdef", "edef",
        "xdef", "let", "newenvironment", "renewenvironment", "newtheorem",
        "newcolumntype", "newif", "newlength", "newcounter", "newsavebox",
        "declaretheorem",
        # Package and document setup.
        "usepackage", "documentclass", "RequirePackage", "LoadClass",
        "definecolor", "colorlet", "setlength", "setcounter", "settowidth",
        "lstset", "lstdefinestyle", "lstdefinelanguage", "hypersetup",
        "tikzset", "pgfplotsset", "sisetup", "captionsetup", "setlist",
        "graphicspath", "bibliographystyle", "addbibresource", "pagestyle",
        "thispagestyle", "hyphenation", "DeclareUnicodeCharacter",
        "DeclareSIUnit", "newacronym", "geometry", "pagenumbering",
        # File inclusion and cross-reference anchors.
        "input", "include", "includeonly", "bibliography", "includegraphics",
        "label",
        # Structural and front-matter directives: the argument is a title or a
        # piece of metadata, not running text.
        "part", "chapter", "section", "subsection", "subsubsection",
        "paragraph", "subparagraph", "title", "subtitle", "author", "authors",
        "affiliation", "institution", "email", "address", "date", "keywords",
        "acmConference", "acmDOI", "acmISBN", "acmBooktitle", "acmPrice",
        "acmYear", "acmSubmissionID", "copyrightyear", "setcopyright",
        "ccsdesc", "IEEEauthorblockN", "IEEEauthorblockA",
        # TikZ/pgf paths: coordinates and anchors read as prose but are code.
        "draw", "node", "path", "fill", "filldraw", "shade", "shadedraw",
        "clip", "coordinate", "tikz", "addplot", "addlegendentry", "pgfdeclare",
        "pgfmathsetmacro", "foreach",
    }
)

# Rows of these environments are column-aligned code, not prose.  Breaking one
# at an '&' is harmless to the output but destroys the alignment that makes the
# source readable, so their bodies are left exactly as written.
ALIGNMENT_ENVIRONMENTS = frozenset(
    {
        "tabular", "tabular*", "tabularx", "tabulary", "tabu", "longtabu",
        "longtable", "supertabular", "xtabular", "tblr", "NiceTabular",
        "array", "matrix", "bmatrix", "Bmatrix", "pmatrix", "vmatrix",
        "Vmatrix", "smallmatrix", "cases", "dcases",
        "align", "align*", "aligned", "alignat", "alignat*", "alignedat",
        "gather", "gather*", "gathered", "split", "eqnarray", "eqnarray*",
        "IEEEeqnarray", "IEEEeqnarray*",
    }
)

# '% !TeX ...' and friends are directives for the editor, not prose.
EDITOR_DIRECTIVE_RE = re.compile(r"^\s*%+\s*!")

# A period closing one of these is an abbreviation, not the end of a sentence.
ABBREVIATIONS = frozenset(
    {
        "e.g.", "i.e.", "cf.", "etc.", "al.", "et.", "vs.", "viz.", "resp.",
        "approx.", "ca.", "cca.", "w.r.t.", "s.t.", "a.k.a.",
        "fig.", "figs.", "sec.", "secs.", "sect.", "tab.", "tabs.", "eq.",
        "eqs.", "alg.", "algs.", "def.", "thm.", "lem.", "prop.", "cor.",
        "ref.", "refs.", "ch.", "chap.", "app.", "no.", "nos.", "vol.", "pp.",
        "p.", "ed.", "eds.", "rev.", "tech.", "rep.",
        "dr.", "mr.", "mrs.", "ms.", "prof.", "st.", "jr.", "sr.",
        "inc.", "ltd.", "co.", "univ.", "dept.", "proc.", "conf.", "int.",
        "j.", "trans.", "assoc.", "syst.", "comput.",
    }
)

# Words that typically open a clause; used to pick a natural break point.
CLAUSE_STARTERS = frozenset(
    {
        "which", "who", "whom", "whose", "that",
        "because", "although", "though", "while", "whereas", "since",
        "unless", "until", "when", "whenever", "where", "wherever",
        "after", "before", "if",
        "however", "moreover", "furthermore", "therefore", "thus", "hence",
        "and", "but", "or", "nor", "yet", "so",
    }
)

# Openers of a leading subordinate clause.  When a sentence starts with one of
# these, its first top-level comma closes that clause and opens the main one.
SUBORDINATORS = frozenset(
    {
        "because", "although", "though", "while", "whereas", "since", "unless",
        "until", "if", "when", "whenever", "where", "wherever", "after",
        "before", "as", "once", "given", "assuming", "despite", "provided",
        "whether", "rather", "unlike", "regardless",
    }
)

# Openers of a short introductory adverbial such as "For instance," or "In this
# revision,".  An article or an adjective is deliberately absent, so that the
# comma in "A universal, language-agnostic scanner" is not mistaken for one.
INTRO_STARTERS = frozenset(
    {
        "for", "in", "to", "by", "with", "at", "on", "from", "during", "under",
        "without", "within", "through", "throughout", "across", "among",
        "besides", "beyond", "unlike", "despite", "instead", "overall",
        "thus", "hence", "however", "moreover", "furthermore", "therefore",
        "finally", "first", "firstly", "second", "secondly", "third", "thirdly",
        "next", "then", "nevertheless", "nonetheless", "additionally",
        "consequently", "specifically", "notably", "importantly", "similarly",
        "conversely", "meanwhile", "recently", "here", "otherwise", "indeed",
        "also", "alternatively", "accordingly", "unfortunately", "fortunately",
        "interestingly", "surprisingly", "ideally", "formally", "intuitively",
        "concretely", "conceptually", "practically", "empirically",
        "essentially", "typically", "generally", "historically",
        "traditionally", "subsequently", "afterwards", "lastly", "altogether",
        "that", "put", "more", "most", "as", "conversely", "crucially",
    }
)

# A short introductory adverbial is at most this many words long.
MAX_INTRO_WORDS = 5

CONTROL_WORD_RE = re.compile(r"\\[A-Za-z]+\*?")
LEADING_COMMAND_RE = re.compile(r"\\([A-Za-z@]+)\*?")
WHITESPACE_RUN_RE = re.compile(r"[ \t]+")
BEGIN_END_RE = re.compile(r"\\(begin|end)\s*\{([^}]*)\}")
FORMAT_PRAGMA_RE = re.compile(r"^\s*%+\s*pluverse-format\s*:\s*(off|on)\s*$", re.IGNORECASE)
COMMENT_MARKER_RE = re.compile(r"^(%+)([ \t]*)(.*)$")
SENTENCE_TAIL_RE = re.compile(r"[.!?][)\]}'\"\u2019\u201d]*$")
TRAILING_WORD_RE = re.compile(r"([A-Za-z][A-Za-z.]*)\.$")
LEADING_WORD_RE = re.compile(r"([A-Za-z']+)")


class FormatError(Exception):
    """Raised when a file cannot be processed."""


@dataclasses.dataclass(frozen=True)
class Options:
    width: int = DEFAULT_WIDTH
    sentence_split: str = "always"  # "always" | "fit"
    clause_split: str = "always"  # "always" | "fit"
    wrap_comments: bool = True


@dataclasses.dataclass(frozen=True)
class Break:
    """A candidate break, covering the whitespace run [start, end)."""

    start: int
    end: int
    tier: int


@dataclasses.dataclass
class FileResult:
    path: Path
    original: str
    formatted: str
    lines_split: int
    unbreakable: list[tuple[int, str]]

    @property
    def changed(self) -> bool:
        return self.original != self.formatted


# --------------------------------------------------------------------------
# Lexical analysis of a single source line
# --------------------------------------------------------------------------


def _skip_verbatim_argument(text: str, index: int, command: str) -> int:
    """Return the index just past the verbatim argument of ``command``."""
    n = len(text)
    j = index

    if command in ("\\lstinline", "\\mintinline"):
        while j < n and text[j] in " \t":
            j += 1
        if j < n and text[j] == "[":
            depth = 0
            while j < n:
                if text[j] == "[":
                    depth += 1
                elif text[j] == "]":
                    depth -= 1
                    if depth == 0:
                        j += 1
                        break
                j += 1
    if command == "\\mintinline" and j < n and text[j] == "{":
        j = _skip_braced_group(text, j)

    if j >= n:
        return n
    delimiter = text[j]
    if delimiter == "{":
        return _skip_braced_group(text, j)
    closing = text.find(delimiter, j + 1)
    return n if closing < 0 else closing + 1


def _skip_braced_group(text: str, index: int) -> int:
    depth = 0
    j = index
    n = len(text)
    while j < n:
        if text[j] == "\\":
            j += 2
            continue
        if text[j] == "{":
            depth += 1
        elif text[j] == "}":
            depth -= 1
            if depth == 0:
                return j + 1
        j += 1
    return n


def scan_line(text: str) -> tuple[int | None, list[tuple[int, int]], list[tuple[int, int]]]:
    """Split a line into its comment, no-break spans, and math spans.

    Returns ``(comment_start, nobreak_spans, math_spans)``.  ``comment_start``
    is the index of the ``%`` that opens a comment, or ``None``.
    """
    n = len(text)
    i = 0
    comment_start: int | None = None
    nobreak: list[tuple[int, int]] = []
    math: list[tuple[int, int]] = []
    math_open: int | None = None

    while i < n:
        char = text[i]

        if char == "\\":
            match = CONTROL_WORD_RE.match(text, i)
            if match:
                name = match.group(0).rstrip("*")
                if name in VERBATIM_COMMANDS:
                    end = _skip_verbatim_argument(text, match.end(), name)
                    nobreak.append((i, end))
                    i = end
                else:
                    i = match.end()
                continue

            pair = text[i : i + 2]
            if pair in ("\\(", "\\["):
                if math_open is None:
                    math_open = i
                i += 2
                continue
            if pair in ("\\)", "\\]"):
                if math_open is not None:
                    math.append((math_open, i + 2))
                    math_open = None
                i += 2
                continue
            # Control symbol.  ``\ `` swallows the space that follows the
            # backslash, so that space must never become a line break.
            nobreak.append((i, min(i + 2, n)))
            i += 2
            continue

        if char == "$":
            step = 2 if text.startswith("$$", i) else 1
            if math_open is None:
                math_open = i
            else:
                math.append((math_open, i + step))
                math_open = None
            i += step
            continue

        if char == "%":
            comment_start = i
            break

        i += 1

    if math_open is not None:
        math.append((math_open, n))
    return comment_start, nobreak, math


# --------------------------------------------------------------------------
# Break-point classification
# --------------------------------------------------------------------------


def _overlaps(start: int, end: int, spans: list[tuple[int, int]]) -> bool:
    return any(start < span_end and span_start < end for span_start, span_end in spans)


def is_sentence_boundary(left: str, right: str) -> bool:
    """Report whether a sentence ends at ``left`` and a new one opens at ``right``."""
    if not left or not right:
        return False
    if not SENTENCE_TAIL_RE.search(left):
        return False
    opener = right[0]
    if not (opener.isupper() or opener in "\\$(`\"'"):
        return False

    core = left.rstrip(")]}'\"\u2019\u201d")
    if not core.endswith("."):
        return True  # '!' or '?' is unambiguous.

    # A period closing a number is an enumeration label ("1. Importance") or
    # part of a decimal, never the end of a sentence.
    if core[:-1] and core[:-1][-1].isdigit():
        return False

    match = TRAILING_WORD_RE.search(core)
    if match:
        word = match.group(1)
        if f"{word.lower()}." in ABBREVIATIONS:
            return False
        if len(word) == 1 and word.isupper():
            return False  # A middle initial, as in "J. Doe".
    return True


def compute_depths(
    text: str,
    nobreak: list[tuple[int, int]],
    openers: str = "{([",
    closers: str = "})]",
) -> list[int]:
    """Bracket nesting depth at each index, ignoring escaped and verbatim text."""
    protected: set[int] = set()
    for start, end in nobreak:
        protected.update(range(start, end))

    depths = [0] * (len(text) + 1)
    depth = 0
    index = 0
    while index < len(text):
        char = text[index]
        if index in protected:
            depths[index] = depth
            index += 1
            continue
        if char == "\\" and index + 1 < len(text):
            depths[index] = depth
            depths[index + 1] = depth
            index += 2
            continue
        if char in openers:
            depths[index] = depth
            depth += 1
        elif char in closers:
            depth = max(0, depth - 1)
            depths[index] = depth
        else:
            depths[index] = depth
        index += 1
    depths[len(text)] = depth
    return depths


def _first_word(text: str) -> str:
    match = LEADING_WORD_RE.match(text.lstrip())
    return match.group(1).lower() if match else ""


def is_hard_clause_boundary(left: str, right: str) -> bool:
    """Report whether a genuine clause ends at ``left``.

    Only punctuation-anchored boundaries qualify.  Splitting on every relative
    pronoun would shatter "the property that we care about" into two lines,
    which is not a clause boundary in any useful sense.
    """
    if left.endswith((";", ":")):
        return True
    if not left.endswith(","):
        return False

    # The clause may open with a command, as in ", \proj must first convert".
    # That yields no leading word, which rules out the two word-based tests
    # below but must not rule out the opener tests that follow them.
    following = _first_word(right)
    # ", and it then invokes ..." / ", which allows ..."
    if following in CLAUSE_STARTERS:
        return True
    # ", corrupting the nesting structure ..." -- a participial clause.
    if following.endswith("ing") and len(following) > 4:
        return True

    words = left.rstrip(",").split()
    if not words:
        return False
    opener = _first_word(left)
    # "Because <subordinate clause>, <main clause>"
    if opener in SUBORDINATORS:
        return True
    # "For instance, ..." but not "A universal, language-agnostic scanner".
    if opener in INTRO_STARTERS and len(words) <= MAX_INTRO_WORDS:
        return True
    return False


def is_clause_boundary(left: str, right: str) -> bool:
    if left.endswith((",", ";", ":")):
        return True
    if right.startswith(("\\item", "\\begin{", "\\end{")):
        return True
    match = LEADING_WORD_RE.match(right)
    return bool(match) and match.group(1).lower() in CLAUSE_STARTERS


def find_breaks(
    code: str,
    nobreak: list[tuple[int, int]],
    math: list[tuple[int, int]],
) -> list[Break]:
    """Return every position in ``code`` at which a line break is safe."""
    candidates: list[Break] = []
    # A comma inside a parenthetical -- the one in "(e.g., within comments)" --
    # is not a clause boundary, so it must not be preferred as a break point.
    paren_depths = compute_depths(code, nobreak, "(", ")")
    for match in WHITESPACE_RUN_RE.finditer(code):
        start, end = match.span()
        if start == 0 or end == len(code):
            continue
        if _overlaps(start, end, nobreak):
            continue

        left = code[:start]
        right = code[end:]
        if not left.strip() or not right.strip():
            continue
        # ``\\`` and starred commands look past spaces for '[' and '*', so a
        # continuation line may not open with either.
        if right[0] in "[*":
            continue
        # An en- or em-dash binds to the words on both sides.
        if left.endswith("--") or right.startswith("--"):
            continue

        # Punctuation that closes a verbatim argument -- the '!' in
        # ``\verb!x!`` -- is a delimiter, not prose.
        after_verbatim = any(span_end == start for _, span_end in nobreak)

        inside_parens = paren_depths[start - 1] > 0

        if not after_verbatim and is_sentence_boundary(left, right):
            tier = TIER_SENTENCE
        elif not after_verbatim and not inside_parens and is_clause_boundary(left, right):
            tier = TIER_CLAUSE
        elif _overlaps(start, end, math):
            tier = TIER_MATH
        else:
            tier = TIER_PLAIN
        candidates.append(Break(start, end, tier))
    return candidates


# --------------------------------------------------------------------------
# Wrapping
# --------------------------------------------------------------------------


def _split_at(code: str, point: Break) -> tuple[str, str]:
    return code[: point.start].rstrip(), code[point.end :]


def split_sentences(code: str) -> list[str]:
    """Split ``code`` at every sentence boundary, regardless of line length."""
    pieces: list[str] = []
    rest = code
    while True:
        comment_start, nobreak, math = scan_line(rest)
        assert comment_start is None
        sentence_breaks = [b for b in find_breaks(rest, nobreak, math) if b.tier == TIER_SENTENCE]
        if not sentence_breaks:
            pieces.append(rest)
            return pieces
        left, right = _split_at(rest, sentence_breaks[0])
        if not left or not right:
            pieces.append(rest)
            return pieces
        pieces.append(left)
        rest = right


def split_clauses(code: str) -> list[str]:
    """Split ``code`` at every genuine, top-level clause boundary."""
    pieces: list[str] = []
    rest = code
    while True:
        comment_start, nobreak, math = scan_line(rest)
        assert comment_start is None
        depths = compute_depths(rest, nobreak)
        boundary = None
        for candidate in find_breaks(rest, nobreak, math):
            # A comma inside "(e.g., within comments)" belongs to the
            # parenthetical, not to the surrounding sentence.
            if depths[candidate.start - 1] != 0:
                continue
            if is_hard_clause_boundary(rest[: candidate.start], rest[candidate.end :]):
                boundary = candidate
                break
        if boundary is None:
            pieces.append(rest)
            return pieces
        left, right = _split_at(rest, boundary)
        if not left or not right:
            pieces.append(rest)
            return pieces
        pieces.append(left)
        rest = right


def fit_wrap(code: str, indent: str, options: Options) -> tuple[list[str], bool]:
    """Break ``code`` until every piece fits, if that is possible safely.

    Returns the pieces and whether an over-long piece had to be left behind.
    """
    limit = options.width - len(indent)
    pieces: list[str] = []
    rest = code
    overlong = False

    while True:
        if len(rest) <= limit:
            pieces.append(rest)
            break

        comment_start, nobreak, math = scan_line(rest)
        assert comment_start is None
        candidates = find_breaks(rest, nobreak, math)
        if not candidates:
            pieces.append(rest)
            overlong = True
            break

        fitting = [b for b in candidates if len(rest[: b.start].rstrip()) <= limit]
        if fitting:
            well_filled = [
                b
                for b in fitting
                if len(rest[: b.start].rstrip()) >= MIN_FILL_RATIO * limit
            ]
            pool = well_filled or fitting
            best_tier = min(b.tier for b in pool)
            chosen = max((b for b in pool if b.tier == best_tier), key=lambda b: b.start)
        else:
            # Nothing fits; break as early as possible so that only the first
            # piece stays over-long.
            chosen = min(candidates, key=lambda b: b.start)
            overlong = True

        left, right = _split_at(rest, chosen)
        if not left or not right:
            pieces.append(rest)
            overlong = True
            break
        pieces.append(left)
        rest = right

    return pieces, overlong


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def format_code(code: str, indent: str, options: Options) -> tuple[list[str], bool]:
    if options.sentence_split == "always":
        sentences = split_sentences(code)
    else:
        sentences = [code]

    pieces: list[str] = []
    overlong = False
    for sentence in sentences:
        # Clause splitting only applies to a sentence that does not already fit;
        # a short sentence keeps its clauses together on one line.
        if (
            options.clause_split == "always"
            and len(indent) + len(sentence) > options.width
        ):
            clauses = split_clauses(sentence)
        else:
            clauses = [sentence]
        for clause in clauses:
            wrapped, piece_overlong = fit_wrap(clause, indent, options)
            pieces.extend(wrapped)
            overlong = overlong or piece_overlong

    # A break may only turn existing whitespace into a newline.  If that
    # invariant was violated the line is left exactly as it was.
    if _normalize(" ".join(pieces)) != _normalize(code):
        return [code], False
    if any(not piece.strip() for piece in pieces):
        return [code], False
    return pieces, overlong


def format_comment_line(indent: str, body: str, options: Options) -> list[str]:
    """Wrap a whole-line comment, repeating its ``%`` marker on each line."""
    match = COMMENT_MARKER_RE.match(body)
    if not match:
        return [indent + body]
    marker, gap, text = match.groups()
    prefix = indent + marker + gap
    if not text.strip():
        return [indent + body]

    limit = options.width - len(prefix)
    if limit < 20:
        return [indent + body]

    pieces: list[str] = []
    rest = text
    while len(rest) > limit:
        candidates = find_breaks(rest, [], [])
        fitting = [b for b in candidates if len(rest[: b.start].rstrip()) <= limit]
        if not fitting:
            break
        well_filled = [
            b for b in fitting if len(rest[: b.start].rstrip()) >= MIN_FILL_RATIO * limit
        ]
        pool = well_filled or fitting
        best_tier = min(b.tier for b in pool)
        chosen = max((b for b in pool if b.tier == best_tier), key=lambda b: b.start)
        left, right = _split_at(rest, chosen)
        if not left or not right:
            break
        pieces.append(left)
        rest = right
    pieces.append(rest)

    if _normalize(" ".join(pieces)) != _normalize(text):
        return [indent + body]
    return [prefix + piece for piece in pieces]


# --------------------------------------------------------------------------
# Whole-file processing
# --------------------------------------------------------------------------


def has_alignment_separator(line: str) -> bool:
    """Report whether the line carries an unescaped, non-comment '&'."""
    comment_start, nobreak, _ = scan_line(line)
    limit = len(line) if comment_start is None else comment_start
    for index in range(limit):
        if line[index] != "&":
            continue
        # '\&' is a literal ampersand; scan_line records it as a control symbol.
        if not _overlaps(index, index + 1, nobreak):
            return True
    return False


def is_directive_line(stripped: str) -> bool:
    """Report whether a line is LaTeX machinery rather than prose."""
    if EDITOR_DIRECTIVE_RE.match(stripped):
        return True
    match = LEADING_COMMAND_RE.match(stripped)
    return bool(match) and match.group(1) in NOBREAK_LINE_COMMANDS


def format_line(line: str, options: Options) -> tuple[list[str], bool]:
    """Format one source line into one or more output lines."""
    stripped = line.strip()
    if not stripped:
        return [line], False

    indent = line[: len(line) - len(line.lstrip())]
    if is_directive_line(stripped):
        return [line], len(line) > options.width

    comment_start, _, _ = scan_line(line)

    if comment_start is not None and not line[len(indent) : comment_start].strip():
        if not options.wrap_comments or len(line) <= options.width:
            return [line], False
        return format_comment_line(indent, line[comment_start:], options), False

    if comment_start is None:
        code = line[len(indent) :]
        comment = ""
    else:
        code = line[len(indent) : comment_start]
        comment = line[comment_start:]

    if not code.strip():
        return [line], False

    # A trailing '%' suppresses the newline that follows it, so the comment has
    # to stay attached to the final piece.
    pieces, overlong = format_code(code, indent, options)
    if comment:
        pieces = list(pieces)
        pieces[-1] = pieces[-1] + comment

    result = [indent + piece for piece in pieces]
    if len(result) == 1:
        result = [line]
    return result, overlong


def format_text(text: str, options: Options) -> tuple[str, int, list[tuple[int, str]]]:
    lines = text.split("\n")
    output: list[str] = []
    lines_split = 0
    unbreakable: list[tuple[int, str]] = []

    verbatim_stack: list[str] = []
    alignment_stack: list[str] = []
    formatting_enabled = True

    for number, line in enumerate(lines, start=1):
        pragma = FORMAT_PRAGMA_RE.match(line)
        if pragma:
            formatting_enabled = pragma.group(1).lower() == "on"
            output.append(line)
            continue

        environments = BEGIN_END_RE.findall(line)
        entering = verbatim_stack or any(
            kind == "begin" and name in VERBATIM_ENVIRONMENTS for kind, name in environments
        )
        aligned = bool(alignment_stack) or any(
            kind == "begin" and name in ALIGNMENT_ENVIRONMENTS for kind, name in environments
        )

        for kind, name in environments:
            if kind == "begin" and name in VERBATIM_ENVIRONMENTS:
                verbatim_stack.append(name)
            elif kind == "end" and verbatim_stack and verbatim_stack[-1] == name:
                verbatim_stack.pop()
            elif kind == "begin" and name in ALIGNMENT_ENVIRONMENTS:
                alignment_stack.append(name)
            elif kind == "end" and alignment_stack and alignment_stack[-1] == name:
                alignment_stack.pop()

        if entering or aligned or not formatting_enabled:
            output.append(line)
            continue

        # A row of a table the environment tracking did not recognise: an
        # unescaped '&' is only legal inside an alignment, so it marks one.
        if has_alignment_separator(line):
            output.append(line)
            continue

        formatted, overlong = format_line(line, options)
        if len(formatted) > 1:
            lines_split += 1
        if overlong and len(line) > options.width:
            unbreakable.append((number, line))
        output.extend(formatted)

    return "\n".join(output), lines_split, unbreakable


def format_file_content(text: str, options: Options) -> str:
    return format_text(text, options)[0]


# --------------------------------------------------------------------------
# Backups
# --------------------------------------------------------------------------


class BackupSession:
    """Copies each file to a timestamped directory before it is rewritten."""

    def __init__(self, root: Path, enabled: bool) -> None:
        self.root = root
        self.enabled = enabled
        self.directory: Path | None = None
        self.entries: list[tuple[Path, Path]] = []

    def _ensure_directory(self) -> Path:
        if self.directory is None:
            stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            directory = self.root / stamp
            suffix = 1
            while directory.exists():
                directory = self.root / f"{stamp}-{suffix}"
                suffix += 1
            directory.mkdir(parents=True)
            self.directory = directory
        return self.directory

    def save(self, path: Path) -> Path | None:
        if not self.enabled:
            return None
        directory = self._ensure_directory()
        absolute = path.resolve()
        try:
            relative = absolute.relative_to(Path.cwd())
        except ValueError:
            relative = Path(*absolute.parts[1:])
        destination = directory / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(absolute, destination)
        self.entries.append((destination, absolute))
        self._write_manifest(directory)
        return destination

    def _write_manifest(self, directory: Path) -> None:
        with (directory / MANIFEST_NAME).open("w", encoding="utf-8") as handle:
            handle.write("# backup\toriginal\n")
            for backup, original in self.entries:
                handle.write(f"{backup.relative_to(directory)}\t{original}\n")


def list_backups(root: Path) -> list[Path]:
    if not root.is_dir():
        return []
    return sorted((child for child in root.iterdir() if child.is_dir()), key=lambda p: p.name)


def restore_backup(root: Path, stamp: str | None) -> int:
    sessions = list_backups(root)
    if not sessions:
        raise FormatError(f"no backups found under {root}")
    if stamp is None:
        session = sessions[-1]
    else:
        matches = [s for s in sessions if s.name == stamp]
        if not matches:
            raise FormatError(f"no backup named {stamp!r} under {root}")
        session = matches[0]

    manifest = session / MANIFEST_NAME
    if not manifest.is_file():
        raise FormatError(f"backup {session} has no {MANIFEST_NAME}")

    restored = 0
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        relative, original = line.split("\t", 1)
        source = session / relative
        if not source.is_file():
            print(f"missing backup file: {source}", file=sys.stderr)
            continue
        destination = Path(original)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        restored += 1
    print(f"restored {restored} file(s) from {session}")
    return restored


# --------------------------------------------------------------------------
# Verifying the built PDF
# --------------------------------------------------------------------------
#
# Comparing PDF bytes is useless: two builds of identical sources differ,
# because the file embeds a creation timestamp and a document ID.  Comparing
# extracted text is better but blind to layout -- it cannot see a line that
# moved, a changed font, or a figure that shifted.
#
# So each page is rasterized and the images are compared.  Rendering is
# deterministic for a given renderer and resolution, and it ignores the
# metadata that makes the raw bytes differ, so identical pixels mean identical
# content *and* identical layout.


def _digest(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest()


@dataclasses.dataclass(frozen=True)
class BuildVerification:
    """Everything needed to rebuild one document.

    The main file determines the rest: LaTeX names its output after the job
    name, so ``main.tex`` yields ``main.pdf``.  The build reads sources from the
    main file's directory but writes every artifact into ``outdir``, a private
    scratch directory.

    Writing elsewhere matters when an editor rebuilds the document on save, as
    LaTeX Workshop, TeXstudio and Antigravity all do.  Two builds sharing one
    directory interleave their writes to ``main.aux``, and a half-written .aux
    makes the next pass die with "File ended while scanning use of
    \\@newl@bel".  A private output directory removes the shared state, and as a
    bonus the author's own ``main.pdf`` is never overwritten.
    """

    main: Path
    dpi: int
    outdir: Path

    @property
    def directory(self) -> Path:
        return self.main.parent

    @property
    def pdf(self) -> Path:
        return self.outdir / f"{self.main.stem}.pdf"


# LaTeX resolves cross-references through the .aux file, so the first pass over
# a clean directory renders "??" where the second renders "Section 2".  Build
# until the .aux stops changing, or the reference and the candidate would differ
# for reasons that have nothing to do with formatting.
MAX_BUILD_PASSES = 5


def build_document(verification: BuildVerification) -> str:
    """Build the document to convergence.  Returns the command used."""
    import subprocess

    name = verification.main.name

    def run(command: list[str], cwd: Path | None = None, extra_paths: Path | None = None) -> None:
        environment = None
        if extra_paths is not None:
            import os

            environment = dict(os.environ)
            for variable in ("BIBINPUTS", "BSTINPUTS", "TEXINPUTS"):
                existing = environment.get(variable, "")
                environment[variable] = f"{extra_paths}:{existing}"
        completed = subprocess.run(
            command,
            cwd=str(cwd or verification.directory),
            capture_output=True,
            text=True,
            env=environment,
        )
        if completed.returncode != 0:
            output = (completed.stdout + completed.stderr).strip().splitlines()
            errors = [line for line in output if line.startswith("!")][:5]
            tail = errors or output[-15:]
            raise FormatError(
                f"build failed (exit {completed.returncode}): "
                f"{' '.join(command)}\n  " + "\n  ".join(tail)
            )

    verification.outdir.mkdir(parents=True, exist_ok=True)

    if shutil.which("latexmk"):
        # latexmk already iterates to a fixed point and runs bibtex/biber.
        command = [
            "latexmk", "-pdf", "-interaction=nonstopmode",
            f"-outdir={verification.outdir}", name,
        ]
        run(command)
        return "latexmk -pdf -outdir=<private>"

    stem = verification.main.stem
    command = [
        "pdflatex", "-interaction=nonstopmode", "-halt-on-error",
        f"-output-directory={verification.outdir}", name,
    ]
    aux = verification.outdir / f"{stem}.aux"
    steps = ["pdflatex"]

    run(command)
    # Without this the citations render as "[?]" and the bibliography is
    # missing entirely, so the verified document would not be the real one.
    bibliography = run_bibliography_tool(verification, run)
    if bibliography:
        steps.append(bibliography)

    previous: bytes | None = None
    for _ in range(MAX_BUILD_PASSES):
        run(command)
        current = aux.read_bytes() if aux.is_file() else b""
        if current == previous:
            break
        previous = current
    steps.append(f"pdflatex (repeated until stable, up to {MAX_BUILD_PASSES}x)")
    return " -> ".join(steps)


def run_bibliography_tool(verification: BuildVerification, run) -> str | None:
    """Run biber or bibtex if the document cites anything.  Returns the tool."""
    stem = verification.main.stem
    directory = verification.outdir

    # biblatex leaves a .bcf control file; the traditional path leaves
    # \citation entries in the .aux.
    if (directory / f"{stem}.bcf").is_file():
        if not shutil.which("biber"):
            return None
        run(["biber", stem], cwd=directory)
        return "biber"

    aux = directory / f"{stem}.aux"
    if not aux.is_file():
        return None
    contents = aux.read_text(encoding="utf-8", errors="replace")
    if "\\citation{" not in contents or "\\bibdata{" not in contents:
        return None
    if not shutil.which("bibtex"):
        return None
    # bibtex reads the .aux from the output directory but must still find the
    # .bib and .bst files, which live beside the sources.
    run(["bibtex", stem], cwd=directory, extra_paths=verification.directory)
    return "bibtex"


def rasterize_pdf(pdf: Path, prefix: Path, dpi: int) -> list[Path]:
    import subprocess

    completed = subprocess.run(
        ["pdftoppm", "-r", str(dpi), "-png", str(pdf), str(prefix)],
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise FormatError(f"pdftoppm failed on {pdf}: {completed.stderr.strip()}")
    return sorted(prefix.parent.glob(f"{prefix.name}-*.png"))


def extract_pdf_text(pdf: Path, destination: Path) -> str:
    import subprocess

    completed = subprocess.run(
        ["pdftotext", "-layout", str(pdf), str(destination)],
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise FormatError(f"pdftotext failed on {pdf}: {completed.stderr.strip()}")
    return destination.read_text(encoding="utf-8", errors="replace")


def write_difference_image(reference: Path, candidate: Path, destination: Path) -> bool:
    """Render a visual diff of two page images, if ImageMagick is available."""
    import subprocess

    if not shutil.which("compare"):
        return False
    subprocess.run(
        ["compare", str(reference), str(candidate), str(destination)],
        capture_output=True,
    )
    return destination.is_file()


def compare_pdfs(
    reference: Path, candidate: Path, dpi: int, workdir: Path
) -> tuple[bool, str]:
    """Compare two PDFs page by page.  Returns ``(identical, description)``."""
    if shutil.which("pdftoppm"):
        reference_pages = rasterize_pdf(reference, workdir / "reference", dpi)
        candidate_pages = rasterize_pdf(candidate, workdir / "candidate", dpi)

        if len(reference_pages) != len(candidate_pages):
            return False, (
                f"page count changed: {len(reference_pages)} -> "
                f"{len(candidate_pages)}"
            )
        if not reference_pages:
            return False, "the build produced a PDF with no pages"

        differing = [
            number
            for number, (before, after) in enumerate(
                zip(reference_pages, candidate_pages), start=1
            )
            if _digest(before) != _digest(after)
        ]
        if not differing:
            return True, f"{len(reference_pages)} page(s) render identically at {dpi} dpi"

        first = differing[0]
        detail = f"page(s) {', '.join(str(n) for n in differing)} render differently"
        image = workdir / f"difference-page-{first}.png"
        if write_difference_image(
            reference_pages[first - 1], candidate_pages[first - 1], image
        ):
            detail += f"\n  visual diff of page {first}: {image}"
        return False, detail

    if shutil.which("pdftotext"):
        before_text = extract_pdf_text(reference, workdir / "reference.txt")
        after_text = extract_pdf_text(candidate, workdir / "candidate.txt")
        if before_text == after_text:
            return True, "extracted text is identical (layout NOT checked: install poppler-utils for pdftoppm)"
        return False, "extracted text differs"

    raise FormatError(
        "cannot compare PDFs: install poppler-utils for 'pdftoppm' (preferred) "
        "or 'pdftotext'"
    )


# --------------------------------------------------------------------------
# Command line interface
# --------------------------------------------------------------------------


def collect_tex_files(paths: list[str]) -> list[Path]:
    found: list[Path] = []
    for raw in paths:
        path = Path(raw)
        if path.is_dir():
            found.extend(sorted(p for p in path.rglob("*.tex") if p.is_file()))
        elif path.is_file():
            if path.suffix != ".tex":
                print(f"skipping {path}: not a .tex file", file=sys.stderr)
                continue
            found.append(path)
        else:
            print(f"skipping {path}: no such file or directory", file=sys.stderr)
    # Preserve order while removing duplicates.
    seen: set[Path] = set()
    unique: list[Path] = []
    for path in found:
        resolved = path.resolve()
        if resolved not in seen:
            seen.add(resolved)
            unique.append(path)
    return unique


def write_atomically(path: Path, text: str) -> None:
    """Replace a file in one step, so no reader ever sees it half written.

    An editor that rebuilds on change -- Antigravity, LaTeX Workshop -- may read
    the file at any moment.  Writing in place would let it read a truncated
    document; a rename is atomic, so it sees either the old file or the new one.
    """
    import os

    temporary = path.with_name(f".{path.name}.pluverse-tmp")
    try:
        temporary.write_text(text, encoding="utf-8", newline="")
        shutil.copystat(path, temporary)
        os.replace(temporary, path)
    except OSError:
        temporary.unlink(missing_ok=True)
        raise


def process_file(path: Path, options: Options) -> FileResult:
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise FormatError(f"{path}: not valid UTF-8 ({error})") from error

    uses_crlf = "\r\n" in text
    normalized = text.replace("\r\n", "\n") if uses_crlf else text

    formatted, lines_split, unbreakable = format_text(normalized, options)
    if uses_crlf:
        formatted = formatted.replace("\n", "\r\n")
        normalized = text
    return FileResult(path, normalized, formatted, lines_split, unbreakable)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pluverse-format.py",
        description="Wrap over-long lines in LaTeX sources without reflowing text.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "The formatter only splits lines; it never joins them, so a line that\n"
            "already fits is left byte-identical.  Add '% pluverse-format: off' to\n"
            "suspend formatting and '% pluverse-format: on' to resume it."
        ),
    )
    parser.add_argument("paths", nargs="*", metavar="FILE_OR_DIR")
    parser.add_argument(
        "-w", "--width", type=int, default=DEFAULT_WIDTH,
        help=f"maximum line length (default: {DEFAULT_WIDTH})",
    )
    parser.add_argument(
        "--sentence-split", choices=("always", "fit"), default="always",
        help="'always' puts every sentence on its own line; 'fit' only breaks "
             "at sentence boundaries when a line is too long (default: always)",
    )
    parser.add_argument(
        "--clause-split", choices=("always", "fit"), default="always",
        help="'always' puts every clause of an over-long sentence on its own "
             "line; 'fit' only breaks enough to reach the width (default: always)",
    )
    parser.add_argument(
        "--no-comment-wrap", dest="wrap_comments", action="store_false",
        help="leave over-long whole-line comments alone",
    )
    parser.add_argument(
        "--check", action="store_true",
        help="do not write anything; exit 1 if any file would change",
    )
    parser.add_argument(
        "--diff", action="store_true",
        help="do not write anything; print a unified diff instead",
    )
    parser.add_argument(
        "--stdout", action="store_true",
        help="do not write anything; print the formatted file to stdout",
    )
    parser.add_argument(
        "--no-backup", dest="backup", action="store_false",
        help="rewrite files without saving a backup copy first",
    )
    parser.add_argument(
        "--backup-dir", default=BACKUP_ROOT_NAME, metavar="DIR",
        help=f"where backups are kept (default: ./{BACKUP_ROOT_NAME})",
    )
    parser.add_argument(
        "--list-backups", action="store_true",
        help="list saved backup sessions and exit",
    )
    parser.add_argument(
        "--restore", nargs="?", const="", metavar="TIMESTAMP",
        help="restore files from a backup session (default: the most recent) and exit",
    )
    verify = parser.add_argument_group(
        "PDF verification",
        "Build the document before and after formatting and prove that the "
        "rendered pages are unchanged.  If they are not, the files are restored "
        "from the backup automatically.",
    )
    verify.add_argument(
        "--verify", metavar="MAIN.TEX",
        help="the main .tex file; it is built before and after formatting and "
             "the rendered pages are compared. The PDF is MAIN.pdf beside it",
    )
    verify.add_argument(
        "--verify-dpi", type=int, default=150, metavar="N",
        help="resolution used to compare rendered pages (default: 150)",
    )
    parser.add_argument("-q", "--quiet", action="store_true", help="only report problems")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    backup_root = Path(args.backup_dir)

    if args.list_backups:
        sessions = list_backups(backup_root)
        if not sessions:
            print(f"no backups under {backup_root}")
        for session in sessions:
            manifest = session / MANIFEST_NAME
            count = 0
            if manifest.is_file():
                count = sum(
                    1
                    for line in manifest.read_text(encoding="utf-8").splitlines()
                    if line and not line.startswith("#")
                )
            print(f"{session.name}\t{count} file(s)")
        return 0

    if args.restore is not None:
        try:
            restore_backup(backup_root, args.restore or None)
        except FormatError as error:
            print(f"error: {error}", file=sys.stderr)
            return 2
        return 0

    if not args.paths:
        parser.error("no input files; pass one or more .tex files or directories")

    if args.width < 20:
        parser.error("--width must be at least 20")

    options = Options(
        width=args.width,
        sentence_split=args.sentence_split,
        clause_split=args.clause_split,
        wrap_comments=args.wrap_comments,
    )

    files = collect_tex_files(args.paths)
    if not files:
        print("no .tex files to format", file=sys.stderr)
        return 2

    dry_run = args.check or args.diff or args.stdout

    verification: BuildVerification | None = None
    reference: ReferencePdf | None = None
    scratch: Path | None = None
    if args.verify:
        if dry_run:
            parser.error("--verify rewrites files, so it cannot be combined "
                         "with --check, --diff or --stdout")
        if not args.backup:
            parser.error("--verify needs backups so it can restore the files "
                         "if the PDF changes; drop --no-backup")
        main_tex = Path(args.verify).resolve()
        if not main_tex.is_file():
            print(f"error: {args.verify}: no such file", file=sys.stderr)
            return 2
        if main_tex.suffix != ".tex":
            print(f"error: {args.verify}: not a .tex file", file=sys.stderr)
            return 2
        scratch = Path(tempfile.mkdtemp(prefix="pluverse-format-verify-"))
        verification = BuildVerification(
            main=main_tex, dpi=args.verify_dpi, outdir=scratch / "build"
        )

        # Build the reference *before* touching anything: if the document does
        # not build to begin with, there is nothing to compare against and the
        # files must be left alone.
        if not args.quiet:
            print(f"building the reference PDF from {main_tex.name}")
        try:
            reference = capture_reference(verification, scratch)
        except (FormatError, OSError) as error:
            print(f"error: {error}", file=sys.stderr)
            shutil.rmtree(scratch, ignore_errors=True)
            return 2
        if not args.quiet:
            print("reference PDF built in a private directory\n")

    backups = BackupSession(backup_root, enabled=args.backup and not dry_run)

    changed_files = 0
    failures = 0
    all_unbreakable: list[tuple[Path, int, str]] = []

    for path in files:
        try:
            result = process_file(path, options)
        except (FormatError, OSError) as error:
            print(f"error: {error}", file=sys.stderr)
            failures += 1
            continue

        for number, line in result.unbreakable:
            all_unbreakable.append((path, number, line))

        if args.stdout:
            sys.stdout.write(result.formatted)
            continue

        if not result.changed:
            if not args.quiet and not args.diff:
                print(f"unchanged   {path}")
            continue

        changed_files += 1

        if args.diff:
            diff = difflib.unified_diff(
                result.original.splitlines(keepends=True),
                result.formatted.splitlines(keepends=True),
                fromfile=f"a/{path}",
                tofile=f"b/{path}",
            )
            sys.stdout.writelines(diff)
            continue

        if args.check:
            print(f"would reformat {path} ({result.lines_split} line(s) split)")
            continue

        try:
            backups.save(path)
            write_atomically(path, result.formatted)
        except OSError as error:
            print(f"error: {path}: {error}", file=sys.stderr)
            failures += 1
            continue

        if not args.quiet:
            print(f"reformatted {path} ({result.lines_split} line(s) split)")

    if all_unbreakable and not args.quiet:
        print(
            f"\n{len(all_unbreakable)} line(s) could not be shortened safely:",
            file=sys.stderr,
        )
        for path, number, line in all_unbreakable:
            print(f"  {path}:{number}: {len(line)} chars", file=sys.stderr)

    if not args.quiet and not args.stdout and not args.diff:
        if backups.directory is not None:
            print(f"\nbackups saved to {backups.directory}")
            print(f"restore with: {sys.argv[0]} --restore {backups.directory.name}")
        if args.check:
            print(f"\n{changed_files} file(s) would be reformatted")
        else:
            print(f"\n{changed_files} file(s) reformatted, {len(files) - changed_files} unchanged")

    if verification is not None and scratch is not None:
        if changed_files == 0:
            if not args.quiet:
                print("\nnothing was reformatted, so the PDF cannot have changed")
            shutil.rmtree(scratch, ignore_errors=True)
            return 2 if failures else 0

        assert reference is not None
        verdict = verify_build_output(verification, reference, scratch, args.quiet)
        if verdict != 0:
            # verify_build_output has already explained what went wrong.
            print("\nverification failed; restoring your files", file=sys.stderr)
            try:
                restore_backup(backup_root, backups.directory.name)
            except FormatError as error:
                print(f"error: could not restore: {error}", file=sys.stderr)
            print(f"diagnostics kept in {scratch}", file=sys.stderr)
            return verdict
        shutil.rmtree(scratch, ignore_errors=True)

    if failures:
        return 2
    if args.check and changed_files:
        return 1
    return 0


@dataclasses.dataclass(frozen=True)
class ReferencePdf:
    copy: Path
    mtime: float
    digest: str


def capture_reference(
    verification: BuildVerification, scratch: Path
) -> ReferencePdf:
    """Build the document once and stash the PDF to compare against later."""
    build_document(verification)
    if not verification.pdf.is_file():
        raise FormatError(
            f"the build produced no {verification.pdf.name}; "
            f"expected it beside {verification.main}"
        )
    copy = scratch / "reference.pdf"
    shutil.copy2(verification.pdf, copy)
    return ReferencePdf(
        copy=copy,
        mtime=verification.pdf.stat().st_mtime,
        digest=_digest(verification.pdf),
    )


def verify_build_output(
    verification: BuildVerification,
    reference: ReferencePdf,
    scratch: Path,
    quiet: bool,
) -> int:
    """Rebuild and compare against the reference.  Returns an exit code."""
    if not quiet:
        print(f"\nrebuilding {verification.main} to verify")
    try:
        build_document(verification)
        if not verification.pdf.is_file():
            print(
                f"error: the rebuild produced no {verification.pdf.name}",
                file=sys.stderr,
            )
            return 3
        # A build that silently skipped the document would compare the PDF
        # against itself and report success, so establish it was regenerated.
        rebuilt = (
            verification.pdf.stat().st_mtime > reference.mtime
            or _digest(verification.pdf) != reference.digest
        )
        if not rebuilt:
            print(
                f"error: {verification.pdf.name} was not regenerated, so "
                "nothing was actually verified",
                file=sys.stderr,
            )
            return 3
        candidate = scratch / "candidate.pdf"
        shutil.copy2(verification.pdf, candidate)
        identical, detail = compare_pdfs(
            reference.copy, candidate, verification.dpi, scratch
        )
    except (FormatError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 3

    if identical:
        if not quiet:
            print(f"{verification.pdf.name} verified unchanged: {detail}")
        return 0
    print(f"error: {verification.pdf.name} changed: {detail}", file=sys.stderr)
    return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
