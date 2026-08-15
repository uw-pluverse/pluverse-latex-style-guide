#!/usr/bin/env python3
"""Tests for bin/pluverse-format.py.

Run with:  python3 -m unittest discover -s test -v
      or:  python3 test/test_pluverse_format.py
"""

from __future__ import annotations

import importlib.util
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "bin" / "pluverse-format.py"

_spec = importlib.util.spec_from_file_location("pluverse_format", SCRIPT)
assert _spec and _spec.loader
pf = importlib.util.module_from_spec(_spec)
# dataclasses resolves annotations through sys.modules, so register first.
sys.modules["pluverse_format"] = pf
_spec.loader.exec_module(pf)


def fmt(text: str, **kwargs: object) -> str:
    options = pf.Options(**kwargs)  # type: ignore[arg-type]
    return pf.format_file_content(text, options)


class PreservationTests(unittest.TestCase):
    """A line under the width with one sentence must survive byte for byte."""

    def test_short_single_sentence_line_is_untouched(self):
        text = "We reduce the program using Perses.\n"
        self.assertEqual(fmt(text), text)

    def test_three_word_line_is_untouched(self):
        text = "Only three words\n"
        self.assertEqual(fmt(text), text)

    def test_trailing_whitespace_on_short_line_is_preserved(self):
        text = "A short line with trailing space.   \n"
        self.assertEqual(fmt(text), text)

    def test_blank_lines_are_preserved(self):
        text = "First paragraph.\n\nSecond paragraph.\n"
        self.assertEqual(fmt(text), text)

    def test_indentation_is_preserved_on_every_piece(self):
        text = (
            "    The reducer removes tokens from the program, and it then "
            "invokes the oracle to check the property.\n"
        )
        result = fmt(text)
        for line in result.splitlines():
            self.assertTrue(line.startswith("    "), line)

    def test_exactly_at_width_is_untouched(self):
        line = "x" * 80 + "\n"
        self.assertEqual(fmt(line), line)

    def test_no_blank_line_is_ever_introduced(self):
        text = (
            "This sentence is quite long and will certainly need to be broken "
            "somewhere along its length.\n"
        )
        result = fmt(text)
        self.assertNotIn("\n\n", result)


class WidthTests(unittest.TestCase):
    def test_long_line_is_broken_under_width(self):
        text = (
            "The reduction algorithm repeatedly removes syntactic units from "
            "the program and then invokes the property test on the candidate.\n"
        )
        result = fmt(text)
        self.assertGreater(len(result.splitlines()), 1)
        for line in result.splitlines():
            self.assertLessEqual(len(line), 80, line)

    def test_words_are_never_reflowed_upward(self):
        text = "Short.\nAnother short line here.\n"
        self.assertEqual(fmt(text), text)

    def test_custom_width(self):
        text = "alpha beta gamma delta epsilon zeta eta theta iota kappa\n"
        result = fmt(text, width=30)
        for line in result.splitlines():
            self.assertLessEqual(len(line), 30, line)


class SentenceTests(unittest.TestCase):
    def test_second_sentence_starts_a_new_line_even_when_short(self):
        text = "We reduce it. The oracle runs.\n"
        self.assertEqual(fmt(text), "We reduce it.\nThe oracle runs.\n")

    def test_three_short_sentences_each_get_a_line(self):
        text = "One. Two. Three.\n"
        self.assertEqual(fmt(text), "One.\nTwo.\nThree.\n")

    def test_sentence_split_respects_indentation(self):
        text = "  First one. Second one.\n"
        self.assertEqual(fmt(text), "  First one.\n  Second one.\n")

    def test_question_and_exclamation_end_sentences(self):
        text = "Does it work? It does. Excellent!\n"
        self.assertEqual(fmt(text), "Does it work?\nIt does.\nExcellent!\n")

    def test_sentence_before_a_latex_command(self):
        text = "This is shown in the plot. \\Cref{fig:one} gives the detail.\n"
        self.assertEqual(
            fmt(text),
            "This is shown in the plot.\n\\Cref{fig:one} gives the detail.\n",
        )

    def test_sentence_split_can_be_limited_to_long_lines(self):
        text = "We reduce it. The oracle runs.\n"
        self.assertEqual(fmt(text, sentence_split="fit"), text)


class AbbreviationTests(unittest.TestCase):
    def test_eg_is_not_a_sentence_boundary(self):
        text = "We use a reducer, e.g. Perses, on the input.\n"
        self.assertEqual(fmt(text), text)

    def test_ie_is_not_a_sentence_boundary(self):
        text = "The result is minimal, i.e. No token can be removed.\n"
        self.assertEqual(fmt(text), text)

    def test_et_al_is_not_a_sentence_boundary(self):
        text = "This follows Sun et al. Perses is the result.\n"
        self.assertEqual(fmt(text), text)

    def test_fig_is_not_a_sentence_boundary(self):
        text = "See Fig. Two for the layout.\n"
        self.assertEqual(fmt(text), text)

    def test_initials_are_not_sentence_boundaries(self):
        text = "The author is J. Doe and the year is 2018.\n"
        self.assertEqual(fmt(text), text)

    def test_decimal_numbers_are_not_sentence_boundaries(self):
        text = "The speedup is 3.5 on average across the suite.\n"
        self.assertEqual(fmt(text), text)


class FalsePositiveTests(unittest.TestCase):
    """Regressions found by running the formatter over this repository."""

    def test_enumeration_label_is_not_a_sentence_boundary(self):
        text = "\\requirement{1. Importance of XXXX}{\n"
        self.assertEqual(fmt(text), text)

    def test_numbered_item_in_prose_is_not_split(self):
        text = "\\requirement{2. Comparison with \\textsc{Baseline}}{\n"
        self.assertEqual(fmt(text), text)

    def test_verb_delimiter_is_not_a_sentence_boundary(self):
        text = "NOTE: use \\verb!\\hla{}!, \\verb!\\hlb{}! $,\\dots$, \\verb!\\hle{}!\n"
        self.assertEqual(fmt(text), text)

    def test_sentence_ending_in_a_group_still_splits(self):
        text = "He said \\emph{no}. Then we left.\n"
        self.assertEqual(fmt(text), "He said \\emph{no}.\nThen we left.\n")

    def test_newcommand_definition_is_never_broken(self):
        text = (
            "\\newcommand{\\requirement}[2]{\\vspace*{5pt}\\noindent"
            "\\textbf{#1}\\\\{\\footnotesize See #2}}\n"
        )
        self.assertEqual(fmt(text), text)

    def test_usepackage_line_is_never_broken(self):
        text = "\\usepackage[a very long option list goes here indeed]{somepackage}\n"
        self.assertEqual(fmt(text), text)

    def test_definition_containing_periods_is_not_sentence_split(self):
        text = "\\newcommand{\\note}{Short. Also short.}\n"
        self.assertEqual(fmt(text), text)

    def test_comment_spacing_after_percent_is_preserved(self):
        text = (
            "%replace XXX with the submission number you are given from the "
            "ASPLOS submission site.\n"
        )
        result = fmt(text)
        for line in result.splitlines():
            self.assertTrue(line.startswith("%"), line)
            self.assertFalse(line.startswith("% "), line)

    def test_tikz_path_is_never_broken(self):
        text = (
            "    \\draw[fill=#1!30, rounded corners=0pt, inner sep=0pt] "
            "([yshift=2pt,xshift=-1pt]X.north west) -- cycle;%\n"
        )
        self.assertEqual(fmt(text), text)

    def test_begin_line_with_long_options_is_not_broken(self):
        text = (
            "\\begin{lstlisting}[language=C, basicstyle=\\ttfamily\\small, "
            "numbers=left, numbersep=4pt, frame=single]\n"
        )
        self.assertEqual(fmt(text), text)

    def test_section_title_is_not_broken(self):
        text = (
            "\\section{A Rather Long Section Title That Runs Past The Eighty "
            "Column Limit Easily}\n"
        )
        self.assertEqual(fmt(text), text)

    def test_section_title_with_two_sentences_is_not_split(self):
        text = "\\section{First. Second.}\n"
        self.assertEqual(fmt(text), text)

    def test_editor_directive_comment_is_not_wrapped(self):
        text = "% !TEX root = ../main.tex and some more text to push past eighty columns here\n"
        self.assertEqual(fmt(text), text)

    def test_prose_bearing_command_still_wraps(self):
        text = (
            "\\hl{NOTE: the meta-review has already listed the changes that "
            "are expected to be done in the revision.}\n"
        )
        result = fmt(text)
        self.assertGreater(len(result.splitlines()), 1)

    def test_item_prose_still_wraps(self):
        text = (
            "  \\item The second item is considerably longer and will need to "
            "be broken somewhere along its length.\n"
        )
        result = fmt(text)
        self.assertGreater(len(result.splitlines()), 1)

    def test_command_names_match_whole_words_not_prefixes(self):
        # '\\defer' must not be skipped just because '\\def' is in the list.
        self.assertTrue(pf.is_directive_line("\\def\\x{1}"))
        self.assertFalse(pf.is_directive_line("\\defer the decision"))
        self.assertFalse(pf.is_directive_line("\\sectionmark{x}"))
        self.assertTrue(pf.is_directive_line("\\section{x}"))



class HardClauseSplitTests(unittest.TestCase):
    """Every clause of an over-long sentence gets its own line."""

    def test_leading_subordinate_clause_is_separated(self):
        text = (
            "Because the \\ladyck grammar parses a stream of predefined tokens "
            "rather than raw characters, \\proj must first convert the source "
            "program into this restricted vocabulary (\\cref{tab:token}).\n"
        )
        lines = fmt(text).splitlines()
        # The main clause must open a line, not sit in the middle of one.
        self.assertTrue(
            any(l.startswith("\\proj must first convert") for l in lines), lines
        )

    def test_clause_opening_with_a_command_is_detected(self):
        # '\\proj' yields no leading word; that must not defeat the opener test.
        self.assertTrue(
            pf.is_hard_clause_boundary(
                "Because the grammar parses tokens,", "\\proj must convert it"
            )
        )

    def test_coordinated_clause_is_separated(self):
        text = (
            "The reducer removes as many tokens as it can from the candidate, "
            "and it then invokes the property test once more.\n"
        )
        lines = fmt(text).splitlines()
        self.assertTrue(any(l.startswith("and it then invokes") for l in lines), lines)

    def test_participial_clause_is_separated(self):
        text = (
            "For instance, a universal tokenizer might misinterpret the Python "
            "division operator as a comment, corrupting the nesting structure.\n"
        )
        lines = fmt(text).splitlines()
        self.assertTrue(any(l.startswith("corrupting the") for l in lines), lines)

    def test_coordinate_adjectives_are_not_a_clause_boundary(self):
        # 'A universal, language-agnostic scanner' must stay together.
        self.assertFalse(
            pf.is_hard_clause_boundary("A universal,", "language-agnostic scanner")
        )
        text = (
            "A universal, language-agnostic scanner cannot safely perform this "
            "extraction because the rules are inherently language-specific.\n"
        )
        lines = fmt(text).splitlines()
        self.assertTrue(lines[0].startswith("A universal, language-agnostic"), lines)

    def test_comma_inside_parentheses_is_not_a_clause_boundary(self):
        text = (
            "The scanner cannot separate structural delimiters from inert text "
            "(e.g., within comments or strings) in a language-agnostic way.\n"
        )
        for line in fmt(text).splitlines():
            self.assertFalse(line.startswith("within comments"), line)

    def test_short_sentence_keeps_its_clauses_together(self):
        text = "We ran it, and it worked.\n"
        self.assertEqual(fmt(text), text)

    def test_clause_split_can_be_reduced_to_fit_only(self):
        text = (
            "For instance, a universal tokenizer might misinterpret the Python "
            "division operator as a comment, corrupting the nesting structure.\n"
        )
        lines = fmt(text, clause_split="fit").splitlines()
        self.assertNotEqual(lines[0], "For instance,")


class TypesettingSafetyTests(unittest.TestCase):
    def test_em_dash_without_spaces_is_never_broken(self):
        text = (
            "The reduction process---which is expensive---dominates the total "
            "running time of the whole toolchain here.\n"
        )
        result = fmt(text)
        self.assertIn("process---which", result)
        self.assertIn("expensive---dominates", result)

    def test_spaced_em_dash_is_never_broken(self):
        text = (
            "The reduction process --- which is really quite expensive --- "
            "dominates the total running time of the toolchain.\n"
        )
        result = fmt(text)
        for line in result.splitlines():
            self.assertFalse(line.endswith("---"), line)
            self.assertFalse(line.lstrip().startswith("---"), line)

    def test_escaped_space_control_symbol_is_not_broken(self):
        text = (
            "The measurements are reported in Fig.\\ 4 and they show that the "
            "approach scales to large inputs.\n"
        )
        result = fmt(text)
        for line in result.splitlines():
            self.assertFalse(line.endswith("\\"), line)
        self.assertIn("Fig.\\ 4", result)

    def test_verb_argument_is_not_broken(self):
        text = (
            "The option \\verb|--enable-token-slicing here| turns the feature "
            "on for every run of the reducer.\n"
        )
        result = fmt(text)
        self.assertIn("\\verb|--enable-token-slicing here|", result)

    def test_continuation_never_starts_with_optional_bracket(self):
        text = (
            "This row ends the tabular block right here \\\\ [2ex] and more "
            "text follows on the very same source line.\n"
        )
        result = fmt(text)
        for line in result.splitlines():
            self.assertFalse(line.lstrip().startswith("["), line)

    def test_only_existing_whitespace_becomes_a_break(self):
        """The joined output must normalize to exactly the input."""
        text = (
            "The tool applies delta debugging to the token sequence and it "
            "reports the smallest program that still triggers the bug.\n"
        )
        result = fmt(text)
        joined = " ".join(line.strip() for line in result.strip().splitlines())
        self.assertEqual(joined, text.strip())

    def test_url_is_left_intact(self):
        text = "See \\url{https://example.com/a very long path} for details.\n"
        self.assertEqual(fmt(text), text)


class CommentTests(unittest.TestCase):
    def test_trailing_comment_stays_attached_to_the_last_piece(self):
        text = (
            "The reducer removes tokens from the candidate program repeatedly "
            "until fixpoint. % keep this comment here\n"
        )
        result = fmt(text)
        self.assertTrue(result.rstrip("\n").endswith("% keep this comment here"))
        self.assertEqual(result.count("%"), 1)

    def test_percent_line_continuation_semantics_are_preserved(self):
        text = "alpha beta gamma%\ndelta epsilon\n"
        self.assertEqual(fmt(text), text)

    def test_escaped_percent_is_not_a_comment(self):
        text = "The reduction removes 90\\% of the tokens in the input file.\n"
        self.assertEqual(fmt(text), text)

    def test_short_comment_is_untouched(self):
        text = "% a short note\n"
        self.assertEqual(fmt(text), text)

    def test_long_comment_is_wrapped_with_its_marker(self):
        text = (
            "% this is a very long explanatory comment that goes well past the "
            "eighty column limit and must be wrapped\n"
        )
        result = fmt(text)
        for line in result.splitlines():
            self.assertLessEqual(len(line), 80, line)
            self.assertTrue(line.startswith("% "), line)

    def test_comment_wrapping_can_be_disabled(self):
        text = (
            "% this is a very long explanatory comment that goes well past the "
            "eighty column limit and must be wrapped\n"
        )
        self.assertEqual(fmt(text, wrap_comments=False), text)


class VerbatimTests(unittest.TestCase):
    def test_verbatim_body_is_untouched(self):
        text = (
            "\\begin{verbatim}\n"
            "int main() { return 0; }  // this line is really quite long "
            "indeed and exceeds eighty columns easily\n"
            "\\end{verbatim}\n"
        )
        self.assertEqual(fmt(text), text)

    def test_lstlisting_body_is_untouched(self):
        text = (
            "\\begin{lstlisting}[language=C]\n"
            "for (int i = 0; i < n; ++i) { total += values[i]; } "
            "/* a long trailing comment that runs past eighty */\n"
            "\\end{lstlisting}\n"
        )
        self.assertEqual(fmt(text), text)

    def test_formatting_resumes_after_the_environment(self):
        text = (
            "\\begin{verbatim}\n"
            "raw. text.\n"
            "\\end{verbatim}\n"
            "Real prose. Another sentence.\n"
        )
        result = fmt(text)
        self.assertIn("raw. text.\n", result)
        self.assertIn("Real prose.\nAnother sentence.\n", result)


class PragmaTests(unittest.TestCase):
    def test_off_and_on_pragmas_bracket_a_region(self):
        text = (
            "% pluverse-format: off\n"
            "Keep this. Exactly as is.\n"
            "% pluverse-format: on\n"
            "Split this. Into two lines.\n"
        )
        result = fmt(text)
        self.assertIn("Keep this. Exactly as is.\n", result)
        self.assertIn("Split this.\nInto two lines.\n", result)


class ClauseTests(unittest.TestCase):
    def test_clause_split_only_applies_to_long_lines(self):
        text = "We ran it, and it worked.\n"
        self.assertEqual(fmt(text), text)

    def test_long_sentence_breaks_at_a_clause_boundary(self):
        text = (
            "The reducer removes as many tokens as it can from the candidate, "
            "and it then invokes the property test once more.\n"
        )
        result = fmt(text)
        lines = result.splitlines()
        self.assertEqual(len(lines), 2)
        self.assertTrue(lines[0].endswith(","), lines[0])

    def test_clause_split_always_is_more_aggressive(self):
        text = (
            "The reducer removes as many tokens as it can from the candidate, "
            "and it then invokes the property test once more.\n"
        )
        aggressive = fmt(text, clause_split="always")
        self.assertGreaterEqual(len(aggressive.splitlines()), 2)
        for line in aggressive.splitlines():
            self.assertLessEqual(len(line), 80, line)


class UnbreakableTests(unittest.TestCase):
    def test_single_long_token_is_left_alone(self):
        text = "\\includegraphics[width=\\textwidth]{" + "a" * 90 + "}\n"
        self.assertEqual(fmt(text), text)

    def test_unbreakable_line_is_reported(self):
        text = "\\includegraphics[width=\\textwidth]{" + "a" * 90 + "}\n"
        _, _, unbreakable = pf.format_text(text, pf.Options())
        self.assertEqual(len(unbreakable), 1)
        self.assertEqual(unbreakable[0][0], 1)


class IdempotenceTests(unittest.TestCase):
    SAMPLE = (
        "\\section{Evaluation}\n"
        "\n"
        "We evaluate Perses on twenty subjects. The reducer removes as many "
        "tokens as it can from the candidate, and it then invokes the property "
        "test once more. The process---which is expensive---dominates.\n"
        "\n"
        "% a long explanatory comment that runs past the eighty column limit "
        "and therefore needs wrapping\n"
        "\\begin{verbatim}\n"
        "untouched. content. here.\n"
        "\\end{verbatim}\n"
        "See \\url{https://example.com/x} and Fig.\\ 3 for the numbers, e.g. "
        "the median reduction ratio.\n"
    )

    def test_formatting_is_idempotent(self):
        once = fmt(self.SAMPLE)
        twice = fmt(once)
        self.assertEqual(once, twice)

    def test_all_lines_fit_after_formatting(self):
        once = fmt(self.SAMPLE)
        for line in once.splitlines():
            self.assertLessEqual(len(line), 80, line)

    def test_normalized_text_is_unchanged_outside_comments(self):
        once = fmt("We reduce it repeatedly. " * 6 + "\n")
        joined = " ".join(line.strip() for line in once.strip().splitlines())
        self.assertEqual(joined, ("We reduce it repeatedly. " * 6).strip())


def code_token_stream(text: str) -> str:
    """The whitespace-normalized source with all comments removed.

    Two documents with the same stream are typeset identically, because a
    newline and a space are the same token to LaTeX.
    """
    pieces = []
    for line in text.split("\n"):
        comment_start, _, _ = pf.scan_line(line)
        pieces.append(line if comment_start is None else line[:comment_start])
    return re.sub(r"\s+", " ", " ".join(pieces)).strip()


class RepositoryCorpusTests(unittest.TestCase):
    """Run the formatter over every .tex file that ships with this repository."""

    @classmethod
    def setUpClass(cls):
        cls.corpus = sorted(REPO_ROOT.rglob("*.tex"))
        if not cls.corpus:
            raise unittest.SkipTest("no .tex files found in the repository")

    def test_output_is_typeset_equivalent(self):
        for path in self.corpus:
            with self.subTest(path=path.relative_to(REPO_ROOT)):
                source = path.read_text(encoding="utf-8")
                self.assertEqual(
                    code_token_stream(source),
                    code_token_stream(fmt(source)),
                    "formatting changed the token stream",
                )

    def test_formatting_is_idempotent(self):
        for path in self.corpus:
            with self.subTest(path=path.relative_to(REPO_ROOT)):
                source = path.read_text(encoding="utf-8")
                once = fmt(source)
                self.assertEqual(once, fmt(once))

    def test_no_line_grows_longer(self):
        for path in self.corpus:
            with self.subTest(path=path.relative_to(REPO_ROOT)):
                source = path.read_text(encoding="utf-8")
                before = max((len(l) for l in source.split("\n")), default=0)
                after = max((len(l) for l in fmt(source).split("\n")), default=0)
                self.assertLessEqual(after, before)



HAVE_PDFLATEX = shutil.which("pdflatex") is not None
HAVE_PDFTOPPM = shutil.which("pdftoppm") is not None

DOCUMENT = (
    "\\documentclass{article}\n"
    "\\begin{document}\n"
    "\\section{Intro}\\label{sec:intro}\n"
    "As shown in Section~\\ref{sec:results}, the approach works well in practice "
    "here and elsewhere.\n"
    "alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu nu xi "
    "omicron% note\n"
    "continuation.\n"
    "\\section{Results}\\label{sec:results}\n"
    "The reduction process---which is expensive---dominates the running time "
    "of the whole toolchain by a wide margin.\n"
    "\\end{document}\n"
)


@unittest.skipUnless(HAVE_PDFLATEX and HAVE_PDFTOPPM, "needs pdflatex and pdftoppm")
class BuildVerificationTests(unittest.TestCase):
    """Formatting must not change a single pixel of the rendered document."""

    def setUp(self):
        import os

        self.tmp = Path(tempfile.mkdtemp())
        self.cwd = Path.cwd()
        os.chdir(self.tmp)
        (self.tmp / "main.tex").write_text(DOCUMENT, encoding="utf-8")

    def tearDown(self):
        import os

        os.chdir(self.cwd)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def verification(self):
        return pf.BuildVerification(main=self.tmp / "main.tex", dpi=150)

    def test_rendered_pdf_is_unchanged(self):
        code = pf.main(["main.tex", "-q", "--verify", "main.tex"])
        self.assertEqual(code, 0)
        self.assertNotEqual(
            (self.tmp / "main.tex").read_text(), DOCUMENT, "nothing was reformatted"
        )

    def test_pdf_path_follows_the_main_file(self):
        self.assertEqual(self.verification().pdf, self.tmp / "main.pdf")
        self.assertEqual(self.verification().directory, self.tmp)

    def test_cross_references_converge_before_the_reference_is_taken(self):
        """A one-pass build renders '??' and would look like a false change."""
        scratch = self.tmp / "scratch"
        scratch.mkdir()
        reference = pf.capture_reference(self.verification(), scratch)
        # Building again from the converged state must reproduce it exactly.
        pf.build_document(self.verification())
        identical, _ = pf.compare_pdfs(
            reference.copy, self.tmp / "main.pdf", 150, scratch
        )
        self.assertTrue(identical, "repeated builds must be deterministic")

    def test_a_real_layout_change_is_detected(self):
        scratch = self.tmp / "scratch"
        scratch.mkdir()
        reference = pf.capture_reference(self.verification(), scratch)

        # Detaching the trailing '%' inserts a space into the output.
        (self.tmp / "main.tex").write_text(
            DOCUMENT.replace("omicron% note\n", "omicron\n% note\n"), encoding="utf-8"
        )
        pf.build_document(self.verification())
        identical, detail = pf.compare_pdfs(
            reference.copy, self.tmp / "main.pdf", 150, scratch
        )
        self.assertFalse(identical, "a changed document must be detected")
        self.assertIn("render differently", detail)

    def test_a_pdf_that_is_not_regenerated_fails_verification(self):
        """Comparing a stale PDF against itself must not report success."""
        scratch = self.tmp / "scratch"
        scratch.mkdir()
        reference = pf.capture_reference(self.verification(), scratch)
        real_build = pf.build_document
        try:
            pf.build_document = lambda verification: "no-op"
            code = pf.verify_build_output(
                self.verification(), reference, scratch, quiet=True
            )
        finally:
            pf.build_document = real_build
        self.assertEqual(code, 3, "a vacuous verification must not pass")

    def test_files_are_restored_when_the_pdf_changes(self):
        """End to end: a formatter bug is caught and the files are put back."""
        original = (self.tmp / "main.tex").read_text()
        real_format = pf.format_text

        def sabotage(text, options):
            # Detaching the trailing '%' inserts a space into the output.
            return text.replace("omicron% note\n", "omicron\n% note\n"), 1, []

        try:
            pf.format_text = sabotage
            code = pf.main(["main.tex", "-q", "--verify", "main.tex"])
        finally:
            pf.format_text = real_format

        self.assertEqual(code, 3)
        self.assertEqual(
            (self.tmp / "main.tex").read_text(), original, "files were not restored"
        )

    def test_text_comparison_is_used_when_pdftoppm_is_absent(self):
        scratch = self.tmp / "scratch"
        scratch.mkdir()
        pf.build_document(self.verification())
        pdf = self.tmp / "main.pdf"
        real_which = shutil.which
        try:
            shutil.which = lambda n, *a, **k: (
                None if n == "pdftoppm" else real_which(n, *a, **k)
            )
            identical, detail = pf.compare_pdfs(pdf, pdf, 150, scratch)
        finally:
            shutil.which = real_which
        self.assertTrue(identical)
        self.assertIn("layout NOT checked", detail)


    def test_files_are_untouched_when_the_build_fails(self):
        (self.tmp / "broken.tex").write_text(
            "\\documentclass{article}\\begin{document}\\undefinedcommand\n", encoding="utf-8"
        )
        code = pf.main(["main.tex", "-q", "--verify", "broken.tex"])
        self.assertEqual(code, 2)
        self.assertEqual((self.tmp / "main.tex").read_text(), DOCUMENT)

    def test_missing_main_file_is_rejected(self):
        self.assertEqual(pf.main(["main.tex", "-q", "--verify", "absent.tex"]), 2)

    def test_non_tex_main_file_is_rejected(self):
        (self.tmp / "notes.txt").write_text("hello\n", encoding="utf-8")
        self.assertEqual(pf.main(["main.tex", "-q", "--verify", "notes.txt"]), 2)

    def test_verify_rejects_dry_run_modes(self):
        with self.assertRaises(SystemExit):
            pf.main(["main.tex", "-q", "--check", "--verify", "main.tex"])

    def test_verify_requires_backups(self):
        with self.assertRaises(SystemExit):
            pf.main(["main.tex", "-q", "--no-backup", "--verify", "main.tex"])



HAVE_BIBTEX = shutil.which("bibtex") is not None

BIB = (
    "@inproceedings{perses2018,\n"
    "  title={Perses: Syntax-guided program reduction},\n"
    "  author={Sun, Chengnian and Su, Zhendong},\n"
    "  booktitle={ICSE}, year={2018}\n"
    "}\n"
)

CITING_DOCUMENT = (
    "\\documentclass{article}\n"
    "\\begin{document}\n"
    "Syntax-guided reduction was introduced by Perses~\\cite{perses2018} and it "
    "remains the standard baseline for this task today.\n"
    "\\bibliographystyle{plain}\n"
    "\\bibliography{refs}\n"
    "\\end{document}\n"
)


@unittest.skipUnless(
    HAVE_PDFLATEX and HAVE_PDFTOPPM and HAVE_BIBTEX, "needs pdflatex, pdftoppm, bibtex"
)
class BibliographyTests(unittest.TestCase):
    """A cited document must render its bibliography on both build paths."""

    def setUp(self):
        import os

        self.tmp = Path(tempfile.mkdtemp())
        self.cwd = Path.cwd()
        os.chdir(self.tmp)
        (self.tmp / "refs.bib").write_text(BIB, encoding="utf-8")
        (self.tmp / "main.tex").write_text(CITING_DOCUMENT, encoding="utf-8")
        self.verification = pf.BuildVerification(main=self.tmp / "main.tex", dpi=150)

    def tearDown(self):
        import os

        os.chdir(self.cwd)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def rendered_text(self) -> str:
        return pf.extract_pdf_text(self.tmp / "main.pdf", self.tmp / "out.txt")

    def test_citations_resolve_on_the_default_path(self):
        pf.build_document(self.verification)
        text = self.rendered_text()
        self.assertNotIn("[?]", text, "citation did not resolve")
        self.assertIn("References", text)

    def test_citations_resolve_without_latexmk(self):
        real_which = shutil.which
        try:
            shutil.which = lambda n, *a, **k: (
                None if n == "latexmk" else real_which(n, *a, **k)
            )
            steps = pf.build_document(self.verification)
        finally:
            shutil.which = real_which
        self.assertIn("bibtex", steps)
        text = self.rendered_text()
        self.assertNotIn("[?]", text, "citation did not resolve without latexmk")
        self.assertIn("References", text)

    def test_a_document_without_citations_skips_bibtex(self):
        (self.tmp / "plain.tex").write_text(
            "\\documentclass{article}\n\\begin{document}\nNo citations here.\n"
            "\\end{document}\n",
            encoding="utf-8",
        )
        verification = pf.BuildVerification(main=self.tmp / "plain.tex", dpi=150)
        real_which = shutil.which
        try:
            shutil.which = lambda n, *a, **k: (
                None if n == "latexmk" else real_which(n, *a, **k)
            )
            steps = pf.build_document(verification)
        finally:
            shutil.which = real_which
        self.assertNotIn("bibtex", steps)

    def test_formatting_a_cited_document_is_verified(self):
        code = pf.main(["main.tex", "-q", "--verify", "main.tex"])
        self.assertEqual(code, 0)
        self.assertNotIn("[?]", self.rendered_text())


class CliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.cwd = Path.cwd()
        import os

        os.chdir(self.tmp)

    def tearDown(self):
        import os

        os.chdir(self.cwd)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def write(self, name: str, text: str) -> Path:
        path = self.tmp / name
        path.write_text(text, encoding="utf-8")
        return path

    def test_in_place_rewrite_creates_a_backup(self):
        path = self.write("a.tex", "One sentence. Two sentences.\n")
        code = pf.main([str(path), "-q"])
        self.assertEqual(code, 0)
        self.assertEqual(path.read_text(), "One sentence.\nTwo sentences.\n")

        sessions = pf.list_backups(Path(pf.BACKUP_ROOT_NAME))
        self.assertEqual(len(sessions), 1)
        manifest = sessions[0] / pf.MANIFEST_NAME
        self.assertTrue(manifest.is_file())

    def test_restore_recovers_the_original(self):
        original = "One sentence. Two sentences.\n"
        path = self.write("a.tex", original)
        pf.main([str(path), "-q"])
        self.assertNotEqual(path.read_text(), original)

        pf.restore_backup(Path(pf.BACKUP_ROOT_NAME), None)
        self.assertEqual(path.read_text(), original)

    def test_no_backup_flag_skips_backups(self):
        path = self.write("a.tex", "One sentence. Two sentences.\n")
        pf.main([str(path), "-q", "--no-backup"])
        self.assertFalse(Path(pf.BACKUP_ROOT_NAME).exists())

    def test_check_mode_does_not_write(self):
        original = "One sentence. Two sentences.\n"
        path = self.write("a.tex", original)
        code = pf.main([str(path), "-q", "--check"])
        self.assertEqual(code, 1)
        self.assertEqual(path.read_text(), original)

    def test_check_mode_is_clean_on_formatted_input(self):
        path = self.write("a.tex", "One sentence.\nTwo sentences.\n")
        self.assertEqual(pf.main([str(path), "-q", "--check"]), 0)

    def test_non_tex_files_are_skipped(self):
        path = self.write("a.txt", "One sentence. Two sentences.\n")
        code = pf.main([str(path), "-q"])
        self.assertEqual(code, 2)
        self.assertEqual(path.read_text(), "One sentence. Two sentences.\n")

    def test_directory_is_searched_recursively(self):
        (self.tmp / "sub").mkdir()
        target = self.tmp / "sub" / "b.tex"
        target.write_text("One sentence. Two sentences.\n", encoding="utf-8")
        pf.main([str(self.tmp / "sub"), "-q"])
        self.assertEqual(target.read_text(), "One sentence.\nTwo sentences.\n")

    def test_unchanged_file_is_not_backed_up(self):
        self.write("a.tex", "One sentence.\n")
        pf.main(["a.tex", "-q"])
        self.assertFalse(Path(pf.BACKUP_ROOT_NAME).exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
