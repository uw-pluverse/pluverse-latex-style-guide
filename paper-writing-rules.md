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

#### 1.2.1 Which Section Is the Golden Standard

The contract says that all sections must agree; it does not say which section moves when they disagree. During revision, the section that was most recently rewritten is often the one with the intended terminology, and the Introduction may be the stale one.

* **Confirm before aligning.** When an agent finds a terminology conflict between sections, it must ask the user which section (or file, or paragraph) is ready and should serve as the golden standard, unless the user has already said so in the task. Do not guess, and do not silently pick a side.
* **User designation overrides the default.** If the user names a golden standard (e.g., "the Approach section is final; align everything else to it"), the agent propagates that section's terminology to all other sections, figures, and tables, and must not change the golden section's terminology itself.
* **Default when the user cannot be asked.** Only if confirmation is impossible (e.g., a non-interactive run) does the Introduction's contribution list and overview serve as the source of truth. In that case the agent must report every conflict it resolved and which side it chose.
* **The override changes the direction, not the contract.** Every other section must still end up matching the golden one verbatim, per Rule 1.1.

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
   Locate the Introduction (e.g., search for `\section{Introduction}` or file containing the intro). Carefully read its contribution list and stage-by-stage overview. This is the paper's default vocabulary source of truth, unless the user has designated another section as the golden standard (Rule 1.2.1).
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
- [ ] **Golden Standard Confirmed:** Where sections disagreed, asked the user which section is the golden standard (or reported the conflicts and the default choice) before aligning the others.

---

## Rule 2: Minimize Em-Dashes to Avoid LLM Hallmarks

### 2.1 Core Principle: Avoid "---" as Parenthetical Crutches
Over-reliance on em-dashes (`---`), particularly paired em-dashes for parenthetical insertions (e.g., `---such as X and Y---`), is one of the most prominent stylistic hallmarks of LLM-generated prose:
* **Why this matters:** Academic peer reviewers actively look for signs of uncurated LLM generation. Frequent em-dashes disrupt sentence rhythm, loosen deductive structure, and create an impression of machine-generated boilerplate.
* **Rule:** Strive to use `---` as little as possible. In formal computer science and mathematical writing, prefer standard, disciplined academic punctuation: parentheses for illustrative lists, commas for appositives, colons for elaborations, or two separate declarative sentences.

---

### 2.2 Standard Replacements for Common Em-Dash Patterns

1. **Illustrative Examples (`---such as ...---`):**
   * **Anti-pattern:**
     `leveraging solver diagnostics---such as quantifier profiles and conflict statistics---to isolate conflicting constraints`
   * **Preferred (Parentheses):**
     `leveraging solver diagnostics (such as quantifier profiles and conflict statistics) to isolate conflicting constraints`
   * Use parentheses `(...)` for examples, parameter settings, tool configurations, and short clarifications that should not derail sentence flow.

2. **Appositives and Descriptive Clauses (`---which ...---`):**
   * **Anti-pattern:**
     `Lean---which has a minimal trusted kernel---offers deductive verification`
   * **Preferred (Commas):**
     `Lean, which has a minimal trusted kernel, offers deductive verification`
   * When an aside integrates smoothly into the cadence of the sentence, standard commas `, ...,` provide a much more natural, scholarly flow.

3. **Elaboration and Consequence (`...---establishing that ...`):**
   * **Anti-pattern:**
     `We evaluate the three objectives---establishing which bottlenecks require Lean.`
   * **Preferred (Subordination or Colon):**
     `We evaluate the three objectives to establish which bottlenecks require Lean.`
     *(or: `...three objectives: the evaluation establishes which bottlenecks...`)*
   * Connective clauses should use explicit subordinating conjunctions (`to establish`, `thereby establishing`) or a colon rather than a trailing em-dash.

4. **Compound Thoughts:**
   * **Anti-pattern:**
     `SMT solvers discharge most queries quickly---however, hard instances time out.`
   * **Preferred (Separate Sentences or Semicolon):**
     `SMT solvers discharge most queries quickly. However, hard instances time out.`
   * Split compound, multi-clause arguments into distinct, crisp declarative sentences.

---

### 2.3 Agent Em-Dash Audit Protocol

Whenever an agent writes, revises, or reviews any section of a paper, it must audit all em-dash occurrences:

1. **Search for em-dashes across LaTeX source files:**
   ```bash
   grep -rn "\-\-\-" --include="*.tex" .
   ```
2. **Review each match:**
   * Does it use `---such as ...---` or `---which ...---`? Replace with parentheses `(...)` or commas `, ...,`.
   * Does it join two independent thoughts? Split into two sentences or use appropriate subordinating conjunctions.
   * Only retain an em-dash if it provides genuine rhetorical emphasis that cannot be achieved with academic punctuation, and ensure its use is exceptionally rare across the entire manuscript.

---

### 2.4 Agent Punctuation Checklist

- [ ] **Em-Dash Audit:** Grepped for `\-\-\-` across all `.tex` files to ensure em-dashes are minimized and never used as parenthetical crutches.
- [ ] **No `---such as ...---`:** Replaced all parenthetical illustrative insertions with standard parentheses `(...)`.
- [ ] **No Disjointed Joins:** Verified that clauses connected by em-dashes are restructured with appropriate academic connectives, colons, or sentence breaks.
