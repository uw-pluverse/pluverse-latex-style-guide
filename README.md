(in progress of restrucing the guide)

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






# Writing 

### Capitalize words in your titles properly.

Use [this website](https://capitalizemytitle.com/style/APA/) to check whether your title conforms. Note that this rule applies to paper titles, subtitles, and all (sub)section titles.



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

### Capitalize the caption for meaningful word.

The first word in caption of Table/Figure should be capitalized, but not for preposition and conjunction word. 

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

### Always use vector graphs and use the right font in the graphs.

- Try to avoid using `.png`, `.jpg` and `.bmp`, because they look blury when zoomed in.

- Always use `.eps` or `.pdf`.

- Make sure the font in the figure is the same font.

### Carefully select the color and the markers in the figure. 

The color and markers of figures, especially for the line chart and bar chart, should be able to distinguished even in black-white printing.

These two websites can help you pick color https://learnui.design/tools/data-color-picker.html and https://colorbrewer2.org/. 

Remember to pick the color that is print-friendly.

### The font of the text in figures should be same as the font of main content.

Usually it should be Times New Roman.


### The font size of text in figures and table should not be larger than the font size of main content

Be carefully when you use resize.


### Use booktab table style. 

For table, you can use this website https://www.tablesgenerator.com/. Now it is more common to use the "booktab table style".

[Here](reference/guide-tables.pdf) is a guide on how to design good-looking tables in LaTex by [Markus Püschel](https://people.inf.ethz.ch/markusp/teaching/guides/guide-tables.pdf).




### Write numbers in words.

If you use numbers such as `1`, `2`, `100`, and `1000`, you should write `one`, `two`, `one hundred`, and `one thousand`.
If you use number such as `2021`, it should write it as `2,021`

More information can be found [here](https://www.dcu.ie/sites/default/files/students_learning/docs/WC_Numbers-in-academic-writing.pdf)

### Avoid using abbreviations.

Do not use English word abbreviations, such as `2nd`, `no.` and `approx.`. Use the full words instead, such as `second`, `number` and `approximately`. You should also avoid using `they're`, `don't`, `can't`, etc; instead you should use `they are`, `do not`, `cannot`. 

Note that you are encouraged to use Latin abbreviations, such as `i.e.`, `e.g.`.

### Try to use bib files from ACM Digitial Library and IEEE Xplore.

Please try to download the paper and bib from ACM Digitial Library and IEEE Xplore. 

DBLP is a good source for tracking a person's publication records and download bib files. Just be careful: sometimes a paper can appear twice if it is published both in conference/journal and arxiv. Please DO NOT select the one from arxiv. 

Avoid the citation from arxiv, if possible. 

### No citations in `abstract`

You should not cite any papers in the `Abstract` section.

### Use macros for constants

If you have some numbers used throughout your paper, create a macro, and use that macro instead.

For example, if you repeatedly mention `Our approach is 35% faster than the state of the art.`, then it is better to refactor your LaTeX into the following

```
usepackage{xspace}
\newcommand{\PerformanceGain}{35\%\xspace}
......
Our approach is \PerformanceGain faster than the state of the art.
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

\Crefname{table}{Table}{Tables}
\crefname{table}{Table}{Tables}
\Crefname{figure}{Figure}{Figures}
\crefname{figure}{Figure}{Figures}
\Crefname{algocf}{Algorithm}{Algorithms}
\crefname{algocf}{Algorithm}{Algorithms}
\Crefname{algorithm}{Algorithm}{Algorithms}
\crefname{algorithm}{Algorithm}{Algorithms}

% https://tex.stackexchange.com/questions/81634/cleveref-configure-symbol-for-all-sectioning-types-once-time
\crefformat{chapter}{\S#2#1#3}
\crefmultiformat{chapter}{\S\S#2#1#3}{ and~#2#1#3}{, #2#1#3}{, and~#2#1#3}

\crefformat{section}{\S#2#1#3}
\crefmultiformat{section}{\S\S#2#1#3}{ and~#2#1#3}{, #2#1#3}{, and~#2#1#3}
```

When referencing labels, instead of using \ref, use \cref.

### Other files in this repo

* `comment_macror.tex`, to leave comments
* `auto_counter_macro.tex`,  If you have a lot of findings/reponses, you can use the following commands to automatic generate counters.
* `abbr_macros.tex`, macro for common macros.
* `response_letter.tex`, a rough template for journal response letter.  

