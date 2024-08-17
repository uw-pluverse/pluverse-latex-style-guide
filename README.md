(in progress of restructuring the guide)

# How to install and use this project


### Installing this project

The recommended way is to add this project as a submodule of your git project. In shell,
enter the directory of your git respository, and type 

```bash
git submodule add git@github.com:uw-pluverse/pluverse-latex-style-guide.git
```

Then in your `main.tex`, type the following text to use the pluverse preamble files,
where `constants.tex` is a file in your project that stores all your project-specific
constants.

```tex
\input{pluverse-latex-style-guide/macro/pluverse-preamble.tex}
\input{constants}
\input{pluverse-latex-style-guide/macro/pluverse-preamble-end.tex}
```


### Cloning your project with submodules

To clone a Git repository along with all its submodules, 
you can use the `--recurse-submodules` flag with the `git clone` command. 
This ensures that all submodules are initialized 
and updated to match the versions specified in the superproject.

Here's the command:

```sh
git clone --recurse-submodules <repository_url>
```

Replace `<repository_url>` with the URL of the repository you want to clone.

### Cloning submodules alone

If you have already cloned a repository without its submodules, you can initialize and update the submodules separately using the following commands:

```sh
git submodule update --init --recursive
```

This will initialize, fetch, and checkout the submodules.


### Updating submodules

Update the submodules to the latest commit from the upstream repository (if the submodule repository has new commits):

```
git submodule update --remote --merge
```


# Tools, Files and Formats

### Use a git repository for collaboration.

- Git is much better at tracking changes than overleaf.

- You can use TexStudio, vim or other editors locally and push you changes to the remote git repository.

### Use a grammar checker.

If you are using Texstudio, please follow this:  https://tex.stackexchange.com/a/282571.

### Short Column Width

Keep a line short. I would recommend to break a line at 60. The benefits of doing this are

- Friendly to version control system. Easy to diff.
- Better bi-directional mapping between the output pdf file and the latex source.
- Friendly to the editor. No need to use the editor's wrapping functionality.

### Decompose a single BIG .tex file into multiple .tex files

- Friendly to version control system. Easy to diff. Minimize merge conflicts.
- Better organization of the paper, for example, each section is in its own file.

### Have a main.tex file

- Easy to identify the entry of the tex project.

### [Deprecated] Install Pluverse macro files

- Enter your latex directory, and run the following command

```bash
$ wget https://raw.githubusercontent.com/uw-pluverse/pluverse-latex-style-guide/master/macro/update-pluverse-macros.sh
$ chmod +x update-pluverse-macros.sh
$ ./update-pluverse-macros.sh
```






# Writing

### Capitalize words in your titles properly.

Use [this website](https://capitalizemytitle.com/style/APA/) to check whether your title conforms. Note that this rule applies to paper titles, subtitles, and all (sub)section titles.

### Use \emph{} to emphasize a text, other than \textit.

- Purpose: This command is used to emphasize text. It is semantically meaningful and is intended to emphasize text in a context-sensitive way.
-	Usage: The text inside the braces {} will be emphasized.
-	Behavior: The \emph command is context-sensitive. If used inside already emphasized text (e.g., inside another \emph), it will typically de-emphasize the text (e.g., change it back to the normal style).

### Use '~' between the words and '\cite', and '\ref'.

This allows the citation or the figure label to stay together with the previous word with a whitespace in between.

- `A and B developed a new approach~\cite{paper-id}`
- `Figure~\ref{figure-label} shows the overall framework.`

### Capitalize Figure and Table in 'Figure~\ref{xxx}' and 'Table~\ref{xxx}'

Correct: `In Figure 1, we know ...`

Wrong: `In figure 1, we know ...`

### Label Naming Convention

* Table: \label{tbl:...}
* Subtable: \label{subtbl:...}
* Figure: \label{fig:...}
* Subfigure: \label{subfig:...}
* Section: \label{sec:...}
* Subsection: \label{subsec:...}
* Subsubsection: \label{subsubsec:...}
* Algorithm: \label{alg:...}
* Line: \label{line:...}

### Put captions above tables, and below figures.

This applies to most of the proceeding formats.

### Capitalize the caption for meaningful words.

The first word in caption of Table/Figure should be capitalized, but not for preposition and conjunction words.

For example, it should be `The Effectiveness of ADF in Three Datasets`.

Here is a detailed guideline from the feedback from a proceeding publisher:

Headline-style capitalization should be used.

**Capitalize**:

 - first and last word, first word after a colon
 - all major words (nouns, pronouns, verbs, adjectives, adverbs)

**Lowercase**:

 - articles (the, a, an)
 - prepositions (regardless of length)
 - conjunctions (and, but, for, or, nor)
 - to, as

Note: 
1. The word immediately preceding the hyphen should be capitalized. For example, it should be `Learning-Based Approach`. An exception is `X-ray`, instead of `X-Ray`.


### Always use vector graphs and use the right font in the graphs.

- Try to avoid using `.png`, `.jpg` and `.bmp`, because they look blury when zoomed in.

- Always use `.eps` or `.pdf`.

- Make sure the font in the figure is the same font.

### Carefully select the color and the markers in the figure.

The color and markers of figures, especially for the line chart and bar chart, should be able to distinguished in black-white printing.

These three websites can help you pick colors:

* [Coloring for Colorblindness](https://davidmathlogic.com/colorblind/#%23D81B60-%231E88E5-%23FFC107-%23004D40)

* [Data Viz Color Palette Generator](https://learnui.design/tools/data-color-picker.html) 

* [ColorBrewer: Color Advice for Maps](https://colorbrewer2.org/)

Remember to pick the color that is colorblindness-friendly and print-friendly.

### The font of the text in figures should be same as the font of main content.

Usually it should be Times New Roman.

By default, the font of the figures generated by Python matplotlib is Type-3 font, which is not accepted by the checking system of camera ready. Use the following commands in Python to avoid this.

```python3
import matplotlib
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42
```


### The font size of text in figures and table should not be larger than the font size of main content

Be carefully when you use resize.


### Use booktab table style.

For table, you can use this website https://www.tablesgenerator.com/. Now it is more common to use the "booktab table style".

[Here](reference/guide-tables.pdf) is a guide on how to design good-looking tables in LaTex by [Markus Püschel](https://people.inf.ethz.ch/markusp/teaching/guides/guide-tables.pdf).

### Adjust the horizontal/vertical space insides table

Use `\setlength` and `\arraystretch` to change the horizontal spacing (column separation) and the vertical spacing (row separation), respectively.

```
\setlength{\tabcolsep}{20pt}
\renewcommand{\arraystretch}{1.5}
```


### Write numbers in words.

If you use numbers such as `1`, `2`, `100`, and `1000`, you should write `one`, `two`, `one hundred`, and `one thousand`.
If you use number such as `2021`, it should write it as `2,021`

More information can be found [here](https://www.dcu.ie/sites/default/files/students_learning/docs/WC_Numbers-in-academic-writing.pdf)

### Do not use abbreviations.

Do not use English word abbreviations, such as `2nd`, `no.` and `approx.`. Use the full words instead, such as `second`, `number` and `approximately`. You should also avoid using `they're`, `don't`, `can't`, etc; instead you should use `they are`, `do not`, `cannot`.

Note that you are encouraged to use Latin abbreviations, such as `i.e.`, `e.g.`.

### Use the word "benchmark" correctly.

A benchmark is a test that measures the performance of hardware or software. For example, in the evaluation of Perses, each subject (e.g., clang-22382) can be considered as a benchmark. A set that includes multiple benchmarks is called a benchmark suite.

Reference: [SPEC CPU2006](https://dl.acm.org/doi/pdf/10.1145/1241601.1241625) and [SPEC CPU2007](https://www.spec.org/cpu2017/Docs/overview.html#benchmarks)

### Evaluation Terminology

- Ratio
    - A ratio says how much of one thing there is compared to another thing.
    It shows that the number of times one value contains or is contained within the other.
    - Formula:
    $A/B$
    - Part-to-Part vs Part-to-Whole
        - Part-to-Part: comparing one part to another part
            - e.g., ratio of bug discovered to bug missed = 2 : 3 or 2/3
        - Part-to-Whole: comparing one part to the whole lot
            - e.g., ratio bug discovered to all bugs = 2 : 5 or 2/5
    - E.g., Perses is 2.07x faster, produces 1.13x smaller results, and reduces 3.99x fewer queries than HDD.
    - [link](https://www.mathsisfun.com/numbers/ratio.html)
- Percentage change / Relative change / Relative difference
    - This shows that change as a percent of the old value.
    When the new value is greater then the old value,
    it is a percentage increase, otherwise it is a decrease.
    - Watchout:
        - A 10% increase from 100 is an increase of 10. BUT! A 10% reduction from 110 is a reduction of 11.
    - Formula:
    $(New Value − Old Value) / Old Value \times100\%$
    - E.g., Perses’s results are respectively 2% and 45% in size of those from DD and HDD.
    - Acronym: %Change
    - [link](https://www.mathsisfun.com/numbers/percentage-change.html)
- Percentage error
    - The difference between Approximate and Exact Values, as a percentage of the Exact Value.
    Percentage Error is all about comparing a guess or estimate to an exact value.
    - Formula:
    $(Approximate Value − Exact Value) / Exact Value \times100\%$
    - E.g., A bug detecting tool only found 95 bugs out of a 100. The tool has a 0.05% error.
    - Acronym: %Error
    - [link](https://www.mathsisfun.com/numbers/percentage-error.html)
- Percentage difference
    - The difference between two values divided by the average of the two values.
    Percentage Difference is used when both values mean the same kind of thing
    (for example the heights of two people).
    - Formula:
    $|First Value − Second Value| / |(First Value + Second Value)/2| * 100\%$
    - Acronym: %Diff or %Difference
    - [link](https://www.mathsisfun.com/percentage-difference.html)

##### Compare & Contrast
- Ratio: how much of one value is compared to another value
- Percentage change: compare an Old Value to a New Value
- Percentage error: compare an Approximate Value to an Exact Value
- Percentage difference: both values mean the Same Kind of thing (rarely used)
- Commonly, we prefer using ratio and %change in our evaluations. %error and %diff is used less frequently as they only apply to specific scenarios.
- Also see this [link](https://www.mathsisfun.com/data/percentage-difference-vs-error.html)

### Try to use bib files from ACM Digitial Library and IEEE Xplore.

Please try to download the paper and bib from ACM Digitial Library and IEEE Xplore.

DBLP is a good source for tracking a person's publication records and download bib files. Just be careful: sometimes a paper can appear twice if it is published both in conference/journal and arxiv. Please DO NOT select the one from arxiv.

Avoid the citation from arxiv, if possible.

### No citations in `abstract`

You should not cite any papers in the `Abstract` section.

### Use macros for constants

If you have some numbers, or string literals (e.g., functions) used throughout your paper, create a macro, and use that macro instead.

For example, if you repeatedly mention `Our approach is 35% faster than the state of the art.`, then it is better to refactor your LaTeX into the following

```
usepackage{xspace}
\newcommand{\PerformanceGain}{35\%\xspace}

......
Our approach is \PerformanceGain faster than the state of the art.
```
You can also use Latex to compute simple arithmetics.
```
\newcommand{\cSizeDecRateProjVsPerses}{%
    \pgfmathparse{(1 - \cSizeAvgProjValue/\cSizeAvgPersesValue)*100}
    \pgfmathprintnumber{\pgfmathresult}\%\xspace%
}
```



### Quote.

Single quotation marks are produced in LaTeX using  ` and  '.

Double quotation marks are `` and ''.

For example

```tex
`Something'
``The title of this paper is hope''
```

### Avoid trailing whitespaces

Trailing whitespaces are not friendly to git, because it introduce unnecessary diff.

If you use TeXStudio, you can enable removing trailing whitespaces on save in the `setting`.

* On MacOs, From the top menu, click `TeXStudio->Preference->Editor`, and tick `Remove Trailing Whitespace on Save`
* Not sure how to set this on other OS.


### Referring to a section, subsection, or a subsubsection

Use `\S\ref{section-label}`. Note that there is no space between `\S` and `\ref{section-label}`

### Words in the math mode, e.g., `\[\]` or `$$`

If you want to use words in a math formula, remember to use \textit to wrap the word.

For example, `$time = ComptueTime(t + 1)$` should be written as `$\textit{time} = \textit{ComputeTime}(t + 1)$`

### ACKNOWLEDGMENTS should not be numbered

ACKNOWLEDGMENTS section shall not have a section number. It should be added using the environment `\begin{ack} \end{ack}` instead of `\section{ack}`

Please note it is ACKNOWLEDGMENTS, not ACKNOWLEDG**E**MENTS.

### Do not start a subsection title right after a section title.


```tex
\section{Approach}
ADD SOMETHING HERE!
\subsection{Overview}
```

### Use \usepackage{subcaption} to include multiple figures in one figure environment.

TBD: need to have an example here.

### Use cleveref

Cleveref automatically determine the type of cross-reference and fill in the appropate
cross-reference (Figure, Table, Section, etc.).

To use cleveref, load the cleveref package last and use the following configurations.
```
\usepackage{cleveref} % This package must be loaded in the end.

\Crefname{algocf}{Algorithm}{Algorithms}
\crefname{algocf}{Algorithm}{Algorithms}
\Crefname{algorithm}{Algorithm}{Algorithms}
\crefname{algorithm}{Algorithm}{Algorithms}
\Crefname{figure}{Figure}{Figures}
\crefname{figure}{Figure}{Figures}
\crefname{listing}{Listing}{Listings}
\Crefname{listing}{Listing}{Listings}
\Crefname{table}{Table}{Tables}
\crefname{table}{Table}{Tables}
\crefname{thm}{Theorem}{Theorems}
\Crefname{thm}{Theorem}{Theorems}

% https://tex.stackexchange.com/questions/81634/cleveref-configure-symbol-for-all-sectioning-types-once-time
\crefformat{chapter}{\S#2#1#3}
\crefmultiformat{chapter}{\S\S#2#1#3}{ and~#2#1#3}{, #2#1#3}{, and~#2#1#3}

\crefformat{section}{\S#2#1#3}
\crefmultiformat{section}{\S\S#2#1#3}{ and~#2#1#3}{, #2#1#3}{, and~#2#1#3}
```

When referencing labels, instead of using \ref, use \cref.


### that v.s. which

* In a defining clause, use that.
* In non-defining clauses, use which.

[grammarly post](https://www.grammarly.com/blog/which-vs-that/)

### always use `first`, `second`, but not `firstly`, `secondly`.

[Merriam Webster](https://www.merriam-webster.com/words-at-play/first-or-firstly#:~:text=Even%20though%20they%20are%20both,the%20best%20bet%20for%20most)

### use `less` with uncountable nouns and `fewer` with plural countable nouns

`Less` is sometimes used with a plural countable noun (e.g., less cars), particularly in conversation. However, this is grammatically incorrect.

### use `(see Section 3)` or `(details in Section 3)` for forward reference.

Note that 
"cf." is not the appropriate abbreviation for referring to details in a specific section. "cf." stands for "confer" in Latin, meaning "compare" or "consult," and is used to direct the reader to other material for comparison, not for additional details.

### It is correct to use either `positive` or `comparative` form with `compared to` 

For example, 

`ME:` 
> Which version is grammatically correct?

  1. Company A has a larger market share, compared to Company B.
  2. Company A has a large market share, compared to Company B.
  

`ChatGPT:`
> The first sentence is grammatically correct:

  Company A has a larger market share, compared to Company B.

  This sentence correctly uses the comparative form "larger" to compare the market
  shares of Company A and Company B. The second sentence,
  "Company A has a large market share, compared to Company B," is not incorrect, but it is less precise because it does not explicitly indicate the comparative nature of the market shares.


[Merriam Webster](https://www.merriam-webster.com/sentences/compared%20to)

[Stackexchange](https://ell.stackexchange.com/questions/325358/comparatives-in-comparison-to-compared-to#:~:text=The%20answerer%20says%3A%20%22It%20is,to%20or%20simply%20compared%20to%22.)


### avoid using `try`, use `attempt`, `strive`, etc.

`Try` is an informal word.

### avoid using `very`

For example, `very effective` can be replaced with `highly effective`. 

You might also consider `remarkably effective` or `amazingly effective`, though Chengnian does not like them much.

### avoid using `lots of` and `a lot of`

From the [grammarly post](https://www.grammarly.com/blog/lots-or-plenty-of/)


> Although lots and plenty are acceptable in academic writing, their
> usage is considered to be informal. In formal academic writing, it
> is more appropriate to use many, much, and more.


### no extra period after `etc.` if `etc.` is at the end of a sentence.

Correct: `X......, etc.`

Incorrect: `X......., etc..`

### use article words before countable singular noun

When a noun is countable and singular, you need to use `a/an/the` to quantify it.

### no mixed use of `such as` and `etc` together

These two phrases cannot be used together. For example, `such as apple, organge, etc.`.

If you use `such as`, then you should strictly follow the structure `such as A, B, C and D`.

### never start with a sentence with a number or lower-case letters.

For example

```
ddmin can handle ...;
```

In stead, you should write

```
The algorithm ddmin can handle ...;
```

Similarly, instead of writing `1 apple a day is good for your body`, you should write `One apple a day ...`.

### banned words

"have no clue", reason: informal idiom, [see](https://dictionary.cambridge.org/dictionary/english/not-have-a-clue-have-no-clue)




### Other files in this repo

* `comment_macror.tex`, to leave comments
* `auto_counter_macro.tex`,  If you have a lot of findings/reponses, you can use the following commands to automatic generate counters.
* `abbr_macros.tex`, macro for common macros.
* `response_letter.tex`, a rough template for journal response letter.


# Tricks

### Use \SetKwFunction inside a caption of an algorithm2e environment

Use `\protect` before the function macro, e.g., `\caption{\protect\Fn my function}`

See [here](https://tex.stackexchange.com/questions/291911/how-can-i-use-an-algorithm2e-function-macro-inside-an-algorithm2e-caption)

# Pluverse Specifics

### Using Commenting Macros

The `pluverse-preamble.tex` file provides commenting macros, such as `\cn{}`. When using these macros, ensure that each macro begins on a new line and that the closing parenthesis is followed by another new line. If your comment spans multiple lines, make sure to use indentation within the macro for clarity.

For example, the following adheres to the recommended style:

```tex
\cn{This is a one-line comment.}
```

```tex
\cn{This is a multi-line comment.
    line 2 % Note the indentation here to highlight the current line is a comment.
    line 3 % Note the indentation here to highlight the current line is a comment.
}
```

We recommend this style because it makes it easier to comment out or remove these macros. For instance, in the following LaTeX code, it is difficult to remove the comment macros cleanly:

```tex
Main text here. \cn{My comment is embedded here, and it is not easy to delete.} Main text here.
```

This example demonstrates a similar issue:

```tex
Main text here. \cn{My comment spans two lines
} Main text here.
```

#### Resolving Comments

If you receive a comment from a reviewer and you address it,
then do not delete the comment but **leave another comment \YourCommentMacro{done}**.
Doing this can notify your reviewer of your response. If the reviewer
feels that their question is well addressed, the reviewer will
comment out the macro.

For example, assume I am a reviewer and leave the following comment

```tex
\cn{My comment here.}
```

Then you address my comment and leave a `done` comment

```text
\cn{My comment here.}
\victor{done}
```

If I feel my question is addressed, I will simply comment out all comment macros like the following

```tex
%\cn{My comment here.}
%\victor{done}
```

