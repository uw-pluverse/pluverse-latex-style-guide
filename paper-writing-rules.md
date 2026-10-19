# Paper Writing Rules for Agents

This document defines standard rules and guidelines for AI agents and human co-authors drafting, editing, and revising academic research papers. When an agent is instructed to write or refine any section of a paper, it must adhere to the rules established here.

---

## Rule 1: Maintain Strict Terminology Consistency

### 1.1 Core Principle: No "Thesaurus Variation" for Technical Terms
In creative or general prose, writers often vary vocabulary to avoid repetition. In computer science and scientific research papers, **synonym variation for technical terms is an anti-pattern**:
* Each distinct concept, artifact, pipeline stage, metric, or problem formulation must have **exactly one canonical term** used consistently throughout the paper.
* **Why this matters:** Peer reviewers assume that different words denote different technical concepts. If a system's intermediate output is called an *execution context* in Section 4, but a *dependency context* in the Abstract, reviewers will assume the system produces two separate types of contexts or will doubt the author's technical precision.
* **Rule:** Pick one canonical noun phrase for each technical entity and stick to it verbatim across all sections, captions, figures, and tables. Ordinary grammatical inflection (plural forms, sentence-initial capitalization, an added article) is fine; substituting a different word or word order is not.

---

### 1.2 Cross-Section Synchronization Contract
Every section of the paper must maintain a strict 1-to-1 vocabulary contract with every other section:

$$\text{Abstract} \iff \text{Intro Contributions} \iff \text{Section Headings / Figures} \iff \text{Evaluation Subsections}$$

1. **Abstract $\leftrightarrow$ Introduction:**
   * Every mechanism, stage, and artifact summarized in the Abstract must use the identical terminology defined in the Introduction's overview paragraphs (e.g., `\paragraph{\circled{1} ...}`) and the contribution list.
2. **Pipeline Overview $\leftrightarrow$ Section Headings:**
   * If Section 4.2 is titled `\subsection{Context Recovery}`, the pipeline overview must call that stage *Context Recovery* (never *Dependency Slicing* or *Context Extraction*).
3. **Text $\leftrightarrow$ Figures & Tables:**
   * Labels inside architecture diagrams, flowchart boxes, and table column headers must match the in-text terminology verbatim.
4. **Problem $\leftrightarrow$ Solution Symmetry:**
   * When contrasting the proposed approach against prior work, the solution's claims must symmetrically answer the exact limitations raised in the problem statement.
   * *Example:* If Paragraph 1 states that prior work suffers from *"reliance on manual harnesses"* and *"heavy runtime instrumentation"*, Paragraph 2 must explicitly resolve them with matching terms (e.g., *"eliminating manual driver engineering"* and *"without requiring runtime instrumentation"*).

---

### 1.3 Single Source of Truth via LaTeX Macros
* Before introducing or writing names of systems, vulnerabilities, benchmarks, or recurring concepts, check the repository's macro/definition files (e.g., `constants.tex`, `macros.tex`, `defs.tex`, `commands.tex`, or the preamble in `main.tex`).
* **Always** use defined LaTeX macros (e.g., `\proj` for the system name, `\PerformanceGain` for a recurring number) instead of hardcoded strings. This guarantees consistent capitalization, hyphenation, font styling, and proper trailing spacing (`\xspace`).
* If a recurring name, number, or concept has no macro yet, define one in the project's macro file (see "Use macros for constants" in `README.md`) and use it everywhere, rather than hardcoding the string.

---

### 1.4 Mandatory Protocol for Agents Before Writing or Editing

Do not assume a fixed folder layout (such as `chapters/` or `sections/`)—different paper repositories structure their source files differently (e.g., flat in the root, inside `sections/`, `src/`, or modular directories). 

Whenever an agent is asked to write, revise, or polish text in a paper, it must follow this 4-step audit protocol across the repository's `.tex` files:

1. **Step 1: Grep Across All TeX Files (Never Guess Terms)**
   Search the entire repository to discover established terms. Do not invent a plausible-sounding term from context or general knowledge:
   ```bash
   grep -rn -i "<term_or_concept>" --include="*.tex" --exclude-dir=pluverse-latex-style-guide .
   ```
2. **Step 2: Audit Introduction & Contributions**
   Locate the Introduction (e.g., search for `\section{Introduction}` or file containing the intro). Carefully read its contribution list and stage-by-stage overview. This is the paper's definitive vocabulary source of truth.
3. **Step 3: Check Section Headings and Figure Labels**
   Locate the methodology/system design sections and inspect their `\section` / `\subsection` titles and accompanying diagram labels to ensure naming alignment.
4. **Step 4: Verify Macro Definitions**
   Identify where macros are stored (e.g., `constants.tex`, `macros.tex`, or `main.tex`) and verify if a macro already exists for the entity or concept being discussed. If none exists and the term recurs, add one there (Rule 1.3).

---

### 1.5 Agent Terminology Checklist

Before committing or reporting completion of any writing task, verify the following:

- [ ] **Grep Verified:** Searched all LaTeX source files (`*.tex`) to verify that all technical noun phrases conform to existing usage.
- [ ] **No Synonym Drifts:** Used the identical noun phrase for each artifact and stage across the Abstract, Introduction, System/Method sections, and Evaluation.
- [ ] **Heading Alignment:** Verified that pipeline stage names match the actual `\section` / `\subsection` titles.
- [ ] **Figure Alignment:** Verified that component names match box labels in architecture diagrams.
- [ ] **Macro Usage:** Used LaTeX macros from definition files (`constants.tex`, `macros.tex`, preamble, etc.) for tool names, benchmarks, and core concepts.
- [ ] **Symmetric Addressing:** Verified that solutions in the contribution directly address the limitation terms in the problem statement.
