## Short Column Width

Keep a line short. I would recommend to break a line at 60. The benefits of doing this are

- Friendly to version control system. Easy to diff. 
- Better bi-directional mapping between the output pdf file and the latex source.
- Friendly to the editor. No need to use the editor's wrapping functionality.

## Decompose a single BIG .tex file into multiple .tex files

- Friendly to version control system. Easy to diff. Minimize merge conflicts.
- Better organization of the paper, for example, each section is in its own file.

## Have a main.tex file

- Easy to identify the entry of the tex project.

## Use '~' between the words and '\cite', and '\ref'.

This allows the citation or the figure label to stay together with the previous word with a whitespace in between.

- `A and B developed a new approach~\cite{paper-id}`
- `Figure~\ref{figure-label} shows the overall framework.`

## Put captions above tables, and below figures.

This applies to most of the proceeding formats.

## Capitalize the caption for meaningful word.

The first word in caption of Table/Figure should be capitalized, but not for preposition and conjunction word. 

For example, it should be `The Effectiveness of ADF in Three Datasets`.

## Always use vector graphs and use the right font in the graphs.

- Try to avoid using `.png`, `.jpg` and `.bmp`, because they look blury when zoomed in.

- Always use `.eps` or `.pdf`.

- Make sure the font in the figure is the same font.

## Carefully select the color and the markers in the figure. 

The color and markers of figures, especially for the line chart and bar chart, should be able to distinguished even in black-white printing.
This website can help you pick color https://learnui.design/tools/data-color-picker.html

## Use booktab table style. 

For table, you can use this website.https://www.tablesgenerator.com/. Now it is more common to use the "booktab table style".

## Write numbers in words.

If you use numbers such as `1`, `2`, `100`, and `1000`, you should write `one`, `two`, `one hundred`, and `one thousand`.
If you use number such as `2021`, it should write it as `2,021`

More information can be found [here](https://www.dcu.ie/sites/default/files/students_learning/docs/WC_Numbers-in-academic-writing.pdf)

## Avod using abbreviations.

Do not use English word abbreviations, such as `2nd`, `no.` and `approx.`. Use the full words instead, such as `second`, `number` and `approximately`.

Note that you are encouraged to use Latine abbreviations, such as `i.e.`, `e.g.`.

## Try to use bib files from ACM Digitial Library and IEEE Xplore.

Avoid the citation from arxiv, if possile.

## No citations in `abstract`

You should not cite any paper in the `Abstract` section.

## Use macros for constants

If you have some numbers used throughout your paper, create a macro, and use that macro instead.

For example, if you repeatedly mention `Our approach is 35% faster than the state of the art.`, then it is better to refactor your LaTeX into the following

```
usepackage{xspace}
\newcommand{\PerformanceGain}{35\%\xspace}
......
Our approach is \PerformanceGain faster than the state of the art.
```

## Use language tool to check the grammar.

If you are using Texstudio, please follow this:  https://tex.stackexchange.com/a/282571.

## Quote.

Single quotation marks are produced in LaTeX using  ` and  '.

Double quotation marks are `` and ''.

For example

```tex
`Something'
``The title of this paper is hope''
```

## Avoid trailing whitespaces

Trailing whitespaces are not friendly to git, because it introduce unnecessary diff.

If you use TeXStudio, you can enable removing trailing whitespaces on save in the `setting`.

* On MacOs, From the top menu, click `TeXStudio->Preference->Editor`, and tick `Remove Trailing Whitespace on Save`
* Not sure how to set this on other OS. 


## Words in the math mode, e.g., `\[\]` or `$$`

If you want to use words in a math formula, remember to use \textit to wrap the word.

For example, `$time = ComptueTime(t + 1)$` should be written as `$\textit{time} = \textit{ComputeTime}(t + 1)$`

## Other files in this repo

* `comment_macror.tex`, to leave comments
* `auto_counter_macro.tex`,  If you have a lot of findings/reponses, you can use the following commands to automatic generate counters.
* `abbr_macros.tex`, macro for common macros.
